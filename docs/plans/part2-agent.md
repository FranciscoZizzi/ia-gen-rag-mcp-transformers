# Plan — Parte 2: un agente con dos fuentes

**Fecha:** 2026-10-04 · **Entrega de la misión:** viernes 2026-10-09
**Alcance:** `agente.py`, el paquete `assistant/`, las corridas de `experimentos/agente/` y la sección de la Parte 2 de `INFORME.md`.

## TL;DR

- Agente con tool calling sobre `deepseek/deepseek-v4-flash-0731` vía OpenRouter, armado con el **SDK de agentes de OpenAI** (`openai-agents`), el framework que recomienda la consigna. La Parte 3 reutiliza el mismo framework con `MCPServerStdio`.
- Las seis herramientas viven en `assistant/tools.py` como funciones Python puras que devuelven texto. `agente.py` las envuelve con `function_tool`; la Parte 3 puede envolver exactamente las mismas funciones con `@mcp.tool()`, así no hay código duplicado.
- `buscar_documentos` es el recuperador de la Parte 1 tal cual quedó congelado en `config/retriever.json`.
- Las descripciones de las herramientas de la API listan los nombres válidos (sectores, especialidades, medicamentos). Esos nombres no se escriben a mano: se descubren al arrancar pidiéndole a la API cada ruta sin parámetro, que devuelve la lista de opciones. Si la API cambia, las descripciones cambian solas.
- Cada corrida deja `respuestas.jsonl`, su `.eval.json` del evaluador oficial y un log `.md` con cada llamada al modelo (tokens y costo que informa OpenRouter), cada llamada a herramienta con sus argumentos y su resultado, y la respuesta.

## 1. Qué mide el evaluador

`evaluar.py agente` calcula sin juez el **ruteo** (proporción de herramientas esperadas que el agente usó: llamar de más no penaliza el ruteo) y le pide a `google/gemini-3.7-flash` tres notas de 1 a 5:

| Métrica | Qué la baja | Decisión de diseño |
|---|---|---|
| Context Relevance | contextos con ruido o incompletos | recuperador con top-1 y reranker (Parte 1); el agente no llama herramientas por las dudas |
| Faithfulness | afirmaciones que no están en los contextos | el prompt prohíbe responder de memoria y agregar recomendaciones propias |
| Answer Relevance | respuesta incompleta | el prompt pide cubrir cada parte de la pregunta con la herramienta que corresponda |

`contextos` tiene que contener **todo** lo que devolvieron las herramientas: si el agente se corrige después de un error de la API, el error también va (es ruido real que el juez debe ver).

## 2. Diseño

```
agente.py                    CLI del contrato: --preguntas, --salida (+ --log, --api-url, --modelo)
assistant/hospital_api.py    cliente HTTP de la API (stdlib); devuelve el JSON como texto también en 4xx
assistant/tools.py           HospitalTools: las seis herramientas + sus descripciones para el modelo
assistant/agent.py           arma el Agent, corre una pregunta y devuelve una traza (llamadas, usage, respuesta)
assistant/usage.py           captura el usage de OpenRouter (tokens y costo) de cada respuesta HTTP
assistant/report.py          escribe el log .md de la corrida
```

- **Una conversación por pregunta**, sin memoria entre preguntas.
- **Usage y costo.** El SDK expone tokens por llamada (`RunResult.raw_responses`), pero no el costo. Un hook de `httpx` en el cliente de OpenAI lee cada respuesta de `/chat/completions` y guarda el bloque `usage` de OpenRouter, que trae `cost` en USD. El log muestra los dos.
- **Errores.** Una herramienta nunca lanza: un nombre inválido devuelve el JSON de error de la API con las opciones válidas, y el modelo puede corregirse. Si falla una corrida entera (red, límite de turnos), se reintenta; si sigue fallando, la pregunta queda con respuesta vacía y el error en el log.

## 3. Tests (TDD, en las costuras)

| Costura | Cubre |
|---|---|
| `HospitalTools` | cada herramienta llama a su ruta y devuelve el JSON como texto; un nombre inválido devuelve el error con opciones sin lanzar; las descripciones listan las opciones que informa la API; `buscar_documentos` devuelve los fragmentos del recuperador |
| `agente.main` | formato de `respuestas.jsonl` (ids y orden), `herramientas` y `contextos` salen de la traza real y el log `.md` tiene argumentos, resultados y usage (el evaluador oficial siempre llama al juez, así que no entra en los tests offline) |

La API se levanta de verdad (`api/servidor.py` en un puerto libre) y el recuperador usa el encoder léxico `hashing_bow`. El único doble es el modelo: un `Model` del SDK con respuestas guionadas, así los tests corren offline y sin costo.

## 4. Experimentos

Cada corrida va a `experimentos/agente/<corrida>/` con `respuestas.jsonl`, `respuestas.jsonl.eval.json` y `respuestas.log.md`. La entregada se copia a la raíz (`respuestas.jsonl`, `.eval.json`, `respuestas.log.md`). El informe tiene una fila por corrida y analiza las preguntas donde el agente falló, con los logs.
