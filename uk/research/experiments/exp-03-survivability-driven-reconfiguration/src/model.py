from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import numpy as np


RESOURCE_NAMES = (
    "motor_a",
    "motor_b",
    "encoder",
    "imu",
    "can1",
    "can2",
)

FUNCTION_NAMES = (
    "stabilization",
    "tracking",
    "telemetry",
    "diagnostics",
)

# Mission/function weights. Sum = 1 exactly.
WEIGHTS = np.array([0.45, 0.30, 0.15, 0.10], dtype=float)

# A function is considered realizable when its continuous resource
# capability reaches this declared threshold.
FUNCTION_THRESHOLDS = np.array([0.50, 0.50, 0.50, 0.50], dtype=float)

# Declared minimum mission functionality for EXP-03.
PHI_MIN = 0.65


@dataclass(frozen=True)
class Configuration:
    id: str
    label: str
    actuator: Optional[int]
    sensor: int
    network: int
    activation: np.ndarray
    gain: float
    safe_stop: bool = False


# All mission-preserving configurations use exactly the same K.
# Therefore EXP-03 cannot obtain its result from gain scheduling.
CONFIGS = {
    "c0": Configuration(
        id="c0",
        label="NOMINAL",
        actuator=0, sensor=2, network=4,
        activation=np.array([1, 1, 1, 1], dtype=float),
        gain=0.8,
    ),
    "c1": Configuration(
        id="c1",
        label="BACKUP_ACTUATOR",
        actuator=1, sensor=2, network=4,
        activation=np.array([1, 1, 1, 1], dtype=float),
        gain=0.8,
    ),
    "c2": Configuration(
        id="c2",
        label="BACKUP_SENSOR",
        actuator=0, sensor=3, network=4,
        activation=np.array([1, 1, 1, 1], dtype=float),
        gain=0.8,
    ),
    "c3": Configuration(
        id="c3",
        label="LIMP_HOME",
        actuator=1, sensor=3, network=5,
        activation=np.array([1, 0, 1, 1], dtype=float),
        gain=0.8,
    ),
    "c4": Configuration(
        id="c4",
        label="SAFE_STOP",
        actuator=None, sensor=3, network=5,
        activation=np.array([0, 0, 0, 1], dtype=float),
        gain=0.0,
        safe_stop=True,
    ),
}

MISSION_CONFIG_IDS = ("c0", "c1", "c2", "c3")
SAFE_STOP_ID = "c4"

# Directed reconfiguration graph for irreversible degradation.
# Edges only move to an alternative or lower-capability structural state;
# no recovery edge is allowed because EXP-03 contains no repair.
TRANSITION_GRAPH = {
    "c0": ("c1", "c2", "c3", "c4"),
    "c1": ("c3", "c4"),
    "c2": ("c3", "c4"),
    "c3": ("c4",),
    "c4": (),
}
