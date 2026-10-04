"""Regenerate experimentos/agente/RESULTS.md from every agent run on disk, so no number is copied by hand.

    python3 scripts/summarize_agent_runs.py

A run is a folder with respuestas.jsonl, its .eval.json (evaluar/evaluar.py agente) and respuestas.log.md.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "experimentos" / "agente"

_TOTAL_ROW = re.compile(r"^\| \*\*Total\*\* \| \| (\d+) \| (\d+) \| (\d+) \((\d+)\) \| \*\*([\d.]+)\*\* \| ([\d.]+) \|$", re.M)


def summarize(run_dir: Path) -> dict | None:
    evaluation = run_dir / "respuestas.jsonl.eval.json"
    log = run_dir / "respuestas.log.md"
    if not evaluation.exists() or not log.exists():
        return None
    summary = json.loads(evaluation.read_text(encoding="utf-8"))["resumen"]
    text = log.read_text(encoding="utf-8")
    calls, tokens_in, tokens_out, reasoning, cost, seconds = _TOTAL_ROW.search(text).groups()
    results = re.findall(r"Resultado:\n\n```text\n(.*?)\n```", text, re.S)
    questions = len(re.findall(r"^## [A-Z]\d+$", text, re.M))
    return {
        "run": run_dir.relative_to(RUNS_DIR).as_posix(), "questions": questions, **summary,
        "model_calls": int(calls), "tool_calls": len(results),
        "api_errors": sum(result.startswith('{"error"') for result in results),
        "tokens_in": int(tokens_in), "tokens_out": int(tokens_out), "reasoning": int(reasoning),
        "agent_cost": float(cost), "seconds": float(seconds),
    }


def main() -> None:
    rows = [row for path in sorted(RUNS_DIR.rglob("respuestas.jsonl")) if (row := summarize(path.parent))]
    lines = [
        "# Corridas del agente",
        "",
        "Generado por `scripts/summarize_agent_runs.py`. Costos en USD: el del agente sale del usage que informa "
        "OpenRouter en cada llamada (ver el log de la corrida); el del juez, del `.eval.json`.",
        "",
        "| Corrida | Preguntas | Ruteo | Context Rel. | Faithfulness | Answer Rel. | Llamadas al modelo | "
        "Llamadas a herramientas | Errores de la API | Tokens entrada | Tokens salida (razonamiento) | "
        "Costo agente | Costo juez | Segundos |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| `{r['run']}` | {r['questions']} | {r['ruteo']:.2f} | {r['context_relevance']:.3f} | "
            f"{r['faithfulness']:.3f} | {r['answer_relevance']:.3f} | {r['model_calls']} | {r['tool_calls']} | "
            f"{r['api_errors']} | {r['tokens_in']} | {r['tokens_out']} ({r['reasoning']}) | "
            f"{r['agent_cost']:.6f} | {r['costo_juez_usd']:.5f} | {r['seconds']:.0f} |")
    lines += ["", f"Total de estas corridas: agente USD {sum(r['agent_cost'] for r in rows):.6f}, "
                  f"juez USD {sum(r['costo_juez_usd'] for r in rows):.5f}."]
    (RUNS_DIR / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
