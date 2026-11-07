from __future__ import annotations

import numpy as np

from model import (
    Configuration,
    WEIGHTS,
    FUNCTION_THRESHOLDS,
    PHI_MIN,
)


def damage_update(rho_i: float, damage: float, eta: float = 1.0) -> float:
    """
    Irreversible EXP-03 specialization of the resource equation:

        rho_i^+ = sat_[0,1](rho_i^- - eta_i D_i)

    No repair term is present.
    """
    return float(np.clip(float(rho_i) - float(eta) * float(damage), 0.0, 1.0))


def resource_groups(config: Configuration, rho: np.ndarray) -> tuple[float, float, float]:
    rho = np.asarray(rho, dtype=float)

    g_a = 0.0 if config.actuator is None else float(rho[config.actuator])
    g_s = float(rho[config.sensor])
    g_n = float(rho[config.network])

    return g_a, g_s, g_n


def capability_vector(config: Configuration, rho: np.ndarray) -> np.ndarray:
    """
    Explicit EXP-03 resource-to-function specialization:

        f1 = g_A g_S
        f2 = g_A g_S g_N
        f3 = g_N
        f4 = g_S g_N
    """
    g_a, g_s, g_n = resource_groups(config, rho)

    return np.array([
        g_a * g_s,
        g_a * g_s * g_n,
        g_n,
        g_s * g_n,
    ], dtype=float)


def realized_functions(config: Configuration, rho: np.ndarray) -> np.ndarray:
    """
    phi_j(c,rho) =
        delta_j(c) * 1[f_j(c,rho) >= theta_j]
    """
    f = capability_vector(config, rho)
    requested = np.asarray(config.activation, dtype=float) > 0.5
    capable = f >= FUNCTION_THRESHOLDS
    return (requested & capable).astype(float)


def survivability(config: Configuration, rho: np.ndarray) -> float:
    """
        S(c,rho) = sum_j w_j f_j(c,rho) delta_j(c)
    """
    f = capability_vector(config, rho)
    return float(WEIGHTS @ (f * config.activation))


def mission_functionality(config: Configuration, rho: np.ndarray) -> float:
    """
        Phi(c,rho) = sum_j w_j phi_j(c,rho)
    """
    phi = realized_functions(config, rho)
    return float(WEIGHTS @ phi)


def input_effectiveness(config: Configuration, rho: np.ndarray) -> float:
    return 0.0 if config.actuator is None else float(rho[config.actuator])


def closed_loop_factor(
    config: Configuration,
    rho: np.ndarray,
    A: float,
) -> float:
    """
    Homogeneous scalar closed-loop dynamics:

        x_{k+1} = (A - bK) x_k

    Therefore:

        gamma(c,rho) = |A - b(c,rho)K(c)|

    gamma < 1 is the exact scalar discrete-time asymptotic stability
    condition for the homogeneous part.
    """
    b = input_effectiveness(config, rho)
    return abs(float(A) - b * float(config.gain))


def lyapunov_multiplier(
    config: Configuration,
    rho: np.ndarray,
    A: float,
) -> float:
    """
    For V(e)=e^2 and e_{k+1}=a_cl e_k:

        Delta V = (a_cl^2 - 1)e_k^2

    This returns a_cl^2 - 1.
    A negative value is equivalent to gamma < 1.
    """
    gamma = closed_loop_factor(config, rho, A)
    return gamma * gamma - 1.0


def admissible(
    config: Configuration,
    rho: np.ndarray,
    A: float,
    phi_min: float = PHI_MIN,
) -> bool:
    if config.safe_stop:
        return False

    return bool(
        mission_functionality(config, rho) >= float(phi_min)
        and closed_loop_factor(config, rho, A) < 1.0
    )


def plant_step(
    x_k: float,
    u_k: float,
    config: Configuration,
    rho: np.ndarray,
    A: float,
    xi_k: float,
) -> float:
    """
        x_{k+1} = A x_k + b(c,rho_k) u_k + xi_k
    """
    b = input_effectiveness(config, rho)
    return float(float(A) * float(x_k) + b * float(u_k) + float(xi_k))
