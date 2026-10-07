"""Part 3 server: python3 servidor_mcp.py [--api-url <url>] [--config config/agent_retriever.json]

Serves the six hospital tools over MCP (stdio transport) with FastMCP. The tools live in
assistant/tools.py (HospitalTools); each function here only delegates, and the model reads the same
descriptions agente.py gives it, with the names the API accepts. The retriever loads once, at start-up.
stdout carries the protocol, so everything else goes to stderr.
"""
from __future__ import annotations

import argparse
import sys
from contextlib import redirect_stdout
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from assistant.hospital_api import HospitalApi
from assistant.tools import DEFAULT_RETRIEVER_CONFIG, REPO_ROOT, HospitalTools
from rag.config import load_config
from rag.retriever import Retriever


def build_server(tools: HospitalTools) -> FastMCP:
    with redirect_stdout(sys.stderr):  # model loading must not write into the protocol stream
        descriptions = tools.descriptions()
        tools.retriever  # noqa: B018 - load the encoder and reranker now, not on the first search

    mcp = FastMCP("hospital-arroyo-claro", log_level="WARNING")

    @mcp.tool(name="buscar_documentos", description=descriptions["buscar_documentos"], structured_output=False)
    def buscar_documentos(consulta: str) -> str:
        return tools.buscar_documentos(consulta)

    @mcp.tool(name="consultar_camas", description=descriptions["consultar_camas"], structured_output=False)
    def consultar_camas(sector: str) -> str:
        return tools.consultar_camas(sector)

    @mcp.tool(name="consultar_guardia", description=descriptions["consultar_guardia"], structured_output=False)
    def consultar_guardia(especialidad: str) -> str:
        return tools.consultar_guardia(especialidad)

    @mcp.tool(name="consultar_turnos", description=descriptions["consultar_turnos"], structured_output=False)
    def consultar_turnos(especialidad: str) -> str:
        return tools.consultar_turnos(especialidad)

    @mcp.tool(name="consultar_farmacia", description=descriptions["consultar_farmacia"], structured_output=False)
    def consultar_farmacia(medicamento: str) -> str:
        return tools.consultar_farmacia(medicamento)

    @mcp.tool(name="consultar_espera", description=descriptions["consultar_espera"], structured_output=False)
    def consultar_espera() -> str:
        return tools.consultar_espera()

    return mcp


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Serve the hospital tools over MCP (stdio).")
    parser.add_argument("--api-url", help="hospital API base URL (default: $HOSPITAL_API_URL or http://127.0.0.1:8765)")
    parser.add_argument("--config", type=Path, default=DEFAULT_RETRIEVER_CONFIG, help="retriever configuration JSON")
    args = parser.parse_args(argv)

    tools = HospitalTools(HospitalApi(args.api_url),
                          retriever_factory=lambda: Retriever.from_config(load_config(args.config), base_dir=REPO_ROOT))
    build_server(tools).run("stdio")


if __name__ == "__main__":
    main()
