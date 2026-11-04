from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class IntegrityParameters:
    beta: float = 0.5
    F_N: float = 0.8
    F_K: float = 0.3


def structural_survivability(rho: np.ndarray) -> float:
    """
    Eq. (5):
        S_k = (1/r) * sum_i rho_i,k
    """
    rho = np.asarray(rho, dtype=float)
    return float(np.mean(rho))


def parametric_integrity(error: float, beta: float = 0.5) -> float:
    """
    Eq. (6):
        P_k = exp(-beta * |e_k|)
    """
    return float(math.exp(-float(beta) * abs(float(error))))


def functional_integrity(S: float, P: float) -> float:
    """
    Eq. (7):
        F_k = S_k * P_k
    """
    return float(S * P)


def classify_regime(F: float, params: IntegrityParameters) -> str:
    """
    Eqs. (8)-(10):
        N  if F >= 0.8
        K  if 0.3 <= F < 0.8
        SK if F < 0.3
    """
    if F >= params.F_N:
        return "N"
    if F >= params.F_K:
        return "K"
    return "SK"
