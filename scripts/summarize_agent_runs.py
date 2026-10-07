"""Regenerate the agent run tables from every run on disk, so no number is copied by hand.

    python3 scripts/summarize_agent_runs.py

Part 2 runs are folders under experimentos/agente/ with respuestas.jsonl, its .eval.json
(evaluar/evaluar.py agente) and respuestas.log.md; Part 3 runs, under experimentos/agente_mcp/, hold the
same files named respuestas_mcp.*. Writes RESULTS.md in each, and experimentos/agente_mcp/COMPARACION.md
with every MCP run next to the Part 2 run of the same name, overall and question by question.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PART2 = (REPO_ROOT / "experimentos" / "agente", "respuestas", "Corridas del agente")
PART3 = (REPO_ROOT / "experimentos" / "agente_mcp", "respuestas_mcp", "Corridas del agente MCP")

_TOTAL_ROW = re.compile(r"^\| \*\*Total\*\* \| \| (\d+) \| (\d+) \| (\d+) \((\d+)\) \| \*\*([\d.]+)\*\* \| ([\d.]+) \|$", re.M)


def summarize(run_dir: Path, runs_dir: Path, stem: str = "respuestas") -> dict | None:
    evaluation = run_dir / f"{stem}.jsonl.eval.json"
    log = run_dir / f"{stem}.log.md"
    if not evaluation.exists() or not log.exists():
        return None
    summary = json.loads(evaluation.read_text(encoding="utf-8"))["resumen"]
    text = log.read_text(encoding="utf-8")
    calls, tokens_in, tokens_out, reasoning, cost, seconds = _TOTAL_ROW.search(text).groups()
    results = re.findall(r"Resultado:\n\n```text\n(.*?)\n```", text, re.S)
    questions = len(re.findall(r"^## [A-Z]\d+$", text, re.M))
    return {
        "run": run_dir.relative_to(runs_dir).as_posix(), "questions": questions, **summary,
        "model_calls": int(calls), "tool_calls": len(results),
        "api_errors": sum(result.startswith('{"error"') for result in results),
        "tokens_in": int(tokens_in), "tokens_out": int(tokens_out), "reasoning": int(reasoning),
        "agent_cost": float(cost), "seconds": float(seconds),
    }


def collect(runs_dir: Path, stem: str) -> list[dict]:
    return [row for path in sorted(runs_dir.rglob(f"{stem}.jsonl")) if (row := summarize(path.parent, runs_dir, stem))]


def results_table(rows: list[dict], title: str) -> list[str]:
    lines = [
        f"# {title}",
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
    return lines


def comparison(part2: list[dict], part3: list[dict]) -> list[str]:
    by_name = {row["run"]: row for row in part2}
    pairs = [(by_name[row["run"]], row) for row in part3 if row["run"] in by_name]
    lines = [
        "# Parte 2 contra Parte 3",
        "",
        "Generado por `scripts/summarize_agent_runs.py`: cada corrida de `experimentos/agente_mcp/` junto a la "
        "corrida de `experimentos/agente/` con el mismo nombre (mismo prompt, modelo, descripciones y recuperador; "
        "cambia el transporte de las herramientas). Costos en USD.",
        "",
        "| Corrida | Parte | Ruteo | Context Rel. | Faithfulness | Answer Rel. | Llamadas al modelo | "
        "Llamadas a herramientas | Tokens entrada | Tokens salida (razonamiento) | Costo agente | Costo juez |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p2, p3 in pairs:
        for part, r in (("2 (function tools)", p2), ("3 (MCP)", p3)):
            lines.append(
                f"| `{r['run']}` | {part} | {r['ruteo']:.2f} | {r['context_relevance']:.3f} | "
                f"{r['faithfulness']:.3f} | {r['answer_relevance']:.3f} | {r['model_calls']} | {r['tool_calls']} | "
                f"{r['tokens_in']} | {r['tokens_out']} ({r['reasoning']}) | {r['agent_cost']:.6f} | "
                f"{r['costo_juez_usd']:.5f} |")
    for p2, p3 in pairs:
        lines += ["", f"## `{p2['run']}`, pregunta por pregunta", "",
                  "| Pregunta | Herramientas P2 | Herramientas P3 | CR / F / AR P2 | CR / F / AR P3 | "
                  "Mismos contextos | Misma respuesta |",
                  "|---|---|---|---|---|---|---|"]
        lines += _per_question(PART2[0] / p2["run"], PART2[1], PART3[0] / p3["run"], PART3[1])
    return lines


def _per_question(dir2: Path, stem2: str, dir3: Path, stem3: str) -> list[str]:
    rows2, rows3 = _rows(dir2 / f"{stem2}.jsonl"), _rows(dir3 / f"{stem3}.jsonl")
    scores2, scores3 = _scores(dir2 / f"{stem2}.jsonl.eval.json"), _scores(dir3 / f"{stem3}.jsonl.eval.json")
    lines = []
    for qid, row2 in rows2.items():
        row3 = rows3.get(qid, {})
        lines.append(
            f"| {qid} | {', '.join(row2['herramientas'])} | {', '.join(row3.get('herramientas', []))} | "
            f"{scores2.get(qid, '—')} | {scores3.get(qid, '—')} | "
            f"{'sí' if row2['contextos'] == row3.get('contextos') else '**no**'} | "
            f"{'sí' if row2['respuesta'] == row3.get('respuesta') else '**no**'} |")
    return lines


def _rows(path: Path) -> dict[str, dict]:
    return {row["id"]: row for row in map(json.loads, path.read_text(encoding="utf-8").splitlines()) if row}


def _scores(path: Path) -> dict[str, str]:
    detail = json.loads(path.read_text(encoding="utf-8"))["detalle"]
    return {d["id"]: f"{d['context_relevance']} / {d['faithfulness']} / {d['answer_relevance']}" for d in detail}


def _write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), end="\n\n")


def main() -> None:
    part2 = collect(PART2[0], PART2[1])
    _write(PART2[0] / "RESULTS.md", results_table(part2, PART2[2]))
    part3 = collect(PART3[0], PART3[1])
    if part3:
        _write(PART3[0] / "RESULTS.md", results_table(part3, PART3[2]))
        _write(PART3[0] / "COMPARACION.md", comparison(part2, part3))


if __name__ == "__main__":
    main()
