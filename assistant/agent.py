"""The tool-calling agent: one fresh conversation per question, traced call by call for the run log."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from agents import (Agent, FunctionTool, Model, ModelSettings, OpenAIChatCompletionsModel, Runner,
                    function_tool, set_tracing_disabled)
from openai import AsyncOpenAI

from assistant.tools import TOOL_NAMES, HospitalTools

OPENROUTER_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "deepseek/deepseek-v4-flash-0731"
MAX_TURNS = 8

INSTRUCTIONS = """Sos el asistente virtual del Hospital Provincial Arroyo Claro. Respondés consultas de pacientes y familiares.

Tenés dos fuentes, y solo podés responder con lo que te devuelvan:
- buscar_documentos: las normas y los procedimientos del hospital (visitas, acompañantes, preparación para estudios, documentación, requisitos, trámites, coberturas, derechos).
- consultar_camas, consultar_guardia, consultar_turnos, consultar_farmacia y consultar_espera: el estado de hoy, que cambia todo el tiempo (camas libres, quién está de guardia, próximos turnos, stock de farmacia, espera en la guardia).

Cómo trabajar:
1. Separá la consulta en sus partes. Cada parte que pregunta por el estado de hoy se responde con la herramienta de la API que corresponde; cada parte que pregunta por una norma, un requisito o un trámite se responde con buscar_documentos. Una misma consulta puede necesitar las dos fuentes.
2. Llamá solo a las herramientas que hacen falta para responder lo que se preguntó. Hacé una búsqueda en los documentos por tema, con una consulta concreta. Si un resultado no trae el dato, reformulá la búsqueda o corregí el nombre con las opciones que informa la API.
3. Nunca respondas de memoria ni completes con conocimiento general: cada dato de tu respuesta tiene que estar en lo que te devolvieron las herramientas. Si no encontraste algo, decilo.

Cómo responder: en español rioplatense, breve y directo, contestando todas las partes de la consulta con los datos concretos (cantidades, nombres, fechas y horarios). No agregues consejos, advertencias ni información que no se haya pedido."""


@dataclass
class ToolCall:
    name: str
    arguments: str  # JSON, as the model sent it
    output: str = ""


@dataclass
class ModelCall:
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cached_tokens: int = 0
    cost: float | None = None  # USD, as OpenRouter reports it; None when the provider gave no usage block
    tool_calls: list[ToolCall] = field(default_factory=list)
    text: str = ""


@dataclass
class AgentRun:
    question_id: str
    question: str
    answer: str = ""
    model_calls: list[ModelCall] = field(default_factory=list)
    attempts: int = 1
    seconds: float = 0.0
    error: str | None = None

    @property
    def tool_calls(self) -> list[ToolCall]:
        return [call for model_call in self.model_calls for call in model_call.tool_calls]

    @property
    def contexts(self) -> list[str]:
        """Everything the tools returned, as text: the evaluator's `contextos`."""
        return [call.output for call in self.tool_calls]

    @property
    def tools(self) -> list[str]:
        """The tools called, each once, in order of first use: the evaluator's `herramientas`."""
        return list(dict.fromkeys(call.name for call in self.tool_calls))

    @property
    def cost(self) -> float:
        return sum(call.cost or 0.0 for call in self.model_calls)

    def to_row(self) -> dict[str, Any]:
        return {"id": self.question_id, "respuesta": self.answer, "contextos": self.contexts,
                "herramientas": self.tools}


class UsageRecorder:
    """Keeps OpenRouter's `usage` block (tokens and cost in USD) of every chat completion, in call order.

    The Agents SDK reports tokens per call but drops the cost, so this hooks into the HTTP client instead.
    """

    def __init__(self):
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, response: httpx.Response) -> None:
        if response.status_code != 200 or not response.request.url.path.endswith("/chat/completions"):
            return
        await response.aread()
        try:
            usage = response.json().get("usage")
        except ValueError:
            return
        if usage:
            self.calls.append(usage)

    def take(self) -> list[dict[str, Any]]:
        calls, self.calls = self.calls, []
        return calls


def openrouter_model(model: str, recorder: UsageRecorder) -> Model:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("falta la variable OPENROUTER_API_KEY")
    client = AsyncOpenAI(base_url=OPENROUTER_URL, api_key=api_key, max_retries=3,
                         http_client=httpx.AsyncClient(timeout=120, event_hooks={"response": [recorder]}))
    return OpenAIChatCompletionsModel(model=model, openai_client=client)


def build_tools(tools: HospitalTools) -> list[FunctionTool]:
    descriptions = tools.descriptions()
    return [function_tool(getattr(tools, name), name_override=name, description_override=descriptions[name])
            for name in TOOL_NAMES]


def build_agent(tools: HospitalTools, model: Model) -> Agent:
    set_tracing_disabled(True)  # tracing uploads to OpenAI and fails without an OpenAI key
    return Agent(name="Asistente Hospital Arroyo Claro", instructions=INSTRUCTIONS, model=model,
                 tools=build_tools(tools),
                 model_settings=ModelSettings(temperature=0, extra_body={"usage": {"include": True}}))


async def answer(agent: Agent, question_id: str, question: str, recorder: UsageRecorder | None = None,
                 attempts: int = 3) -> AgentRun:
    """Run one question in a fresh conversation; retry the whole run when it fails, keep the last error."""
    start = time.monotonic()
    error = None
    for attempt in range(1, attempts + 1):
        if recorder:
            recorder.take()
        try:
            result = await Runner.run(agent, question, max_turns=MAX_TURNS)
        except Exception as exc:  # network, provider or max-turns failure: the whole run is retried
            error = f"{type(exc).__name__}: {exc}"
            continue
        run = _trace(result, question_id, question, recorder.take() if recorder else [])
        run.attempts, run.seconds = attempt, time.monotonic() - start
        return run
    return AgentRun(question_id, question, attempts=attempts, seconds=time.monotonic() - start, error=error)


def _trace(result, question_id: str, question: str, usages: list[dict[str, Any]]) -> AgentRun:
    outputs = {}
    for item in result.new_items:
        if item.type == "tool_call_output_item":
            raw = item.raw_item
            call_id = raw["call_id"] if isinstance(raw, dict) else raw.call_id
            outputs[call_id] = item.output if isinstance(item.output, str) else json.dumps(item.output, ensure_ascii=False)

    model_calls = []
    for index, response in enumerate(result.raw_responses):
        usage = response.usage
        call = ModelCall(
            input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
            reasoning_tokens=getattr(usage.output_tokens_details, "reasoning_tokens", 0) or 0,
            cached_tokens=getattr(usage.input_tokens_details, "cached_tokens", 0) or 0,
        )
        if index < len(usages):
            call.cost = usages[index].get("cost")
        for item in response.output:
            if getattr(item, "type", None) == "function_call":
                call.tool_calls.append(ToolCall(item.name, item.arguments, outputs.get(item.call_id, "")))
            elif getattr(item, "type", None) == "message":
                call.text += "".join(getattr(part, "text", "") for part in item.content)
        model_calls.append(call)

    final = result.final_output
    return AgentRun(question_id, question, answer=final if isinstance(final, str) else str(final or ""),
                    model_calls=model_calls)
