# Parte 2 contra Parte 3

Generado por `scripts/summarize_agent_runs.py`: cada corrida de `experimentos/agente_mcp/` junto a la corrida de `experimentos/agente/` con el mismo nombre (mismo prompt, modelo, descripciones y recuperador; cambia el transporte de las herramientas). Costos en USD.

| Corrida | Parte | Ruteo | Context Rel. | Faithfulness | Answer Rel. | Llamadas al modelo | Llamadas a herramientas | Tokens entrada | Tokens salida (razonamiento) | Costo agente | Costo juez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `extra/v2-margen` | 2 (function tools) | 1.00 | 5.000 | 5.000 | 5.000 | 24 | 16 | 45170 | 2476 (1107) | 0.003856 | 0.01857 |
| `extra/v2-margen` | 3 (MCP) | 1.00 | 5.000 | 5.000 | 4.917 | 24 | 16 | 45278 | 2463 (1131) | 0.003968 | 0.01798 |
| `v2-margen` | 2 (function tools) | 1.00 | 4.917 | 5.000 | 5.000 | 24 | 15 | 44982 | 2311 (818) | 0.003642 | 0.01629 |
| `v2-margen` | 3 (MCP) | 1.00 | 5.000 | 5.000 | 5.000 | 24 | 15 | 44898 | 2329 (896) | 0.003789 | 0.01593 |

## `extra/v2-margen`, pregunta por pregunta

| Pregunta | Herramientas P2 | Herramientas P3 | CR / F / AR P2 | CR / F / AR P3 | Mismos contextos | Misma respuesta |
|---|---|---|---|---|---|---|
| Y01 | buscar_documentos | buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | sí |
| Y02 | buscar_documentos | buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| Y03 | buscar_documentos | buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | sí |
| Y04 | consultar_camas | consultar_camas | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| Y05 | consultar_guardia | consultar_guardia | 5 / 5 / 5 | 5 / 5 / 5 | sí | sí |
| Y06 | consultar_turnos | consultar_turnos | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| Y07 | consultar_farmacia | consultar_farmacia | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| Y08 | consultar_espera | consultar_espera | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| Y09 | consultar_turnos, buscar_documentos | consultar_turnos, buscar_documentos | 5 / 5 / 5 | 5 / 5 / 4 | sí | **no** |
| Y10 | consultar_camas, buscar_documentos | consultar_camas, buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| Y11 | consultar_farmacia, buscar_documentos | consultar_farmacia, buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| Y12 | consultar_espera, buscar_documentos | consultar_espera, buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | **no** | **no** |

## `v2-margen`, pregunta por pregunta

| Pregunta | Herramientas P2 | Herramientas P3 | CR / F / AR P2 | CR / F / AR P3 | Mismos contextos | Misma respuesta |
|---|---|---|---|---|---|---|
| A01 | buscar_documentos | buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | sí |
| A02 | buscar_documentos | buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| A03 | buscar_documentos | buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | sí |
| A04 | buscar_documentos | buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| A05 | consultar_camas | consultar_camas | 5 / 5 / 5 | 5 / 5 / 5 | sí | sí |
| A06 | consultar_guardia | consultar_guardia | 5 / 5 / 5 | 5 / 5 / 5 | sí | sí |
| A07 | consultar_turnos | consultar_turnos | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| A08 | consultar_farmacia | consultar_farmacia | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| A09 | consultar_espera | consultar_espera | 5 / 5 / 5 | 5 / 5 / 5 | sí | sí |
| A10 | consultar_camas, buscar_documentos | consultar_camas, buscar_documentos | 4 / 5 / 5 | 5 / 5 / 5 | **no** | **no** |
| A11 | consultar_turnos, buscar_documentos | consultar_turnos, buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
| A12 | consultar_farmacia, buscar_documentos | consultar_farmacia, buscar_documentos | 5 / 5 / 5 | 5 / 5 / 5 | sí | **no** |
