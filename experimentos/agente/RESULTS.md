# Corridas del agente

Generado por `scripts/summarize_agent_runs.py`. Costos en USD: el del agente sale del usage que informa OpenRouter en cada llamada (ver el log de la corrida); el del juez, del `.eval.json`.

| Corrida | Preguntas | Ruteo | Context Rel. | Faithfulness | Answer Rel. | Llamadas al modelo | Llamadas a herramientas | Errores de la API | Tokens entrada | Tokens salida (razonamiento) | Costo agente | Costo juez | Segundos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `extra/v0-minimo` | 12 | 1.00 | 4.917 | 5.000 | 5.000 | 28 | 22 | 5 | 27511 | 3793 (1343) | 0.005273 | 0.01720 | 186 |
| `extra/v1-base` | 12 | 1.00 | 5.000 | 5.000 | 5.000 | 24 | 17 | 0 | 45402 | 2580 (1170) | 0.003993 | 0.01923 | 148 |
| `extra/v2-margen` | 12 | 1.00 | 5.000 | 5.000 | 5.000 | 24 | 16 | 0 | 45170 | 2476 (1107) | 0.003856 | 0.01857 | 140 |
| `v0-minimo` | 12 | 1.00 | 5.000 | 5.000 | 5.000 | 24 | 15 | 0 | 22082 | 2933 (810) | 0.004090 | 0.01727 | 199 |
| `v1-base` | 12 | 1.00 | 5.000 | 5.000 | 5.000 | 24 | 15 | 0 | 44912 | 2436 (936) | 0.003801 | 0.01682 | 172 |
| `v1-base-rep2` | 12 | 1.00 | 5.000 | 5.000 | 5.000 | 24 | 15 | 0 | 44845 | 2284 (856) | 0.003605 | 0.01508 | 145 |
| `v2-margen` | 12 | 1.00 | 4.917 | 5.000 | 5.000 | 24 | 15 | 0 | 44982 | 2311 (818) | 0.003642 | 0.01629 | 176 |

Total de estas corridas: agente USD 0.028260, juez USD 0.12046.
