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

### Resumen

`agente.py` es un agente con tool calling sobre **`deepseek/deepseek-v4-flash-0731`** (vía OpenRouter), armado con el **SDK de agentes de OpenAI** (`openai-agents`). Tiene las seis herramientas de la consigna: `buscar_documentos` llama al recuperador de la Parte 1 y las otras cinco a la API del hospital.

| Corrida entregada (`respuestas.jsonl`, dev) | Ruteo | Context Relevance | Faithfulness | Answer Relevance | Costo del agente |
|---|---|---|---|---|---|
| `v2-margen` | **1,00** | **4,92** | **5,00** | **5,00** | USD 0,0036 |

Las tres métricas quedan por encima de 4 y el ruteo es perfecto en las 12 preguntas. El log de la corrida está en `respuestas.log.md`, y su evaluación en `respuestas.jsonl.eval.json`. Para reproducirla:

```bash
python3 api/servidor.py &
export OPENROUTER_API_KEY=...
python3 agente.py --preguntas datos/preguntas_agente_dev.jsonl --salida respuestas.jsonl   # también escribe respuestas.log.md
python3 evaluar/evaluar.py agente --preguntas datos/preguntas_agente_dev.jsonl --respuestas respuestas.jsonl
```

### Diseño

- **Herramientas en un solo lugar.** Las seis herramientas viven en `assistant/tools.py` como funciones Python que devuelven texto. `agente.py` las expone con `function_tool`, y el servidor MCP de la Parte 3 puede envolver las mismas funciones con `@mcp.tool()`. Una herramienta nunca lanza una excepción: si el nombre no existe, devuelve el error de la API con la lista de opciones, y el modelo puede corregirse.
- **Descripciones que el modelo puede usar.** La descripción de cada herramienta de la API incluye los nombres válidos (sectores, especialidades y medicamentos). Esos nombres no están escritos a mano: al arrancar, el agente le pide cada ruta a la API sin parámetro y la API responde con sus opciones. La descripción de `buscar_documentos` dice qué tipo de preguntas resuelve (normas, requisitos y trámites, no el estado del día) y lista los títulos de los 20 documentos, que se leen del corpus.
- **Prompt.** Pide separar la consulta en partes y resolver cada una con su fuente (estado del día → API, norma o trámite → documentos), no responder nunca de memoria y contestar breve, con los datos concretos y sin agregar consejos. Esas dos reglas apuntan a Faithfulness y a Context Relevance.
- **Una conversación por pregunta**, con `temperature = 0` y hasta 8 turnos. Si una corrida falla (por la red o por el límite de turnos), se repite completa hasta 3 veces. Si sigue fallando, la pregunta queda con respuesta vacía y el error en el log.
- **`contextos` y `herramientas` salen de la traza real** del SDK: cada resultado de herramienta entra como texto, incluidos los errores de la API si los hubo.
- **Log y costo.** El SDK informa los tokens de cada llamada al modelo, pero no el costo. Un hook en el cliente HTTP guarda el bloque `usage` que devuelve OpenRouter en cada respuesta, que trae el costo en USD. El log `.md` muestra, para cada pregunta, cada llamada al modelo con sus tokens (de entrada, en caché, de salida y de razonamiento) y su costo, cada herramienta con sus argumentos y su resultado, y la respuesta.

### Corridas

Todas las corridas están en `experimentos/agente/`, con su `respuestas.jsonl`, su `.eval.json` y su log. La tabla completa está en `experimentos/agente/RESULTS.md`, que genera `scripts/summarize_agent_runs.py`. Además de dev, armamos un set propio de 12 preguntas (`eval_extra/preguntas_agente_extra.jsonl`), con la misma forma, sobre documentos y entradas de la API que dev no usa. Tiene nombres coloquiales ("UTI", "psiquiatra", "paracetamol de 500") y combinaciones nuevas de las dos fuentes.

| Corrida | Qué cambia | Set | Ruteo | CR | F | AR | Llamadas a herramientas | Errores de la API | Costo agente (USD) |
|---|---|---|---|---|---|---|---|---|---|
| `v0-minimo` | Ablación: descripciones de una línea y prompt de una línea | dev | 1,00 | 5,00 | 5,00 | 5,00 | 15 | 0 | 0,0041 |
| `v0-minimo` | ídem | propio | 1,00 | 4,92 | 5,00 | 5,00 | 22 | 5 | 0,0053 |
| `v1-base` | Descripciones con opciones y temas, prompt completo, recuperador de la Parte 1 (k = 1) | dev | 1,00 | 5,00 | 5,00 | 5,00 | 15 | 0 | 0,0038 |
| `v1-base-rep2` | Repetición de v1 | dev | 1,00 | 5,00 | 5,00 | 5,00 | 15 | 0 | 0,0036 |
| `v1-base` | ídem | propio | 1,00 | 5,00 | 5,00 | 5,00 | 17 | 0 | 0,0040 |
| **`v2-margen`** | **v1 + corte adaptativo del recuperador (hasta 3 fragmentos, margen 0,45)** | **dev** | **1,00** | **4,92** | **5,00** | **5,00** | 15 | 0 | 0,0036 |
| `v2-margen` | ídem | propio | 1,00 | 5,00 | 5,00 | 5,00 | 16 | 0 | 0,0039 |

El ablación `v0-minimo` muestra que, en estas preguntas, el modelo rutea bien solo con los nombres de las herramientas. Lo que aportan las descripciones aparece en el set propio. Sin la lista de opciones, el modelo prueba nombres que la API no conoce ("UTI", "psiquiatría", "psicología", "paracetamol", "levotiroxina 50"): hace 5 llamadas fallidas, 22 llamadas a herramientas en lugar de 16 o 17, y cuesta un 35 % más. Esos errores además quedan en los contextos, y el juez le baja la Context Relevance a Y05. Con las opciones en la descripción no hubo ningún error de la API en ninguna corrida. Las descripciones más largas duplican los tokens de entrada (unos 45 000 contra 22 000–27 000 por corrida), pero la entrada es barata, la mitad sale de la caché y el modelo razona menos, así que el costo total baja.

### Dónde falló el agente

Con el juez, ninguna pregunta de v1 bajó de 5. Pero leyendo los logs aparecen fallas que el juez no castigó.

- **A10 (pediatría), en v1, en las dos repeticiones y en v0.** El agente busca, por ejemplo, "acompañante en internación de pediatría puede quedarse". El recuperador devuelve un solo fragmento, y es la regla general de internación ("se permite un acompañante por paciente internado durante la noche, salvo en terapia intensiva"), no la de pediatría ("madre, padre o tutor pueden permanecer las 24 horas"). La respuesta es fiel a ese contexto, así que el juez le pone 5, pero es menos precisa que la referencia: no dice que la permanencia es de 24 horas. La causa está en el recuperador. Con k = 1 (la configuración óptima de la Parte 1), el reranker eligió `internacion/Acompañante` con un puntaje de 0,39 a 0,60, y `visitas/Pediatría` quedó 2° o 3°, a menos de 0,4 del primero. En las otras 13 búsquedas del agente, el mejor fragmento sacó 0,88 o más y el segundo quedó a más de 0,5.
- **El arreglo, `v2-margen`:** `config/agent_retriever.json` usa el mismo encoder, el mismo chunking y el mismo reranker que la Parte 1, pero con un corte adaptativo, `top_k = 3` y `max_margin = 0,45`. Cuando el reranker está seguro devuelve un fragmento, y cuando duda devuelve los que quedan cerca del mejor. En las 14 búsquedas de v2 (dev y set propio), solo la de A10 devolvió más de un fragmento (tres), y la respuesta pasó a ser la correcta ("madre, padre o tutor pueden permanecer las 24 horas"). El precio es que el juez ve dos fragmentos de más en A10 y baja su Context Relevance a 4 (4,92 de promedio). Preferimos una respuesta correcta a un punto de CR. El margen de 0,45 sale de mirar los puntajes de las búsquedas de v1 en dev y en el set propio, así que es una elección informada por esos datos. `recuperar.py` (Parte 1) sigue usando `config/retriever.json`, con k = 1.
- **A09 (espera en verde).** La respuesta da los 135 minutos, pero no aclara, como la referencia, que eso supera las 2 horas que el triage fija para el nivel verde. El agente solo consultó la API, que es la herramienta esperada, y el juez le puso 5 en Answer Relevance. En la pregunta Y12 del set propio, que pide explícitamente el máximo, el agente sí combinó `consultar_espera` con `buscar_documentos`.
- **Días de la semana (A07, A11).** El agente agrega el día de la semana ("miércoles 7 de octubre"), que la API no informa. El dato es correcto, porque el 7 y el 14 de octubre de 2026 caen miércoles, pero no está en los contextos. El juez no lo penalizó en Faithfulness.

Conclusión: en dev el juez está saturado (5,00 en casi todo), y los problemas reales solo se ven leyendo los logs. Por eso cada corrida deja el suyo.

### Modelo y precios

El id `deepseek/deepseek-v4-flash-0731` sigue en el catálogo de OpenRouter, pero el 2026-10-04 su precio era USD 0,0152 / 1,28 por millón de tokens (entrada / salida), distinto del 0,04 / 0,64 de la consigna. Los costos de este informe son los que devolvió OpenRouter en cada llamada, no estimaciones hechas con la tabla de precios.

### Costo de ejecución

Cada corrida de 12 preguntas hace 24 llamadas al modelo y tarda entre 2,5 y 3 minutos en CPU. De ese tiempo, unos 20 s son la carga de e5-large y del reranker, que se hace una sola vez y recién en la primera búsqueda en documentos. El agente cuesta unos USD 0,004 por corrida, unos USD 0,0003 por pregunta. El juez del evaluador cuesta unas 4 veces más, alrededor de USD 0,017 por corrida.

## Parte 3: las mismas herramientas como servidor MCP

### Resumen

`servidor_mcp.py` expone las seis herramientas de la Parte 2 como un servidor MCP. Usa FastMCP, del SDK oficial `mcp` 1.x, con transporte stdio. `agente_mcp.py` es el agente de la Parte 2 sin herramientas propias: lanza el servidor con `MCPServerStdio` (de `openai-agents`), descubre las herramientas con `tools/list` y las llama con `tools/call`. El modelo es el mismo, `deepseek/deepseek-v4-flash-0731` vía OpenRouter.

| Corrida entregada (`respuestas_mcp.jsonl`, dev) | Ruteo | Context Relevance | Faithfulness | Answer Relevance | Costo del agente |
|---|---|---|---|---|---|
| `v2-margen` por MCP | **1,00** | **5,00** | **5,00** | **5,00** | USD 0,003789 |

El log de la corrida está en `respuestas_mcp.log.md` y su evaluación, en `respuestas_mcp.jsonl.eval.json`. Son copias de `experimentos/agente_mcp/v2-margen/`. Para reproducirla:

```bash
python3 api/servidor.py &
export OPENROUTER_API_KEY=...
python3 agente_mcp.py --preguntas datos/preguntas_agente_dev.jsonl --salida respuestas_mcp.jsonl   # también escribe respuestas_mcp.log.md
python3 evaluar/evaluar.py agente --preguntas datos/preguntas_agente_dev.jsonl --respuestas respuestas_mcp.jsonl
```

### Diseño: que la comparación mida solo el protocolo

El objetivo es que la Parte 2 y la Parte 3 difieran únicamente en cómo viajan las herramientas: llamadas a funciones de Python en la Parte 2 y mensajes MCP por stdio en la Parte 3. Todo lo demás es igual, y los tests lo verifican.

- **Las herramientas están en un solo lugar.** Cada `@mcp.tool()` de `servidor_mcp.py` es una función de una línea que llama al método correspondiente de `HospitalTools` (`assistant/tools.py`), el mismo que usa la Parte 2. `agente_mcp.py` no tiene código propio para la API ni para el recuperador; un test revisa sus imports.
- **Descripciones idénticas.** El servidor toma la descripción de cada herramienta de `HospitalTools.descriptions()` al arrancar, con las opciones que informa la API, igual que `agente.py`. Un test lanza el servidor por stdio con un cliente MCP real, sin LLM, y comprueba que lo que devuelve `tools/list` es idéntico, carácter por carácter, a esas descripciones. Otro test comprueba que `tools/call` devuelve el mismo texto que la herramienta llamada directamente.
- **Mismo prompt, mismo modelo y mismos parámetros.** Los dos agentes se arman con la misma función: las mismas instrucciones, `temperature = 0`, hasta 8 turnos, 3 reintentos por pregunta y la misma captura de usage. El servidor usa el mismo recuperador que la Parte 2 (`config/agent_retriever.json`).
- **Contextos normalizados.** El SDK devuelve el resultado de una herramienta MCP como un bloque `{"type": "text", "text": ...}`, no como texto plano. Sin normalizarlo, el juez habría recibido los contextos envueltos en ese JSON. La traza extrae el texto. Un test corre los dos agentes con los mismos turnos de un modelo guionado y comprueba que escriben **filas idénticas**: misma respuesta, mismos `contextos` y mismas `herramientas`.
- **Esquemas estrictos.** FastMCP declara los argumentos como objetos abiertos, y el SDK no puede pasar un objeto abierto a modo estricto. Así, el modelo habría visto esquemas distintos a los de la Parte 2, que usa `function_tool` con esquema estricto. Para evitarlo, el servidor declara `additionalProperties: false` y el agente pide `convert_schemas_to_strict`. El modelo recibe los mismos esquemas que en la Parte 2. Solo cambia el `title` interno que genera cada librería (`buscar_documentosArguments` en lugar de `buscar_documentos_args`).
- **Timeout de arranque.** El servidor carga e5-large y el reranker y embebe el corpus antes de responder `initialize`. Por eso el recuperador se carga una sola vez y no en la primera búsqueda. En una prueba sin LLM, el arranque tardó 112 s con los modelos ya descargados. El SDK corta la sesión a los 5 s por defecto, así que `agente_mcp.py` espera hasta 900 s, para cubrir también una primera corrida que tenga que descargar unos 4,5 GB de modelos. Mientras carga, stdout se redirige a stderr, porque stdout es el canal del protocolo.

### Parte 2 contra Parte 3

Los números salen de `experimentos/agente_mcp/COMPARACION.md` y `experimentos/agente_mcp/RESULTS.md`, que genera `scripts/summarize_agent_runs.py` a partir de los `.eval.json` y los logs. Costos en USD.

| Set | Corrida | Parte | Ruteo | CR | F | AR | Llamadas al modelo | Llamadas a herramientas | Tokens de entrada | Tokens de salida (razonamiento) | Costo agente | Costo juez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev | `v2-margen` | 2 | 1,00 | 4,917 | 5,000 | 5,000 | 24 | 15 | 44 982 | 2 311 (818) | 0,003642 | 0,01629 |
| dev | `v2-margen` | 3 (MCP) | 1,00 | 5,000 | 5,000 | 5,000 | 24 | 15 | 44 898 | 2 329 (896) | 0,003789 | 0,01593 |
| dev | `v2-margen-rep2` | 3 (MCP) | 1,00 | 5,000 | 5,000 | 5,000 | 24 | 15 | 44 994 | 2 234 (794) | 0,003550 | 0,01835 |
| propio | `extra/v2-margen` | 2 | 1,00 | 5,000 | 5,000 | 5,000 | 24 | 16 | 45 170 | 2 476 (1 107) | 0,003856 | 0,01857 |
| propio | `extra/v2-margen` | 3 (MCP) | 1,00 | 5,000 | 5,000 | 4,917 | 24 | 16 | 45 278 | 2 463 (1 131) | 0,003968 | 0,01798 |

Las dos partes hacen el mismo trabajo: el mismo ruteo, las mismas 24 llamadas al modelo, la misma cantidad de llamadas a herramientas, unos 45 000 tokens de entrada y un costo del agente dentro del mismo rango. En cada set cambia una sola nota del juez, en una sola pregunta, y en sentidos opuestos: sube la CR de A10 en dev y baja la AR de Y09 en el set propio.

### Ruido o protocolo

Para saber si esas diferencias vienen del transporte, las comparamos con lo que cambia entre dos corridas **idénticas** de la misma parte. En la Parte 2 son `v1-base` y `v1-base-rep2`, y en la Parte 3, `v2-margen` y `v2-margen-rep2`. Aunque la temperatura es 0, el modelo no es determinista. Los números de esta tabla salen de comparar los `respuestas*.jsonl` y las llamadas registradas en los logs de cada par de corridas.

| Comparación | Respuestas idénticas | Contextos idénticos | Mismas llamadas y argumentos | Notas del juez distintas |
|---|---|---|---|---|
| **Ruido, Parte 2:** `v1-base` contra `v1-base-rep2` | 5/12 | 12/12 | 10/12 | ninguna |
| **Ruido, Parte 3:** `v2-margen` contra `v2-margen-rep2` | 6/12 | 11/12 | 9/12 | ninguna |
| Parte 2 contra Parte 3, dev, corrida 1 | 5/12 | 11/12 | 9/12 | A10 |
| Parte 2 contra Parte 3, dev, repetición | 5/12 | 11/12 | 8/12 | A10 |
| Parte 2 contra Parte 3, set propio | 3/12 | 11/12 | 9/12 | Y09 |

**Conclusión: todas las diferencias entre la Parte 2 y la Parte 3 están dentro del ruido.**
- Entre dos corridas idénticas ya cambia la redacción de más de la mitad de las respuestas y la consulta de 2 o 3 búsquedas. Entre partes cambia lo mismo y en la misma proporción.
- Las consultas que cambian son reformulaciones de una o dos palabras: "quién" en lugar de "quiénes", "gestación" en lugar de "embarazo", "de la farmacia" en lugar de "en la farmacia".
- No encontramos ninguna diferencia atribuible al protocolo en las métricas, en las herramientas elegidas, en los tokens ni en el costo.
- Del protocolo solo es el tiempo, que se analiza más abajo.

### Pregunta por pregunta

- **A10 (pediatría, dev): CR 4 en la Parte 2 y 5 en la Parte 3. Es ruido, y además esconde una regresión que el juez no detectó.**
  - En la corrida entregada de MCP, el agente buscó "acompañante de un niño durante la internación en pediatría". Con esa redacción, el reranker quedó seguro y el corte adaptativo devolvió **un solo fragmento, el equivocado**: la regla general de internación ("se permite un acompañante por paciente internado durante la noche"). La respuesta volvió a ser la de v1, menos precisa que la referencia, que dice que madre, padre o tutor pueden quedarse las 24 horas.
  - **El juez no detectó la regresión:** le puso 5/5/5, porque la respuesta es fiel a un contexto corto. La CR "mejoró" justamente porque el contexto tenía menos fragmentos.
  - En la repetición, la consulta fue "acompañante en internación de pediatría puede quedarse": volvieron los tres fragmentos y la respuesta correcta, y el juez también le puso 5. En la Parte 2, ese mismo tipo de contexto de tres fragmentos había recibido un 4. Es decir, el juez tampoco puntúa de forma estable el mismo tipo de contexto.
  - **Esto refuerza el riesgo de sobreajuste del margen 0,45.** Ese margen se eligió mirando los puntajes de las búsquedas de v1, y la corrección de A10 depende de cómo redacte la consulta el modelo. Basta con cambiar dos palabras para que el reranker quede seguro y el margen no se active. Con un solo caso no hay evidencia de que el arreglo generalice.
- **Y09 (kinesiología, set propio): AR 5 en la Parte 2 y 4 en la Parte 3. Es ruido de redacción.** Las llamadas y los contextos son idénticos en las dos partes. Esta vez la respuesta no menciona que hay que llevar la orden médica, y la justificación del juez dice exactamente eso. La respuesta de la Parte 2 sí la nombraba.
- **Y12 (espera en amarillo, set propio): contextos distintos, misma nota (5/5/5). Es ruido.** La consulta salió con otra redacción ("tiempo máximo de espera en guardia según clasificación triage amarillo"). Con ella, el corte adaptativo dejó pasar un segundo fragmento del mismo documento de triage, y el juez no lo castigó.

### Los tres intentos de la corrida entregada

La corrida de dev de MCP se intentó tres veces en la misma carpeta, y solo el tercer intento forma parte de los resultados. En los dos intentos fallidos, el servidor MCP, las herramientas y la API del hospital funcionaron. **Las fallas fueron de red, entre la computadora y OpenRouter, no del código.**

1. **Primer intento:** A01 a A11 se completaron, y A12 falló los tres reintentos con `APIConnectionError`. No se corrió el juez. Según la salida del agente, ese intento costó USD 0,003024.
2. **Segundo intento:** fallaron las 12 preguntas con `APIConnectionError`, y no hubo ningún cobro. El diagnóstico mostró que algo en la red local interceptaba HTTPS de forma intermitente y presentaba un certificado autofirmado. La librería `httpx`, que usa el cliente de OpenAI, rechazaba la conexión (`CERTIFICATE_VERIFY_FAILED: self-signed certificate in certificate chain`). Minutos después, el certificado volvió a ser el legítimo.
3. **Tercer intento:** se corrió después de verificar la conexión y se completó sin errores. Es la corrida entregada.

Cada intento sobrescribió la carpeta del anterior, así que **los logs `.md` de los dos intentos fallidos no se conservan**. Lo que se sabe de ellos sale de la salida por consola y del diagnóstico que hicimos en el momento.

### Costo

| Concepto | Agente | Juez | Total |
|---|---|---|---|
| 3 corridas de `experimentos/agente_mcp/` (`RESULTS.md`) | 0,011307 | 0,05226 | 0,063567 |
| Primer intento fallido de la corrida de dev | 0,003292 | — | 0,003292 |
| **Total de la Parte 3** | **0,014599** | **0,05226** | **0,066859** |

El costo del intento fallido es lo que subió el contador de la key durante ese intento. El agente había registrado USD 0,003024 en su salida por consola, pero el log se sobrescribió. El contraste con el contador de la key, para toda la misión, está en "Costo total en OpenRouter".

### Tiempo

- **Por pregunta, la Parte 3 tarda menos:** la suma de los tiempos por pregunta es de 126 s en la corrida de dev y de 97 s en la repetición, contra 176 s de `v2-margen` en la Parte 2. Esto pasa porque el recuperador se carga al arrancar el servidor y no dentro de la primera búsqueda.
- **Pero hay que sumar el arranque:** antes de la primera pregunta, el servidor tarda entre unos 60 s, en la corrida entregada, y 112 s, en la prueba sin LLM, en cargar los modelos y embeber el corpus.

El tiempo total de una corrida queda en el mismo orden en las dos partes. La diferencia solo cambia en qué momento se paga la carga del recuperador.

### MCP Inspector

Para verificar que el servidor funciona con cualquier cliente MCP, lo conectamos también al MCP Inspector 2.9.0, que no usa ningún LLM, y desde ahí llamamos a cada una de las seis herramientas con la configuración real (e5-large y el reranker).

El comando de la consigna (`npx @modelcontextprotocol/inspector python3 servidor_mcp.py`) no alcanzó, por dos motivos. Por eso lanzamos el Inspector con un archivo de configuración (`--config`), fuera del repo:

- **Timeout.** El servidor tarda unos 112 s en responder `initialize`, porque antes carga los modelos y embebe el corpus. El Inspector corta la conexión a los 30 s por defecto. En el archivo pusimos el campo `connectionTimeout` del servidor en 300 000 ms.
- **Red.** Para evitar los problemas de red descritos más arriba, el servidor se lanzó con `HF_HUB_OFFLINE=1`. Así usa los modelos que ya están en la caché y no consulta Hugging Face al arrancar.

```json
{
  "mcpServers": {
    "hospital": {
      "type": "stdio",
      "command": "<python del entorno virtual>",
      "args": ["servidor_mcp.py", "--api-url", "http://127.0.0.1:8765"],
      "cwd": "<raíz del repositorio>",
      "env": { "HF_HUB_OFFLINE": "1", "PYTHONIOENCODING": "utf-8" },
      "connectionTimeout": 300000,
      "requestTimeout": 300000
    }
  }
}
```

```bash
npx @modelcontextprotocol/inspector@2.9.0 --web --config <archivo>.json
```

Capturas, en `experimentos/inspector/`:

| Captura | Qué muestra |
|---|---|
| `00_conectado.png` | El servidor `hospital` conectado por stdio (MCP 2025-11-25) |
| `01_lista_herramientas.png` | `tools/list`: las seis herramientas, con la descripción de `buscar_documentos` (incluye los temas de los documentos) y su argumento `consulta` |
| `02_buscar_documentos.png` | Tres fragmentos de pediatría, entre ellos *Régimen de visitas — Pediatría* ("madre, padre o tutor pueden permanecer las 24 horas") |
| `03_consultar_camas.png` | `pediatria`: 24 camas, 17 ocupadas y 7 libres |
| `04_consultar_guardia.png` | `cardiologia`: Dr. Julián Ferreyra (08:00-20:00) y Dra. Paula Benítez (20:00-08:00) |
| `05_consultar_turnos.png` | `dermatologia`: turnos el 2026-11-03 a las 11:00 y el 2026-11-05 a las 11:30 |
| `06_consultar_farmacia.png` | `levotiroxina 50 mcg`: stock de 90 comprimidos |
| `07_consultar_espera.png` | Minutos de espera por nivel de triage: rojo 0, naranja 7, amarillo 48, verde 135, azul 210 |

Las seis herramientas respondieron desde el Inspector con el mismo JSON y los mismos fragmentos que reciben los agentes, sin pasar por ningún modelo.

## Parte 4: una capa de atención en NumPy

`atencion.py`, en la raíz, implementa solo con NumPy las cinco funciones que describe `atencion/test_atencion.py`: `softmax`, `atencion`, `autoatencion` (con máscara causal opcional), `multicabeza` y `layer_norm`. Ningún valor está escrito a mano: el ejemplo de la clase ("the cat sat", d = 4) solo aparece como entrada de los tests.

**Resultado: los 14 tests pasan,** con el archivo de tests tal cual lo entregó la cátedra.

```text
$ python3 atencion/test_atencion.py atencion.py
test_escala_por_raiz_de_dk ... ok
test_formas_con_n_distinto_de_d ... ok
test_mascara_causal ... ok
test_matriz_de_atencion ... ok
test_permutar_filas_permuta_la_salida ... ok
test_salida ... ok
test_invariante_a_escala_y_corrimiento ... ok
test_por_fila ... ok
test_valor_de_la_clase ... ok
test_dos_cabezas_concatenan_y_proyectan ... ok
test_una_cabeza_con_wo_identidad_es_autoatencion ... ok
test_estable_con_numeros_grandes ... ok
test_filas_suman_uno ... ok
test_valor_de_la_clase ... ok
Ran 14 tests
OK
```

Las convenciones salen de los tests:

- **Vectores fila.** `X` es una matriz (n, d) con un token por fila, y cada proyección es `X @ W`.
- **`softmax`** trabaja sobre el último eje y resta el máximo de cada fila antes de la exponencial, para que no haya desborde con números grandes.
- **`atencion`** calcula `A = softmax(Q Kᵀ / √d_k)`, con `d_k` leído de K, y devuelve `A V` junto con `A`. La máscara causal pone −∞ arriba de la diagonal **antes** del softmax: así esos pesos dan exactamente 0 y cada fila sigue sumando 1.
- **`multicabeza`** recibe las cabezas ya separadas, cada una con sus propias `(Wq, Wk, Wv)`. Concatena sus salidas en el orden de la lista y las proyecta con `Wo`.
- **`layer_norm`** normaliza cada fila con la varianza poblacional y `eps` dentro de la raíz, sin gamma ni beta. Con [2, 0, 1, 1] da ±1,4142, el valor del test; con la varianza muestral daría 1,2247.

`pytest` corre también estos 14 tests, a través de `tests/test_atencion_catedra.py`, que ejecuta el archivo de la cátedra sin modificarlo. Como control adicional comparamos las funciones con una implementación de referencia basada en `scipy` (`softmax` y `zscore`) sobre 200 casos al azar, con y sin máscara: la diferencia máxima fue 0. Esta parte no usa ningún LLM y su costo en OpenRouter es cero.

## Parte 5: un bloque de transformer a mano

Pendiente.

## Costo total en OpenRouter

**No tuvimos acceso al dashboard de actividad de OpenRouter,** porque la key es de la cuenta del grupo. Por eso contrastamos el costo registrado en el repo con el uso que informa la API para la key (`GET /api/v1/key`), consultada el 2026-10-09. Ese contador **incluye todo lo que se gastó con esta key desde que se creó**, no solo esta misión.

### Costo de la misión según el repo

El costo del agente sale de los logs y el del juez, de los `.eval.json`. Los dos los suma `scripts/summarize_agent_runs.py` (ver `experimentos/agente/RESULTS.md` y `experimentos/agente_mcp/RESULTS.md`). En USD:

| Parte | Agente | Juez | Total |
|---|---|---|---|
| 1 (sin LLM) | 0 | 0 | 0 |
| 2: 7 corridas de `experimentos/agente/` | 0,028260 | 0,120460 | 0,148720 |
| 3: 3 corridas de `experimentos/agente_mcp/` | 0,011307 | 0,052260 | 0,063567 |
| 3: primer intento fallido de la corrida de dev (por el contador de la key; su log se sobrescribió) | 0,003292 | — | 0,003292 |
| **Total con respaldo en el repo** | **0,042859** | **0,172720** | **0,215579** |
| 2: prueba de humo de 2 preguntas, fuera de `experimentos/` y sin archivo en el repo | 0,0011 | — | 0,0011 |

Por modelo: el agente (`deepseek/deepseek-v4-flash-0731`) costó USD 0,042859 y el juez (`google/gemini-3.7-flash`), USD 0,172720. El juez es el 80 % del gasto.

### Contraste con el contador de la key

| Tramo | Registros del repo | Contador de la key | Diferencia (contador − registros) |
|---|---|---|---|
| Hasta antes de la Parte 3 | 0,148720 (Parte 2) | 0,247026 (lectura antes de la Parte 3) | +0,098306 |
| Parte 3 | 0,066859 | 0,063462 (de 0,247026 a 0,310488) | −0,003397 |
| Después de la última lectura de la Parte 3 | 0 | 0,003403 (de 0,310488 a 0,313891) | +0,003403 |
| **Total** | **0,215579** | **0,313891** (lectura del 2026-10-09; límite de la key: USD 1,00) | **+0,098312** |

- **Casi toda la diferencia es anterior a la Parte 3:** unos USD 0,098. La prueba de humo de la Parte 2 explicaría USD 0,0011 de ese monto. Sin ella quedan unos USD 0,097.
- **La diferencia de la Parte 3 se compensa con lo que el contador subió después:** durante la Parte 3 el contador subió USD 0,003397 menos que los registros. Después de la última lectura subió USD 0,003403, aunque no hicimos ninguna llamada paga: solo consultamos `/api/v1/key`, que no cobra. Es posible que el contador todavía no hubiera sumado las últimas evaluaciones cuando lo leímos, pero no lo pudimos confirmar.
- **La API informa también un uso semanal (USD 0,086) y uno mensual (USD 0,236).** No verificamos si el mensual corresponde al mes calendario. Si fuera así, unos USD 0,078 del contador serían anteriores a octubre y, por lo tanto, anteriores a esta misión.

**La diferencia de unos USD 0,098 no se pudo atribuir con certeza.** Las causas posibles son otras pruebas o misiones hechas con la misma key, o llamadas que no quedaron registradas en los archivos del repo. No pudimos confirmar ninguna de las dos.

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
