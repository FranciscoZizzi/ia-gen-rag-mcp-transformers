# CLAUDE.md

Course mission, in Spanish: `mission.md`. Five parts: vector RAG (1), tool-calling agent (2), MCP server (3), NumPy attention layer (4) and a transformer block by hand (5, done without AI). Deadline: Friday 2026-10-09. Plans live in `docs/plans/`, the Part 1 spec in `SPEC.md`.

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
```

## Layout

- `rag/`: retrieval library (config, corpus, chunking, encoders, index, selection, retriever).
- `recuperar.py`: thin CLI adapter over `rag.Retriever`; reads `config/retriever.json`.
- `scripts/`: experiment runner and score analysis.
- `experimentos/`: one `<run>.jsonl`, `<run>.config.json` and `<run>.jsonl.eval.json` per configuration, plus the generated `RESULTS.md`.

## Workflow

- TDD, red then green, one vertical slice at a time. Tests live only at the agreed seams: the `recuperar.py` contract, `Retriever`, `chunk_corpus` and `select`.
- Mock only at the Hugging Face boundary. Everywhere else use the lexical `hashing_bow` encoder: real code, deterministic and offline.
- Retrieval code never reads `evidencia`; only tests and analysis do.
- One commit per work unit, Conventional Commits, one feature branch per part, rebase-merge PRs (no squash).

## Gotchas

- `atencion/test_atencion.py` reads and rewrites `sys.argv` at import time, so pytest only collects `tests/` (see `pyproject.toml`). Run it as `python3 atencion/test_atencion.py atencion.py`.
- The grader matches evidence as a normalized substring: a chunk boundary must never cut a sentence.
- Every `intfloat/multilingual-e5-*` model needs the `query: ` / `passage: ` prefixes, set in the encoder config.
- `paraphrase-multilingual-MiniLM-L12-v2` truncates its input at 128 tokens.
