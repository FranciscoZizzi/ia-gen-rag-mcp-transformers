"""Run a grid of retrieval configurations and score each one with the official evaluator.

    python3 scripts/run_experiments.py experimentos/grids/A-encoders.json

The grid crosses named encoders, chunkings and selections (see SPEC.md). Each run writes
experimentos/<run>.jsonl and <run>.config.json, then evaluar/evaluar.py writes <run>.jsonl.eval.json.
<run>.config.json is a complete retriever config: `recuperar.py --config` reproduces the run.
Rankings are computed once per (encoder, chunking); selections only cut them.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("TQDM_DISABLE", "1")  # silence model-loading progress bars in the logs

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from rag.chunking import chunk_corpus  # noqa: E402
from rag.config import ChunkingConfig, EncoderConfig, RetrieverConfig, SelectionConfig  # noqa: E402
from rag.corpus import load_corpus  # noqa: E402
from rag.encoders import build_encoder  # noqa: E402
from rag.io import read_jsonl, write_jsonl  # noqa: E402
from rag.retriever import Retriever  # noqa: E402
from rag.selection import select  # noqa: E402

EVALUATOR = REPO_ROOT / "evaluar" / "evaluar.py"


def run_grid(grid_path: Path, out_dir: Path, cache_dir: Path) -> None:
    grid = json.loads(grid_path.read_text(encoding="utf-8"))
    questions_path = REPO_ROOT / grid["questions"]
    corpus_dir = grid.get("corpus_dir", "datos/corpus")
    questions = read_jsonl(questions_path)
    documents = load_corpus(REPO_ROOT / corpus_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for encoder_name, encoder_spec in grid["encoders"].items():
        encoder_config = EncoderConfig(**encoder_spec)
        encoder = build_encoder(encoder_config)
        for chunking_name, chunking_spec in grid["chunkings"].items():
            chunking = ChunkingConfig(**chunking_spec)
            base = RetrieverConfig(encoder_config, chunking, SelectionConfig(), corpus_dir)
            retriever = Retriever(chunk_corpus(documents, chunking), encoder, base, cache_dir)
            rankings = retriever.rank_many([question["pregunta"] for question in questions])
            for selection_name, selection_spec in grid["selections"].items():
                selection = SelectionConfig(**selection_spec)
                run = f"{grid['stage']}-{encoder_name}-{chunking_name}-{selection_name}"
                results_path = out_dir / f"{run}.jsonl"
                write_jsonl(results_path, (
                    {"id": question["id"], "fragmentos": [scored.text for scored in select(ranking, selection)]}
                    for question, ranking in zip(questions, rankings)
                ))
                config = RetrieverConfig(encoder_config, chunking, selection, corpus_dir)
                (out_dir / f"{run}.config.json").write_text(
                    json.dumps(config.to_dict(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                summary = evaluate(questions_path, results_path)
                print(f"{run:55s} CR {summary['context_relevance']:.3f}  recall {summary['recall']:.3f}  "
                      f"precision {summary['precision']:.3f}  k {summary['k']:.2f}", flush=True)
    write_results_table(out_dir)


def evaluate(questions_path: Path, results_path: Path) -> dict:
    """Score a results file with the unmodified official evaluator, which writes <results>.eval.json."""
    subprocess.run([sys.executable, str(EVALUATOR), "recuperacion", "--preguntas", str(questions_path),
                    "--resultados", str(results_path)], check=True, capture_output=True, text=True, cwd=REPO_ROOT)
    return json.loads(Path(f"{results_path}.eval.json").read_text(encoding="utf-8"))["resumen"]


def write_results_table(out_dir: Path) -> None:
    """Regenerate RESULTS.md from every run on disk, so no number is ever copied by hand."""
    header = ("| Run | Encoder | Chunking | Metadatos | Corte | CR | Recall | Precision | MRR | k medio | Caracteres |\n"
              "|---|---|---|---|---|---|---|---|---|---|---|\n")
    rows = []
    for config_path in sorted(out_dir.glob("*.config.json")):
        run = config_path.name.removesuffix(".config.json")
        eval_path = out_dir / f"{run}.jsonl.eval.json"
        if not eval_path.exists():
            continue
        config = RetrieverConfig.from_dict(json.loads(config_path.read_text(encoding="utf-8")))
        s = json.loads(eval_path.read_text(encoding="utf-8"))["resumen"]
        rows.append(f"| [{run}]({eval_path.name}) | {describe_encoder(config.encoder)} | "
                    f"{describe_chunking(config.chunking)} | {'sí' if config.chunking.metadata else 'no'} | "
                    f"{describe_selection(config.selection)} | {s['context_relevance']:.3f} | {s['recall']:.3f} | "
                    f"{s['precision']:.3f} | {s['mrr']:.3f} | {s['k']:.2f} | {s['caracteres']:.0f} |\n")
    (out_dir / "RESULTS.md").write_text(
        "# Resultados de la Parte 1\n\nGenerado por `scripts/run_experiments.py` a partir de los `.eval.json` "
        "del evaluador oficial. No editar a mano.\n\n" + header + "".join(rows), encoding="utf-8")


def describe_encoder(encoder: EncoderConfig) -> str:
    if encoder.type == "hashing_bow":
        return "léxico (bolsa de palabras)"
    name = encoder.model.split("/")[-1]
    return f"{name} (promedio de tokens)" if encoder.type == "mean_pooling" else name


def describe_chunking(chunking: ChunkingConfig) -> str:
    if chunking.strategy == "fixed":
        return f"fixed ≤{chunking.max_chars}, solap. {chunking.overlap_sentences}"
    if chunking.strategy == "section":
        return f"section ≤{chunking.max_chars}"
    return chunking.strategy


def describe_selection(selection: SelectionConfig) -> str:
    parts = [f"k={selection.top_k}" if selection.min_score is None and selection.max_margin is None
             else f"k≤{selection.top_k}"]
    if selection.min_score is not None:
        parts.append(f"s≥{selection.min_score:g}")
    if selection.max_margin is not None:
        parts.append(f"Δ≤{selection.max_margin:g}")
    return ", ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("grid", type=Path, help="grid JSON (see SPEC.md)")
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "experimentos")
    parser.add_argument("--cache-dir", type=Path, default=REPO_ROOT / ".cache" / "embeddings")
    args = parser.parse_args()
    run_grid(args.grid, args.out_dir, args.cache_dir)


if __name__ == "__main__":
    main()
