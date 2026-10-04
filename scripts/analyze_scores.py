"""Explain the experiment numbers.

    python3 scripts/analyze_scores.py diagnose experimentos/grids/A-encoders.json --out experimentos/analisis/A.md
    python3 scripts/analyze_scores.py compare A-mbert-section700meta-k1 C-e5base-...

diagnose: for every (encoder, chunking) of a grid, the full ranking's hit@k and MRR, how far the chunk
with the evidence stands above the best other chunk, the spread of all cosine scores, truncation and
encoding time. compare: two runs question by question, with a paired bootstrap interval for the CR gap.
Evidence is used here only to label rankings, never to retrieve.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

os.environ.setdefault("TQDM_DISABLE", "1")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from rag.analysis import gold_rank, hit_rate, mean_reciprocal_rank, paired_bootstrap  # noqa: E402
from rag.chunking import chunk_corpus  # noqa: E402
from rag.config import ChunkingConfig, EncoderConfig, RetrieverConfig, SelectionConfig  # noqa: E402
from rag.corpus import load_corpus  # noqa: E402
from rag.encoders import build_encoder  # noqa: E402
from rag.io import read_jsonl  # noqa: E402
from rag.retriever import Retriever  # noqa: E402


def diagnose(grid_path: Path) -> str:
    grid = json.loads(grid_path.read_text(encoding="utf-8"))
    questions = read_jsonl(REPO_ROOT / grid["questions"])
    corpus_dir = grid.get("corpus_dir", "datos/corpus")
    documents = load_corpus(REPO_ROOT / corpus_dir)
    lines = ["| Encoder | Chunking | hit@1 | hit@3 | hit@5 | MRR | Evidencia − mejor otro | Margen 1º − 2º "
             "| Coseno medio ± desvío | Chunks truncados | Pasajes (s) | Consulta (ms) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for encoder_name, encoder_spec in grid["encoders"].items():
        encoder_config = EncoderConfig(**encoder_spec)
        encoder = build_encoder(encoder_config)
        for chunking_name, chunking_spec in grid["chunkings"].items():
            chunking = ChunkingConfig(**chunking_spec)
            chunks = chunk_corpus(documents, chunking)
            config = RetrieverConfig(encoder_config, chunking, SelectionConfig(), corpus_dir)
            started = time.perf_counter()
            retriever = Retriever(chunks, encoder, config)  # no cache: the timing must be real
            passages_seconds = time.perf_counter() - started
            started = time.perf_counter()
            rankings = retriever.rank_many([question["pregunta"] for question in questions])
            query_ms = 1000 * (time.perf_counter() - started) / len(questions)

            ranks = [gold_rank(ranking, question["evidencia"]) for ranking, question in zip(rankings, questions)]
            separations, margins, all_scores = [], [], []
            for ranking, question in zip(rankings, questions):
                gold = {id(scored) for scored in ranking if gold_rank([scored], question["evidencia"])}
                gold_best = max(scored.score for scored in ranking if id(scored) in gold)
                other_best = max(scored.score for scored in ranking if id(scored) not in gold)
                separations.append(gold_best - other_best)
                margins.append(ranking[0].score - ranking[1].score)
                all_scores.extend(scored.score for scored in ranking)
            truncated = "—"
            if hasattr(encoder, "passage_token_counts"):
                counts = encoder.passage_token_counts([chunk.render(chunking.metadata) for chunk in chunks])
                truncated = f"{100 * sum(count > encoder.max_seq_length for count in counts) / len(counts):.0f} %"
            lines.append(
                f"| {encoder_name} | {chunking_name} | {hit_rate(ranks, 1):.2f} | {hit_rate(ranks, 3):.2f} | "
                f"{hit_rate(ranks, 5):.2f} | {mean_reciprocal_rank(ranks):.3f} | {statistics.mean(separations):+.3f} | "
                f"{statistics.mean(margins):.3f} | {statistics.mean(all_scores):.3f} ± {statistics.pstdev(all_scores):.3f} | "
                f"{truncated} | {passages_seconds:.1f} | {query_ms:.0f} |")
            print(lines[-1], flush=True)
    return "\n".join(lines) + "\n"


def compare(run_a: str, run_b: str, out_dir: Path) -> str:
    def per_question(run: str) -> dict[str, float]:
        detail = json.loads((out_dir / f"{run}.jsonl.eval.json").read_text(encoding="utf-8"))["detalle"]
        return {row["id"]: row["context_relevance"] for row in detail}

    a, b = per_question(run_a), per_question(run_b)
    ids = sorted(a)
    differences = [b[qid] - a[qid] for qid in ids]
    low, high = paired_bootstrap(differences)
    wins, losses = sum(d > 0 for d in differences), sum(d < 0 for d in differences)
    changed = [f"| {qid} | {a[qid]:.2f} | {b[qid]:.2f} |" for qid in ids if a[qid] != b[qid]]
    return "\n".join([
        f"**{run_b}** vs **{run_a}**: CR {statistics.mean(b.values()):.3f} vs {statistics.mean(a.values()):.3f}, "
        f"diferencia media {statistics.mean(differences):+.3f} (IC 95 % bootstrap pareado: {low:+.3f} a {high:+.3f}). "
        f"Mejora en {wins} preguntas, empeora en {losses}, empata en {len(ids) - wins - losses}.",
        "",
        f"| Pregunta | {run_a} | {run_b} |",
        "|---|---|---|",
        *changed,
    ]) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    diagnose_parser = commands.add_parser("diagnose")
    diagnose_parser.add_argument("grid", type=Path)
    diagnose_parser.add_argument("--out", type=Path)
    compare_parser = commands.add_parser("compare")
    compare_parser.add_argument("run_a")
    compare_parser.add_argument("run_b")
    compare_parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "experimentos")
    compare_parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    report = diagnose(args.grid) if args.command == "diagnose" else compare(args.run_a, args.run_b, args.out_dir)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()
