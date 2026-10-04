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
