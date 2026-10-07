"""Part 3 contract: python3 agente_mcp.py --preguntas <questions.jsonl> --salida <answers.jsonl>

The Part 2 agent (same model, prompt and settings) with no tools of its own: it launches servidor_mcp.py
over stdio, discovers the six tools with tools/list and calls them with tools/call
(python3 api/servidor.py must be running). Writes the same rows as agente.py,
{"id", "respuesta", "contextos", "herramientas"}, and the run's Markdown log next to them.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from agents import Model
from agents.mcp import MCPServerStdio

from assistant.agent import (DEFAULT_MODEL, UsageRecorder, build_mcp_agent, openrouter_model, recording_http_client,
                             run_questions)
from assistant.report import write_log
from rag.io import read_jsonl, write_jsonl

REPO_ROOT = Path(__file__).resolve().parent
SERVER = REPO_ROOT / "servidor_mcp.py"
DEFAULT_RETRIEVER_CONFIG = REPO_ROOT / "config" / "agent_retriever.json"
# The server loads the encoder and reranker before answering initialize (~20 s, longer on a first download).
SERVER_TIMEOUT_SECONDS = 300


def mcp_server(api_url: str | None, config: Path) -> MCPServerStdio:
    """servidor_mcp.py as a child process; it sees this environment except the OpenRouter key."""
    args = [str(SERVER), "--config", str(config)] + (["--api-url", api_url] if api_url else [])
    env = {key: value for key, value in os.environ.items() if key != "OPENROUTER_API_KEY"}
    return MCPServerStdio(params={"command": sys.executable, "args": args, "cwd": str(REPO_ROOT), "env": env},
                          name="hospital", cache_tools_list=True,
                          client_session_timeout_seconds=SERVER_TIMEOUT_SECONDS)


def main(argv: list[str] | None = None, model: Model | None = None) -> None:
    parser = argparse.ArgumentParser(description="Answer patients' questions with the agent over the MCP server.")
    parser.add_argument("--preguntas", type=Path, required=True, help="questions JSONL with id and pregunta")
    parser.add_argument("--salida", type=Path, required=True, help="output JSONL with id, respuesta, contextos, herramientas")
    parser.add_argument("--log", type=Path, help="Markdown run log (default: <salida without .jsonl>.log.md)")
    parser.add_argument("--modelo", default=DEFAULT_MODEL, help="OpenRouter model id")
    parser.add_argument("--api-url", help="hospital API base URL, passed to the server "
                                          "(default: $HOSPITAL_API_URL or http://127.0.0.1:8765)")
    parser.add_argument("--config", type=Path, default=DEFAULT_RETRIEVER_CONFIG,
                        help="retriever configuration JSON, passed to the server")
    args = parser.parse_args(argv)

    questions = read_jsonl(args.preguntas)
    recorder = UsageRecorder()

    async def run_all():
        async with recording_http_client(recorder) as http_client:
            agent_model = model or openrouter_model(args.modelo, http_client)
            async with mcp_server(args.api_url, args.config.resolve()) as server:
                return await run_questions(build_mcp_agent(server, agent_model), questions, recorder)

    runs = asyncio.run(run_all())
    write_jsonl(args.salida, (run.to_row() for run in runs))
    log = args.log or args.salida.with_name(args.salida.name.removesuffix(".jsonl") + ".log.md")
    write_log(log, runs, model=args.modelo, questions=args.preguntas,
              header="Transporte: MCP stdio (`servidor_mcp.py`), herramientas descubiertas con tools/list")


if __name__ == "__main__":
    main()
