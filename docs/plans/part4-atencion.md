# Plan — Parte 4: una capa de atención en NumPy

**Fecha:** 2026-10-09 · **Entrega de la misión:** viernes 2026-10-09
**Alcance:** `atencion.py` en la raíz, verificado con `atencion/test_atencion.py` sin modificar.

## Convenciones que fija el test

- **Vectores fila:** `X` es (n, d) con un token por fila, y cada proyección es `X @ W`, con `W` de forma (d, d_k).
- **`softmax`:** sobre el último eje y estable, restando el máximo de cada fila.
- **`atencion`:** escala por `sqrt(d_k)`, con `d_k = K.shape[-1]`. La máscara causal pone −∞ arriba de la diagonal **antes** del softmax.
- **`multicabeza`:** recibe las cabezas ya separadas, como tuplas `(Wq, Wk, Wv)`. Concatena sus salidas en el orden de la lista y después aplica `Wo`.
- **`layer_norm`:** por fila, con varianza poblacional y `eps` dentro de la raíz, sin gamma ni beta. Con [2, 0, 1, 1] da ±1,4142, que es lo que exige el test; con la varianza muestral daría 1,2247.

## Commits (TDD)

1. Esqueleto: las cinco firmas con `NotImplementedError`. Los 14 tests en rojo.
2. `softmax`: 3 de 14.
3. `atencion`, con la máscara: 4 de 14.
4. `autoatencion`: 9 de 14.
5. `multicabeza`: 11 de 14.
6. `layer_norm`: 14 de 14.
7. Un wrapper de pytest que corre el test de la cátedra como subproceso.
8. Docs.

## Verificación

- Los 14 tests de la cátedra pasan.
- Comparé contra una implementación de referencia con `scipy.special.softmax` y `scipy.stats.zscore`, sobre 200 casos al azar y con y sin máscara: diferencia máxima de 0. El script no quedó en el repo.
