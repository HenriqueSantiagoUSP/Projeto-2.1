"""
Biblioteca de Mínimos Quadrados usando NumPy.

Calcula os coeficientes de uma função polinomial que melhor se ajusta
aos dados fornecidos, minimizando a soma dos quadrados dos resíduos.
"""

import numpy as np


def minimos_quadrados(x, y, grau=1):
    """
    Calcula os coeficientes da função polinomial de grau `grau`
    que melhor aproxima os dados (x, y) pelo método dos mínimos quadrados.

    Para grau=1 (reta): f(x) = a*x + b
        Resolve o sistema normal:  (A^T A) c = A^T y
        onde A é a matriz de Vandermonde.

    Parâmetros:
        x     : array-like, valores independentes
        y     : array-like, valores dependentes
        grau  : int, grau do polinômio (padrão: 1 para reta)

    Retorna:
        coefs : np.ndarray, coeficientes [a_n, a_{n-1}, ..., a_1, a_0]
                Para grau=1: [a, b] onde f(x) = a*x + b
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if len(x) != len(y):
        raise ValueError("x e y devem ter o mesmo tamanho")

    if len(x) < grau + 1:
        raise ValueError(f"São necessários pelo menos {grau + 1} pontos para grau {grau}")

    # monta a matriz de Vandermonde: cada coluna é x^k, k = grau, grau-1, ..., 0
    # A[i, j] = x[i]^(grau - j)
    A = np.vander(x, N=grau + 1, increasing=False)

    # sistema normal: (A^T A) c = A^T y
    ATA = A.T @ A
    ATy = A.T @ y

    # resolve o sistema
    coefs = np.linalg.solve(ATA, ATy)

    return coefs


def avaliar(coefs, x):
    """
    Avalia o polinômio com coeficientes `coefs` nos pontos `x`.

    Parâmetros:
        coefs : array-like, coeficientes [a_n, ..., a_1, a_0]
        x     : array-like, pontos de avaliação

    Retorna:
        y : np.ndarray, valores f(x)
    """
    return np.polyval(coefs, x)


def residuos(coefs, x, y):
    """
    Calcula os resíduos (y - f(x)) e métricas de qualidade do ajuste.

    Retorna:
        dict com:
            - residuos: array dos resíduos
            - SSE: soma dos quadrados dos resíduos
            - SST: soma dos quadrados totais
            - R2: coeficiente de determinação
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    y_pred = avaliar(coefs, x)
    res = y - y_pred

    SSE = np.sum(res ** 2)
    SST = np.sum((y - np.mean(y)) ** 2)
    R2 = 1 - SSE / SST if SST > 0 else 0.0

    return {
        "residuos": res,
        "SSE": SSE,
        "SST": SST,
        "R2": R2,
    }


def formatar_equacao(coefs, var="x"):
    """Retorna string legível da equação do polinômio."""
    grau = len(coefs) - 1
    termos = []
    for i, c in enumerate(coefs):
        exp = grau - i
        if exp == 0:
            termos.append(f"{c:+.4f}")
        elif exp == 1:
            termos.append(f"{c:+.4f}{var}")
        else:
            termos.append(f"{c:+.4f}{var}^{exp}")
    eq = " ".join(termos)
    # limpar o + inicial
    if eq.startswith("+"):
        eq = eq[1:]
    return f"f({var}) = {eq.strip()}"
