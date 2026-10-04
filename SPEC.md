# SPEC — Part 1: vector retriever

Implementation plan and rationale: `docs/plans/part1-vector-rag.md`.

## Contract

```bash
python3 recuperar.py --preguntas <questions.jsonl> --salida <results.jsonl> [--config config/retriever.json]
```

- **Input**: one JSON object per line with `id` and `pregunta`. Any other key, `evidencia` included, is ignored.
- **Output**: one line per input question, in input order: `{"id": "<id>", "fragmentos": ["<text>", ...]}`, fragments ordered by relevance, UTF-8.
- **Configuration**: `config/retriever.json` unless `--config` says otherwise. Paths inside it are relative to the repository root.
- `evaluar/evaluar.py recuperacion` accepts the output.

## Behavior

1. **Corpus.** Every `*.md` in `corpus_dir`. `# ` is the document title, `## ` opens a section, and text before the first `##` is a section without heading. Blocks are separated by blank lines.
2. **Sentences.** Each list item is a unit. Within a paragraph, a sentence ends after `.`, `!` or `?` followed by whitespace and an uppercase letter, a digit or an opening mark (`¿`, `¡`, `(`, quotes).
3. **Chunking.** No chunk is empty, cuts a sentence or crosses documents.

   | Strategy | Chunks |
   |---|---|
   | `paragraph` | One per block, verbatim |
   | `section` | One per section, verbatim. A section longer than `max_chars` is packed block by block; a block longer than `max_chars` is packed sentence by sentence |
   | `fixed` | The document's sentences packed greedily up to `max_chars`, joined by spaces. The next chunk repeats the last `overlap_sentences` sentences when they still leave room for a new one |
   | `sentence` | One per sentence |

   A single unit longer than `max_chars` becomes a chunk of its own.
4. **Metadata.** With `metadata: true` a chunk is rendered as `"<title> — <section>\n<text>"`, or `"<title>\n<text>"` when it has no section. The rendered text is both what gets embedded and the returned fragment.
5. **Scoring.** Passages and queries are embedded with the configured encoder (L2-normalized, with the encoder's prefixes) and scored by cosine similarity.
6. **Reranking (optional).** With a `reranker`, a cross-encoder re-scores the bi-encoder's best `candidates` chunks, reading query and passage together; the ranking keeps only those candidates, in the cross-encoder's order.
7. **Cut-off.** All chunks are ranked by descending score, ties in corpus order, then:
   - keep at most `top_k`;
   - drop candidates below `min_score`, if set;
   - drop candidates more than `max_margin` below the best, if set;
   - always keep the best candidate.

## Configuration

```json
{
  "corpus_dir": "datos/corpus",
  "encoder": {
    "type": "sentence_transformer",
    "model": "intfloat/multilingual-e5-base",
    "revision": null,
    "query_prefix": "query: ",
    "passage_prefix": "passage: ",
    "max_seq_length": null,
    "batch_size": 16
  },
  "chunking": {"strategy": "section", "max_chars": 700, "overlap_sentences": 0, "metadata": true},
  "selection": {"top_k": 1, "min_score": null, "max_margin": null},
  "reranker": null
}
```

`reranker`, when set: `{"model": "BAAI/bge-reranker-v2-m3", "candidates": 10, "revision": null, "batch_size": 16}`.

Unknown keys are rejected, so a typo in a grid cannot pass silently.

| Encoder `type` | What it is |
|---|---|
| `mean_pooling` | A raw transformer (BERT) via `transformers`: masked mean of the last hidden layer. The mandatory baseline |
| `sentence_transformer` | A model trained for sentence embeddings, via `sentence-transformers` |
| `hashing_bow` | Lexical bag of words with hashed term counts. Offline test double and lexical sanity row, not a transformer |

## Experiments

A grid file in `experimentos/grids/` crosses named encoders, chunkings and selections:

```json
{
  "stage": "A",
  "questions": "datos/preguntas_recuperacion_dev.jsonl",
  "encoders": {"e5base": {"type": "sentence_transformer", "model": "intfloat/multilingual-e5-base", "query_prefix": "query: ", "passage_prefix": "passage: "}},
  "chunkings": {"section700-meta": {"strategy": "section", "max_chars": 700, "metadata": true}},
  "selections": {"k1": {"top_k": 1}, "k3": {"top_k": 3}}
}
```

An optional top-level `"reranker"` applies to every run of the grid. Each combination is a run named `<stage>-<encoder>-<chunking>-<selection>` that writes `experimentos/<run>.jsonl` and `experimentos/<run>.config.json`, then runs the official evaluator, which writes `experimentos/<run>.jsonl.eval.json`. `experimentos/RESULTS.md` is regenerated from every run on disk. `<run>.config.json` is a complete configuration: `recuperar.py --config` reproduces the run.

`--questions eval_extra/preguntas_recuperacion_extra.jsonl --out-dir experimentos/extra` runs the same grid on the extra validation set, used only to confirm finalists.

## Tested seams

Agreed with the team: tests only at the seams that decide the grade or that Parts 2–3 reuse.

| Seam | Covers |
|---|---|
| `recuperar.main` | Output format, ids and order, no use of `evidencia`, the official evaluator accepts the output |
| `Retriever` | Descending ranking, search = ranking + cut-off, metadata headers, embedding cache keyed by content, reranker order |
| `chunk_corpus` | Each strategy's output and the invariants of §3 |
| `select` | The cut-off rules of §7 |

## Acceptance

- [x] The contract command runs from a clean clone after `pip install -r requirements.txt`, with no extra flags (checked on 2026-10-04: CR 1.00 on dev, output byte-identical to the committed `resultados.jsonl`).
- [x] The winning configuration is fixed in `config/retriever.json`, with both model revisions pinned.
- [x] At least 3 encoders compared, the BERT baseline included; every row of the report table has its `.eval.json` in `experimentos/`.
- [x] The delivered configuration clearly beats the BERT baseline: +0.70 CR on dev (95% paired bootstrap interval +0.50 to +0.90).
- [x] `INFORME.md` explains the choice with numbers.
- [x] `pytest` passes offline.

# SPEC — Part 2: tool-calling agent

Plan and rationale: `docs/plans/part2-agent.md`. Results and failure analysis: `INFORME.md`, Parte 2.

## Contract

```bash
python3 api/servidor.py &
OPENROUTER_API_KEY=... python3 agente.py --preguntas <questions.jsonl> --salida <answers.jsonl> \
    [--log <run.log.md>] [--modelo <openrouter id>] [--api-url <url>] [--config config/agent_retriever.json]
```

- **Input**: one JSON object per line with `id` and `pregunta`; any other key is ignored.
- **Output**: one line per input question, in input order: `{"id", "respuesta", "contextos", "herramientas"}`. `contextos` is every tool result as text, failed API calls included; `herramientas` the tools called, each once, in order of first use. A question whose run fails three times still gets a row, with an empty answer.
- **Log**: `<salida without .jsonl>.log.md` unless `--log` says otherwise: per question, every model call with its tokens and the cost OpenRouter reports, every tool call with arguments and result, and the answer.
- **Defaults**: model `deepseek/deepseek-v4-flash-0731`, API `$HOSPITAL_API_URL` or `http://127.0.0.1:8765`.

## Tools

`assistant/tools.py` (`HospitalTools`), plain functions that return text and never raise:

| Tool | Does |
|---|---|
| `buscar_documentos(consulta)` | The Part 1 retriever with `config/agent_retriever.json`: fragments separated by `---` lines |
| `consultar_camas(sector)` | `GET /camas` |
| `consultar_guardia(especialidad)` | `GET /guardia` |
| `consultar_turnos(especialidad)` | `GET /turnos` |
| `consultar_farmacia(medicamento)` | `GET /farmacia` |
| `consultar_espera()` | `GET /espera` |

The API tools return the route's JSON verbatim, error bodies (with the valid options) included. Their descriptions list the valid names, discovered at start-up by calling each route without its parameter; `buscar_documentos` lists the corpus document titles. The retriever loads lazily, on the first search.

`config/agent_retriever.json` is `config/retriever.json` with an adaptive cut-off (`top_k` 3, `max_margin` 0.45): one fragment when the reranker is sure, up to three when the runners-up score close to the best.

## Tested seams

| Seam | Covers |
|---|---|
| `HospitalTools` | Tool names, each route's JSON as text, API-style name matching, errors with options instead of exceptions, descriptions with the API's options, retriever fragments, lazy retriever |
| `agente.main` | Row format, ids and order, the six tools offered, `herramientas` and `contextos` from the calls actually made (failed ones included), the log's arguments, results and per-call usage, a failing question still gets a row |

The API is the real `api/servidor.py` on a free port and the retriever the lexical `hashing_bow`; the only double is the model, a scripted `agents.Model`.

## Acceptance

- [x] The contract command runs against the API and writes `respuestas.jsonl` and `respuestas.log.md`.
- [x] Routing 1.00 and the three judge metrics above 4 on dev (`respuestas.jsonl.eval.json`: 4.92 / 5.00 / 5.00).
- [x] One `.log.md` per benchmark run, in `experimentos/agente/`.
- [x] `INFORME.md` analyses the questions where the agent failed, from the logs.
- [x] `pytest` passes offline.
