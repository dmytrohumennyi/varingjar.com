from __future__ import annotations

from pathlib import Path
import csv
import json
import numpy as np

from model import CONFIGS, TRANSITION_GRAPH, SAFE_STOP_ID
from equations import admissible

ROOT = Path(__file__).resolve().parents[1]
CONFIG_IDS = tuple(CONFIGS.keys())


def write_matrix(name: str, matrix: list[list[int]]):
    path = ROOT / "data" / name
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["from\\to", *CONFIG_IDS])
        for cid, row in zip(CONFIG_IDS, matrix):
            w.writerow([cid, *row])


def structural_matrix() -> list[list[int]]:
    return [
        [1 if target in TRANSITION_GRAPH[current] else 0 for target in CONFIG_IDS]
        for current in CONFIG_IDS
    ]


def feasible_matrix(rho: np.ndarray, A: float, phi_min: float) -> list[list[int]]:
    matrix = []
    for current in CONFIG_IDS:
        successors = TRANSITION_GRAPH[current]
        mission_successors = [cid for cid in successors if cid != SAFE_STOP_ID]
        feasible = [cid for cid in mission_successors if admissible(CONFIGS[cid], rho, A, phi_min)]
        row = []
        for target in CONFIG_IDS:
            value = 0
            if target in feasible:
                value = 1
            elif target == SAFE_STOP_ID and SAFE_STOP_ID in successors and not feasible:
                value = 1
            row.append(value)
        matrix.append(row)
    return matrix


def actual_matrix(decisions: list[dict]) -> list[list[int]]:
    matrix = [[0 for _ in CONFIG_IDS] for _ in CONFIG_IDS]
    for row in decisions:
        if int(row["selected"]) == 1:
            i = CONFIG_IDS.index(row["current"])
            j = CONFIG_IDS.index(row["candidate"])
            matrix[i][j] = 1
    return matrix


def main():
    manifest = json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))
    with (ROOT / "data" / "decisions.csv").open("r", encoding="utf-8") as f:
        decisions = list(csv.DictReader(f))

    rho0 = np.asarray(manifest["rho0"], dtype=float)
    rho_fault1 = rho0.copy(); rho_fault1[0] = 0.0
    rho_fault2 = rho_fault1.copy(); rho_fault2[2] = 0.0

    A = float(manifest["config"]["A"])
    phi_min = float(manifest["phi_min"])

    write_matrix("transition_structural.csv", structural_matrix())
    write_matrix("transition_feasible_fault1.csv", feasible_matrix(rho_fault1, A, phi_min))
    write_matrix("transition_feasible_fault2.csv", feasible_matrix(rho_fault2, A, phi_min))
    write_matrix("transition_actual.csv", actual_matrix(decisions))


if __name__ == "__main__":
    main()
