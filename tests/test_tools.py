"""HospitalTools: the six tools that agente.py exposes to the model and the MCP server will reuse."""
import json

import pytest

from assistant.hospital_api import HospitalApi
from assistant.tools import TOOL_NAMES, HospitalTools


@pytest.fixture
def tools(api_url, lexical_retriever):
    return HospitalTools(HospitalApi(api_url), retriever=lexical_retriever)


def test_tool_names_are_the_ones_the_grader_checks():
    assert TOOL_NAMES == ["buscar_documentos", "consultar_camas", "consultar_guardia", "consultar_turnos",
                          "consultar_farmacia", "consultar_espera"]


def test_each_api_tool_returns_its_route_json_as_text(tools):
    camas = json.loads(tools.consultar_camas("pediatria"))
    assert camas["sector"] == "pediatria" and camas["datos"]["libres"] == camas["datos"]["total"] - camas["datos"]["ocupadas"]
    assert json.loads(tools.consultar_guardia("cardiologia"))["especialidad"] == "cardiologia"
    assert json.loads(tools.consultar_turnos("traumatologia"))["especialidad"] == "traumatologia"
    assert "datos" in json.loads(tools.consultar_farmacia("enalapril 10 mg"))
    assert "minutos_por_nivel" in json.loads(tools.consultar_espera())


def test_names_are_matched_like_the_api_does(tools):
    assert json.loads(tools.consultar_camas("Terapia Intensiva"))["sector"] == "terapia_intensiva"


def test_an_unknown_name_returns_the_api_error_with_the_valid_options_instead_of_raising(tools):
    error = json.loads(tools.consultar_camas("astronautas"))

    assert "error" in error and "pediatria" in error["opciones"]


def test_api_tool_descriptions_list_the_options_the_api_reports(tools):
    descriptions = tools.descriptions()

    assert set(descriptions) == set(TOOL_NAMES)
    assert "terapia_intensiva" in descriptions["consultar_camas"]
    assert "cardiologia" in descriptions["consultar_guardia"]
    assert "traumatologia" in descriptions["consultar_turnos"]
    assert "enalapril 10 mg" in descriptions["consultar_farmacia"]


def test_buscar_documentos_returns_the_retriever_fragments(tools, lexical_retriever):
    query = "¿Qué hay que llevar a la primera consulta con un especialista?"
    expected = [fragment.text for fragment in lexical_retriever.search(query)]

    result = tools.buscar_documentos(query)

    assert expected and all(text in result for text in expected)


def test_the_retriever_is_built_lazily_on_the_first_search(api_url, lexical_retriever):
    built = []

    def factory():
        built.append(True)
        return lexical_retriever

    tools = HospitalTools(HospitalApi(api_url), retriever_factory=factory)
    tools.consultar_espera()
    assert not built

    tools.buscar_documentos("donar sangre")
    tools.buscar_documentos("visitas")
    assert built == [True]
