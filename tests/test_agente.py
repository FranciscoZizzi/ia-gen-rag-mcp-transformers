"""Contract of agente.py, run offline: real API, lexical retriever and a scripted stand-in for the LLM."""
import json

import pytest
from scripted_model import ScriptedModel

import agente

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
def run_agente(tmp_path, api_url, lexical_config):
    def run(questions=QUESTIONS, script=SCRIPT):
        questions_path = tmp_path / "preguntas.jsonl"
        questions_path.write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in questions), encoding="utf-8")
        output = tmp_path / "respuestas.jsonl"
        model = ScriptedModel(script)
        agente.main(["--preguntas", str(questions_path), "--salida", str(output), "--api-url", api_url,
                     "--config", str(lexical_config)], model=model)
        rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
        return rows, (tmp_path / "respuestas.log.md").read_text(encoding="utf-8"), model
    return run


def test_writes_one_row_per_question_in_input_order_with_the_contract_keys(run_agente):
    rows, _, _ = run_agente()

    assert [row["id"] for row in rows] == ["Q1", "Q2"]
    assert all(set(row) == {"id", "respuesta", "contextos", "herramientas"} for row in rows)
    assert rows[0]["respuesta"] == "Hay camas libres y podés quedarte."


def test_the_model_is_offered_the_six_tools(run_agente):
    _, _, model = run_agente()

    assert sorted(model.tools_seen) == sorted(["buscar_documentos", "consultar_camas", "consultar_guardia",
                                               "consultar_turnos", "consultar_farmacia", "consultar_espera"])


def test_herramientas_and_contextos_come_from_the_tool_calls_actually_made(run_agente):
    rows, _, _ = run_agente()
    first, second = rows

    assert first["herramientas"] == ["consultar_camas", "buscar_documentos"]
    assert json.loads(first["contextos"][0])["datos"]["libres"] == 7
    assert first["contextos"][1] and not first["contextos"][1].startswith("{")  # retriever fragments, not API JSON
    assert second["herramientas"] == ["consultar_camas", "consultar_espera"]
    assert "opciones" in json.loads(second["contextos"][0])  # a failed call is context the agent received too
    assert "minutos_por_nivel" in json.loads(second["contextos"][1])


def test_the_log_shows_each_tool_call_with_arguments_and_result_and_the_usage_of_each_model_call(run_agente):
    _, log, _ = run_agente()

    q2 = log[log.index("## Q2"):]
    assert '`consultar_camas` con argumentos `{"sector": "astronautas"}`' in q2
    assert "minutos_por_nivel" in q2
    assert q2.count("### Llamada al modelo") == 3
    assert "100 tokens de entrada" in q2 and "10 de salida" in q2
    assert "Depende del nivel de triage." in q2


def test_a_question_whose_run_keeps_failing_still_gets_a_row_and_the_error_is_logged(run_agente):
    script = {QUESTIONS[0]["pregunta"]: SCRIPT[QUESTIONS[0]["pregunta"]]}  # Q2 has no script: the model raises

    rows, log, _ = run_agente(script=script)

    assert [row["id"] for row in rows] == ["Q1", "Q2"]
    assert rows[1] == {"id": "Q2", "respuesta": "", "contextos": [], "herramientas": []}
    assert "**Error:**" in log[log.index("## Q2"):]
