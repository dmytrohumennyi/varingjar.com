from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class DegradationParameters:
    """
    Reference regime-dependent degradation rates and damage coefficients.

    lambda_N  = 0.01
    lambda_K  = 0.05
    lambda_SK = 0.10

    EXP-01 is irreversible:
        u_rep = 0
    """
    lambda_N: float = 0.01
    lambda_K: float = 0.05
    lambda_SK: float = 0.10

    eta_N: float = 1.0
    eta_K: float = 1.5
    eta_SK: float = 2.0

    def degradation_rate(self, regime: str) -> float:
        return {
            "N": self.lambda_N,
            "K": self.lambda_K,
            "SK": self.lambda_SK,
        }[regime]

    def damage_sensitivity(self, regime: str) -> float:
        return {
            "N": self.eta_N,
            "K": self.eta_K,
            "SK": self.eta_SK,
        }[regime]


class ResourceModel:
    def __init__(self, params: DegradationParameters, rho0: np.ndarray):
        self.p = params
        self.rho = np.clip(np.asarray(rho0, dtype=float), 0.0, 1.0)

    def apply_damage_event(self, resource_id: int, D: float, regime: str) -> None:
        """
        Damage term from:
            rho[i,k+1] =
                rho[i,k]
                - lambda_i(s_k)*dt
                - eta_i*D[i,k]
                + mu_i*u_rep[i,k]

        For an irreversible experiment u_rep = 0.

        This method applies only the instantaneous -eta*D term.
        """
        eta = self.p.damage_sensitivity(regime)
        self.rho[resource_id] = np.clip(
            self.rho[resource_id] - eta * float(D),
            0.0,
            1.0,
        )

    def destroy_irreversibly(self, resource_id: int, regime: str) -> float:
        """
        Compute the damage impulse D needed to reduce the selected resource
        exactly to rho=0 under the theory's -eta*D damage term.

        Returns D for logging.
        """
        eta = self.p.damage_sensitivity(regime)
        D = float(self.rho[resource_id] / eta)
        self.apply_damage_event(resource_id, D, regime)
        return D

    def step_degradation(self, regime: str, dt: float) -> np.ndarray:
        """
        Continuous resource consumption:
            rho[k+1] = rho[k] - lambda(s_k)*dt

        No repair/compensation term is present in EXP-01.
        """
        lam = self.p.degradation_rate(regime)
        self.rho = np.clip(self.rho - lam * float(dt), 0.0, 1.0)
        return self.rho.copy()
