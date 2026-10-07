# CLAUDE.md

Course mission, in Spanish: `mission.md`. Five parts: vector RAG (1), tool-calling agent (2), MCP server (3), NumPy attention layer (4) and a transformer block by hand (5, done without AI). Deadline: Friday 2026-10-09. Plans live in `docs/plans/`, the Part 1, 2 and 3 specs in `SPEC.md`.

## Language

- Code in English: modules, identifiers, docstrings, comments and commit messages.
- Grader-facing names stay exactly as the mission spells them: `recuperar.py`, `agente.py`, `servidor_mcp.py`, `agente_mcp.py`, `atencion.py`, the CLI flags (`--preguntas`, `--salida`), the JSON keys (`id`, `pregunta`, `evidencia`, `fragmentos`, `respuesta`, `contextos`, `herramientas`), `experimentos/` and the Part 2–3 tool names (`buscar_documentos`, `consultar_camas`, ...).
- `INFORME.md`, the report the graders read, is written in Spanish.

## Never modify

`evaluar/`, `api/`, `datos/` and `atencion/test_atencion.py`: the graders run their own copies. Call `evaluar/evaluar.py` as a subprocess, never import and patch it.

## Setup

```bash
uv venv .venv --python 3.14
uv pip install --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .venv/bin/python -r requirements-dev.txt
```

Install the CPU torch wheel first: the default Linux wheel pulls several GB of CUDA libraries.

## Commands

```bash
.venv/bin/python -m pytest                                    # offline, a few seconds
.venv/bin/python recuperar.py --preguntas datos/preguntas_recuperacion_dev.jsonl --salida resultados.jsonl
.venv/bin/python evaluar/evaluar.py recuperacion --preguntas datos/preguntas_recuperacion_dev.jsonl --resultados resultados.jsonl
.venv/bin/python scripts/run_experiments.py experimentos/grids/<grid>.json
.venv/bin/python api/servidor.py &                            # the agent needs it; the tests start their own copy
.venv/bin/python agente.py --preguntas datos/preguntas_agente_dev.jsonl --salida experimentos/agente/<run>/respuestas.jsonl
.venv/bin/python evaluar/evaluar.py agente --preguntas datos/preguntas_agente_dev.jsonl --respuestas experimentos/agente/<run>/respuestas.jsonl
.venv/bin/python agente_mcp.py --preguntas datos/preguntas_agente_dev.jsonl --salida experimentos/agente_mcp/<run>/respuestas_mcp.jsonl
.venv/bin/python scripts/summarize_agent_runs.py              # regenerates the RESULTS.md files and experimentos/agente_mcp/COMPARACION.md
```

The agent and the judge need `OPENROUTER_API_KEY`; keep it in `.env` (git-ignored) and `export $(cat .env)`.

## Layout

- `rag/`: retrieval library (config, corpus, text, chunking, encoders, selection, reranking, retriever, analysis).
- `recuperar.py`: thin CLI adapter over `rag.Retriever`; reads `config/retriever.json`.
- `scripts/`: experiment runner and score analysis (Part 1); agent ablation and run summary (Part 2).
- `assistant/`: Part 2 agent (hospital API client, the six tools, agent runner with usage capture, Markdown run log).
- `agente.py`: thin CLI adapter over `assistant`; its retriever reads `config/agent_retriever.json`.
- `servidor_mcp.py`: Part 3 FastMCP server (stdio); each `@mcp.tool()` delegates to `HospitalTools`, with the same descriptions.
- `agente_mcp.py`: Part 3 CLI; the Part 2 agent with its tools from `servidor_mcp.py` via `MCPServerStdio`. No API or retriever code of its own.
- `experimentos/agente/`: one folder per agent run (`respuestas.jsonl`, `.eval.json`, `.log.md`), `extra/` for `eval_extra/preguntas_agente_extra.jsonl`.
- `experimentos/agente_mcp/`: the same per-run folders for Part 3 (`respuestas_mcp.*`), plus the generated `COMPARACION.md` with Part 2.
- `experimentos/`: one `<run>.jsonl`, `<run>.config.json` and `<run>.jsonl.eval.json` per configuration, plus the generated `RESULTS.md`; `experimentos/extra/` holds the same runs on the extra validation set (`eval_extra/`).

## Workflow

- TDD, red then green, one vertical slice at a time. Tests live only at the agreed seams: the `recuperar.py`, `agente.py` and `agente_mcp.py` contracts, `servidor_mcp.py` (in process and over stdio), `Retriever`, `chunk_corpus`, `select` and `HospitalTools`.
- Mock only at the Hugging Face boundary and the LLM (a scripted `agents.Model`); tests start the real `api/servidor.py`. Everywhere else use the lexical `hashing_bow` encoder: real code, deterministic and offline.
- Retrieval code never reads `evidencia`; only tests and analysis do.
- One commit per work unit, Conventional Commits, one feature branch per part, rebase-merge PRs (no squash).

## Gotchas

- `atencion/test_atencion.py` reads and rewrites `sys.argv` at import time, so pytest only collects `tests/` (see `pyproject.toml`). Run it as `python3 atencion/test_atencion.py atencion.py`.
- The grader matches evidence as a normalized substring: a chunk boundary must never cut a sentence.
- Every `intfloat/multilingual-e5-*` model needs the `query: ` / `passage: ` prefixes, set in the encoder config.
- `paraphrase-multilingual-MiniLM-L12-v2` truncates its input at 128 tokens.
- On Windows, never name a file `con.*`, `nul.*`, `prn.*` or `aux.*`: they are devices, and reading one blocks.
- `servidor_mcp.py` speaks the protocol on stdout: anything else printed there breaks the client. Log to stderr.
- The MCP server loads e5-large and the reranker and embeds the corpus before it answers `initialize` (~2 min on CPU); `agente_mcp.py` waits up to 900 s.
- FastMCP leaves argument objects open, and the Agents SDK then drops strict mode: `servidor_mcp.py` closes them so Part 3 sees the Part 2 schemas.
- The API binds IPv4 only: use `127.0.0.1`, since `localhost` tries `::1` first and stalls ~2 s per call on Windows.
