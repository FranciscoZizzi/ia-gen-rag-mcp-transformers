"""Contract of recuperar.py: the command the graders run on the hidden test questions."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import recuperar

REPO_ROOT = Path(__file__).resolve().parents[1]
DEV_QUESTIONS = REPO_ROOT / "datos" / "preguntas_recuperacion_dev.jsonl"

LEXICAL_CONFIG = {
    "corpus_dir": "datos/corpus",
    "encoder": {"type": "hashing_bow"},
    "chunking": {"strategy": "paragraph"},
    "selection": {"top_k": 3},
}


@pytest.fixture
def config_path(tmp_path):
    path = tmp_path / "retriever.json"
    path.write_text(json.dumps(LEXICAL_CONFIG), encoding="utf-8")
    return path


def run_recuperar(questions: Path, output: Path, config: Path) -> None:
    recuperar.main(["--preguntas", str(questions), "--salida", str(output), "--config", str(config)])


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_official_evaluator_accepts_the_output(tmp_path, config_path):
    output = tmp_path / "resultados.jsonl"
    run_recuperar(DEV_QUESTIONS, output, config_path)

    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / "evaluar" / "evaluar.py"), "recuperacion",
         "--preguntas", str(DEV_QUESTIONS), "--resultados", str(output)],
        capture_output=True, text=True, check=False,
    )

    assert completed.returncode == 0, completed.stderr
    summary = json.loads((tmp_path / "resultados.jsonl.eval.json").read_text(encoding="utf-8"))["resumen"]
    assert summary["recall"] > 0


def test_writes_one_line_per_question_with_the_same_ids_in_input_order(tmp_path, config_path):
    by_id = {question["id"]: question for question in read_jsonl(DEV_QUESTIONS)}
    questions = tmp_path / "preguntas.jsonl"
    questions.write_text("".join(json.dumps(by_id[qid], ensure_ascii=False) + "\n" for qid in ["R07", "R02", "R15"]),
                         encoding="utf-8")
    output = tmp_path / "resultados.jsonl"

    run_recuperar(questions, output, config_path)

    rows = read_jsonl(output)
    assert [row["id"] for row in rows] == ["R07", "R02", "R15"]
    assert all(row["fragmentos"] and all(isinstance(text, str) and text for text in row["fragmentos"]) for row in rows)


def test_never_reads_the_evidence(tmp_path, config_path):
    with_evidence = read_jsonl(DEV_QUESTIONS)
    without_evidence = tmp_path / "preguntas_sin_evidencia.jsonl"
    without_evidence.write_text(
        "".join(json.dumps({"id": q["id"], "pregunta": q["pregunta"]}, ensure_ascii=False) + "\n" for q in with_evidence),
        encoding="utf-8")

    run_recuperar(DEV_QUESTIONS, tmp_path / "con.jsonl", config_path)
    run_recuperar(without_evidence, tmp_path / "sin.jsonl", config_path)

    assert read_jsonl(tmp_path / "sin.jsonl") == read_jsonl(tmp_path / "con.jsonl")
