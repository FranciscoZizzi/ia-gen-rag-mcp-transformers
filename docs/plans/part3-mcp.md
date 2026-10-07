# Plan — Parte 3: las mismas herramientas como servidor MCP

**Fecha:** 2026-10-07 · **Entrega de la misión:** viernes 2026-10-09
**Alcance:** `servidor_mcp.py`, `agente_mcp.py`, las corridas de `experimentos/agente_mcp/` y la comparación con la Parte 2.

## TL;DR

- `servidor_mcp.py` usa FastMCP (SDK `mcp` 1.x, transporte stdio) y registra las seis herramientas con `@mcp.tool()`. Cada función solo delega en `HospitalTools` (`assistant/tools.py`), así que la lógica sigue en un solo lugar.
- `agente_mcp.py` es el agente de la Parte 2 sin herramientas propias. Lanza el servidor con `MCPServerStdio`, descubre las herramientas con `tools/list` y las llama con `tools/call`.
- La comparación con la Parte 2 tiene que medir **el transporte y nada más**. Por eso son iguales el prompt, el modelo, los parámetros, el recuperador (`config/agent_retriever.json`), las descripciones, los esquemas de argumentos y la forma de los `contextos`. Los tests lo verifican.

## Qué hizo falta para que la comparación sea justa

| Diferencia que trae el SDK | Arreglo | Dónde |
|---|---|---|
| Las descripciones de la API son dinámicas (opciones válidas) | El servidor las toma de `HospitalTools.descriptions()` al arrancar | `servidor_mcp.build_server` |
| FastMCP deja abiertos los objetos de argumentos, y el SDK de agentes no convierte un objeto abierto en esquema estricto | El servidor declara `additionalProperties: false`, y el agente pide `convert_schemas_to_strict` | `_ClosedArgumentsFastMCP`, `build_mcp_agent` |
| El resultado de una herramienta MCP llega como bloques `{"type": "text", "text": ...}` | La traza se queda con el texto, igual que en la Parte 2 | `assistant/agent._tool_output_text` |
| `stdio_client` solo hereda unas pocas variables de entorno | Se le pasa el entorno completo, menos `OPENROUTER_API_KEY` | `agente_mcp.mcp_server` |
| El servidor carga e5-large y el reranker y embebe el corpus antes de `initialize` (112 s medidos en CPU) | La sesión espera hasta 900 s | `agente_mcp.SERVER_TIMEOUT_SECONDS` |

Lo único distinto que queda es el `title` del esquema, que cada librería genera por su cuenta (`buscar_documentosArguments` contra `buscar_documentos_args`).

## Reglas del protocolo

- stdout es el canal del protocolo. El recuperador se carga una sola vez, al armar el servidor, con stdout redirigido a stderr. FastMCP manda sus logs a stderr.
- `agente_mcp.py` no importa el recuperador ni el cliente de la API. Solo usa el agente, el log y la lectura y escritura de JSONL, y un test lo verifica.

## Tests

| Costura | Cubre |
|---|---|
| `servidor_mcp.build_server` | Las seis herramientas con sus nombres, descripciones idénticas a las de la Parte 2, los mismos argumentos y un esquema cerrado, sin `outputSchema`; recuperador cargado una vez y stdout limpio |
| Servidor por stdio (sin LLM) | `tools/list` y `tools/call` desde un `ClientSession` real dan el mismo texto que las herramientas llamadas en proceso; un nombre inválido devuelve el error con sus opciones |
| `agente_mcp.main` | Formato de filas; el modelo ve las descripciones y los esquemas de la Parte 2; para los mismos turnos del modelo, las filas son **idénticas** a las de `agente.py`; log con transporte, argumentos, resultados y usage; una pregunta que falla igual tiene su fila; no hay imports de la API ni del recuperador |

## Corridas

Cada corrida va a `experimentos/agente_mcp/<corrida>/`, con `respuestas_mcp.jsonl`, `respuestas_mcp.jsonl.eval.json` y `respuestas_mcp.log.md`. La entregada se copia a la raíz. `scripts/summarize_agent_runs.py` genera `RESULTS.md` y `COMPARACION.md`, donde cada corrida MCP aparece al lado de la corrida de la Parte 2 con el mismo nombre.
