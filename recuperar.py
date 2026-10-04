"""Part 1 contract: python3 recuperar.py --preguntas <questions.jsonl> --salida <results.jsonl>

Writes one line per question, {"id": ..., "fragmentos": [...]}, fragments ordered by relevance.
The retrieval setup comes from config/retriever.json (see SPEC.md).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from rag.config import load_config
from rag.io import read_jsonl, write_jsonl
from rag.retriever import Retriever

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = REPO_ROOT / "config" / "retriever.json"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Retrieve the most relevant corpus fragments for each question.")
    parser.add_argument("--preguntas", type=Path, required=True, help="questions JSONL with id and pregunta")
    parser.add_argument("--salida", type=Path, required=True, help="output JSONL with id and fragmentos")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="retriever configuration JSON")
    args = parser.parse_args(argv)

    questions = read_jsonl(args.preguntas)
    retriever = Retriever.from_config(load_config(args.config), base_dir=REPO_ROOT)
    results = retriever.search_many([question["pregunta"] for question in questions])
    write_jsonl(args.salida, (
        {"id": question["id"], "fragmentos": [fragment.text for fragment in fragments]}
        for question, fragments in zip(questions, results)
    ))


if __name__ == "__main__":
    main()
