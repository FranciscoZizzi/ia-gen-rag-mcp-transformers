"""The assistant's six tools as plain functions that return text, plus the descriptions the model reads.

agente.py wraps them with the Agents SDK's function_tool; the Part 3 MCP server can wrap the very same
methods with @mcp.tool(), so the tools live in one place.
"""
from __future__ import annotations

from collections.abc import Callable
from functools import cached_property
from pathlib import Path

from assistant.hospital_api import HospitalApi
from rag.config import load_config
from rag.corpus import load_corpus
from rag.retriever import Retriever

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RETRIEVER_CONFIG = REPO_ROOT / "config" / "retriever.json"

TOOL_NAMES = ["buscar_documentos", "consultar_camas", "consultar_guardia", "consultar_turnos",
              "consultar_farmacia", "consultar_espera"]

FRAGMENT_SEPARATOR = "\n\n---\n\n"

# Model-facing text, in Spanish like the questions. "{opciones}" is filled with the names the API accepts.
_DESCRIPTIONS = {
    "buscar_documentos": (
        "Busca en los documentos del hospital (normas y procedimientos que casi no cambian) y devuelve los "
        "fragmentos más relevantes. Usala para todo lo que es una regla o un trámite: horarios de visita, quién "
        "puede acompañar o quedarse, preparación y ayunos para estudios, qué documentación llevar, requisitos, "
        "cómo pedir o retirar algo, coberturas, derechos del paciente. No informa el estado del día. "
        "Hacé una búsqueda por tema, con una consulta concreta en español (por ejemplo 'qué documentación "
        "llevar a la primera consulta'). Temas de los documentos: {temas}."
    ),
    "consultar_camas": (
        "Estado de hoy de las camas de internación de un sector: total, ocupadas y libres. "
        "Sectores válidos: {opciones}."
    ),
    "consultar_guardia": (
        "Profesionales de guardia hoy en una especialidad, con su horario (por ejemplo 20:00-08:00 es el "
        "turno noche). Especialidades válidas: {opciones}."
    ),
    "consultar_turnos": (
        "Próximos turnos disponibles (fecha y hora) en consultorios externos de una especialidad, del más "
        "cercano al más lejano. Especialidades válidas: {opciones}."
    ),
    "consultar_farmacia": (
        "Stock actual de un medicamento en la farmacia del hospital y, si no hay, la fecha prevista de "
        "reposición. No dice cómo retirarlo. Medicamentos válidos: {opciones}."
    ),
    "consultar_espera": (
        "Minutos de espera actuales en la guardia para cada nivel de triage (rojo, naranja, amarillo, verde, "
        "azul). No recibe parámetros."
    ),
}

_ROUTES = {"consultar_camas": "/camas", "consultar_guardia": "/guardia", "consultar_turnos": "/turnos",
           "consultar_farmacia": "/farmacia"}


class HospitalTools:
    def __init__(self, api: HospitalApi, retriever: Retriever | None = None,
                 retriever_factory: Callable[[], Retriever] | None = None,
                 corpus_dir: Path = REPO_ROOT / "datos" / "corpus"):
        self.api = api
        self._retriever = retriever
        self._retriever_factory = retriever_factory or _frozen_retriever
        self._corpus_dir = Path(corpus_dir)

    @property
    def retriever(self) -> Retriever:
        """Built on the first search: loading the Part 1 encoder and reranker takes a while."""
        if self._retriever is None:
            self._retriever = self._retriever_factory()
        return self._retriever

    def buscar_documentos(self, consulta: str) -> str:
        """The Part 1 retriever's fragments for the query, best first, separated by '---' lines."""
        return FRAGMENT_SEPARATOR.join(fragment.text for fragment in self.retriever.search(consulta))

    def consultar_camas(self, sector: str) -> str:
        """GET /camas: total, occupied and free beds of a ward."""
        return self.api.get("/camas", sector=sector)

    def consultar_guardia(self, especialidad: str) -> str:
        """GET /guardia: today's on-call staff of a specialty and their hours."""
        return self.api.get("/guardia", especialidad=especialidad)

    def consultar_turnos(self, especialidad: str) -> str:
        """GET /turnos: next available outpatient appointments of a specialty."""
        return self.api.get("/turnos", especialidad=especialidad)

    def consultar_farmacia(self, medicamento: str) -> str:
        """GET /farmacia: stock of a drug and, when out of stock, the restock date."""
        return self.api.get("/farmacia", medicamento=medicamento)

    def consultar_espera(self) -> str:
        """GET /espera: current emergency-room waiting minutes per triage level."""
        return self.api.get("/espera")

    def descriptions(self) -> dict[str, str]:
        """What the model reads for each tool, with the valid names discovered from the API and the corpus."""
        return {name: _DESCRIPTIONS[name].format(**self._placeholders(name)) for name in TOOL_NAMES}

    def _placeholders(self, name: str) -> dict[str, str]:
        if name == "buscar_documentos":
            return {"temas": "; ".join(self._document_titles)}
        if name in _ROUTES:
            return {"opciones": ", ".join(self.api.options(_ROUTES[name]))}
        return {}

    @cached_property
    def _document_titles(self) -> list[str]:
        return [document.title for document in load_corpus(self._corpus_dir)]


def _frozen_retriever() -> Retriever:
    """The delivered Part 1 configuration, exactly what recuperar.py runs."""
    return Retriever.from_config(load_config(DEFAULT_RETRIEVER_CONFIG), base_dir=REPO_ROOT)
