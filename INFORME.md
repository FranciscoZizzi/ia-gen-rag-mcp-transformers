# Informe — Misión RAG, MCP y Transformers

Hospital Provincial Arroyo Claro (ficticio). Entrega: viernes 9 de octubre de 2026.

## Parte 1: RAG vectorial

### Resumen

La configuración entregada (`config/retriever.json`) corta cada documento por secciones (`##`, hasta 700 caracteres) y les antepone el título del documento y de la sección. Los fragmentos se embeben con **`intfloat/multilingual-e5-large`**, los 5 mejores se reordenan con el cross-encoder **`BAAI/bge-reranker-v2-m3`** y se devuelve **un fragmento** por pregunta.

| Configuración | CR dev | CR set propio |
|---|---|---|
| Línea de base: BERT multilingüe, promedio de tokens, mismo chunking, k = 1 | 0,30 | 0,15 |
| e5-large, mismo chunking, k = 1 | 1,00 | 0,92 |
| **Entregada: e5-large + reranker sobre los 5 mejores, k = 1** | **1,00** | **0,98** |

Contra la línea de base, el encoder elegido mejora la CR en +0,70 en dev (IC 95 % por bootstrap pareado: +0,50 a +0,90) y en +0,78 en el set propio (+0,63 a +0,90). Mejora 14 de 20 y 27 de 34 preguntas, y no empeora ninguna. La Parte 1 no usa LLM: su costo en OpenRouter es cero.

Para reproducirla:

```bash
python3 recuperar.py --preguntas datos/preguntas_recuperacion_dev.jsonl --salida resultados.jsonl
python3 evaluar/evaluar.py recuperacion --preguntas datos/preguntas_recuperacion_dev.jsonl --resultados resultados.jsonl
```

Cada fila de las tablas tiene su `.eval.json` en `experimentos/`, y su `<run>.config.json` se le puede pasar a `recuperar.py --config` para repetir esa corrida exacta.

### Qué premia la métrica

El evaluador busca cada evidencia como texto literal (normalizado) dentro de los fragmentos. La precisión cuenta fragmentos, no caracteres. Con una sola evidencia por pregunta, devolver k fragmentos con uno solo correcto da como máximo 2/(k+1): 1,00 con k = 1, 0,67 con k = 2 y 0,50 con k = 3. Por eso lo que decide el puntaje es que el **primer** fragmento sea el correcto (hit@1).

De ahí salen dos reglas de diseño:

- **Ningún fragmento corta una oración.** Si un corte partiera la frase de evidencia, la pregunta valdría 0 aunque la recuperación hubiera sido correcta. Los tests lo verifican para las diez configuraciones de chunking con la normalización del propio evaluador.
- **Un segundo fragmento sólo conviene si p₂ > p₁/2**, donde p₁ y p₂ son las probabilidades de que la evidencia esté en el primero y en el segundo. La etapa C lo pone a prueba.

### Cómo comparamos

Usamos dos conjuntos de preguntas:

- **dev**: las 20 preguntas de la cátedra. Cada pregunta vale 0,05 de CR, así que una diferencia menor es un empate.
- **set propio** (`eval_extra/`): 34 preguntas coloquiales con 36 frases de evidencia, cada una textual y única en el corpus. Cubren los tres documentos que dev no toca (internación, salud mental y teleconsulta) e incluyen dos preguntas con dos evidencias. Lo redactamos con asistencia de IA y lo usamos para confirmar finalistas, no para tunear: no hay ningún ajuste por pregunta.

La búsqueda fue por etapas, una variable por vez: encoder (A), chunking (B), corte (C) y reranking (D). Hubo 61 corridas sobre dev y 60 sobre el set propio, todas medidas con `evaluar/evaluar.py` sin modificar. El control léxico (bolsa de palabras, párrafos, k = 3) reproduce el 0,35 de la consigna (fila `A0`), lo que valida el pipeline de punta a punta.

### Etapa A: el encoder

Chunking fijo (sección hasta 700 caracteres, con metadatos). Con k = 1 la CR es el hit@1; con k = 3, el recall es el hit@3.

| Encoder | Tipo | Parámetros | CR k = 1, dev | Recall k = 3, dev | CR k = 1, set propio | Recall k = 3, set propio |
|---|---|---|---|---|---|---|
| `google-bert/bert-base-multilingual-cased` | Línea de base, promedio de tokens | 178 M | 0,30 | 0,45 | 0,15 | 0,31 |
| `dccuchile/bert-base-spanish-wwm-cased` | Promedio de tokens | 110 M | 0,45 | 0,65 | 0,31 | 0,51 |
| Bolsa de palabras (control) | Léxico | — | 0,55 | 0,80 | 0,42 | 0,56 |
| `paraphrase-multilingual-MiniLM-L12-v2` | Embeddings de oraciones | 118 M | 0,95 | 1,00 | 0,58 | 0,88 |
| `multilingual-e5-small` | Embeddings de oraciones | 118 M | 0,90 | 1,00 | 0,83 | 0,97 |
| `multilingual-e5-base` | Embeddings de oraciones | 278 M | 0,95 | 1,00 | 0,86 | 1,00 |
| `multilingual-e5-large` | Embeddings de oraciones | 560 M | **1,00** | 1,00 | **0,92** | 0,97 |
| `BAAI/bge-m3` | Embeddings de oraciones | 568 M | **1,00** | 1,00 | 0,89 | 1,00 |

Dev se satura: dos encoders aciertan las 20 preguntas. El set propio separa a los finalistas y además desarma un falso positivo: MiniLM empata con e5-base en dev (0,95) y cae a 0,58 en el set propio.

### Por qué ganó e5-large

El diagnóstico (`scripts/analyze_scores.py diagnose`, tablas completas en `experimentos/analisis/`) mira el ranking entero, no sólo el fragmento devuelto. Para cada pregunta mide cuánto queda el chunk con la evidencia por encima del mejor chunk sin ella, en unidades del desvío de los puntajes de esa pregunta, y promedia sobre las preguntas.

| Encoder | hit@1 dev | Separación dev (desvíos) | hit@1 set propio | Separación set propio (desvíos) | Coseno medio ± desvío | Consulta (ms) |
|---|---|---|---|---|---|---|
| BERT multilingüe | 0,30 | −0,35 | 0,15 | −0,89 | 0,60 ± 0,06 | 37 |
| BETO | 0,45 | −0,18 | 0,32 | −0,44 | 0,86 ± 0,02 | 30 |
| Bolsa de palabras | 0,55 | +0,51 | 0,44 | −0,51 | 0,10 ± 0,06 | 0 |
| MiniLM | 0,95 | +0,87 | 0,59 | +0,34 | 0,25 ± 0,14 | 12 |
| e5-small | 0,90 | +1,70 | 0,85 | +1,27 | 0,81 ± 0,02 | 12 |
| e5-base | 0,95 | +1,74 | 0,88 | +1,04 | 0,79 ± 0,03 | 58 |
| **e5-large** | **1,00** | **+1,80** | **0,94** | **+1,40** | 0,79 ± 0,03 | 140 |
| BGE-M3 | 1,00 | +1,71 | 0,91 | +1,35 | 0,41 ± 0,08 | 113 |

- **BERT sin ajustar no sabe comparar oraciones.** Lo preentrenaron para predecir palabras enmascaradas, no para que dos textos con el mismo sentido queden cerca. Al promediar sus tokens, todos los fragmentos se parecen: con BETO, el coseno medio es 0,86 con un desvío de 0,02. Lo decisivo es que la separación es **negativa**: el chunk con la evidencia queda, en promedio, por debajo del mejor distractor. Por eso pierde incluso contra una bolsa de palabras. Cambiar el chunking no lo rescata: en las diez estrategias de la etapa B, BERT queda entre 0,25 y 0,30 en dev y entre 0,12 y 0,26 en el set propio.
- **El nivel del coseno no es lo que importa.** Los E5 también tienen cosenos comprimidos (0,79 ± 0,03), pero el chunk correcto queda casi dos desvíos por encima del resto. Estos modelos se entrenaron con aprendizaje contrastivo sobre pares de textos relacionados, y usan prefijos distintos para la consulta y el pasaje. Por la misma razón, un umbral absoluto de coseno no se puede trasladar de un encoder a otro.
- **MiniLM se entrenó para paráfrasis, no para pregunta → pasaje,** y trunca la entrada a 128 tokens. Tiene la menor separación de los modelos de embeddings (+0,87 en dev, +0,34 en el set propio): acierta cuando la pregunta comparte palabras con la respuesta y falla con las preguntas indirectas.
- **e5-large contra BGE-M3**: los dos aciertan todo dev. e5-large gana en el set propio (0,92 contra 0,89 de CR) y tiene la mayor separación en ambos conjuntos; los dos tienen el mismo tamaño. BGE-M3 es algo más rápido por consulta (113 contra 140 ms), una diferencia irrelevante para este uso.

Las preguntas que la línea de base pierde muestran los distractores del corpus. En R01 ("mi papá está en terapia intensiva…"), BERT devuelve *Pediatría — Fiebre* y e5-large *Régimen de visitas — Unidad de terapia intensiva de adultos*. En R02 (endoscopía), BERT elige otra sección del mismo documento (*Ecografía ginecológica*). En R03 ("¿tengo que ir en ayunas?"), BERT trae *Donación de sangre*, que menciona el ayuno. En R20 (curva de glucosa), elige la sección vecina *Ayuno* del laboratorio. La comparación pregunta por pregunta está en `experimentos/analisis/baseline-vs-e5large-*.md`.

### Etapa B: el chunking

| Chunking (e5-large) | Chunks | CR dev | CR set propio |
|---|---|---|---|
| **section ≤700 + metadatos** | 56 | **1,00** | **0,92** |
| section ≤400 + metadatos | 61 | 1,00 | 0,92 |
| fixed 400 + metadatos | 42 | 1,00 | 0,92 |
| fixed 200 + metadatos | 87 | 0,85 | 0,92 |
| paragraph + metadatos | 68 | 0,95 | 0,89 |
| sentence + metadatos | 137 | 0,75 | 0,89 |
| fixed 400 con solapamiento de 1 oración | 48 | 0,75 | 0,86 |
| section ≤700 **sin** metadatos | 56 | 0,90 | 0,84 |

- **Los metadatos suman entre 0,05 y 0,10** en los dos conjuntos, para e5-large y para BGE-M3. En el corpus hay dos secciones llamadas "Ayuno" (cirugía y laboratorio, preguntas R08 y R09): sólo el título del documento las distingue.
- **Cortar por sección queda primero o empatado** en todo. Entre ≤700 y ≤400 hay un empate exacto. Elegimos ≤700 porque con ese límite ninguna sección se parte, y porque en la Parte 2 el agente recibe la sección completa (por ejemplo, todas las reglas de visita de un sector) a cambio de unos 50 caracteres más por fragmento (349 contra 303 en promedio).
- **El solapamiento empeora.** Las ventanas casi iguales compiten entre sí por el primer puesto.

### Etapa C: el corte

Sobre e5-large con secciones y metadatos:

| Corte | CR dev | CR set propio |
|---|---|---|
| **k = 1** | **1,00** | **0,92** |
| k = 2 | 0,67 | 0,67 |
| k = 3 | 0,50 | 0,50 |
| k = 5 | 0,33 | 0,35 |
| k ≤ 2, margen ≤ 0,01 respecto del mejor | 1,00 | 0,92 |
| k ≤ 2, margen ≤ 0,03 | 0,87 | 0,79 |
| k ≤ 3, coseno ≥ 0,85 | 0,83 | 0,86 |
| k ≤ 3, coseno ≥ 0,89 | 1,00 | 0,92 |

Ningún corte le gana a k = 1. En los casi-empates de e5-large (margen menor a 0,006) con una sola evidencia, el primero acierta tres veces y el segundo una: p₂ ≈ 0,25 queda por debajo de p₁/2 ≈ 0,38. Devolver dos fragmentos en esos casos gana en una pregunta lo que pierde en tres. El margen de 0,01 sólo empata, y ante un empate nos quedamos con la regla más simple.

### Etapa D: reranking con un cross-encoder

Un cross-encoder lee la pregunta y el pasaje juntos, con atención entre las dos, así que distingue matices que dos vectores calculados por separado no capturan. Es demasiado lento para puntuar todo el corpus (unos 0,6 s por par en CPU), por eso sólo reordena los mejores candidatos de e5-large.

| Reranking (e5-large, k = 1) | CR dev | CR set propio | Tiempo por pregunta |
|---|---|---|---|
| Sin reranker | 1,00 | 0,92 | 0,15 s |
| bge-reranker-v2-m3 sobre los 10 mejores | 1,00 | 0,98 | ~6 s |
| **bge-reranker-v2-m3 sobre los 5 mejores** | **1,00** | **0,98** | ~3 s |

Con el reranker, el primer fragmento contiene la evidencia en las 34 preguntas del set propio. El 0,98 se explica por las dos preguntas con dos evidencias: con un solo fragmento llegan como máximo a 0,67. La mejora (+0,06, dos preguntas) supera el umbral de ruido. La cantidad de candidatos y k se fijaron antes de mirar el resultado. Con 5 candidatos se obtiene lo mismo que con 10, porque e5-large siempre deja la evidencia entre sus 5 primeros, y el reranking cuesta la mitad.

### Costo de ejecución

En CPU (8 núcleos), la corrida del contrato sobre las 20 preguntas dev tarda 114 s y usa 4,3 GB de RAM. Se reparte así: cargar e5-large, 14 s; cargar el reranker, 4 s; embeber los 56 fragmentos, 24 s; y el resto, unos 3,5 s por pregunta. La primera corrida además descarga unos 4,5 GB de modelos, con las revisiones fijadas en la configuración. Si la máquina no alcanza, `experimentos/A-e5large-section700meta-k1.config.json` es la misma configuración sin reranker: unas 2,5 veces más rápida, con 1,00 en dev y 0,92 en el set propio.

### Sobreajuste y limitaciones

- Ninguna decisión se tomó sólo con dev, que está saturado. Cada finalista se confirmó en el set propio, y en los empates elegimos la opción más simple: k = 1 frente al margen, y secciones enteras frente a ventanas.
- El set propio lo escribimos nosotros, con asistencia de IA, y puede ser más fácil o más difícil que el conjunto de test de la cátedra. Su valor está en que ordenó a los encoders igual que la separación medida, y en que expuso a MiniLM.
- Con k = 1, una pregunta con dos evidencias en secciones distintas llega como máximo a 0,67. Dev no tiene preguntas así; en el set propio hay dos, y la etapa C muestra que devolver dos fragmentos a todas las preguntas cuesta mucho más de lo que esas dos recuperan.

## Parte 2: un agente con dos fuentes

Pendiente.

## Parte 3: las mismas herramientas como servidor MCP

Pendiente.

## Parte 4: una capa de atención en NumPy

Pendiente.

## Parte 5: un bloque de transformer a mano

Pendiente.

## Costo total en OpenRouter

Parte 1: USD 0 (no usa LLM). El resto queda pendiente.

## Apéndice: tablas completas de la Parte 1

Generadas por `scripts/run_experiments.py` a partir de los `.eval.json` del evaluador oficial: una fila por configuración probada. Los nombres de las corridas son `<etapa>-<encoder>-<chunking>-<corte>`; el sufijo `meta` indica metadatos y `rrk1` el reranking con k = 1.

### dev (`datos/preguntas_recuperacion_dev.jsonl`)

| Run | Encoder | Chunking | Metadatos | Corte | CR | Recall | Precision | MRR | k medio | Caracteres |
|---|---|---|---|---|---|---|---|---|---|---|
| [A-beto-section700meta-k1](experimentos/A-beto-section700meta-k1.jsonl.eval.json) | bert-base-spanish-wwm-cased (promedio de tokens) | section ≤700 | sí | k=1 | 0.450 | 0.450 | 0.450 | 0.450 | 1.00 | 320 |
| [A-beto-section700meta-k3](experimentos/A-beto-section700meta-k3.jsonl.eval.json) | bert-base-spanish-wwm-cased (promedio de tokens) | section ≤700 | sí | k=3 | 0.325 | 0.650 | 0.217 | 0.542 | 3.00 | 949 |
| [A-bgem3-section700meta-k1](experimentos/A-bgem3-section700meta-k1.jsonl.eval.json) | bge-m3 | section ≤700 | sí | k=1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [A-bgem3-section700meta-k3](experimentos/A-bgem3-section700meta-k3.jsonl.eval.json) | bge-m3 | section ≤700 | sí | k=3 | 0.500 | 1.000 | 0.333 | 1.000 | 3.00 | 894 |
| [A-e5base-section700meta-k1](experimentos/A-e5base-section700meta-k1.jsonl.eval.json) | multilingual-e5-base | section ≤700 | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 341 |
| [A-e5base-section700meta-k3](experimentos/A-e5base-section700meta-k3.jsonl.eval.json) | multilingual-e5-base | section ≤700 | sí | k=3 | 0.500 | 1.000 | 0.333 | 0.975 | 3.00 | 930 |
| [A-e5large-section700meta-k1](experimentos/A-e5large-section700meta-k1.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [A-e5large-section700meta-k3](experimentos/A-e5large-section700meta-k3.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=3 | 0.500 | 1.000 | 0.333 | 1.000 | 3.00 | 916 |
| [A-e5small-section700meta-k1](experimentos/A-e5small-section700meta-k1.jsonl.eval.json) | multilingual-e5-small | section ≤700 | sí | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 352 |
| [A-e5small-section700meta-k3](experimentos/A-e5small-section700meta-k3.jsonl.eval.json) | multilingual-e5-small | section ≤700 | sí | k=3 | 0.500 | 1.000 | 0.333 | 0.942 | 3.00 | 910 |
| [A-lexical-section700meta-k1](experimentos/A-lexical-section700meta-k1.jsonl.eval.json) | léxico (bolsa de palabras) | section ≤700 | sí | k=1 | 0.550 | 0.550 | 0.550 | 0.550 | 1.00 | 290 |
| [A-lexical-section700meta-k3](experimentos/A-lexical-section700meta-k3.jsonl.eval.json) | léxico (bolsa de palabras) | section ≤700 | sí | k=3 | 0.400 | 0.800 | 0.267 | 0.650 | 3.00 | 805 |
| [A-mbert-section700meta-k1](experimentos/A-mbert-section700meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | sí | k=1 | 0.300 | 0.300 | 0.300 | 0.300 | 1.00 | 283 |
| [A-mbert-section700meta-k3](experimentos/A-mbert-section700meta-k3.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | sí | k=3 | 0.225 | 0.450 | 0.150 | 0.358 | 3.00 | 899 |
| [A-minilm-section700meta-k1](experimentos/A-minilm-section700meta-k1.jsonl.eval.json) | paraphrase-multilingual-MiniLM-L12-v2 | section ≤700 | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 341 |
| [A-minilm-section700meta-k3](experimentos/A-minilm-section700meta-k3.jsonl.eval.json) | paraphrase-multilingual-MiniLM-L12-v2 | section ≤700 | sí | k=3 | 0.500 | 1.000 | 0.333 | 0.975 | 3.00 | 903 |
| [A0-lexical-paragraph-k3](experimentos/A0-lexical-paragraph-k3.jsonl.eval.json) | léxico (bolsa de palabras) | paragraph | no | k=3 | 0.350 | 0.700 | 0.233 | 0.642 | 3.00 | 535 |
| [B-bgem3-fixed200meta-k1](experimentos/B-bgem3-fixed200meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤200, solap. 0 | sí | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 210 |
| [B-bgem3-fixed200o1meta-k1](experimentos/B-bgem3-fixed200o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤200, solap. 1 | sí | k=1 | 0.800 | 0.800 | 0.800 | 0.800 | 1.00 | 222 |
| [B-bgem3-fixed400meta-k1](experimentos/B-bgem3-fixed400meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤400, solap. 0 | sí | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 387 |
| [B-bgem3-fixed400o1meta-k1](experimentos/B-bgem3-fixed400o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤400, solap. 1 | sí | k=1 | 0.750 | 0.750 | 0.750 | 0.750 | 1.00 | 387 |
| [B-bgem3-fixed800meta-k1](experimentos/B-bgem3-fixed800meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤800, solap. 0 | sí | k=1 | 0.850 | 0.850 | 0.850 | 0.850 | 1.00 | 610 |
| [B-bgem3-fixed800o1meta-k1](experimentos/B-bgem3-fixed800o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤800, solap. 1 | sí | k=1 | 0.850 | 0.850 | 0.850 | 0.850 | 1.00 | 622 |
| [B-bgem3-paragraphmeta-k1](experimentos/B-bgem3-paragraphmeta-k1.jsonl.eval.json) | bge-m3 | paragraph | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 270 |
| [B-bgem3-section400meta-k1](experimentos/B-bgem3-section400meta-k1.jsonl.eval.json) | bge-m3 | section ≤400 | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 303 |
| [B-bgem3-section700-k1](experimentos/B-bgem3-section700-k1.jsonl.eval.json) | bge-m3 | section ≤700 | no | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 289 |
| [B-bgem3-sentencemeta-k1](experimentos/B-bgem3-sentencemeta-k1.jsonl.eval.json) | bge-m3 | sentence | sí | k=1 | 0.800 | 0.800 | 0.800 | 0.800 | 1.00 | 155 |
| [B-e5large-fixed200meta-k1](experimentos/B-e5large-fixed200meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤200, solap. 0 | sí | k=1 | 0.850 | 0.850 | 0.850 | 0.850 | 1.00 | 203 |
| [B-e5large-fixed200o1meta-k1](experimentos/B-e5large-fixed200o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤200, solap. 1 | sí | k=1 | 0.800 | 0.800 | 0.800 | 0.800 | 1.00 | 222 |
| [B-e5large-fixed400meta-k1](experimentos/B-e5large-fixed400meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤400, solap. 0 | sí | k=1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 390 |
| [B-e5large-fixed400o1meta-k1](experimentos/B-e5large-fixed400o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤400, solap. 1 | sí | k=1 | 0.750 | 0.750 | 0.750 | 0.750 | 1.00 | 382 |
| [B-e5large-fixed800meta-k1](experimentos/B-e5large-fixed800meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤800, solap. 0 | sí | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 619 |
| [B-e5large-fixed800o1meta-k1](experimentos/B-e5large-fixed800o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤800, solap. 1 | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 630 |
| [B-e5large-paragraphmeta-k1](experimentos/B-e5large-paragraphmeta-k1.jsonl.eval.json) | multilingual-e5-large | paragraph | sí | k=1 | 0.950 | 0.950 | 0.950 | 0.950 | 1.00 | 270 |
| [B-e5large-section400meta-k1](experimentos/B-e5large-section400meta-k1.jsonl.eval.json) | multilingual-e5-large | section ≤400 | sí | k=1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 303 |
| [B-e5large-section700-k1](experimentos/B-e5large-section700-k1.jsonl.eval.json) | multilingual-e5-large | section ≤700 | no | k=1 | 0.900 | 0.900 | 0.900 | 0.900 | 1.00 | 289 |
| [B-e5large-sentencemeta-k1](experimentos/B-e5large-sentencemeta-k1.jsonl.eval.json) | multilingual-e5-large | sentence | sí | k=1 | 0.750 | 0.750 | 0.750 | 0.750 | 1.00 | 149 |
| [B-mbert-fixed200meta-k1](experimentos/B-mbert-fixed200meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤200, solap. 0 | sí | k=1 | 0.300 | 0.300 | 0.300 | 0.300 | 1.00 | 230 |
| [B-mbert-fixed200o1meta-k1](experimentos/B-mbert-fixed200o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤200, solap. 1 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 225 |
| [B-mbert-fixed400meta-k1](experimentos/B-mbert-fixed400meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤400, solap. 0 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 361 |
| [B-mbert-fixed400o1meta-k1](experimentos/B-mbert-fixed400o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤400, solap. 1 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 363 |
| [B-mbert-fixed800meta-k1](experimentos/B-mbert-fixed800meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤800, solap. 0 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 568 |
| [B-mbert-fixed800o1meta-k1](experimentos/B-mbert-fixed800o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤800, solap. 1 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 609 |
| [B-mbert-paragraphmeta-k1](experimentos/B-mbert-paragraphmeta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | paragraph | sí | k=1 | 0.300 | 0.300 | 0.300 | 0.300 | 1.00 | 250 |
| [B-mbert-section400meta-k1](experimentos/B-mbert-section400meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤400 | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 274 |
| [B-mbert-section700-k1](experimentos/B-mbert-section700-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | no | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 235 |
| [B-mbert-sentencemeta-k1](experimentos/B-mbert-sentencemeta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | sentence | sí | k=1 | 0.250 | 0.250 | 0.250 | 0.250 | 1.00 | 164 |
| [C-e5large-section700meta-k2](experimentos/C-e5large-section700meta-k2.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=2 | 0.667 | 1.000 | 0.500 | 1.000 | 2.00 | 624 |
| [C-e5large-section700meta-k2m005](experimentos/C-e5large-section700meta-k2m005.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.005 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [C-e5large-section700meta-k2m01](experimentos/C-e5large-section700meta-k2m01.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.01 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [C-e5large-section700meta-k2m02](experimentos/C-e5large-section700meta-k2m02.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.02 | 0.933 | 1.000 | 0.900 | 1.000 | 1.20 | 401 |
| [C-e5large-section700meta-k2m03](experimentos/C-e5large-section700meta-k2m03.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.03 | 0.867 | 1.000 | 0.800 | 1.000 | 1.40 | 459 |
| [C-e5large-section700meta-k3m01](experimentos/C-e5large-section700meta-k3m01.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, Δ≤0.01 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [C-e5large-section700meta-k3m02](experimentos/C-e5large-section700meta-k3m02.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, Δ≤0.02 | 0.917 | 1.000 | 0.883 | 1.000 | 1.30 | 428 |
| [C-e5large-section700meta-k3s085](experimentos/C-e5large-section700meta-k3s085.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.85 | 0.825 | 1.000 | 0.758 | 1.000 | 1.65 | 519 |
| [C-e5large-section700meta-k3s087](experimentos/C-e5large-section700meta-k3s087.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.87 | 0.975 | 1.000 | 0.967 | 1.000 | 1.10 | 387 |
| [C-e5large-section700meta-k3s089](experimentos/C-e5large-section700meta-k3s089.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.89 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [C-e5large-section700meta-k5](experimentos/C-e5large-section700meta-k5.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=5 | 0.333 | 1.000 | 0.200 | 1.000 | 5.00 | 1437 |
| [D-e5large-section700meta-rrk1](experimentos/D-e5large-section700meta-rrk1.jsonl.eval.json) | multilingual-e5-large + bge-reranker-v2-m3 (top 10) | section ≤700 | sí | k=1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |
| [D-e5large-section700meta-rrk2](experimentos/D-e5large-section700meta-rrk2.jsonl.eval.json) | multilingual-e5-large + bge-reranker-v2-m3 (top 10) | section ≤700 | sí | k=2 | 0.667 | 1.000 | 0.500 | 1.000 | 2.00 | 615 |
| [D5-e5large-section700meta-rrk1](experimentos/D5-e5large-section700meta-rrk1.jsonl.eval.json) | multilingual-e5-large + bge-reranker-v2-m3 (top 5) | section ≤700 | sí | k=1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 | 349 |

### Set propio (`eval_extra/preguntas_recuperacion_extra.jsonl`)

| Run | Encoder | Chunking | Metadatos | Corte | CR | Recall | Precision | MRR | k medio | Caracteres |
|---|---|---|---|---|---|---|---|---|---|---|
| [A-beto-section700meta-k1](experimentos/extra/A-beto-section700meta-k1.jsonl.eval.json) | bert-base-spanish-wwm-cased (promedio de tokens) | section ≤700 | sí | k=1 | 0.314 | 0.309 | 0.324 | 0.324 | 1.00 | 308 |
| [A-beto-section700meta-k3](experimentos/extra/A-beto-section700meta-k3.jsonl.eval.json) | bert-base-spanish-wwm-cased (promedio de tokens) | section ≤700 | sí | k=3 | 0.271 | 0.515 | 0.186 | 0.407 | 3.00 | 941 |
| [A-bgem3-section700meta-k1](experimentos/extra/A-bgem3-section700meta-k1.jsonl.eval.json) | bge-m3 | section ≤700 | sí | k=1 | 0.892 | 0.882 | 0.912 | 0.912 | 1.00 | 326 |
| [A-bgem3-section700meta-k3](experimentos/extra/A-bgem3-section700meta-k3.jsonl.eval.json) | bge-m3 | section ≤700 | sí | k=3 | 0.518 | 1.000 | 0.353 | 0.951 | 3.00 | 902 |
| [A-e5base-section700meta-k1](experimentos/extra/A-e5base-section700meta-k1.jsonl.eval.json) | multilingual-e5-base | section ≤700 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 299 |
| [A-e5base-section700meta-k3](experimentos/extra/A-e5base-section700meta-k3.jsonl.eval.json) | multilingual-e5-base | section ≤700 | sí | k=3 | 0.518 | 1.000 | 0.353 | 0.931 | 3.00 | 902 |
| [A-e5large-section700meta-k1](experimentos/extra/A-e5large-section700meta-k1.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=1 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 327 |
| [A-e5large-section700meta-k3](experimentos/extra/A-e5large-section700meta-k3.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=3 | 0.503 | 0.971 | 0.343 | 0.956 | 3.00 | 860 |
| [A-e5small-section700meta-k1](experimentos/extra/A-e5small-section700meta-k1.jsonl.eval.json) | multilingual-e5-small | section ≤700 | sí | k=1 | 0.833 | 0.824 | 0.853 | 0.853 | 1.00 | 352 |
| [A-e5small-section700meta-k3](experimentos/extra/A-e5small-section700meta-k3.jsonl.eval.json) | multilingual-e5-small | section ≤700 | sí | k=3 | 0.503 | 0.971 | 0.343 | 0.907 | 3.00 | 952 |
| [A-lexical-section700meta-k1](experimentos/extra/A-lexical-section700meta-k1.jsonl.eval.json) | léxico (bolsa de palabras) | section ≤700 | sí | k=1 | 0.422 | 0.412 | 0.441 | 0.441 | 1.00 | 254 |
| [A-lexical-section700meta-k3](experimentos/extra/A-lexical-section700meta-k3.jsonl.eval.json) | léxico (bolsa de palabras) | section ≤700 | sí | k=3 | 0.297 | 0.559 | 0.206 | 0.490 | 3.00 | 746 |
| [A-mbert-section700meta-k1](experimentos/extra/A-mbert-section700meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | sí | k=1 | 0.147 | 0.147 | 0.147 | 0.147 | 1.00 | 291 |
| [A-mbert-section700meta-k3](experimentos/extra/A-mbert-section700meta-k3.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | sí | k=3 | 0.159 | 0.309 | 0.108 | 0.221 | 3.00 | 896 |
| [A-minilm-section700meta-k1](experimentos/extra/A-minilm-section700meta-k1.jsonl.eval.json) | paraphrase-multilingual-MiniLM-L12-v2 | section ≤700 | sí | k=1 | 0.578 | 0.574 | 0.588 | 0.588 | 1.00 | 333 |
| [A-minilm-section700meta-k3](experimentos/extra/A-minilm-section700meta-k3.jsonl.eval.json) | paraphrase-multilingual-MiniLM-L12-v2 | section ≤700 | sí | k=3 | 0.459 | 0.882 | 0.314 | 0.721 | 3.00 | 879 |
| [B-bgem3-fixed200meta-k1](experimentos/extra/B-bgem3-fixed200meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤200, solap. 0 | sí | k=1 | 0.774 | 0.765 | 0.794 | 0.794 | 1.00 | 186 |
| [B-bgem3-fixed200o1meta-k1](experimentos/extra/B-bgem3-fixed200o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤200, solap. 1 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 194 |
| [B-bgem3-fixed400meta-k1](experimentos/extra/B-bgem3-fixed400meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤400, solap. 0 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 349 |
| [B-bgem3-fixed400o1meta-k1](experimentos/extra/B-bgem3-fixed400o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤400, solap. 1 | sí | k=1 | 0.804 | 0.794 | 0.824 | 0.824 | 1.00 | 352 |
| [B-bgem3-fixed800meta-k1](experimentos/extra/B-bgem3-fixed800meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤800, solap. 0 | sí | k=1 | 0.804 | 0.794 | 0.824 | 0.824 | 1.00 | 604 |
| [B-bgem3-fixed800o1meta-k1](experimentos/extra/B-bgem3-fixed800o1meta-k1.jsonl.eval.json) | bge-m3 | fixed ≤800, solap. 1 | sí | k=1 | 0.804 | 0.794 | 0.824 | 0.824 | 1.00 | 598 |
| [B-bgem3-paragraphmeta-k1](experimentos/extra/B-bgem3-paragraphmeta-k1.jsonl.eval.json) | bge-m3 | paragraph | sí | k=1 | 0.833 | 0.824 | 0.853 | 0.853 | 1.00 | 236 |
| [B-bgem3-section400meta-k1](experimentos/extra/B-bgem3-section400meta-k1.jsonl.eval.json) | bge-m3 | section ≤400 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 272 |
| [B-bgem3-section700-k1](experimentos/extra/B-bgem3-section700-k1.jsonl.eval.json) | bge-m3 | section ≤700 | no | k=1 | 0.843 | 0.838 | 0.853 | 0.853 | 1.00 | 257 |
| [B-bgem3-sentencemeta-k1](experimentos/extra/B-bgem3-sentencemeta-k1.jsonl.eval.json) | bge-m3 | sentence | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 145 |
| [B-e5large-fixed200meta-k1](experimentos/extra/B-e5large-fixed200meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤200, solap. 0 | sí | k=1 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 187 |
| [B-e5large-fixed200o1meta-k1](experimentos/extra/B-e5large-fixed200o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤200, solap. 1 | sí | k=1 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 194 |
| [B-e5large-fixed400meta-k1](experimentos/extra/B-e5large-fixed400meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤400, solap. 0 | sí | k=1 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 356 |
| [B-e5large-fixed400o1meta-k1](experimentos/extra/B-e5large-fixed400o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤400, solap. 1 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 356 |
| [B-e5large-fixed800meta-k1](experimentos/extra/B-e5large-fixed800meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤800, solap. 0 | sí | k=1 | 0.892 | 0.882 | 0.912 | 0.912 | 1.00 | 615 |
| [B-e5large-fixed800o1meta-k1](experimentos/extra/B-e5large-fixed800o1meta-k1.jsonl.eval.json) | multilingual-e5-large | fixed ≤800, solap. 1 | sí | k=1 | 0.863 | 0.853 | 0.882 | 0.882 | 1.00 | 605 |
| [B-e5large-paragraphmeta-k1](experimentos/extra/B-e5large-paragraphmeta-k1.jsonl.eval.json) | multilingual-e5-large | paragraph | sí | k=1 | 0.892 | 0.882 | 0.912 | 0.912 | 1.00 | 233 |
| [B-e5large-section400meta-k1](experimentos/extra/B-e5large-section400meta-k1.jsonl.eval.json) | multilingual-e5-large | section ≤400 | sí | k=1 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 268 |
| [B-e5large-section700-k1](experimentos/extra/B-e5large-section700-k1.jsonl.eval.json) | multilingual-e5-large | section ≤700 | no | k=1 | 0.843 | 0.838 | 0.853 | 0.853 | 1.00 | 261 |
| [B-e5large-sentencemeta-k1](experimentos/extra/B-e5large-sentencemeta-k1.jsonl.eval.json) | multilingual-e5-large | sentence | sí | k=1 | 0.892 | 0.882 | 0.912 | 0.912 | 1.00 | 144 |
| [B-mbert-fixed200meta-k1](experimentos/extra/B-mbert-fixed200meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤200, solap. 0 | sí | k=1 | 0.176 | 0.176 | 0.176 | 0.176 | 1.00 | 219 |
| [B-mbert-fixed200o1meta-k1](experimentos/extra/B-mbert-fixed200o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤200, solap. 1 | sí | k=1 | 0.147 | 0.147 | 0.147 | 0.147 | 1.00 | 211 |
| [B-mbert-fixed400meta-k1](experimentos/extra/B-mbert-fixed400meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤400, solap. 0 | sí | k=1 | 0.206 | 0.206 | 0.206 | 0.206 | 1.00 | 363 |
| [B-mbert-fixed400o1meta-k1](experimentos/extra/B-mbert-fixed400o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤400, solap. 1 | sí | k=1 | 0.176 | 0.176 | 0.176 | 0.176 | 1.00 | 376 |
| [B-mbert-fixed800meta-k1](experimentos/extra/B-mbert-fixed800meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤800, solap. 0 | sí | k=1 | 0.265 | 0.265 | 0.265 | 0.265 | 1.00 | 601 |
| [B-mbert-fixed800o1meta-k1](experimentos/extra/B-mbert-fixed800o1meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | fixed ≤800, solap. 1 | sí | k=1 | 0.265 | 0.265 | 0.265 | 0.265 | 1.00 | 601 |
| [B-mbert-paragraphmeta-k1](experimentos/extra/B-mbert-paragraphmeta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | paragraph | sí | k=1 | 0.206 | 0.206 | 0.206 | 0.206 | 1.00 | 242 |
| [B-mbert-section400meta-k1](experimentos/extra/B-mbert-section400meta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤400 | sí | k=1 | 0.206 | 0.206 | 0.206 | 0.206 | 1.00 | 273 |
| [B-mbert-section700-k1](experimentos/extra/B-mbert-section700-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | section ≤700 | no | k=1 | 0.255 | 0.250 | 0.265 | 0.265 | 1.00 | 224 |
| [B-mbert-sentencemeta-k1](experimentos/extra/B-mbert-sentencemeta-k1.jsonl.eval.json) | bert-base-multilingual-cased (promedio de tokens) | sentence | sí | k=1 | 0.118 | 0.118 | 0.118 | 0.118 | 1.00 | 138 |
| [C-e5large-section700meta-k2](experimentos/extra/C-e5large-section700meta-k2.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=2 | 0.667 | 0.971 | 0.515 | 0.956 | 2.00 | 593 |
| [C-e5large-section700meta-k2m005](experimentos/extra/C-e5large-section700meta-k2m005.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.005 | 0.902 | 0.926 | 0.897 | 0.941 | 1.12 | 362 |
| [C-e5large-section700meta-k2m01](experimentos/extra/C-e5large-section700meta-k2m01.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.01 | 0.922 | 0.956 | 0.912 | 0.956 | 1.15 | 368 |
| [C-e5large-section700meta-k2m02](experimentos/extra/C-e5large-section700meta-k2m02.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.02 | 0.853 | 0.956 | 0.809 | 0.956 | 1.35 | 423 |
| [C-e5large-section700meta-k2m03](experimentos/extra/C-e5large-section700meta-k2m03.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤2, Δ≤0.03 | 0.794 | 0.971 | 0.706 | 0.956 | 1.62 | 488 |
| [C-e5large-section700meta-k3m01](experimentos/extra/C-e5large-section700meta-k3m01.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, Δ≤0.01 | 0.906 | 0.956 | 0.892 | 0.956 | 1.24 | 392 |
| [C-e5large-section700meta-k3m02](experimentos/extra/C-e5large-section700meta-k3m02.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, Δ≤0.02 | 0.818 | 0.956 | 0.770 | 0.956 | 1.56 | 479 |
| [C-e5large-section700meta-k3s085](experimentos/extra/C-e5large-section700meta-k3s085.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.85 | 0.857 | 0.941 | 0.819 | 0.941 | 1.35 | 420 |
| [C-e5large-section700meta-k3s087](experimentos/extra/C-e5large-section700meta-k3s087.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.87 | 0.911 | 0.926 | 0.912 | 0.941 | 1.12 | 361 |
| [C-e5large-section700meta-k3s089](experimentos/extra/C-e5large-section700meta-k3s089.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k≤3, s≥0.89 | 0.922 | 0.912 | 0.941 | 0.941 | 1.00 | 327 |
| [C-e5large-section700meta-k5](experimentos/extra/C-e5large-section700meta-k5.jsonl.eval.json) | multilingual-e5-large | section ≤700 | sí | k=5 | 0.347 | 1.000 | 0.212 | 0.963 | 5.00 | 1404 |
| [D-e5large-section700meta-rrk1](experimentos/extra/D-e5large-section700meta-rrk1.jsonl.eval.json) | multilingual-e5-large + bge-reranker-v2-m3 (top 10) | section ≤700 | sí | k=1 | 0.980 | 0.971 | 1.000 | 1.000 | 1.00 | 329 |
| [D-e5large-section700meta-rrk2](experimentos/extra/D-e5large-section700meta-rrk2.jsonl.eval.json) | multilingual-e5-large + bge-reranker-v2-m3 (top 10) | section ≤700 | sí | k=2 | 0.686 | 1.000 | 0.529 | 1.000 | 2.00 | 639 |
| [D5-e5large-section700meta-rrk1](experimentos/extra/D5-e5large-section700meta-rrk1.jsonl.eval.json) | multilingual-e5-large + bge-reranker-v2-m3 (top 5) | section ≤700 | sí | k=1 | 0.980 | 0.971 | 1.000 | 1.000 | 1.00 | 329 |
