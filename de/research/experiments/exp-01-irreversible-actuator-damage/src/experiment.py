from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import csv
import json
import numpy as np

from model import LPVPlant, PlantParameters
from resources import ResourceModel, DegradationParameters
from integrity import (
    IntegrityParameters,
    structural_survivability,
    parametric_integrity,
    functional_integrity,
    classify_regime,
)
from controller import ControllerGains, TwoActuatorController


@dataclass(frozen=True)
class ExperimentConfig:
    dt: float = 0.01
    t_end: float = 16.0
    fault_time: float = 5.0

    # reference scalar plant initial condition
    x0: float = 0.20
    rho0_1: float = 1.0
    rho0_2: float = 1.0

    # deterministic disturbance injection for EXP-01
    xi_nominal: float = 0.05
    xi_post_fault: float = 0.40

    # baseline = fixed nominal gain; supervisor experiment will set True
    adaptive_control: bool = False

    # deterministic by construction; kept in manifest for reproducibility
    seed: int = 26082026


def run(config: ExperimentConfig) -> list[dict]:
    np.random.seed(config.seed)

    plant = LPVPlant(PlantParameters(), x0=config.x0)
    resources = ResourceModel(
        DegradationParameters(),
        rho0=np.array([config.rho0_1, config.rho0_2], dtype=float),
    )
    integrity_cfg = IntegrityParameters()
    controller = TwoActuatorController(ControllerGains())

    rows: list[dict] = []
    fault_applied = False

    times = np.arange(0.0, config.t_end + config.dt / 2.0, config.dt)

    for k, t in enumerate(times):
        # 1. Evaluate current integrity before the external event.
        error_pre = plant.x
        S_pre = structural_survivability(resources.rho)
        P_pre = parametric_integrity(error_pre, integrity_cfg.beta)
        F_pre = functional_integrity(S_pre, P_pre)
        regime_pre = classify_regime(F_pre, integrity_cfg)

        # 2. External, irreversible structural damage.
        D2 = 0.0
        if (not fault_applied) and t >= config.fault_time:
            # Uses the theory's -eta*D damage term to make rho_2 = 0.
            D2 = resources.destroy_irreversibly(resource_id=1, regime=regime_pre)
            fault_applied = True

        # 3. Recompute integrity after the damage event.
        error = plant.x
        S = structural_survivability(resources.rho)
        P = parametric_integrity(error, integrity_cfg.beta)
        F = functional_integrity(S, P)
        regime = classify_regime(F, integrity_cfg)

        # 4. Baseline control: Eq. (11) with K_N fixed.
        #    The regime is still computed and logged; it also drives
        #    the degradation law, as in Eq. (4).
        u_cmd, u_channels = controller.command(
            x_hat=plant.x,
            regime=regime,
            adaptive=config.adaptive_control,
        )

        # 5. Disturbance injection.
        xi = config.xi_nominal if t < config.fault_time else config.xi_post_fault

        # 6. LPV plant transition Eq. (1), specialized to scalar Eq. (3).
        x_k = plant.x
        rho_k = resources.rho.copy()
        Bd = plant.input_matrix(rho_k)
        x_next = plant.step(u_channels, rho_k, xi)

        # 7. Resource degradation Eq. (4), with u_rep = 0.
        rho_next = resources.step_degradation(regime=regime, dt=config.dt)

        rows.append({
            "k": k,
            "time_s": float(t),
            "x_k": float(x_k),
            "x_k1": float(x_next),
            "rho1_k": float(rho_k[0]),
            "rho2_k": float(rho_k[1]),
            "rho1_k1": float(rho_next[0]),
            "rho2_k1": float(rho_next[1]),
            "B1_eff": float(Bd[0]),
            "B2_eff": float(Bd[1]),
            "damage_D2": float(D2),
            "S_k": float(S),
            "P_k": float(P),
            "F_k": float(F),
            "regime": regime,
            "u_cmd": float(u_cmd),
            "u1_cmd": float(u_channels[0]),
            "u2_cmd": float(u_channels[1]),
            "xi_k": float(xi),
        })

    return rows


def save_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    cfg = ExperimentConfig()
    rows = run(cfg)

    data_path = project_root / "data" / "exp01_baseline.csv"
    save_csv(rows, data_path)

    manifest = {
        "experiment": "EXP-01",
        "purpose": "baseline with irreversible actuator #2 destruction",
        "config": asdict(cfg),
        "theory_mapping": {
            "plant": "Eq. (1), scalar reference Eq. (3)",
            "resource_degradation": "Eq. (4), u_rep = 0",
            "S": "Eq. (5)",
            "P": "Eq. (6)",
            "F": "Eq. (7)",
            "regime": "Eqs. (8)-(10)",
            "control": "Eq. (11), baseline fixes K=K_N",
        },
        "experiment_specialization": {
            "B_d_rho": "(B/2) * [rho1, rho2]",
            "fault": "damage impulse D2 computed so -eta*D2 makes rho2 exactly zero",
            "disturbance": {
                "before_fault": cfg.xi_nominal,
                "after_fault": cfg.xi_post_fault,
            },
        },
    }
    (project_root / "data" / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    # Key events
    fault_row = next(r for r in rows if r["damage_D2"] > 0.0)
    first_K = next((r for r in rows if r["regime"] == "K"), None)
    first_SK = next((r for r in rows if r["regime"] == "SK"), None)
    first_F0 = next((r for r in rows if r["F_k"] <= 0.0), None)

    print("EXP-01 / mathematical baseline")
    print(f"fault:  t={fault_row['time_s']:.2f}s, rho2={fault_row['rho2_k']:.3f}")
    if first_K:
        print(f"K:      t={first_K['time_s']:.2f}s, F={first_K['F_k']:.6f}")
    if first_SK:
        print(f"SK:     t={first_SK['time_s']:.2f}s, F={first_SK['F_k']:.6f}")
    if first_F0:
        print(f"F=0:    t={first_F0['time_s']:.2f}s")
    else:
        print("F=0:    not reached in simulation horizon")
    print(f"CSV:    {data_path}")


if __name__ == "__main__":
    main()
