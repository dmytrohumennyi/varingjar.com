from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from model import CONFIGS, SAFE_STOP_ID, TRANSITION_GRAPH
from equations import (
    survivability,
    mission_functionality,
    closed_loop_factor,
    lyapunov_multiplier,
    admissible,
)


@dataclass(frozen=True)
class Candidate:
    config_id: str
    S: float
    Phi: float
    gamma: float
    delta_v_factor: float
    admissible: bool
    selected: bool = False


def evaluate_candidate(
    config_id: str,
    rho: np.ndarray,
    A: float,
    phi_min: float,
) -> Candidate:
    c = CONFIGS[config_id]

    return Candidate(
        config_id=config_id,
        S=survivability(c, rho),
        Phi=mission_functionality(c, rho),
        gamma=closed_loop_factor(c, rho, A),
        delta_v_factor=lyapunov_multiplier(c, rho, A),
        admissible=admissible(c, rho, A, phi_min),
    )


def select_configuration(
    current_id: str,
    rho: np.ndarray,
    A: float,
    phi_min: float,
):
    """
    Direct EXP-03 implementation of the article-level decision:

        c* in argmax_c S(c,rho)

    subject to:

        Phi(c,rho) >= Phi_min
        stability(c,rho)

    No transition score, risk weight, time penalty, or hidden ranking
    coefficient is used.

    Only graph successors of the current configuration are evaluated.
    The graph encodes irreversible structural degradation; no repair or
    upward-recovery transition exists in EXP-03. SAFE_STOP is evaluated
    only as a fallback when no mission-preserving successor is admissible.
    """
    successors = TRANSITION_GRAPH[current_id]
    mission_successors = [cid for cid in successors if cid != SAFE_STOP_ID]

    candidates = [
        evaluate_candidate(cid, rho, A, phi_min)
        for cid in mission_successors
    ]

    feasible = [c for c in candidates if c.admissible]

    if feasible:
        winner = max(feasible, key=lambda c: c.S)
        selected = Candidate(
            config_id=winner.config_id,
            S=winner.S,
            Phi=winner.Phi,
            gamma=winner.gamma,
            delta_v_factor=winner.delta_v_factor,
            admissible=winner.admissible,
            selected=True,
        )
        return selected, candidates

    # Article-level fallback: SAFE_STOP when no admissible mission
    # configuration exists.
    if SAFE_STOP_ID not in successors:
        return None, candidates

    safe = evaluate_candidate(SAFE_STOP_ID, rho, A, phi_min)
    selected = Candidate(
        config_id=safe.config_id,
        S=safe.S,
        Phi=safe.Phi,
        gamma=safe.gamma,
        delta_v_factor=safe.delta_v_factor,
        admissible=False,
        selected=True,
    )
    return selected, candidates
