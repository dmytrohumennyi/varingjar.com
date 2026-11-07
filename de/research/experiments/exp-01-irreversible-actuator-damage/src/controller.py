from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ControllerGains:
    """
    Reference regime-dependent gains:
        K_N  = 0.8
        K_K  = 0.5
        K_SK = 0.2
    """
    K_N: float = 0.8
    K_K: float = 0.5
    K_SK: float = 0.2

    def for_regime(self, regime: str) -> float:
        return {
            "N": self.K_N,
            "K": self.K_K,
            "SK": self.K_SK,
        }[regime]


class TwoActuatorController:
    def __init__(self, gains: ControllerGains):
        self.gains = gains

    def command(self, x_hat: float, regime: str, adaptive: bool) -> tuple[float, np.ndarray]:
        """
        Eq. (11):
            u_k = -K_s * x_hat_k

        For the baseline experiment adaptive=False:
        K_N remains fixed even after the failure.

        The scalar command is split equally between two physical actuator
        channels. The plant's B_d(rho) determines how much of each command
        reaches the plant.
        """
        K = self.gains.for_regime(regime) if adaptive else self.gains.K_N
        u_cmd = -K * float(x_hat)
        u_channels = np.array([u_cmd / 2.0, u_cmd / 2.0], dtype=float)
        return float(u_cmd), u_channels
