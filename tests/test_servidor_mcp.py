"""servidor_mcp.py: the six HospitalTools over MCP, with the descriptions and arguments agente.py offers."""
import asyncio
import json
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import servidor_mcp
from assistant.agent import build_tools
from assistant.hospital_api import HospitalApi
from assistant.tools import TOOL_NAMES, HospitalTools
from rag.config import load_config
from rag.retriever import Retriever

REPO_ROOT = Path(__file__).resolve().parents[1]
ARGUMENTS = {
    "buscar_documentos": {"consulta": "¿Qué hay que llevar a la primera consulta con un especialista?"},
    "consultar_camas": {"sector": "pediatria"},
    "consultar_guardia": {"especialidad": "cardiologia"},
    "consultar_turnos": {"especialidad": "traumatologia"},
    "consultar_farmacia": {"medicamento": "enalapril 10 mg"},
    "consultar_espera": {},
}


@pytest.fixture
def direct_tools(api_url, lexical_config):
    """The tools as agente.py calls them in-process: what the server must reproduce."""
    retriever = Retriever.from_config(load_config(lexical_config), base_dir=REPO_ROOT)
    return HospitalTools(HospitalApi(api_url), retriever=retriever)


def test_the_server_offers_the_six_tools_with_the_part_2_descriptions_and_arguments(direct_tools):
    server = servidor_mcp.build_server(direct_tools)

    listed = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert sorted(listed) == sorted(TOOL_NAMES)
    assert {name: tool.description for name, tool in listed.items()} == direct_tools.descriptions()
    for function_tool in build_tools(direct_tools):
        schema = listed[function_tool.name].inputSchema
        assert sorted(schema.get("properties", {})) == sorted(function_tool.params_json_schema["properties"])
        assert sorted(schema.get("required", [])) == sorted(function_tool.params_json_schema.get("required", []))
        assert schema["additionalProperties"] is False  # closed, as the strict Part 2 schemas are
        assert listed[function_tool.name].outputSchema is None  # plain text, like the Part 2 tools


def test_the_retriever_is_built_once_when_the_server_is_built_and_nothing_reaches_stdout(
        api_url, lexical_retriever, capsys):
    built = []

    def noisy_factory():
        print("loading models...")  # a library writing to stdout would corrupt the stdio protocol
        built.append(True)
        return lexical_retriever

    server = servidor_mcp.build_server(HospitalTools(HospitalApi(api_url), retriever_factory=noisy_factory))
    assert built == [True]

    asyncio.run(server.call_tool("buscar_documentos", {"consulta": "donar sangre"}))
    asyncio.run(server.call_tool("buscar_documentos", {"consulta": "visitas"}))

    assert built == [True]
    assert capsys.readouterr().out == ""


async def _over_stdio(api_url, config):
    params = StdioServerParameters(command=sys.executable, cwd=str(REPO_ROOT),
                                   args=[str(REPO_ROOT / "servidor_mcp.py"), "--api-url", api_url, "--config", str(config)])
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        tools = (await session.list_tools()).tools
        results = {name: await session.call_tool(name, arguments) for name, arguments in ARGUMENTS.items()}
        unknown = await session.call_tool("consultar_camas", {"sector": "astronautas"})
    return tools, results, unknown


def test_over_stdio_tools_list_and_tools_call_match_the_in_process_tools(api_url, lexical_config, direct_tools):
    tools, results, unknown = asyncio.run(_over_stdio(api_url, lexical_config))

    assert sorted(tool.name for tool in tools) == sorted(TOOL_NAMES)
    assert {tool.name: tool.description for tool in tools} == direct_tools.descriptions()
    assert all(tool.inputSchema["type"] == "object" for tool in tools)
    for name, arguments in ARGUMENTS.items():
        result = results[name]
        assert not result.isError
        assert [block.text for block in result.content] == [getattr(direct_tools, name)(**arguments)]
    assert "pediatria" in json.loads(unknown.content[0].text)["opciones"]
