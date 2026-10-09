"""Part 4: an attention layer in NumPy, checked by atencion/test_atencion.py.

Conventions (the graders' tests fix them):
- Row vectors: X is (n, d), one token per row, and every projection is X @ W with W of shape (d, d_k).
- Every normalization runs over the last axis, i.e. along each row.

Run: python3 atencion/test_atencion.py atencion.py
"""
import numpy as np


def softmax(M):
    """Turn each row of scores into probabilities: non-negative and summing to 1 (last axis)."""
    raise NotImplementedError


def atencion(Q, K, V, mascara=False):
    """Scaled dot-product attention; returns (output, A) with A = softmax(Q K^T / sqrt(d_k))."""
    raise NotImplementedError


def autoatencion(X, Wq, Wk, Wv, mascara=False):
    """Self-attention: queries, keys and values are all projections of the same tokens X."""
    raise NotImplementedError


def multicabeza(X, cabezas, Wo, mascara=False):
    """Multi-head attention over the heads [(Wq, Wk, Wv), ...]; returns the output projected by Wo."""
    raise NotImplementedError


def layer_norm(x, eps=1e-5):
    """Normalize each row to mean 0 and variance 1."""
    raise NotImplementedError
