"""Ablation for the Part 2 report: agente.py with bare tool descriptions and a one-line prompt.

Same CLI as agente.py. It strips what the delivered agent adds on top of the tool names: the valid names
discovered from the API, the corpus topics, the routing hints and the answer rules.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agente  # noqa: E402
from assistant import agent, tools  # noqa: E402

BARE_DESCRIPTIONS = {
    "buscar_documentos": "Busca en los documentos del hospital.",
    "consultar_camas": "Consulta las camas de un sector.",
    "consultar_guardia": "Consulta la guardia de una especialidad.",
    "consultar_turnos": "Consulta los turnos de una especialidad.",
    "consultar_farmacia": "Consulta un medicamento en la farmacia.",
    "consultar_espera": "Consulta la espera en la guardia.",
}
BARE_INSTRUCTIONS = "Sos el asistente del Hospital Provincial Arroyo Claro. Usá las herramientas para responder."

if __name__ == "__main__":
    tools._DESCRIPTIONS = BARE_DESCRIPTIONS
    agent.INSTRUCTIONS = BARE_INSTRUCTIONS
    agente.main()
