# Resultados de la Parte 1

Preguntas: `eval_extra/preguntas_recuperacion_extra.jsonl`. Generado por `scripts/run_experiments.py` a partir de los `.eval.json` del evaluador oficial. No editar a mano.

| Run | Encoder | Chunking | Metadatos | Corte | CR | Recall | Precision | MRR | k medio | Caracteres |
|---|---|---|---|---|---|---|---|---|---|---|
| [A-beto-section700meta-k1](A-beto-section700meta-k1.jsonl.eval.json) | bert-base-spanish-wwm-cased (promedio de tokens) | section ≤700 | sí | k=1 | 0.314 | 0.309 | 0.324 | 0.324 | 1.00 | 308 |
| [A-beto-section700meta-k3](A-beto-section700meta-k3.jsonl.eval.json) | bert-base-spanish-wwm-cased (promedio de tokens) | section ≤700 | sí | k=3 | 0.271 | 0.515 | 0.186 | 0.407 | 3.00 | 941 |
| [A-bgem3-section700meta-k1](A-bgem3-section700meta-k1.jsonl.eval.json) | bge-m3 | section ≤700 | sí | k=1 | 0.892 | 0.882 | 0.912 | 0.912 | 1.00 | 326 |
| [A-bgem3-section700meta-k3](A-bgem3-section700meta-k3.jsonl.eval.json) | bge-m3 | section ≤700 | sí | k=3 | 0.518 | 1.000 | 0.353 | 0.951 | 3.00 | 902 |
| [A-e5base-section700meta-k1](A-e5base-section700meta-k1.jsonl.eval.json) | multilingual-e5-base | section ≤700 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 299 |
| [A-e5base-section700meta-k3](A-e5base-section700meta-k3.jsonl.eval.json) | multilingual-e5-base | section ≤700 | sí | k=3 | 0.518 | 1.000 | 0.353 | 0.931 | 3.00 | 902 |
| [A-e5large-section700meta-k1](A-e5large-section700meta-k1.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=1 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 327 |
| [A-e5large-section700meta-k3](A-e5large-section700meta-k3.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=3 | 0.503 | 0.971 | 0.343 | 0.956 | 3.00 | 860 |
| [A-e5small-section700meta-k1](A-e5small-section700meta-k1.jsonl.eval.json) | multilingual-e5-small | section ≤700 | sí | k=1 | 0.833 | 0.824 | 0.853 | 0.853 | 1.00 | 352 |
| [A-e5small-section700meta-k3](A-e5small-section700meta-k3.jsonl.eval.json) | multilingual-e5-small | section ≤700 | sí | k=3 | 0.503 | 0.971 | 0.343 | 0.907 | 3.00 | 952 |
| [A-lexical-section700meta-k1](A-lexical-section700meta-k1.jsonl.eval.json) | léxico (bolsa de palabras) | section ≤700 | sí | k=1 | 0.422 | 0.412 | 0.441 | 0.441 | 1.00 | 254 |
| [A-lexical-section700meta-k3](A-lexical-section700meta-k3.jsonl.eval.json) | léxico (bolsa de palabras) | section ≤700 | sí | k=3 | 0.297 | 0.559 | 0.206 | 0.490 | 3.00 | 746 |
| [A-mbert-section700meta-k1](A-mbert-section700meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | sí | k=1 | 0.147 | 0.147 | 0.147 | 0.147 | 1.00 | 291 |
| [A-mbert-section700meta-k3](A-mbert-section700meta-k3.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | sí | k=3 | 0.159 | 0.309 | 0.108 | 0.221 | 3.00 | 896 |
| [A-minilm-section700meta-k1](A-minilm-section700meta-k1.jsonl.eval.json) | paraphrase-multilingual-MiniLM-L12-v2 | section ≤700 | sí | k=1 | 0.578 | 0.574 | 0.588 | 0.588 | 1.00 | 333 |
| [A-minilm-section700meta-k3](A-minilm-section700meta-k3.jsonl.eval.json) | paraphrase-multilingual-MiniLM-L12-v2 | section ≤700 | sí | k=3 | 0.459 | 0.882 | 0.314 | 0.721 | 3.00 | 879 |
| [B-bgem3-fixed200meta-k1](B-bgem3-fixed200meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤200, solap. 0 | sí | k=1 | 0.774 | 0.765 | 0.794 | 0.794 | 1.00 | 186 |
| [B-bgem3-fixed200o1meta-k1](B-bgem3-fixed200o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤200, solap. 1 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 194 |
| [B-bgem3-fixed400meta-k1](B-bgem3-fixed400meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤400, solap. 0 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 349 |
| [B-bgem3-fixed400o1meta-k1](B-bgem3-fixed400o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤400, solap. 1 | sí | k=1 | 0.804 | 0.794 | 0.824 | 0.824 | 1.00 | 352 |
| [B-bgem3-fixed800meta-k1](B-bgem3-fixed800meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤800, solap. 0 | sí | k=1 | 0.804 | 0.794 | 0.824 | 0.824 | 1.00 | 604 |
| [B-bgem3-fixed800o1meta-k1](B-bgem3-fixed800o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤800, solap. 1 | sí | k=1 | 0.804 | 0.794 | 0.824 | 0.824 | 1.00 | 598 |
| [B-bgem3-paragraphmeta-k1](B-bgem3-paragraphmeta-k1.jsonl.eval.json) | bge-m3 | paragraph | sí | k=1 | 0.833 | 0.824 | 0.853 | 0.853 | 1.00 | 236 |
| [B-bgem3-section400meta-k1](B-bgem3-section400meta-k1.jsonl.eval.json) | bge-m3 | section ≤400 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 272 |
| [B-bgem3-section700-k1](B-bgem3-section700-k1.jsonl.eval.json) | bge-m3 | section ≤700 | no | k=1 | 0.843 | 0.838 | 0.853 | 0.853 | 1.00 | 257 |
| [B-bgem3-sentencemeta-k1](B-bgem3-sentencemeta-k1.jsonl.eval.json) | bge-m3 | sentence | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 145 |
| [B-e5large-fixed200meta-k1](B-e5large-fixed200meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤200, solap. 0 | sí | k=1 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 187 |
| [B-e5large-fixed200o1meta-k1](B-e5large-fixed200o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤200, solap. 1 | sí | k=1 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 194 |
| [B-e5large-fixed400meta-k1](B-e5large-fixed400meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤400, solap. 0 | sí | k=1 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 356 |
| [B-e5large-fixed400o1meta-k1](B-e5large-fixed400o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤400, solap. 1 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 356 |
| [B-e5large-fixed800meta-k1](B-e5large-fixed800meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤800, solap. 0 | sí | k=1 | 0.892 | 0.882 | 0.912 | 0.912 | 1.00 | 615 |
| [B-e5large-fixed800o1meta-k1](B-e5large-fixed800o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤800, solap. 1 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 605 |
| [B-e5large-paragraphmeta-k1](B-e5large-paragraphmeta-k1.jsonl.eval.json) | multilingual-e5-large | paragraph | sí | k=1 | 0.892 | 0.882 | 0.912 | 0.912 | 1.00 | 233 |
| [B-e5large-section400meta-k1](B-e5large-section400meta-k1.jsonl.eval.json) | multilingual-e5-large | section ≤400 | sí | k=1 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 268 |
| [B-e5large-section700-k1](B-e5large-section700-k1.jsonl.eval.json) | multilingual-e5-large | section ≤700 | no | k=1 | 0.843 | 0.838 | 0.853 | 0.853 | 1.00 | 261 |
| [B-e5large-sentencemeta-k1](B-e5large-sentencemeta-k1.jsonl.eval.json) | multilingual-e5-large | sentence | sí | k=1 | 0.892 | 0.882 | 0.912 | 0.912 | 1.00 | 144 |
| [B-mbert-fixed200meta-k1](B-mbert-fixed200meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤200, solap. 0 | sí | k=1 | 0.176 | 0.176 | 0.176 | 0.176 | 1.00 | 219 |
| [B-mbert-fixed200o1meta-k1](B-mbert-fixed200o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤200, solap. 1 | sí | k=1 | 0.147 | 0.147 | 0.147 | 0.147 | 1.00 | 211 |
| [B-mbert-fixed400meta-k1](B-mbert-fixed400meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤400, solap. 0 | sí | k=1 | 0.206 | 0.206 | 0.206 | 0.206 | 1.00 | 363 |
| [B-mbert-fixed400o1meta-k1](B-mbert-fixed400o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤400, solap. 1 | sí | k=1 | 0.176 | 0.176 | 0.176 | 0.176 | 1.00 | 376 |
| [B-mbert-fixed800meta-k1](B-mbert-fixed800meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤800, solap. 0 | sí | k=1 | 0.265 | 0.265 | 0.265 | 0.265 | 1.00 | 601 |
| [B-mbert-fixed800o1meta-k1](B-mbert-fixed800o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤800, solap. 1 | sí | k=1 | 0.265 | 0.265 | 0.265 | 0.265 | 1.00 | 601 |
| [B-mbert-paragraphmeta-k1](B-mbert-paragraphmeta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | paragraph | sí | k=1 | 0.206 | 0.206 | 0.206 | 0.206 | 1.00 | 242 |
| [B-mbert-section400meta-k1](B-mbert-section400meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤400 | sí | k=1 | 0.206 | 0.206 | 0.206 | 0.206 | 1.00 | 273 |
| [B-mbert-section700-k1](B-mbert-section700-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | no | k=1 | 0.255 | 0.250 | 0.265 | 0.265 | 1.00 | 224 |
| [B-mbert-sentencemeta-k1](B-mbert-sentencemeta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | sentence | sí | k=1 | 0.118 | 0.118 | 0.118 | 0.118 | 1.00 | 138 |
| [C-e5large-section700meta-k2](C-e5large-section700meta-k2.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=2 | 0.667 | 0.971 | 0.515 | 0.956 | 2.00 | 593 |
| [C-e5large-section700meta-k2m005](C-e5large-section700meta-k2m005.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.005 | 0.902 | 0.926 | 0.897 | 0.941 | 1.12 | 362 |
| [C-e5large-section700meta-k2m01](C-e5large-section700meta-k2m01.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.01 | 0.922 | 0.956 | 0.912 | 0.956 | 1.15 | 368 |
| [C-e5large-section700meta-k2m02](C-e5large-section700meta-k2m02.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.02 | 0.853 | 0.956 | 0.809 | 0.956 | 1.35 | 423 |
| [C-e5large-section700meta-k2m03](C-e5large-section700meta-k2m03.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.03 | 0.794 | 0.971 | 0.706 | 0.956 | 1.62 | 488 |
| [C-e5large-section700meta-k3m01](C-e5large-section700meta-k3m01.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, Δ≤0.01 | 0.906 | 0.956 | 0.892 | 0.956 | 1.24 | 392 |
| [C-e5large-section700meta-k3m02](C-e5large-section700meta-k3m02.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, Δ≤0.02 | 0.818 | 0.956 | 0.770 | 0.956 | 1.56 | 479 |
| [C-e5large-section700meta-k3s085](C-e5large-section700meta-k3s085.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.85 | 0.857 | 0.941 | 0.819 | 0.941 | 1.35 | 420 |
| [C-e5large-section700meta-k3s087](C-e5large-section700meta-k3s087.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.87 | 0.911 | 0.926 | 0.912 | 0.941 | 1.12 | 361 |
| [C-e5large-section700meta-k3s089](C-e5large-section700meta-k3s089.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.89 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 327 |
| [C-e5large-section700meta-k5](C-e5large-section700meta-k5.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=5 | 0.347 | 1.000 | 0.212 | 0.963 | 5.00 | 1404 |
| [D-e5large-section700meta-rrk1](D-e5large-section700meta-rrk1.jsonl.eval.json) | multilingual-e5-large + bge-reranker-v2-m3 (top 10) | section ≤700 | sí | k=1 | 0.980 | 0.971 | 1.000 | 1.000 | 1.00 | 329 |
| [D-e5large-section700meta-rrk2](D-e5large-section700meta-rrk2.jsonl.eval.json) | multilingual-e5-large + bge-reranker-v2-m3 (top 10) | section ≤700 | sí | k=2 | 0.686 | 1.000 | 0.529 | 1.000 | 2.00 | 639 |
| [D5-e5large-section700meta-rrk1](D5-e5large-section700meta-rrk1.jsonl.eval.json) | multilingual-e5-large + bge-reranker-v2-m3 (top 5) | section ≤700 | sí | k=1 | 0.980 | 0.971 | 1.000 | 1.000 | 1.00 | 329 |
