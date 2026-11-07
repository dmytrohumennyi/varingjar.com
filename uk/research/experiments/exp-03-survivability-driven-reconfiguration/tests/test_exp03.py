import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from model import CONFIGS, PHI_MIN
from equations import (
    damage_update,
    capability_vector,
    survivability,
    mission_functionality,
    closed_loop_factor,
    lyapunov_multiplier,
    plant_step,
)
from selector import select_configuration
from experiment import (
    ExperimentConfig,
    simulate_supervised,
    simulate_baseline,
)


def test_damage_equation_complete_destruction():
    rho_minus = 1.0
    D = rho_minus
    assert damage_update(rho_minus, D, eta=1.0) == 0.0


def test_first_fault_selector_is_argmax_S():
    rho = np.ones(6)
    rho[0] = 0.0

    winner, candidates = select_configuration(
        "c0", rho, A=0.9, phi_min=PHI_MIN
    )

    feasible = [c for c in candidates if c.admissible]

    assert winner.config_id == "c1"
    assert winner.S == max(c.S for c in feasible)


def test_second_fault_selector_is_argmax_S():
    rho = np.ones(6)
    rho[0] = 0.0
    rho[2] = 0.0

    winner, candidates = select_configuration(
        "c1", rho, A=0.9, phi_min=PHI_MIN
    )

    feasible = [c for c in candidates if c.admissible]

    assert winner.config_id == "c3"
    assert winner.S == max(c.S for c in feasible)


def test_exact_expected_metrics_first_fault():
    rho = np.ones(6)
    rho[0] = 0.0

    assert abs(survivability(CONFIGS["c1"], rho) - 1.0) < 1e-12
    assert abs(mission_functionality(CONFIGS["c1"], rho) - 1.0) < 1e-12
    assert abs(survivability(CONFIGS["c3"], rho) - 0.70) < 1e-12
    assert abs(mission_functionality(CONFIGS["c3"], rho) - 0.70) < 1e-12


def test_exact_expected_metrics_second_fault():
    rho = np.ones(6)
    rho[0] = 0.0
    rho[2] = 0.0

    assert abs(survivability(CONFIGS["c3"], rho) - 0.70) < 1e-12
    assert abs(mission_functionality(CONFIGS["c3"], rho) - 0.70) < 1e-12


def test_scalar_stability_and_lyapunov_equivalence():
    rho = np.ones(6)

    gamma = closed_loop_factor(CONFIGS["c1"], rho, A=0.9)
    dv = lyapunov_multiplier(CONFIGS["c1"], rho, A=0.9)

    assert gamma < 1.0
    assert dv < 0.0
    assert abs(dv - (gamma**2 - 1.0)) < 1e-12


def test_plant_step_equation_exact():
    rho = np.ones(6)
    x = 0.2
    u = -0.8 * x
    actual = plant_step(
        x, u, CONFIGS["c0"], rho, A=0.9, xi_k=0.02
    )
    expected = 0.9 * x + 1.0 * u + 0.02
    assert abs(actual - expected) < 1e-12


def test_destroyed_resources_never_recover():
    rows, _, _, _ = simulate_supervised(ExperimentConfig())

    for row in rows:
        if row["time_s"] >= 5.0:
            assert row["rho_motor_a"] == 0.0

        if row["time_s"] >= 12.0:
            assert row["rho_encoder"] == 0.0


def test_verified_configuration_path():
    rows, _, _, _ = simulate_supervised(ExperimentConfig())

    seen = []
    for row in rows:
        if not seen or row["config"] != seen[-1]:
            seen.append(row["config"])

    assert seen == ["c0", "c1", "c3"]


def test_verify_is_real_and_passes():
    _, _, _, verification = simulate_supervised(ExperimentConfig())

    assert len(verification) == 2

    for row in verification:
        assert row["pass"] == 1
        assert row["Phi"] >= PHI_MIN
        assert row["gamma"] < 1.0


def test_matched_resource_histories():
    supervised, _, _, _ = simulate_supervised(ExperimentConfig())
    baseline, _ = simulate_baseline(ExperimentConfig())

    keys = [
        "rho_motor_a", "rho_motor_b", "rho_encoder",
        "rho_imu", "rho_can1", "rho_can2"
    ]

    for s, b in zip(supervised, baseline):
        assert s["time_s"] == b["time_s"]

        for key in keys:
            assert s[key] == b[key]


def test_frozen_baseline_invalid_after_first_fault():
    baseline, _ = simulate_baseline(ExperimentConfig())

    for row in baseline:
        if row["time_s"] >= 5.0:
            assert row["Phi"] < PHI_MIN


def test_same_gain_all_mission_configurations():
    gains = [
        CONFIGS[cid].gain
        for cid in ("c0", "c1", "c2", "c3")
    ]

    assert gains == [0.8, 0.8, 0.8, 0.8]
