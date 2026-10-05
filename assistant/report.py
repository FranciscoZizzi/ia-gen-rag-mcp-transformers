"""The Markdown log of a benchmark run: every model call, tool call and answer, with usage and cost."""
from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from assistant.agent import AgentRun


def write_log(path: Path, runs: Sequence[AgentRun], *, model: str, questions: Path, header: str = "") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(render_log(runs, model=model, questions=questions, header=header), encoding="utf-8")


def render_log(runs: Sequence[AgentRun], *, model: str, questions: Path, header: str = "") -> str:
    calls = [call for run in runs for call in run.model_calls]
    lines = [
        "# Log de corrida del agente",
        "",
        f"- Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"- Modelo: `{model}`",
        f"- Preguntas: `{questions}` ({len(runs)})",
    ]
    if header:
        lines.append(f"- {header}")
    lines += [
        "",
        "## Resumen",
        "",
        "| Pregunta | Herramientas | Llamadas al modelo | Tokens entrada | Tokens salida (razonamiento) | Costo USD | Segundos |",
        "|---|---|---|---|---|---|---|",
    ]
    for run in runs:
        lines.append(
            f"| {run.question_id} | {', '.join(run.tools) or '—'} | {len(run.model_calls)} | "
            f"{sum(c.input_tokens for c in run.model_calls)} | {sum(c.output_tokens for c in run.model_calls)} "
            f"({sum(c.reasoning_tokens for c in run.model_calls)}) | {run.cost:.6f} | {run.seconds:.1f} |")
    lines += [
        f"| **Total** | | {len(calls)} | {sum(c.input_tokens for c in calls)} | "
        f"{sum(c.output_tokens for c in calls)} ({sum(c.reasoning_tokens for c in calls)}) | "
        f"**{sum(run.cost for run in runs):.6f}** | {sum(run.seconds for run in runs):.1f} |",
        "",
    ]
    for run in runs:
        lines += _render_run(run)
    return "\n".join(lines) + "\n"


def _render_run(run: AgentRun) -> list[str]:
    lines = [f"## {run.question_id}", "", f"**Pregunta:** {run.question}", ""]
    if run.attempts > 1:
        lines += [f"_Intentos: {run.attempts}_", ""]
    for number, call in enumerate(run.model_calls, start=1):
        cost = "sin dato" if call.cost is None else f"USD {call.cost:.6f}"
        lines += [f"### Llamada al modelo {number}", "",
                  f"Usage: {call.input_tokens} tokens de entrada ({call.cached_tokens} en caché), "
                  f"{call.output_tokens} de salida ({call.reasoning_tokens} de razonamiento), {cost}.", ""]
        if call.text and call.tool_calls:
            lines += ["Texto del modelo:", "", _quote(call.text), ""]
        for tool_call in call.tool_calls:
            lines += [f"**Herramienta** `{tool_call.name}` con argumentos `{_compact(tool_call.arguments)}`", "",
                      "Resultado:", "", "```text", tool_call.output, "```", ""]
    if run.error:
        lines += [f"**Error:** `{run.error}`", ""]
    lines += ["**Respuesta:**", "", _quote(run.answer or "(sin respuesta)"), "",
              f"Herramientas: {', '.join(run.tools) or 'ninguna'} · costo USD {run.cost:.6f}", ""]
    return lines


def _compact(arguments: str) -> str:
    try:
        return json.dumps(json.loads(arguments or "{}"), ensure_ascii=False)
    except ValueError:
        return arguments


def _quote(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in text.strip().splitlines())
