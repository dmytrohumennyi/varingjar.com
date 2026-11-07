from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import csv
import json
import numpy as np

from model import (
    CONFIGS,
    RESOURCE_NAMES,
    WEIGHTS,
    FUNCTION_THRESHOLDS,
    PHI_MIN,
    TRANSITION_GRAPH,
)
from equations import (
    damage_update,
    capability_vector,
    realized_functions,
    survivability,
    mission_functionality,
    input_effectiveness,
    closed_loop_factor,
    lyapunov_multiplier,
    admissible,
    plant_step,
)
from selector import select_configuration


@dataclass(frozen=True)
class ExperimentConfig:
    dt: float = 0.01
    t_end: float = 16.0

    fault_motor_time: float = 5.0
    fault_encoder_time: float = 12.0

    A: float = 0.9
    x0: float = 0.20
    disturbance: float = 0.02

    phi_min: float = PHI_MIN


# Clean initial condition: every resource is healthy.
# The only degradation mechanisms in EXP-03 are the two declared
# irreversible damage events.
RHO0 = np.ones(6, dtype=float)


def write_csv(rows, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def apply_declared_fault(
    rho: np.ndarray,
    resource_index: int,
) -> tuple[np.ndarray, float]:
    """
    Complete irreversible destruction through the damage equation.

    D_i is selected as rho_i^- with eta_i = 1, therefore:
        rho_i^+ = sat(rho_i^- - D_i) = 0.
    """
    rho = rho.copy()
    rho_before = float(rho[resource_index])
    damage = rho_before
    rho[resource_index] = damage_update(
        rho_i=rho_before,
        damage=damage,
        eta=1.0,
    )
    return rho, damage


class ReconfigurationFSM:
    """
    One stage per L2 supervisor cycle:

        ANALYZE -> SELECT -> APPLY -> VERIFY

    VERIFY is an actual recomputation of Phi and the stability condition.
    """
    def __init__(self):
        self.phase = "IDLE"
        self.target = None
        self.origin = None
        self.last_selection = None

    def trigger(self, current_id: str):
        if self.phase != "IDLE":
            raise RuntimeError("Cannot trigger non-idle supervisor.")
        self.origin = current_id
        self.phase = "ANALYZE"

    def step(
        self,
        current_id: str,
        rho: np.ndarray,
        A: float,
        phi_min: float,
    ):
        action = ""
        selection = None
        verification = None

        if self.phase == "ANALYZE":
            action = "ANALYZE"
            self.phase = "SELECT"

        elif self.phase == "SELECT":
            selection, candidates = select_configuration(
                current_id=current_id,
                rho=rho,
                A=A,
                phi_min=phi_min,
            )
            self.last_selection = (selection, candidates)
            self.target = selection.config_id
            action = "SELECT"
            self.phase = "APPLY"

        elif self.phase == "APPLY":
            action = "APPLY"
            current_id = self.target
            self.phase = "VERIFY"

        elif self.phase == "VERIFY":
            action = "VERIFY"
            c = CONFIGS[current_id]

            if c.safe_stop:
                verification = {
                    "pass": True,
                    "reason": "SAFE_STOP_FALLBACK",
                    "Phi": mission_functionality(c, rho),
                    "gamma": closed_loop_factor(c, rho, A),
                }
            else:
                phi = mission_functionality(c, rho)
                gamma = closed_loop_factor(c, rho, A)
                ok = bool(phi >= phi_min and gamma < 1.0)
                verification = {
                    "pass": ok,
                    "reason": "ADMISSIBLE" if ok else "VERIFY_FAILED",
                    "Phi": phi,
                    "gamma": gamma,
                }

                if not ok:
                    current_id = "c4"

            self.phase = "IDLE"
            self.target = None
            self.origin = None

        return current_id, action, selection, verification


def log_state(
    k,
    t,
    branch,
    current_id,
    phase,
    event,
    x,
    x_next,
    u,
    xi,
    rho,
    A,
    phi_min,
):
    c = CONFIGS[current_id]
    f = capability_vector(c, rho)
    phi = realized_functions(c, rho)

    return {
        "k": k,
        "time_s": float(t),
        "branch": branch,
        "config": current_id,
        "phase": phase,
        "event": event,
        "x_k": float(x),
        "x_k1": float(x_next),
        "u_k": float(u),
        "xi_k": float(xi),

        "rho_motor_a": float(rho[0]),
        "rho_motor_b": float(rho[1]),
        "rho_encoder": float(rho[2]),
        "rho_imu": float(rho[3]),
        "rho_can1": float(rho[4]),
        "rho_can2": float(rho[5]),

        "f_stabilization": float(f[0]),
        "f_tracking": float(f[1]),
        "f_telemetry": float(f[2]),
        "f_diagnostics": float(f[3]),

        "phi_stabilization": float(phi[0]),
        "phi_tracking": float(phi[1]),
        "phi_telemetry": float(phi[2]),
        "phi_diagnostics": float(phi[3]),

        "S": float(survivability(c, rho)),
        "Phi": float(mission_functionality(c, rho)),
        "b_eff": float(input_effectiveness(c, rho)),
        "gamma": float(closed_loop_factor(c, rho, A)),
        "delta_v_factor": float(lyapunov_multiplier(c, rho, A)),
        "valid": int(admissible(c, rho, A, phi_min)),
    }


def simulate_supervised(cfg: ExperimentConfig):
    rho = RHO0.copy()
    current = "c0"
    x = float(cfg.x0)
    fsm = ReconfigurationFSM()

    rows = []
    decisions = []
    events = []
    verification_rows = []

    fault1_done = False
    fault2_done = False

    times = np.arange(0.0, cfg.t_end + cfg.dt / 2.0, cfg.dt)

    for k, t in enumerate(times):
        event_tokens = []

        if (not fault1_done) and t >= cfg.fault_motor_time:
            rho, D = apply_declared_fault(rho, 0)
            fault1_done = True
            event_tokens.append("MOTOR_A_DESTROYED")
            events.append({
                "time_s": float(t),
                "branch": "supervised",
                "event": "MOTOR_A_DESTROYED",
                "resource": "motor_a",
                "damage_D": D,
                "rho_after": float(rho[0]),
            })

        if (not fault2_done) and t >= cfg.fault_encoder_time:
            rho, D = apply_declared_fault(rho, 2)
            fault2_done = True
            event_tokens.append("ENCODER_DESTROYED")
            events.append({
                "time_s": float(t),
                "branch": "supervised",
                "event": "ENCODER_DESTROYED",
                "resource": "encoder",
                "damage_D": D,
                "rho_after": float(rho[2]),
            })

        c_before = CONFIGS[current]

        if (
            not c_before.safe_stop
            and not admissible(c_before, rho, cfg.A, cfg.phi_min)
            and fsm.phase == "IDLE"
        ):
            fsm.trigger(current)
            events.append({
                "time_s": float(t),
                "branch": "supervised",
                "event": f"INVALIDATE_{current}",
                "resource": "",
                "damage_D": "",
                "rho_after": "",
            })

        previous = current
        current, action, selection, verification = fsm.step(
            current_id=current,
            rho=rho,
            A=cfg.A,
            phi_min=cfg.phi_min,
        )

        if action:
            events.append({
                "time_s": float(t),
                "branch": "supervised",
                "event": (
                    f"{action}_{previous}_TO_{current}"
                    if action == "APPLY"
                    else f"{action}_{previous}"
                ),
                "resource": "",
                "damage_D": "",
                "rho_after": "",
            })

        if action == "SELECT":
            winner, candidates = fsm.last_selection
            for cand in candidates:
                decisions.append({
                    "time_s": float(t),
                    "current": previous,
                    "candidate": cand.config_id,
                    "S": cand.S,
                    "Phi": cand.Phi,
                    "gamma": cand.gamma,
                    "delta_v_factor": cand.delta_v_factor,
                    "admissible": int(cand.admissible),
                    "selected": int(cand.config_id == winner.config_id),
                })

            if winner.config_id == "c4":
                decisions.append({
                    "time_s": float(t),
                    "current": previous,
                    "candidate": "c4",
                    "S": winner.S,
                    "Phi": winner.Phi,
                    "gamma": winner.gamma,
                    "delta_v_factor": winner.delta_v_factor,
                    "admissible": 0,
                    "selected": 1,
                })

        if action == "VERIFY":
            verification_rows.append({
                "time_s": float(t),
                "config": current,
                "pass": int(bool(verification["pass"])),
                "reason": verification["reason"],
                "Phi": float(verification["Phi"]),
                "gamma": float(verification["gamma"]),
            })

        c = CONFIGS[current]

        # Control is held at zero during ANALYZE/SELECT/APPLY.
        # Once APPLY has completed, the new configuration is active and
        # VERIFY evaluates its actual post-apply state.
        hold = fsm.phase in ("SELECT", "APPLY")
        u = 0.0 if hold or c.safe_stop else -c.gain * x

        x_next = plant_step(
            x_k=x,
            u_k=u,
            config=c,
            rho=rho,
            A=cfg.A,
            xi_k=cfg.disturbance,
        )

        rows.append(log_state(
            k=k,
            t=t,
            branch="supervised",
            current_id=current,
            phase=fsm.phase,
            event="|".join(event_tokens),
            x=x,
            x_next=x_next,
            u=u,
            xi=cfg.disturbance,
            rho=rho,
            A=cfg.A,
            phi_min=cfg.phi_min,
        ))

        x = float(x_next)

    return rows, decisions, events, verification_rows


def simulate_baseline(cfg: ExperimentConfig):
    """
    Matched control branch.

    Everything is identical except:
        c(t) == c0
        no reconfiguration FSM is executed.
    """
    rho = RHO0.copy()
    current = "c0"
    x = float(cfg.x0)

    rows = []
    events = []

    fault1_done = False
    fault2_done = False

    times = np.arange(0.0, cfg.t_end + cfg.dt / 2.0, cfg.dt)

    for k, t in enumerate(times):
        event_tokens = []

        if (not fault1_done) and t >= cfg.fault_motor_time:
            rho, D = apply_declared_fault(rho, 0)
            fault1_done = True
            event_tokens.append("MOTOR_A_DESTROYED")
            events.append({
                "time_s": float(t),
                "branch": "baseline",
                "event": "MOTOR_A_DESTROYED",
                "resource": "motor_a",
                "damage_D": D,
                "rho_after": float(rho[0]),
            })

        if (not fault2_done) and t >= cfg.fault_encoder_time:
            rho, D = apply_declared_fault(rho, 2)
            fault2_done = True
            event_tokens.append("ENCODER_DESTROYED")
            events.append({
                "time_s": float(t),
                "branch": "baseline",
                "event": "ENCODER_DESTROYED",
                "resource": "encoder",
                "damage_D": D,
                "rho_after": float(rho[2]),
            })

        c = CONFIGS[current]
        u = -c.gain * x

        x_next = plant_step(
            x_k=x,
            u_k=u,
            config=c,
            rho=rho,
            A=cfg.A,
            xi_k=cfg.disturbance,
        )

        rows.append(log_state(
            k=k,
            t=t,
            branch="baseline",
            current_id=current,
            phase="FROZEN",
            event="|".join(event_tokens),
            x=x,
            x_next=x_next,
            u=u,
            xi=cfg.disturbance,
            rho=rho,
            A=cfg.A,
            phi_min=cfg.phi_min,
        ))

        x = float(x_next)

    return rows, events


def threshold_sweep(cfg: ExperimentConfig):
    """
    Sensitivity after both declared faults.

    This exposes rather than hides the dependence on Phi_min.
    """
    rho = RHO0.copy()
    rho, _ = apply_declared_fault(rho, 0)
    rho, _ = apply_declared_fault(rho, 2)

    rows = []

    for i in range(101):
        phi_min = round(i / 100.0, 2)
        winner, candidates = select_configuration(
            current_id="c1",
            rho=rho,
            A=cfg.A,
            phi_min=phi_min,
        )

        rows.append({
            "Phi_min": float(phi_min),
            "selected_config": winner.config_id,
            "selected_S": float(winner.S),
            "selected_Phi": float(winner.Phi),
        })

    return rows


def main():
    root = Path(__file__).resolve().parents[1]
    cfg = ExperimentConfig()

    supervised, decisions, sup_events, verification = simulate_supervised(cfg)
    baseline, base_events = simulate_baseline(cfg)
    sweep = threshold_sweep(cfg)

    write_csv(supervised, root / "data" / "supervised.csv")
    write_csv(baseline, root / "data" / "baseline_frozen.csv")
    write_csv(decisions, root / "data" / "decisions.csv")
    write_csv(sup_events + base_events, root / "data" / "events.csv")
    write_csv(verification, root / "data" / "verification.csv")
    write_csv(sweep, root / "data" / "phi_min_sensitivity.csv")

    manifest = {
        "experiment": "EXP-03",
        "title": "Survivability-driven structural reconfiguration after irreversible resource loss",
        "config": asdict(cfg),

        "resources": list(RESOURCE_NAMES),
        "rho0": RHO0.tolist(),

        "weights": WEIGHTS.tolist(),
        "function_thresholds": FUNCTION_THRESHOLDS.tolist(),
        "phi_min": cfg.phi_min,

        "configurations": {
            cid: {
                "label": c.label,
                "actuator": c.actuator,
                "sensor": c.sensor,
                "network": c.network,
                "activation": c.activation.tolist(),
                "gain": c.gain,
                "safe_stop": c.safe_stop,
            }
            for cid, c in CONFIGS.items()
        },

        "faults": [
            {
                "time_s": cfg.fault_motor_time,
                "resource_index": 0,
                "resource": "motor_a",
                "equation": "rho_plus = sat_[0,1](rho_minus - eta*D)",
                "eta": 1.0,
                "damage_rule": "D = rho_minus",
            },
            {
                "time_s": cfg.fault_encoder_time,
                "resource_index": 2,
                "resource": "encoder",
                "equation": "rho_plus = sat_[0,1](rho_minus - eta*D)",
                "eta": 1.0,
                "damage_rule": "D = rho_minus",
            },
        ],

        "controlled_factor": "structural reconfiguration enabled vs disabled",

        "held_constant": [
            "plant model",
            "initial resource vector",
            "fault schedule",
            "disturbance",
            "K=0.8 for c0,c1,c2,c3",
            "function thresholds",
            "mission weights",
            "Phi_min",
        ],

        "transition_graph": {
            cid: list(successors)
            for cid, successors in TRANSITION_GRAPH.items()
        },

        "selector": {
            "objective": "maximize S(c,rho)",
            "constraints": [
                "Phi(c,rho) >= Phi_min",
                "|A - b(c,rho)K(c)| < 1",
            ],
            "candidate_set": "directed successors TRANSITION_GRAPH[current]",
            "fallback": "SAFE_STOP if feasible set is empty",
        },

        "supervisor": {
            "frequency_hz": 100,
            "dt_s": cfg.dt,
            "protocol": ["ANALYZE", "SELECT", "APPLY", "VERIFY"],
            "one_phase_per_cycle": True,
        },

        "plotting_contract": {
            "plotter_reads_only": [
                "CSV logs",
                "manifest.json",
            ],
            "plotter_imports_model": False,
            "plotter_imports_selector": False,
            "plotter_imports_experiment": False,
        },

        "no_continuous_degradation": True,
        "no_repair": True,
        "no_noise": True,
        "no_transition_score": True,
        "no_risk_weight": True,
        "no_gain_scheduling": True,
    }

    (root / "data" / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print("EXP-03 strict run")
    for row in decisions:
        if int(row["selected"]) == 1:
            print(
                f'{row["time_s"]:.2f}s '
                f'{row["current"]} -> {row["candidate"]} '
                f'S={row["S"]:.6f} '
                f'Phi={row["Phi"]:.2f} '
                f'gamma={row["gamma"]:.6f}'
            )

    for row in verification:
        print(
            f'{row["time_s"]:.2f}s VERIFY {row["config"]}: '
            f'pass={row["pass"]} '
            f'Phi={row["Phi"]:.2f} '
            f'gamma={row["gamma"]:.6f}'
        )


if __name__ == "__main__":
    main()
