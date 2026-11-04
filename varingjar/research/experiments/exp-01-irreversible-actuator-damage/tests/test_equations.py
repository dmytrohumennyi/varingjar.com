import sys
from pathlib import Path
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from model import LPVPlant, PlantParameters
from resources import ResourceModel, DegradationParameters
from integrity import (
    IntegrityParameters,
    structural_survivability,
    parametric_integrity,
    functional_integrity,
    classify_regime,
)


def test_lpv_plant_equation():
    p = PlantParameters(A=0.9, B=1.0, E=1.0)
    plant = LPVPlant(p, x0=0.2)
    rho = np.array([1.0, 0.5])
    u = np.array([-0.1, -0.2])
    xi = 0.05

    expected = 0.9 * 0.2 + ((1.0 / 2.0) * rho) @ u + 1.0 * xi
    actual = plant.step(u=u, rho=rho, xi=xi)
    assert abs(actual - expected) < 1e-12


def test_irreversible_damage_is_eta_D_term():
    resources = ResourceModel(DegradationParameters(), np.array([1.0, 0.83]))
    D = resources.destroy_irreversibly(1, regime="K")
    assert abs(D - 0.83 / 1.5) < 1e-12
    assert resources.rho[1] == 0.0

    for _ in range(100):
        resources.step_degradation("SK", 0.01)
        assert resources.rho[1] == 0.0


def test_integrity_equations():
    rho = np.array([0.8, 0.4])
    e = 0.7
    beta = 0.5

    S = structural_survivability(rho)
    P = parametric_integrity(e, beta)
    F = functional_integrity(S, P)

    assert abs(S - 0.6) < 1e-12
    assert abs(P - math.exp(-0.5 * 0.7)) < 1e-12
    assert abs(F - S * P) < 1e-12


def test_regime_thresholds():
    cfg = IntegrityParameters()
    assert classify_regime(0.80, cfg) == "N"
    assert classify_regime(0.79, cfg) == "K"
    assert classify_regime(0.30, cfg) == "K"
    assert classify_regime(0.29, cfg) == "SK"
