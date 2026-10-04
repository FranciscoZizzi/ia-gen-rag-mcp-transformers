# Plan — Parte 1: RAG vectorial

**Estado:** propuesta para revisar · **Fecha:** 2026-10-04 · **Entrega de la misión:** viernes 2026-10-09
**Alcance:** `recuperar.py`, los experimentos de `experimentos/` y la sección de la Parte 1 de `INFORME.md`.

## TL;DR

- El recuperador vive en un paquete `rag/` (código en inglés). `recuperar.py` es un adaptador fino que respeta el contrato de la cátedra y lee la configuración ganadora de `config/retriever.json`.
- El evaluador premia **acertar el primer fragmento**. Con una evidencia por pregunta, devolver k fragmentos con uno solo correcto da como máximo 2/(k+1). El diseño maximiza hit@1 y devuelve un segundo fragmento sólo cuando hay un empate real.
- Comparamos 5 encoders transformer (BERT multilingüe como línea de base obligatoria, MiniLM, E5 small y base, BGE-M3), 4 estrategias de chunking y varias políticas de corte, por etapas. Cada configuración se mide con `evaluar/evaluar.py` sin modificar y deja su `.eval.json` en `experimentos/`.
- Hipótesis de partida, a confirmar con números: E5-base o BGE-M3, chunking por sección con título y sección antepuestos, corte adaptativo de 1 a 2 fragmentos.
- Desarrollo con TDD y un encoder léxico de prueba, así los tests unitarios corren offline en segundos.

## 1. Qué mide el evaluador y qué implica

`evaluar.py recuperacion` normaliza fragmentos y evidencias (NFKC, minúsculas, espacios colapsados) y busca cada evidencia como **substring** de algún fragmento:

- *recall*: evidencias encontradas / evidencias de la pregunta;
- *precision*: fragmentos que contienen alguna evidencia / fragmentos devueltos;
- *context_relevance* (CR): media armónica por pregunta, promediada sobre las preguntas. También reporta `mrr`, el `k` medio y los `caracteres` medios.

El detalle por pregunta queda en `<resultados>.eval.json`, así que cada corrida `experimentos/<run>.jsonl` deja su `experimentos/<run>.jsonl.eval.json`.

Con una sola evidencia por pregunta (las 20 de dev) y un único fragmento que la contiene:

| Fragmentos devueltos (k) | CR si la evidencia está | CR si no está |
|---|---|---|
| 1 | 1,00 | 0 |
| 2 | 0,67 | 0 |
| 3 | 0,50 | 0 |
| 5 | 0,33 | 0 |

El 0,35 de la línea de base léxica de la consigna (top-3 párrafos) equivale a encontrar la evidencia en el 70 % de las preguntas.

Consecuencias de diseño:

1. **Integridad de la evidencia.** Si un corte parte la frase de evidencia, la pregunta vale 0 aunque la recuperación haya sido correcta. Regla: ningún chunk corta una oración. Lo verifica un test.
2. **Lo que paga es hit@1.** Si p₁ y p₂ son las probabilidades de que la evidencia esté en el primer y en el segundo fragmento, devolver dos conviene sólo cuando p₂ > p₁/2. En la práctica eso pasa cuando los dos primeros puntajes están casi empatados, por eso el corte va por margen relativo y no por un top-k fijo.
3. **Nunca devolver 0 fragmentos**: la precisión queda en 0 y la pregunta también.
4. **El largo no penaliza acá, pero sí en la Parte 2.** CR no mira caracteres, así que devolver documentos enteros "funcionaría". Pero este mismo recuperador alimenta al agente, y el juez de la Parte 2 castiga el "ruido de más". Cada fila reporta `caracteres` y no elegimos chunks gigantes.
5. **Solapamiento.** Si dos ventanas solapadas contienen la evidencia y se devuelven juntas, la precisión sube sin que el recuperador sea mejor. Lo reportamos y no lo usamos como truco.
6. **Ruido estadístico.** Con 20 preguntas, una pregunta vale 0,05 de CR. Una diferencia menor es un empate.

## 2. El corpus en números

| Medida | Valor |
|---|---|
| Documentos | 20 (14,5 k caracteres) |
| Secciones, contando introducciones y documentos sin `##` | 56 |
| Párrafos o bloques de lista | 68 |
| Oraciones | ~137 |
| Largo de sección | mínimo 67, mediana 193, máximo 658 caracteres |

- **8 documentos no tienen `##`** (accesos, alta, donacion_sangre, farmacia, kinesiologia, salud_mental, telemedicina, vacunatorio), y 6 de las 20 preguntas dev caen ahí (R07, R10, R11, R15, R16, R18). El chunking por sección tiene que caer a párrafos en esos casos.
- **Cada evidencia dev está entera dentro de una sola oración**, un solo párrafo y una sola sección. El invariante "ningún chunk corta una oración" alcanza.
- **Distractores** que el diseño tiene que resolver:
  - R08 y R09 están en secciones con el mismo nombre ("Ayuno") de documentos distintos. Sólo el título del documento las separa, de ahí los metadatos título + sección.
  - R01 (terapia intensiva): `internacion.md` ("salvo en terapia intensiva") compite con `visitas.md`.
  - R16 (tatuaje): `preparacion_estudios.md` (resonancia) compite con `donacion_sangre.md`.
  - R02 y R03: varios ayunos distintos dentro del mismo documento. Hace falta granularidad de sección, no de documento.
- **Tres documentos no tienen ninguna pregunta dev** (internacion, salud_mental, telemedicina), y el test oculto es "sobre los mismos documentos". El set de validación propio (§8) tiene que cubrirlos.

## 3. Convenciones

- **Código en inglés**: módulos, clases, funciones, variables, docstrings, comentarios y mensajes de commit.
- **Los nombres del contrato no se traducen**: `recuperar.py`, `--preguntas`, `--salida`, las claves `id`, `pregunta`, `evidencia` y `fragmentos`, y la carpeta `experimentos/`. La cátedra depende de ellos.
- **Intocables**: `evaluar/`, `api/`, `datos/` y `atencion/test_atencion.py`. El evaluador se invoca por subprocess, tal cual está.
- **El recuperador nunca lee `evidencia`.** La usan sólo los tests de integridad y el script de análisis.
- Dependencias de ejecución: sólo las de `requirements.txt`. Para desarrollo, `requirements-dev.txt` con pytest. La configuración va en JSON (stdlib, sin PyYAML).
- Compatibilidad con Python ≥ 3.10: desarrollamos con 3.14, pero la cátedra puede correr otra versión.
- Lo que lee la cátedra (`INFORME.md`) va en castellano.

## 4. Arquitectura

```
datos/corpus/*.md
      │ load_corpus()
      ▼
Document(title, sections) ──► chunk(strategy) ──► Chunk(text, title, section)
                                                     │ encode_passages()
pregunta ──► encode_queries() ──► coseno ◄── VectorIndex (L2-normalizado, en caché)
                                    │ candidatos ordenados
                                    ▼
                        [rerank con cross-encoder]   (opcional)
                                    │
                                    ▼
             select(top_k, min_score, max_margin) ──► fragmentos
```

### Estructura de archivos

```
recuperar.py              # CLI del contrato: parsea args, carga la config, escribe el JSONL
rag/
  config.py               # RetrieverConfig y sus partes (dataclasses inmutables); carga y valida JSON
  text.py                 # normalize_for_match() (igual a la del evaluador) y split_sentences()
  corpus.py               # load_corpus() -> list[Document]
  chunking.py             # Chunk y las estrategias fixed, paragraph, section y sentence
  encoders.py             # MeanPoolingEncoder, SentenceTransformerEncoder, HashingBowEncoder
  index.py                # VectorIndex con caché de embeddings en disco
  selection.py            # select(): top-k, umbral absoluto y margen relativo
  reranking.py            # CrossEncoderReranker (opcional)
  retriever.py            # Retriever.from_config(), search(), search_many()
config/retriever.json     # configuración ganadora, congelada
scripts/
  run_experiments.py      # corre una grilla, llama a evaluar.py y regenera la tabla
  analyze_scores.py       # hit@k, márgenes, distribución de cosenos, bootstrap
experimentos/
  grids/*.json            # definiciones de las grillas
  <run>.jsonl             # salida del recuperador para esa configuración
  <run>.jsonl.eval.json   # salida de evaluar.py: la evidencia obligatoria
  <run>.config.json       # configuración exacta de la corrida
  RESULTS.md              # tabla generada a partir de los .eval.json
tests/
```

`buscar_documentos(consulta)` (Parte 2) y el servidor MCP (Parte 3) van a construir un único `Retriever` desde `config/retriever.json` y llamar a `search()`. Por eso el recuperador es una librería y `recuperar.py` sólo la adapta al contrato.

### Interfaces

```python
@dataclass(frozen=True)
class Chunk:
    chunk_id: str          # "visitas#3"
    doc_id: str            # "visitas"
    title: str             # "Régimen de visitas"
    section: str | None    # "Unidad de terapia intensiva de adultos"
    text: str              # verbatim corpus text, never cut mid-sentence

    def render(self, with_metadata: bool) -> str: ...


class Encoder(Protocol):
    max_seq_length: int | None

    def encode_queries(self, texts: Sequence[str]) -> np.ndarray: ...   # (n, d), L2-normalized
    def encode_passages(self, texts: Sequence[str]) -> np.ndarray: ...  # (m, d), L2-normalized


def select(ranked: Sequence[ScoredChunk], *, top_k: int,
           min_score: float | None = None, max_margin: float | None = None) -> list[ScoredChunk]: ...


class Retriever:
    @classmethod
    def from_config(cls, config: RetrieverConfig) -> "Retriever": ...
    def search(self, query: str) -> list[ScoredChunk]: ...
    def search_many(self, queries: Sequence[str]) -> list[list[ScoredChunk]]: ...
```

Forma de `config/retriever.json` (valores ilustrativos, los fijan los experimentos):

```json
{
  "corpus_dir": "datos/corpus",
  "encoder": {
    "type": "sentence_transformer",
    "model": "intfloat/multilingual-e5-base",
    "revision": "<commit sha>",
    "query_prefix": "query: ",
    "passage_prefix": "passage: "
  },
  "chunking": {"strategy": "section", "max_chars": 700, "overlap_sentences": 0, "metadata": true},
  "selection": {"top_k": 2, "min_score": null, "max_margin": 0.03},
  "reranker": null
}
```

### Decisiones

| # | Decisión | Por qué |
|---|---|---|
| D1 | Separar el *scoring* (encoder + chunking → candidatos ordenados) de la *selección* (k y umbrales) | Barrer k y umbrales no recalcula embeddings: la etapa C sale gratis |
| D2 | El texto de cada chunk es el del corpus, sin reescribir, y ningún corte cae dentro de una oración | Integridad de la evidencia (§1, punto 1) |
| D3 | Encabezado opcional `Título — Sección`, que se embebe y se devuelve con el chunk | Separa R08 de R09 y le da contexto al agente de la Parte 2 |
| D4 | Prefijos por encoder en la config. Los E5 (todos los tamaños, no sólo base) usan `query: ` y `passage: `; BGE-M3, MiniLM y BERT no usan prefijo | Los E5 multilingües no traen prompts configurados para sentence-transformers (verificado en el hub), así que hay que anteponerlos a mano |
| D5 | La línea de base BERT se implementa con `transformers` (`AutoModel` + promedio enmascarado de la última capa), con `mean_pool()` como función pura | Es lo que pide la consigna, y se testea con tensores de juguete |
| D6 | Siempre se devuelve al menos un fragmento | §1, punto 3 |
| D7 | Caché de embeddings en `.cache/`, con clave = hash de (modelo, revisión, prefijo, textos de los chunks) | Experimentos rápidos; una clave por contenido no puede quedar vieja |
| D8 | Inferencia determinística (`model.eval()`, `torch.inference_mode()`, orden estable) y revisión del modelo fijada en la config final | La corrida de la cátedra tiene que dar lo mismo que la nuestra |
| D9 | Un encoder léxico `hashing_bow` (bolsa de palabras con hashing) | Doble de prueba offline para los tests, y fila de control que debería reproducir el ~0,35 de la consigna |

## 5. Pasos de implementación (TDD)

Rama `feat/part1-retriever`. Los tests se escriben en rodajas verticales: un test en rojo, el código mínimo para ponerlo en verde, y el siguiente.

**Decisión del 2026-10-04:** hay tests sólo en los cuatro seams críticos: el contrato de `recuperar.py`, `Retriever`, `chunk_corpus` y `select`. Lo demás (texto, corpus, encoders, config, runner y análisis) se ejercita a través de esos seams o se verifica con corridas reales del evaluador.

| Paso | Qué | Cómo se verifica |
|---|---|---|
| 0 | Setup: venv, torch para CPU, `requirements-dev.txt`, configuración de pytest con `testpaths = ["tests"]`, `CLAUDE.md`, `SPEC.md` (sección Parte 1) | — |
| 1 | `rag/text.py`: `normalize_for_match()` y `split_sentences()` para castellano | A través de los tests de chunking: oraciones con "2.500 pesos", ítems de lista y las evidencias dev tienen que quedar enteras |
| 2 | `rag/corpus.py`: `Document` y `Section` desde el Markdown | A través de los tests de chunking (documentos sintéticos y el corpus real) |
| 3 | `rag/chunking.py`: estrategias `fixed`, `paragraph`, `section` y `sentence` | **Seam `chunk_corpus`**: salida literal de cada estrategia sobre documentos sintéticos; en el corpus real, ningún chunk vacío, toda evidencia dev dentro de algún chunk, ningún chunk cruza documentos |
| 4 | `rag/selection.py`: `select()` como función pura | **Seam `select`**: top-k; `min_score`; `max_margin`; siempre ≥ 1 |
| 5 | `rag/encoders.py`: los tres encoders y `build_encoder()` | Corridas reales del evaluador en la etapa A |
| 6 | `rag/index.py` y `rag/retriever.py` | **Seam `Retriever`**, con `hashing_bow`: orden descendente; `search` = ranking + corte; la caché no recalcula si nada cambió y no queda vieja si cambia el corpus |
| 7 | `recuperar.py` y `config/retriever.json` | **Seam del contrato**: una línea por pregunta, mismos ids y orden; funciona sin la clave `evidencia`; `evaluar/evaluar.py recuperacion` acepta la salida |
| 8 | Primera corrida real: la línea de base BERT | Primer `.eval.json` en `experimentos/` |
| 9 | `scripts/run_experiments.py`: corre una grilla, llama a `evaluar.py`, guarda `<run>.config.json` y regenera `experimentos/RESULTS.md` | Corrida real de la etapa A |
| 10 | `scripts/analyze_scores.py` | Contraste con los números del evaluador oficial |

`testpaths = ["tests"]` no es opcional: `atencion/test_atencion.py` lee `sys.argv[1]` y modifica `sys.argv` al importarse, así que si pytest lo recolecta, la recolección falla.

Los tests corren en pocos segundos y sin red.

## 6. Diseño experimental

La búsqueda va por etapas, una coordenada por vez, en lugar de una grilla completa. Cada fila deja tres archivos: `experimentos/<run>.jsonl`, `<run>.jsonl.eval.json` y `<run>.config.json`. El nombre de la corrida es `<etapa>-<encoder>-<chunking>-<corte>`, por ejemplo `A-e5base-section-meta-k1`. En total son unas 50 a 60 filas, ninguna con costo: la Parte 1 no usa LLM.

### Etapa A: el encoder

Chunking fijo (sección + metadatos), con k = 1 y k = 3. Con k = 1 el CR es directamente hit@1, y con k = 3 el recall es hit@3: los dos salen del evaluador oficial.

| Encoder | Rol | Prefijos | `max_seq_length` | Parámetros |
|---|---|---|---|---|
| `google-bert/bert-base-multilingual-cased` | Línea de base obligatoria (promedio de tokens) | — | 512 | 178 M |
| `dccuchile/bert-base-spanish-wwm-cased` | Línea de base extra, opcional (BETO) | — | 512 | 110 M |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Embeddings de oraciones | — | **128** | 118 M |
| `intfloat/multilingual-e5-small` | Embeddings de oraciones | `query: ` / `passage: ` | 512 | 118 M |
| `intfloat/multilingual-e5-base` | Embeddings de oraciones | `query: ` / `passage: ` | 512 | 278 M |
| `BAAI/bge-m3` | Embeddings de oraciones (vector denso) | — | 8192 | 568 M |
| `hashing_bow` | Control léxico: debería dar ~0,35 con párrafos y k = 3 | — | — | — |

MiniLM trunca a 128 tokens, y la sección más larga (658 caracteres más el encabezado) los supera. El análisis reporta qué porcentaje de chunks se trunca con cada encoder, para no confundir "encoder peor" con "encoder que no vio el final del chunk".

Para que la comparación sea justa, la línea de base BERT también corre con su mejor chunking y su mejor corte (fila `A-mbert-best`).

### Etapa B: el chunking (los dos mejores encoders de la etapa A)

| Estrategia | Parámetros |
|---|---|
| `fixed`: oraciones empaquetadas hasta un tamaño | `max_chars` ∈ {200, 400, 800} × `overlap_sentences` ∈ {0, 1} |
| `paragraph` | — |
| `section`: si una sección supera `max_chars`, se parte por párrafos | `max_chars` ∈ {400, 700} |
| `sentence`: una oración por chunk | — |

Con la mejor combinación, ablación de metadatos: con y sin encabezado.

### Etapa C: el corte (mejor encoder + mejor chunking)

- `top_k` ∈ {1, 2, 3, 5}.
- `min_score`, barrido sobre percentiles de los puntajes de ese encoder: los cosenos no son comparables entre encoders.
- `max_margin` ∈ {0,01; 0,02; 0,03; 0,05; 0,10} con `k_max` ∈ {2, 3}.

### Etapa D (opcional, si sobra tiempo)

Reranking con `BAAI/bge-reranker-v2-m3`, un cross-encoder multilingüe, sobre los 10 primeros candidatos del bi-encoder, con el corte aplicado al puntaje del reranker. Es la palanca con más potencial para hit@1.

### La tabla del informe

| Run | Encoder | Chunking | Metadatos | Corte | CR | Recall | Precision | MRR | k medio | Caracteres | Evaluación |
|---|---|---|---|---|---|---|---|---|---|---|---|

La genera `run_experiments.py` en `experimentos/RESULTS.md` a partir de los `.eval.json`, así ningún número se copia a mano.

## 7. Cómo explicar por qué ganó el encoder

El criterio de éxito pide explicarlo con números:

- hit@1, hit@3 y MRR por encoder, con el mismo chunking.
- Separación de puntajes: coseno del chunk correcto contra el del mejor incorrecto, y margen entre el primero y el segundo. La hipótesis a mostrar es que en BERT sin ajustar todos los cosenos caen en una franja alta y angosta (anisotropía), y por eso ni el primer puesto ni los umbrales discriminan.
- Tabla por pregunta, ganador contra línea de base, a partir del `detalle` de los `.eval.json`: qué preguntas se dieron vuelta y qué distractor de la §2 explica cada una.
- Intervalo de confianza del 95 % para la diferencia de CR, con bootstrap pareado sobre las preguntas.
- Truncamiento por encoder, tamaño del modelo y latencia, como criterios de desempate.

## 8. Control de sobreajuste

- Una diferencia menor a 0,05 de CR (una pregunta) es un empate. En empate gana la configuración más simple o el modelo más chico.
- Elegir dentro de una meseta de la grilla, no en un pico aislado.
- **Set de validación propio**: 20 a 30 preguntas nuevas en `eval_extra/preguntas_recuperacion_extra.jsonl` (fuera de `datos/`), con el mismo formato, evidencia textual del corpus y el tono coloquial de dev, redactadas por el grupo. Tiene que cubrir los tres documentos sin preguntas dev e incluir algunas preguntas con dos evidencias, por ejemplo "¿cuándo me dan el alta después de una cesárea y a qué hora?" (`maternidad.md` + `alta.md`). Sirve sólo para confirmar al finalista, no para tunear.
- Dev trae sólo preguntas de una evidencia, pero la consigna dice "una o más". Por eso, salvo que los números digan lo contrario, preferimos el corte por margen, que devuelve dos fragmentos cuando los dos son relevantes, antes que un k = 1 fijo.
- Nada de reglas por palabra clave ni de ajustes por pregunta.

## 9. Criterios de aceptación

- [ ] `python3 recuperar.py --preguntas datos/preguntas_recuperacion_dev.jsonl --salida resultados.jsonl` corre desde un clon limpio después de `pip install -r requirements.txt`, sin flags extra.
- [ ] La configuración ganadora está fija en `config/retriever.json`, con la revisión del modelo fijada.
- [ ] `evaluar/evaluar.py recuperacion` acepta la salida.
- [ ] Hay al menos 3 encoders comparados, incluida la línea de base BERT, y cada fila de la tabla tiene su `.eval.json` en `experimentos/`.
- [ ] La configuración entregada le gana a BERT con claridad, con la diferencia y su intervalo de confianza.
- [ ] `INFORME.md` tiene la sección de la Parte 1: tabla, elección y explicación con números.
- [ ] `pytest` pasa y los tests unitarios corren offline.
- [ ] PR de `feat/part1-retriever` a `main` con la historia limpia (rebase and merge, sin squash).

## 10. Riesgos

| Riesgo | Mitigación |
|---|---|
| En Linux, `pip install torch` baja la variante CUDA (varios GB) | Instalar antes la versión para CPU: `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| Python 3.14 sin rueda para alguna dependencia | venv con Python 3.12 (`uv venv --python 3.12`) |
| Descargas de modelos: ~8 GB entre los encoders y el reranker | Bajar sólo lo que use cada etapa. En empate, el modelo más chico, porque la cátedra lo descarga al correr |
| MiniLM trunca a 128 tokens | Reportarlo y probarlo con chunks más chicos |
| BGE-M3 es el más lento en CPU | Medir la latencia; con 56 a 137 chunks son segundos igual |
| Una evidencia partida entre dos chunks | Test de integridad para todas las estrategias |
| Sobreajuste a las 20 preguntas dev | §8 |
| Un modelo cambia en el hub | Fijar `revision` en la configuración final |

## 11. Cronograma

La Parte 1 es el camino crítico: `buscar_documentos`, en las Partes 2 y 3, llama a este recuperador. La Parte 4 (NumPy) es independiente y puede avanzar en paralelo.

| Día | Objetivo |
|---|---|
| Domingo 4/10 | Paso 0, `CLAUDE.md`, `SPEC.md`, pasos 1 a 4 |
| Lunes 5/10 | Pasos 5 a 8 (primer número: la línea de base BERT) y paso 9 |
| Martes 6/10 | Etapas A a C, paso 10 y análisis; se congela `config/retriever.json`. Desde acá puede arrancar la Parte 2 |
| Miércoles 7/10 (mañana) | Etapa D y set propio si hay tiempo; sección de la Parte 1 en `INFORME.md`; PR |

## 12. Commits previstos

1. `chore: add dev tooling, CLAUDE.md and part 1 SPEC.md`
2. `feat(text): add evaluator-compatible normalization and sentence splitter`
3. `feat(corpus): parse markdown documents into titled sections`
4. `feat(chunking): add fixed, paragraph, section and sentence strategies`
5. `feat(selection): add top-k, min-score and margin cut-off`
6. `feat(encoders): add mean-pooling BERT, sentence-transformer and lexical encoders`
7. `feat(retriever): add vector index with embedding cache`
8. `feat(cli): add recuperar.py contract entrypoint and default config`
9. `feat(experiments): add experiment runner and results table`
10. `feat(analysis): add score diagnostics and paired bootstrap`
11. `exp: ...` (un commit por etapa, el último congela la configuración ganadora)
12. `docs(report): add part 1 section to INFORME.md`

## Fuera de alcance por ahora

- Búsqueda híbrida léxica + densa (BM25 + embeddings). Es la siguiente palanca si la etapa D no alcanza.
- Fine-tuning de encoders.
- Expansión de consultas con un LLM: cuesta plata y la Parte 1 no la necesita.
