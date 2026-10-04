"""chunk_corpus: how documents become the fragments the grader checks for evidence."""
import importlib.util
from pathlib import Path

import pytest

from rag.chunking import chunk_corpus
from rag.config import ChunkingConfig
from rag.corpus import load_corpus, parse_document
from rag.io import read_jsonl

REPO_ROOT = Path(__file__).resolve().parents[1]

SAMPLE = parse_document("guia", """# Guía de prueba

Introducción breve.

## Horarios

Abre a las 8:00. Cierra a las 20:00.

Los sábados abre de 9:00 a 12:00.

## Requisitos

- Traer DNI.
- Traer la orden médica.
""")


def chunk_sample(**config) -> list[tuple[str | None, str]]:
    return [(chunk.section, chunk.text) for chunk in chunk_corpus([SAMPLE], ChunkingConfig(**config))]


def test_paragraph_strategy_emits_each_block_verbatim():
    assert chunk_sample(strategy="paragraph") == [
        (None, "Introducción breve."),
        ("Horarios", "Abre a las 8:00. Cierra a las 20:00."),
        ("Horarios", "Los sábados abre de 9:00 a 12:00."),
        ("Requisitos", "- Traer DNI.\n- Traer la orden médica."),
    ]


def test_sentence_strategy_emits_one_chunk_per_sentence_and_list_item():
    assert chunk_sample(strategy="sentence") == [
        (None, "Introducción breve."),
        ("Horarios", "Abre a las 8:00."),
        ("Horarios", "Cierra a las 20:00."),
        ("Horarios", "Los sábados abre de 9:00 a 12:00."),
        ("Requisitos", "Traer DNI."),
        ("Requisitos", "Traer la orden médica."),
    ]


def test_fixed_strategy_packs_whole_sentences_up_to_max_chars():
    assert chunk_sample(strategy="fixed", max_chars=40) == [
        (None, "Introducción breve. Abre a las 8:00."),
        ("Horarios", "Cierra a las 20:00."),
        ("Horarios", "Los sábados abre de 9:00 a 12:00."),
        ("Requisitos", "Traer DNI. Traer la orden médica."),
    ]


def test_fixed_strategy_repeats_trailing_sentences_only_when_a_new_one_still_fits():
    assert chunk_sample(strategy="fixed", max_chars=40, overlap_sentences=1) == [
        (None, "Introducción breve. Abre a las 8:00."),
        ("Horarios", "Abre a las 8:00. Cierra a las 20:00."),
        ("Horarios", "Los sábados abre de 9:00 a 12:00."),
        ("Requisitos", "Traer DNI. Traer la orden médica."),
    ]


def test_section_strategy_keeps_each_section_whole_when_it_fits():
    assert chunk_sample(strategy="section", max_chars=700) == [
        (None, "Introducción breve."),
        ("Horarios", "Abre a las 8:00. Cierra a las 20:00.\n\nLos sábados abre de 9:00 a 12:00."),
        ("Requisitos", "- Traer DNI.\n- Traer la orden médica."),
    ]


@pytest.mark.parametrize("max_chars, expected", [
    (40, [
        (None, "Introducción breve."),
        ("Horarios", "Abre a las 8:00. Cierra a las 20:00."),
        ("Horarios", "Los sábados abre de 9:00 a 12:00."),
        ("Requisitos", "- Traer DNI.\n- Traer la orden médica."),
    ]),
    (30, [
        (None, "Introducción breve."),
        ("Horarios", "Abre a las 8:00."),
        ("Horarios", "Cierra a las 20:00."),
        ("Horarios", "Los sábados abre de 9:00 a 12:00."),
        ("Requisitos", "Traer DNI."),
        ("Requisitos", "Traer la orden médica."),
    ]),
])
def test_section_strategy_splits_long_sections_by_block_then_by_sentence(max_chars, expected):
    assert chunk_sample(strategy="section", max_chars=max_chars) == expected


def test_metadata_header_names_the_document_and_the_section():
    intro, horarios = chunk_corpus([SAMPLE], ChunkingConfig(strategy="paragraph"))[:2]

    assert horarios.render(with_metadata=True) == "Guía de prueba — Horarios\nAbre a las 8:00. Cierra a las 20:00."
    assert intro.render(with_metadata=True) == "Guía de prueba\nIntroducción breve."
    assert horarios.render(with_metadata=False) == "Abre a las 8:00. Cierra a las 20:00."


def _grader_norm():
    """The grader's own normalization, loaded from evaluar/evaluar.py without modifying it."""
    spec = importlib.util.spec_from_file_location("evaluar", REPO_ROOT / "evaluar" / "evaluar.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.norm


norm = _grader_norm()
CORPUS = load_corpus(REPO_ROOT / "datos" / "corpus")
DEV_EVIDENCE = [e for q in read_jsonl(REPO_ROOT / "datos" / "preguntas_recuperacion_dev.jsonl") for e in q["evidencia"]]
TRICKY_SENTENCES = [
    "Salud Integral Andina: cobertura total en internación; copago de consulta de 2.500 pesos.",
    "Las altas se dan de 10:00 a 12:00, después de la recorrida médica de la mañana.",
    "Nivel 3, amarillo (urgencia): atención dentro de los 60 minutos.",
]
EXPERIMENT_CONFIGS = [
    ChunkingConfig("paragraph"),
    ChunkingConfig("sentence"),
    ChunkingConfig("section", max_chars=400),
    ChunkingConfig("section", max_chars=700),
    *(ChunkingConfig("fixed", max_chars=size, overlap_sentences=overlap) for size in (200, 400, 800) for overlap in (0, 1)),
]


@pytest.mark.parametrize("config", EXPERIMENT_CONFIGS, ids=repr)
def test_every_dev_evidence_and_tricky_sentence_fits_whole_in_some_chunk(config):
    chunks = [norm(chunk.text) for chunk in chunk_corpus(CORPUS, config)]

    missing = [text for text in DEV_EVIDENCE + TRICKY_SENTENCES if not any(norm(text) in chunk for chunk in chunks)]

    assert missing == []


@pytest.mark.parametrize("config", EXPERIMENT_CONFIGS, ids=repr)
def test_no_chunk_is_empty(config):
    assert all(chunk.text.strip() for chunk in chunk_corpus(CORPUS, config))


def test_chunks_never_span_two_documents():
    chunks = chunk_corpus(CORPUS, ChunkingConfig("fixed", max_chars=100_000))

    assert sorted(chunk.doc_id for chunk in chunks) == sorted(document.doc_id for document in CORPUS)
