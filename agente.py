"""Part 2 contract: python3 agente.py --preguntas <questions.jsonl> --salida <answers.jsonl>

Answers each question with a tool-calling agent over the Part 1 retriever and the hospital API
(python3 api/servidor.py must be running). Writes one line per question,
{"id", "respuesta", "contextos", "herramientas"}, and the run's Markdown log next to it.
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from agents import Model

from assistant.agent import (DEFAULT_MODEL, UsageRecorder, build_agent, openrouter_model, recording_http_client,
                             run_questions)
from assistant.hospital_api import HospitalApi
from assistant.report import write_log
from assistant.tools import DEFAULT_RETRIEVER_CONFIG, REPO_ROOT, HospitalTools
from rag.config import load_config
from rag.io import read_jsonl, write_jsonl
from rag.retriever import Retriever


def main(argv: list[str] | None = None, model: Model | None = None) -> None:
    parser = argparse.ArgumentParser(description="Answer patients' questions with a tool-calling agent.")
    parser.add_argument("--preguntas", type=Path, required=True, help="questions JSONL with id and pregunta")
    parser.add_argument("--salida", type=Path, required=True, help="output JSONL with id, respuesta, contextos, herramientas")
    parser.add_argument("--log", type=Path, help="Markdown run log (default: <salida without .jsonl>.log.md)")
    parser.add_argument("--modelo", default=DEFAULT_MODEL, help="OpenRouter model id")
    parser.add_argument("--api-url", help="hospital API base URL (default: $HOSPITAL_API_URL or http://127.0.0.1:8765)")
    parser.add_argument("--config", type=Path, default=DEFAULT_RETRIEVER_CONFIG, help="retriever configuration JSON")
    args = parser.parse_args(argv)

    questions = read_jsonl(args.preguntas)
    tools = HospitalTools(HospitalApi(args.api_url),
                          retriever_factory=lambda: Retriever.from_config(load_config(args.config), base_dir=REPO_ROOT))
    recorder = UsageRecorder()

    async def run_all():
        async with recording_http_client(recorder) as http_client:
            agent = build_agent(tools, model or openrouter_model(args.modelo, http_client))
            return await run_questions(agent, questions, recorder)

    runs = asyncio.run(run_all())
    write_jsonl(args.salida, (run.to_row() for run in runs))
    log = args.log or args.salida.with_name(args.salida.name.removesuffix(".jsonl") + ".log.md")
    write_log(log, runs, model=args.modelo, questions=args.preguntas)


if __name__ == "__main__":
    main()
