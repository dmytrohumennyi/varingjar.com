from __future__ import annotations

from pathlib import Path
import csv
import json
import hashlib
import math


ROOT = Path(__file__).resolve().parents[1]
TOL = 1e-12


def load_csv(name):
    with (ROOT / "data" / name).open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def close(a, b, tol=TOL):
    return abs(float(a) - float(b)) <= tol


def config_obj(manifest, config_id):
    return manifest["configurations"][config_id]


def rho_from_row(row):
    return [
        float(row["rho_motor_a"]),
        float(row["rho_motor_b"]),
        float(row["rho_encoder"]),
        float(row["rho_imu"]),
        float(row["rho_can1"]),
        float(row["rho_can2"]),
    ]


def independent_formula(manifest, row):
    c = config_obj(manifest, row["config"])
    rho = rho_from_row(row)

    actuator = c["actuator"]
    sensor = c["sensor"]
    network = c["network"]

    g_a = 0.0 if actuator is None else rho[actuator]
    g_s = rho[sensor]
    g_n = rho[network]

    f = [
        g_a * g_s,
        g_a * g_s * g_n,
        g_n,
        g_s * g_n,
    ]

    thresholds = manifest["function_thresholds"]
    activation = c["activation"]
    weights = manifest["weights"]

    phi = [
        1.0 if activation[i] > 0.5 and f[i] >= thresholds[i] else 0.0
        for i in range(4)
    ]

    S = sum(
        weights[i] * f[i] * activation[i]
        for i in range(4)
    )

    Phi = sum(
        weights[i] * phi[i]
        for i in range(4)
    )

    b = 0.0 if actuator is None else rho[actuator]
    A = float(manifest["config"]["A"])
    K = float(c["gain"])
    gamma = abs(A - b * K)
    delta_v_factor = gamma * gamma - 1.0

    x = float(row["x_k"])
    u = float(row["u_k"])
    xi = float(row["xi_k"])
    x_next = A * x + b * u + xi

    valid = (
        0 if c["safe_stop"]
        else int(Phi >= float(manifest["phi_min"]) and gamma < 1.0)
    )

    return {
        "f": f,
        "phi": phi,
        "S": S,
        "Phi": Phi,
        "b_eff": b,
        "gamma": gamma,
        "delta_v_factor": delta_v_factor,
        "x_k1": x_next,
        "valid": valid,
    }


def audit_timeseries(manifest, rows, name):
    checked = 0

    for row in rows:
        e = independent_formula(manifest, row)

        columns = [
            ("f_stabilization", e["f"][0]),
            ("f_tracking", e["f"][1]),
            ("f_telemetry", e["f"][2]),
            ("f_diagnostics", e["f"][3]),
            ("phi_stabilization", e["phi"][0]),
            ("phi_tracking", e["phi"][1]),
            ("phi_telemetry", e["phi"][2]),
            ("phi_diagnostics", e["phi"][3]),
            ("S", e["S"]),
            ("Phi", e["Phi"]),
            ("b_eff", e["b_eff"]),
            ("gamma", e["gamma"]),
            ("delta_v_factor", e["delta_v_factor"]),
            ("x_k1", e["x_k1"]),
        ]

        for column, expected in columns:
            if not close(row[column], expected):
                raise AssertionError(
                    f"{name}: row k={row['k']} column={column}: "
                    f"CSV={row[column]} expected={expected}"
                )

        if int(row["valid"]) != int(e["valid"]):
            raise AssertionError(
                f"{name}: row k={row['k']} valid mismatch."
            )

        checked += 1

    return checked


def audit_branch_equivalence(supervised, baseline):
    if len(supervised) != len(baseline):
        raise AssertionError("Branch lengths differ.")

    rho_cols = [
        "rho_motor_a", "rho_motor_b", "rho_encoder",
        "rho_imu", "rho_can1", "rho_can2"
    ]

    for s, b in zip(supervised, baseline):
        if not close(s["time_s"], b["time_s"]):
            raise AssertionError("Time bases differ.")

        for c in rho_cols:
            if not close(s[c], b[c]):
                raise AssertionError(
                    f"Resource history differs between branches at "
                    f"t={s['time_s']} column={c}."
                )


def audit_faults(manifest, supervised, baseline):
    faults = manifest["faults"]

    for fault in faults:
        tf = float(fault["time_s"])
        idx = int(fault["resource_index"])

        col = [
            "rho_motor_a", "rho_motor_b", "rho_encoder",
            "rho_imu", "rho_can1", "rho_can2"
        ][idx]

        for rows, branch in [
            (supervised, "supervised"),
            (baseline, "baseline"),
        ]:
            for row in rows:
                t = float(row["time_s"])
                if t >= tf and not close(row[col], 0.0):
                    raise AssertionError(
                        f"{branch}: destroyed resource {col} recovered "
                        f"at t={t}."
                    )


def audit_decisions(manifest, decisions):
    groups = {}

    for row in decisions:
        key = (row["time_s"], row["current"])
        groups.setdefault(key, []).append(row)

    for key, rows in groups.items():
        feasible = [
            r for r in rows
            if int(r["admissible"]) == 1
        ]

        selected = [
            r for r in rows
            if int(r["selected"]) == 1
        ]

        if feasible:
            if len(selected) != 1:
                raise AssertionError(
                    f"Decision {key}: expected exactly one selected row."
                )

            max_s = max(float(r["S"]) for r in feasible)

            if not close(selected[0]["S"], max_s):
                raise AssertionError(
                    f"Decision {key}: selected candidate is not argmax S."
                )


def audit_verification(manifest, verification):
    phi_min = float(manifest["phi_min"])

    for row in verification:
        if row["reason"] == "SAFE_STOP_FALLBACK":
            continue

        expected = (
            float(row["Phi"]) >= phi_min
            and float(row["gamma"]) < 1.0
        )

        if int(row["pass"]) != int(expected):
            raise AssertionError(
                f"VERIFY mismatch at t={row['time_s']}."
            )


def load_matrix(name):
    rows = load_csv(name)
    config_ids = list(rows[0].keys())[1:]
    matrix = []
    row_ids = []
    first_key = list(rows[0].keys())[0]
    for row in rows:
        row_ids.append(row[first_key])
        matrix.append([int(row[cid]) for cid in config_ids])
    return row_ids, config_ids, matrix


def independent_admissible(manifest, config_id, rho):
    c = manifest["configurations"][config_id]
    if c["safe_stop"]:
        return False

    actuator = c["actuator"]
    sensor = c["sensor"]
    network = c["network"]

    g_a = 0.0 if actuator is None else rho[actuator]
    g_s = rho[sensor]
    g_n = rho[network]

    f = [g_a*g_s, g_a*g_s*g_n, g_n, g_s*g_n]
    phi = [
        1.0 if c["activation"][i] > 0.5 and f[i] >= manifest["function_thresholds"][i] else 0.0
        for i in range(4)
    ]
    Phi = sum(manifest["weights"][i] * phi[i] for i in range(4))
    A = float(manifest["config"]["A"])
    b = 0.0 if actuator is None else rho[actuator]
    gamma = abs(A - b * float(c["gain"]))
    return bool(Phi >= float(manifest["phi_min"]) and gamma < 1.0)


def expected_structural_matrix(manifest):
    config_ids = list(manifest["configurations"].keys())
    graph = manifest["transition_graph"]
    return [
        [1 if target in graph[current] else 0 for target in config_ids]
        for current in config_ids
    ]


def expected_feasible_matrix(manifest, rho):
    config_ids = list(manifest["configurations"].keys())
    graph = manifest["transition_graph"]
    safe = "c4"
    matrix = []
    for current in config_ids:
        successors = graph[current]
        mission_successors = [cid for cid in successors if cid != safe]
        feasible = [cid for cid in mission_successors if independent_admissible(manifest, cid, rho)]
        row = []
        for target in config_ids:
            value = 0
            if target in feasible:
                value = 1
            elif target == safe and safe in successors and not feasible:
                value = 1
            row.append(value)
        matrix.append(row)
    return matrix


def audit_transition_matrices(manifest, decisions):
    config_ids = list(manifest["configurations"].keys())
    rho0 = [float(v) for v in manifest["rho0"]]
    rho1 = list(rho0); rho1[0] = 0.0
    rho2 = list(rho1); rho2[2] = 0.0

    expected = {
        "transition_structural.csv": expected_structural_matrix(manifest),
        "transition_feasible_fault1.csv": expected_feasible_matrix(manifest, rho1),
        "transition_feasible_fault2.csv": expected_feasible_matrix(manifest, rho2),
    }

    actual_expected = [[0 for _ in config_ids] for _ in config_ids]
    for row in decisions:
        if int(row["selected"]) == 1:
            i = config_ids.index(row["current"])
            j = config_ids.index(row["candidate"])
            actual_expected[i][j] = 1
    expected["transition_actual.csv"] = actual_expected

    for name, expected_matrix in expected.items():
        row_ids, col_ids, observed = load_matrix(name)
        if row_ids != config_ids or col_ids != config_ids:
            raise AssertionError(f"{name}: row/column identifiers do not match configurations.")
        if observed != expected_matrix:
            raise AssertionError(f"{name}: matrix does not match independent recomputation.")


def audit_decision_graph(manifest, decisions):
    graph = manifest["transition_graph"]
    groups = {}
    for row in decisions:
        groups.setdefault((row["time_s"], row["current"]), []).append(row)
    for (_, current), rows in groups.items():
        logged = {row["candidate"] for row in rows}
        mission_successors = {cid for cid in graph[current] if cid != "c4"}
        if logged != mission_successors:
            raise AssertionError(
                f"Decision from {current}: logged candidates {sorted(logged)} "
                f"do not equal graph successors {sorted(mission_successors)}."
            )


def write_checksums():
    paths = [
        ROOT / "data" / "manifest.json",
        ROOT / "data" / "supervised.csv",
        ROOT / "data" / "baseline_frozen.csv",
        ROOT / "data" / "decisions.csv",
        ROOT / "data" / "events.csv",
        ROOT / "data" / "verification.csv",
        ROOT / "data" / "phi_min_sensitivity.csv",
        ROOT / "data" / "transition_structural.csv",
        ROOT / "data" / "transition_feasible_fault1.csv",
        ROOT / "data" / "transition_feasible_fault2.csv",
        ROOT / "data" / "transition_actual.csv",
    ]

    figure_dir = ROOT / "figures"
    if figure_dir.exists():
        paths.extend(sorted(figure_dir.glob("*.png")))

    lines = []

    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT)}")

    (ROOT / "data" / "checksums.sha256").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main():
    manifest = json.loads(
        (ROOT / "data" / "manifest.json").read_text(encoding="utf-8")
    )

    supervised = load_csv("supervised.csv")
    baseline = load_csv("baseline_frozen.csv")
    decisions = load_csv("decisions.csv")
    verification = load_csv("verification.csv")

    n_sup = audit_timeseries(
        manifest, supervised, "supervised"
    )
    n_base = audit_timeseries(
        manifest, baseline, "baseline"
    )

    audit_branch_equivalence(supervised, baseline)
    audit_faults(manifest, supervised, baseline)
    audit_decisions(manifest, decisions)
    audit_decision_graph(manifest, decisions)
    audit_transition_matrices(manifest, decisions)
    audit_verification(manifest, verification)

    # Plotter separation audit.
    plot_text = (ROOT / "src" / "plot_results.py").read_text(
        encoding="utf-8"
    )

    forbidden = [
        "from model",
        "import model",
        "from equations",
        "import equations",
        "from selector",
        "import selector",
        "from experiment",
        "import experiment",
    ]

    for token in forbidden:
        if token in plot_text:
            raise AssertionError(
                f"Plotter imports simulation logic: {token}"
            )

    forbidden_plot_literals = [
        "axvline(5.0",
        "axvline(12.0",
        "axhline(0.65",
    ]

    for token in forbidden_plot_literals:
        if token in plot_text:
            raise AssertionError(
                f"Plotter hard-codes experiment datum: {token}"
            )

    write_checksums()

    report = f"""# EXP-03 independent numerical audit

Status: **PASS**

The audit intentionally does not import `equations.py`, `selector.py`,
or `experiment.py` for numerical recomputation.

Checked:

- {n_sup} supervised time-series rows;
- {n_base} frozen-baseline time-series rows;
- every logged function capability `f_j`;
- every binary function state `phi_j`;
- every `S`;
- every `Phi`;
- every effective actuator coefficient `b`;
- every scalar stability factor `gamma`;
- every Lyapunov multiplier `gamma^2 - 1`;
- every plant transition `x[k+1]`;
- every `valid` flag;
- identical resource histories in both branches;
- permanent zero after each irreversible fault;
- logged candidates equal the directed graph successors of the current configuration;
- selected candidate is `argmax S` over admissible graph successors;
- structural, fault-conditioned, and actual transition matrices are independently recomputed;
- VERIFY result equals recomputed `Phi >= Phi_min` and `gamma < 1`;
- plotting code imports no model, equations, selector, or experiment module.

Plotting contract:

`experiment.py -> CSV / manifest -> plot_results.py -> PNG`

No state, survivability, mission-functionality, candidate-selection, or
fault equation is executed inside `plot_results.py`.
"""

    (ROOT / "AUDIT_REPORT.md").write_text(
        report,
        encoding="utf-8",
    )

    print(report)


if __name__ == "__main__":
    main()
