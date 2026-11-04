from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class PlantParameters:
    """
    Reference scalar plant from the mathematical framework:
        x[k+1] = A*x[k] + B_d(rho[k])*u[k] + E*xi[k]

    A=0.9 and B=1.0 are the values used in the reference scalar model.

    For EXP-01 we specialize the general LPV input matrix to two parallel
    actuator channels:
        B_d(rho) = (B/2) * [rho_1, rho_2]

    This is an explicit experiment specialization of the general
    B_d(rho) term, not a new state equation.
    """
    A: float = 0.9
    B: float = 1.0
    E: float = 1.0


class LPVPlant:
    def __init__(self, params: PlantParameters, x0: float):
        self.p = params
        self.x = float(x0)

    def input_matrix(self, rho: np.ndarray) -> np.ndarray:
        rho = np.asarray(rho, dtype=float)
        if rho.shape != (2,):
            raise ValueError("EXP-01 expects exactly two actuator resources.")
        return (self.p.B / 2.0) * rho

    def step(self, u: np.ndarray, rho: np.ndarray, xi: float) -> float:
        """
        Implements:
            x[k+1] = A_d(rho_k)x[k] + B_d(rho_k)u[k] + E_d(rho_k)xi[k]

        EXP-01 uses constant A and E, while B_d depends on resource health.
        """
        u = np.asarray(u, dtype=float)
        Bd = self.input_matrix(rho)
        x_next = self.p.A * self.x + float(Bd @ u) + self.p.E * float(xi)
        self.x = float(x_next)
        return self.x
