# Corridas del agente MCP

Generado por `scripts/summarize_agent_runs.py`. Costos en USD: el del agente sale del usage que informa OpenRouter en cada llamada (ver el log de la corrida); el del juez, del `.eval.json`.

| Corrida | Preguntas | Ruteo | Context Rel. | Faithfulness | Answer Rel. | Llamadas al modelo | Llamadas a herramientas | Errores de la API | Tokens entrada | Tokens salida (razonamiento) | Costo agente | Costo juez | Segundos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `extra/v2-margen` | 12 | 1.00 | 5.000 | 5.000 | 4.917 | 24 | 16 | 0 | 45278 | 2463 (1131) | 0.003968 | 0.01798 | 170 |
| `v2-margen` | 12 | 1.00 | 5.000 | 5.000 | 5.000 | 24 | 15 | 0 | 44898 | 2329 (896) | 0.003789 | 0.01593 | 126 |
| `v2-margen-rep2` | 12 | 1.00 | 5.000 | 5.000 | 5.000 | 24 | 15 | 0 | 44994 | 2234 (794) | 0.003550 | 0.01835 | 97 |

Total de estas corridas: agente USD 0.011307, juez USD 0.05226.
