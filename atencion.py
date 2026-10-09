"""Part 4: an attention layer in NumPy, checked by atencion/test_atencion.py.

Conventions (the graders' tests fix them):
- Row vectors: X is (n, d), one token per row, and every projection is X @ W with W of shape (d, d_k).
- Every normalization runs over the last axis, i.e. along each row.

Run: python3 atencion/test_atencion.py atencion.py
"""
import numpy as np


def softmax(M):
    """Turn each row of scores into probabilities: non-negative and summing to 1 (last axis).

    softmax(z)_i = exp(z_i) / sum_j exp(z_j). Subtracting the row maximum first leaves the result unchanged
    (it cancels between numerator and denominator) but keeps exp from overflowing: exp(1000) is inf,
    exp(0) is 1. A score of -inf (a masked position) becomes exactly 0.
    """
    M = np.asarray(M, dtype=float)
    e = np.exp(M - M.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def atencion(Q, K, V, mascara=False):
    """Scaled dot-product attention; returns (output, A) with A = softmax(Q K^T / sqrt(d_k)).

    Q is (n_q, d_k), K is (n_k, d_k) and V is (n_k, d_v). Row i of Q K^T scores how well query i matches
    each key. Dividing by sqrt(d_k) keeps the scores' spread independent of the dimension: a dot product of
    d_k terms grows like sqrt(d_k), and without the scale the softmax saturates into a near one-hot row.
    Each row of A is a probability distribution over the keys, and output = A V mixes the values with
    those weights, so output is (n_q, d_v).

    With mascara=True (causal mask), every score above the diagonal is set to -inf *before* the softmax:
    token i may only attend to tokens 0..i, and each row still sums to 1 over the allowed positions.
    Masking after the softmax would leave rows that no longer sum to 1.
    """
    Q, K, V = (np.asarray(M, dtype=float) for M in (Q, K, V))
    d_k = K.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)
    if mascara:
        future = np.triu(np.ones(scores.shape, dtype=bool), k=1)
        scores = np.where(future, -np.inf, scores)
    A = softmax(scores)
    return A @ V, A


def autoatencion(X, Wq, Wk, Wv, mascara=False):
    """Self-attention: queries, keys and values are all projections of the same tokens X.

    X is (n, d). Q = X Wq and K = X Wk are (n, d_k), V = X Wv is (n, d_v): each token asks (query),
    advertises what it holds (key) and carries content (value) through separate learned matrices, so
    "what I look for" and "what I offer" can differ. Returns (output, A) with A (n, n) and output (n, d_v).
    Permuting the rows of X permutes the output the same way: attention alone has no notion of order.
    """
    X = np.asarray(X, dtype=float)
    return atencion(X @ Wq, X @ Wk, X @ Wv, mascara=mascara)


def multicabeza(X, cabezas, Wo, mascara=False):
    """Multi-head attention over the heads [(Wq, Wk, Wv), ...]; returns the output projected by Wo.

    Each head is a self-attention with its own weights (and its own d_k), so different heads can attend to
    different relations between the same tokens. The heads' outputs, each (n, d_v_h), are concatenated
    side by side in list order into (n, sum of d_v_h), and Wo mixes them back into one representation.
    The heads arrive already split: the caller decides how each one slices the model dimension.
    """
    salidas = [autoatencion(X, Wq, Wk, Wv, mascara=mascara)[0] for Wq, Wk, Wv in cabezas]
    return np.concatenate(salidas, axis=-1) @ Wo


def layer_norm(x, eps=1e-5):
    """Normalize each row to mean 0 and variance 1.

    Each token (row) is normalized on its own, over its features (last axis):
    (x - mean) / sqrt(var + eps), with the population variance (divide by d, not d - 1). This keeps the
    scale of the activations stable from layer to layer, whatever the sequence length or the other tokens.
    eps avoids dividing by zero on a constant row. Shifting or scaling a row leaves the result unchanged,
    up to the small effect of eps. No learned gain or bias (gamma, beta): the tests' signature has none.
    """
    x = np.asarray(x, dtype=float)
    media = x.mean(axis=-1, keepdims=True)
    varianza = x.var(axis=-1, keepdims=True)
    return (x - media) / np.sqrt(varianza + eps)
