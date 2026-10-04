# Resultados de la Parte 1

Preguntas: `datos/preguntas_recuperacion_dev.jsonl`. Generado por `scripts/run_experiments.py` a partir de los `.eval.json` del evaluador oficial. No editar a mano.

| Run | Encoder | Chunking | Metadatos | Corte | CR | Recall | Precision | MRR | k medio | Caracteres |
|---|---|---|---|---|---|---|---|---|---|---|
| [A-beto-section700meta-k1](A-beto-section700meta-k1.jsonl.eval.json) | bert-base-spanish-wwm-cased (promedio de tokens) | section ≤700 | sí | k=1 | 0.450 | 0.450 | 0.450 | 0.450 | 1.00 | 320 |
| [A-beto-section700meta-k3](A-beto-section700meta-k3.jsonl.eval.json) | bert-base-spanish-wwm-cased (promedio de tokens) | section ≤700 | sí | k=3 | 0.325 | 0.650 | 0.217 | 0.542 | 3.00 | 949 |
| [A-bgem3-section700meta-k1](A-bgem3-section700meta-k1.jsonl.eval.json) | bge-m3 | section ≤700 | sí | k=1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [A-bgem3-section700meta-k3](A-bgem3-section700meta-k3.jsonl.eval.json) | bge-m3 | section ≤700 | sí | k=3 | 0.500 | 1.000 | 0.333 | 1.000 | 3.00 | 894 |
| [A-e5base-section700meta-k1](A-e5base-section700meta-k1.jsonl.eval.json) | multilingual-e5-base | section ≤700 | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 341 |
| [A-e5base-section700meta-k3](A-e5base-section700meta-k3.jsonl.eval.json) | multilingual-e5-base | section ≤700 | sí | k=3 | 0.500 | 1.000 | 0.333 | 0.975 | 3.00 | 930 |
| [A-e5large-section700meta-k1](A-e5large-section700meta-k1.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [A-e5large-section700meta-k3](A-e5large-section700meta-k3.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=3 | 0.500 | 1.000 | 0.333 | 1.000 | 3.00 | 916 |
| [A-e5small-section700meta-k1](A-e5small-section700meta-k1.jsonl.eval.json) | multilingual-e5-small | section ≤700 | sí | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 352 |
| [A-e5small-section700meta-k3](A-e5small-section700meta-k3.jsonl.eval.json) | multilingual-e5-small | section ≤700 | sí | k=3 | 0.500 | 1.000 | 0.333 | 0.942 | 3.00 | 910 |
| [A-lexical-section700meta-k1](A-lexical-section700meta-k1.jsonl.eval.json) | léxico (bolsa de palabras) | section ≤700 | sí | k=1 | 0.550 | 0.550 | 0.550 | 0.550 | 1.00 | 290 |
| [A-lexical-section700meta-k3](A-lexical-section700meta-k3.jsonl.eval.json) | léxico (bolsa de palabras) | section ≤700 | sí | k=3 | 0.400 | 0.800 | 0.267 | 0.650 | 3.00 | 805 |
| [A-mbert-section700meta-k1](A-mbert-section700meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | sí | k=1 | 0.300 | 0.300 | 0.300 | 0.300 | 1.00 | 283 |
| [A-mbert-section700meta-k3](A-mbert-section700meta-k3.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | sí | k=3 | 0.225 | 0.450 | 0.150 | 0.358 | 3.00 | 899 |
| [A-minilm-section700meta-k1](A-minilm-section700meta-k1.jsonl.eval.json) | paraphrase-multilingual-MiniLM-L12-v2 | section ≤700 | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 341 |
| [A-minilm-section700meta-k3](A-minilm-section700meta-k3.jsonl.eval.json) | paraphrase-multilingual-MiniLM-L12-v2 | section ≤700 | sí | k=3 | 0.500 | 1.000 | 0.333 | 0.975 | 3.00 | 903 |
| [A0-lexical-paragraph-k3](A0-lexical-paragraph-k3.jsonl.eval.json) | léxico (bolsa de palabras) | paragraph | no | k=3 | 0.350 | 0.700 | 0.233 | 0.642 | 3.00 | 535 |
| [B-bgem3-fixed200meta-k1](B-bgem3-fixed200meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤200, solap. 0 | sí | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 210 |
| [B-bgem3-fixed200o1meta-k1](B-bgem3-fixed200o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤200, solap. 1 | sí | k=1 | 0.800 | 0.800 | 0.800 | 0.800 | 1.00 | 222 |
| [B-bgem3-fixed400meta-k1](B-bgem3-fixed400meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤400, solap. 0 | sí | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 387 |
| [B-bgem3-fixed400o1meta-k1](B-bgem3-fixed400o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤400, solap. 1 | sí | k=1 | 0.750 | 0.750 | 0.750 | 0.750 | 1.00 | 387 |
| [B-bgem3-fixed800meta-k1](B-bgem3-fixed800meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤800, solap. 0 | sí | k=1 | 0.850 | 0.850 | 0.850 | 0.850 | 1.00 | 610 |
| [B-bgem3-fixed800o1meta-k1](B-bgem3-fixed800o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤800, solap. 1 | sí | k=1 | 0.850 | 0.850 | 0.850 | 0.850 | 1.00 | 622 |
| [B-bgem3-paragraphmeta-k1](B-bgem3-paragraphmeta-k1.jsonl.eval.json) | bge-m3 | paragraph | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 270 |
| [B-bgem3-section400meta-k1](B-bgem3-section400meta-k1.jsonl.eval.json) | bge-m3 | section ≤400 | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 303 |
| [B-bgem3-section700-k1](B-bgem3-section700-k1.jsonl.eval.json) | bge-m3 | section ≤700 | no | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 289 |
| [B-bgem3-sentencemeta-k1](B-bgem3-sentencemeta-k1.jsonl.eval.json) | bge-m3 | sentence | sí | k=1 | 0.800 | 0.800 | 0.800 | 0.800 | 1.00 | 155 |
| [B-e5large-fixed200meta-k1](B-e5large-fixed200meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤200, solap. 0 | sí | k=1 | 0.850 | 0.850 | 0.850 | 0.850 | 1.00 | 203 |
| [B-e5large-fixed200o1meta-k1](B-e5large-fixed200o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤200, solap. 1 | sí | k=1 | 0.800 | 0.800 | 0.800 | 0.800 | 1.00 | 222 |
| [B-e5large-fixed400meta-k1](B-e5large-fixed400meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤400, solap. 0 | sí | k=1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 390 |
| [B-e5large-fixed400o1meta-k1](B-e5large-fixed400o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤400, solap. 1 | sí | k=1 | 0.750 | 0.750 | 0.750 | 0.750 | 1.00 | 382 |
| [B-e5large-fixed800meta-k1](B-e5large-fixed800meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤800, solap. 0 | sí | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 619 |
| [B-e5large-fixed800o1meta-k1](B-e5large-fixed800o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤800, solap. 1 | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 630 |
| [B-e5large-paragraphmeta-k1](B-e5large-paragraphmeta-k1.jsonl.eval.json) | multilingual-e5-large | paragraph | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 270 |
| [B-e5large-section400meta-k1](B-e5large-section400meta-k1.jsonl.eval.json) | multilingual-e5-large | section ≤400 | sí | k=1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 303 |
| [B-e5large-section700-k1](B-e5large-section700-k1.jsonl.eval.json) | multilingual-e5-large | section ≤700 | no | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 289 |
| [B-e5large-sentencemeta-k1](B-e5large-sentencemeta-k1.jsonl.eval.json) | multilingual-e5-large | sentence | sí | k=1 | 0.750 | 0.750 | 0.750 | 0.750 | 1.00 | 149 |
| [B-mbert-fixed200meta-k1](B-mbert-fixed200meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤200, solap. 0 | sí | k=1 | 0.300 | 0.300 | 0.300 | 0.300 | 1.00 | 230 |
| [B-mbert-fixed200o1meta-k1](B-mbert-fixed200o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤200, solap. 1 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 225 |
| [B-mbert-fixed400meta-k1](B-mbert-fixed400meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤400, solap. 0 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 361 |
| [B-mbert-fixed400o1meta-k1](B-mbert-fixed400o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤400, solap. 1 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 363 |
| [B-mbert-fixed800meta-k1](B-mbert-fixed800meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤800, solap. 0 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 568 |
| [B-mbert-fixed800o1meta-k1](B-mbert-fixed800o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤800, solap. 1 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 609 |
| [B-mbert-paragraphmeta-k1](B-mbert-paragraphmeta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | paragraph | sí | k=1 | 0.300 | 0.300 | 0.300 | 0.300 | 1.00 | 250 |
| [B-mbert-section400meta-k1](B-mbert-section400meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤400 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 274 |
| [B-mbert-section700-k1](B-mbert-section700-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | no | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 235 |
| [B-mbert-sentencemeta-k1](B-mbert-sentencemeta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | sentence | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 164 |
| [C-e5large-section700meta-k2](C-e5large-section700meta-k2.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=2 | 0.667 | 1.000 | 0.500 | 1.000 | 2.00 | 624 |
| [C-e5large-section700meta-k2m005](C-e5large-section700meta-k2m005.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.005 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [C-e5large-section700meta-k2m01](C-e5large-section700meta-k2m01.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.01 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [C-e5large-section700meta-k2m02](C-e5large-section700meta-k2m02.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.02 | 0.933 | 1.000 | 0.900 | 1.000 | 1.20 | 401 |
| [C-e5large-section700meta-k2m03](C-e5large-section700meta-k2m03.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.03 | 0.867 | 1.000 | 0.800 | 1.000 | 1.40 | 459 |
| [C-e5large-section700meta-k3m01](C-e5large-section700meta-k3m01.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, Δ≤0.01 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [C-e5large-section700meta-k3m02](C-e5large-section700meta-k3m02.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, Δ≤0.02 | 0.917 | 1.000 | 0.883 | 1.000 | 1.30 | 428 |
| [C-e5large-section700meta-k3s085](C-e5large-section700meta-k3s085.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.85 | 0.825 | 1.000 | 0.758 | 1.000 | 1.65 | 519 |
| [C-e5large-section700meta-k3s087](C-e5large-section700meta-k3s087.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.87 | 0.975 | 1.000 | 0.967 | 1.000 | 1.10 | 387 |
| [C-e5large-section700meta-k3s089](C-e5large-section700meta-k3s089.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.89 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [C-e5large-section700meta-k5](C-e5large-section700meta-k5.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=5 | 0.333 | 1.000 | 0.200 | 1.000 | 5.00 | 1437 |
