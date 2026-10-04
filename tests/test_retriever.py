"""Retriever: the library seam that recuperar.py, buscar_documentos (Part 2) and the MCP server share."""
from dataclasses import replace

from rag.chunking import chunk_corpus
from rag.config import ChunkingConfig, EncoderConfig, RerankerConfig, RetrieverConfig, SelectionConfig
from rag.corpus import parse_document
from rag.encoders import HashingBowEncoder
from rag.retriever import Retriever

DOCUMENT = parse_document("guia", """# Guía de prueba

Introducción breve.

## Horarios

Abre a las 8:00. Cierra a las 20:00.

Los sábados abre de 9:00 a 12:00.

## Requisitos

- Traer DNI.
- Traer la orden médica.
""")
PARAGRAPHS = ChunkingConfig(strategy="paragraph")
CHUNKS = chunk_corpus([DOCUMENT], PARAGRAPHS)


def lexical_retriever(chunks=CHUNKS, chunking=PARAGRAPHS, top_k=1, reranker_config=None, **kwargs) -> Retriever:
    config = RetrieverConfig(EncoderConfig("hashing_bow"), chunking, SelectionConfig(top_k=top_k), reranker=reranker_config)
    return Retriever(chunks, kwargs.pop("encoder", HashingBowEncoder()), config, **kwargs)


def test_ranks_every_chunk_by_descending_similarity():
    ranking = lexical_retriever().rank_many(["traer la orden médica"])[0]

    assert ranking[0].text == "- Traer DNI.\n- Traer la orden médica."
    assert sorted(scored.chunk.chunk_id for scored in ranking) == sorted(chunk.chunk_id for chunk in CHUNKS)
    assert [scored.score for scored in ranking] == sorted((scored.score for scored in ranking), reverse=True)


def test_search_returns_the_head_of_the_ranking_after_the_cut_off():
    retriever = lexical_retriever(top_k=2)
    query = "¿a qué hora abre los sábados?"

    assert retriever.search(query) == retriever.rank_many([query])[0][:2]


def test_fragments_carry_the_metadata_header_when_enabled():
    with_metadata = ChunkingConfig(strategy="paragraph", metadata=True)
    retriever = lexical_retriever(chunks=chunk_corpus([DOCUMENT], with_metadata), chunking=with_metadata)

    assert retriever.search("traer la orden médica")[0].text == (
        "Guía de prueba — Requisitos\n- Traer DNI.\n- Traer la orden médica.")


class CountingEncoder(HashingBowEncoder):
    """Counts passage batches: encoding passages is the expensive call at the Hugging Face boundary."""

    def __init__(self):
        super().__init__()
        self.passage_batches = 0

    def encode_passages(self, texts):
        self.passage_batches += 1
        return super().encode_passages(texts)


def test_reuses_cached_passage_embeddings_when_nothing_changed(tmp_path):
    first, second = CountingEncoder(), CountingEncoder()

    lexical_retriever(encoder=first, cache_dir=tmp_path)
    lexical_retriever(encoder=second, cache_dir=tmp_path)

    assert (first.passage_batches, second.passage_batches) == (1, 0)


def test_cache_never_serves_embeddings_of_an_older_corpus(tmp_path):
    lexical_retriever(cache_dir=tmp_path)
    *unchanged, last = CHUNKS
    edited = [*unchanged, type(last)(last.chunk_id, last.doc_id, last.title, last.section, "- Traer el carnet de vacunación.")]

    retriever = lexical_retriever(chunks=edited, cache_dir=tmp_path)

    assert retriever.search("carnet de vacunación")[0].text == "- Traer el carnet de vacunación."


class ShortestFirstReranker:
    """Stands in for a cross-encoder at the Hugging Face boundary: prefers shorter passages."""

    def rerank(self, query, candidates):
        return sorted((replace(scored, score=-float(len(scored.text))) for scored in candidates),
                      key=lambda scored: -scored.score)


def test_a_reranker_reorders_the_best_candidates_by_its_own_scores():
    retriever = lexical_retriever(reranker_config=RerankerConfig(model="fake", candidates=2),
                                  reranker=ShortestFirstReranker())

    ranking = retriever.rank_many(["traer la orden médica"])[0]

    assert [scored.text for scored in ranking] == ["Introducción breve.", "- Traer DNI.\n- Traer la orden médica."]
