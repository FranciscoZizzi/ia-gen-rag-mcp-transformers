"""Contract of agente_mcp.py, run offline: the real MCP server over stdio, real API, lexical retriever and a
scripted stand-in for the LLM. Part 3 must offer the model what Part 2 does and record the same rows."""
import ast
import json
from pathlib import Path

import pytest
from scripted_model import ScriptedModel

import agente
import agente_mcp
from assistant.agent import build_tools
from assistant.hospital_api import HospitalApi
from assistant.tools import TOOL_NAMES, HospitalTools

REPO_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = [
    {"id": "Q1", "pregunta": "¿Hay camas en pediatría y me puedo quedar con mi hijo?"},
    {"id": "Q2", "pregunta": "¿Cuánto se espera en la guardia?"},
]
SCRIPT = {
    QUESTIONS[0]["pregunta"]: [
        [("consultar_camas", {"sector": "pediatría"}), ("buscar_documentos", {"consulta": "acompañante en pediatría"})],
        "Hay camas libres y podés quedarte.",
    ],
    QUESTIONS[1]["pregunta"]: [
        [("consultar_camas", {"sector": "astronautas"})],
        [("consultar_espera", {})],
        "Depende del nivel de triage.",
    ],
}


@pytest.fixture
def run(tmp_path, api_url, lexical_config):
    """Runs agente_mcp.py (or, for comparison, agente.py) on the questions with a scripted model."""
    def run_with(main=agente_mcp.main, script=SCRIPT, name="respuestas_mcp"):
        questions_path = tmp_path / "preguntas.jsonl"
        questions_path.write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in QUESTIONS), encoding="utf-8")
        output = tmp_path / f"{name}.jsonl"
        model = ScriptedModel(script)
        main(["--preguntas", str(questions_path), "--salida", str(output), "--api-url", api_url,
              "--config", str(lexical_config)], model=model)
        rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
        return rows, (tmp_path / f"{name}.log.md").read_text(encoding="utf-8"), model
    return run_with


def test_writes_one_row_per_question_in_input_order_with_the_contract_keys(run):
    rows, _, _ = run()

    assert [row["id"] for row in rows] == ["Q1", "Q2"]
    assert all(set(row) == {"id", "respuesta", "contextos", "herramientas"} for row in rows)
    assert rows[0]["respuesta"] == "Hay camas libres y podés quedarte."


def test_the_model_sees_the_six_tools_with_the_part_2_descriptions_and_schemas(run, api_url, lexical_retriever):
    _, _, model = run()
    part2 = {tool.name: tool for tool in build_tools(HospitalTools(HospitalApi(api_url), retriever=lexical_retriever))}

    assert sorted(model.tool_specs) == sorted(TOOL_NAMES)
    for name, (description, schema) in model.tool_specs.items():
        assert description == part2[name].description
        assert sorted(schema["properties"]) == sorted(part2[name].params_json_schema["properties"])
        assert schema.get("additionalProperties") is False  # strict, like the Part 2 function tools


def test_rows_match_part_2_for_the_same_model_turns(run):
    mcp_rows, _, _ = run()
    part2_rows, _, _ = run(main=agente.main, name="respuestas")

    assert mcp_rows == part2_rows  # same answers, plain-text contextos and tool names: only the transport differs


def test_herramientas_and_contextos_come_from_the_tool_calls_actually_made(run):
    rows, _, _ = run()
    first, second = rows

    assert first["herramientas"] == ["consultar_camas", "buscar_documentos"]
    assert json.loads(first["contextos"][0])["datos"]["libres"] == 7
    assert first["contextos"][1] and not first["contextos"][1].startswith("{")  # fragments, not a wrapped MCP block
    assert second["herramientas"] == ["consultar_camas", "consultar_espera"]
    assert "opciones" in json.loads(second["contextos"][0])
    assert "minutos_por_nivel" in json.loads(second["contextos"][1])


def test_the_log_shows_the_transport_each_tool_call_and_the_usage_of_each_model_call(run):
    _, log, _ = run()

    assert "MCP" in log[:log.index("## Resumen")]
    q2 = log[log.index("## Q2"):]
    assert '`consultar_camas` con argumentos `{"sector": "astronautas"}`' in q2
    assert "minutos_por_nivel" in q2
    assert q2.count("### Llamada al modelo") == 3
    assert "100 tokens de entrada" in q2 and "10 de salida" in q2
    assert "Depende del nivel de triage." in q2


def test_a_question_whose_run_keeps_failing_still_gets_a_row_and_the_error_is_logged(run):
    rows, log, _ = run(script={QUESTIONS[0]["pregunta"]: SCRIPT[QUESTIONS[0]["pregunta"]]})

    assert rows[1] == {"id": "Q2", "respuesta": "", "contextos": [], "herramientas": []}
    assert "**Error:**" in log[log.index("## Q2"):]


def test_agente_mcp_has_no_code_of_its_own_for_the_api_or_the_retriever():
    tree = ast.parse((REPO_ROOT / "agente_mcp.py").read_text(encoding="utf-8"))
    imported = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    imported |= {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}

    assert not any(module == "rag" or module.startswith(("rag.", "assistant.tools", "assistant.hospital_api"))
                   for module in imported)
