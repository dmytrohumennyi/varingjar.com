from __future__ import annotations

from pathlib import Path
import csv
import matplotlib.pyplot as plt


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def floats(rows: list[dict], key: str) -> list[float]:
    return [float(r[key]) for r in rows]


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "exp01_baseline.csv"
    out_dir = project_root / "figures"
    out_dir.mkdir(exist_ok=True)

    rows = load_csv(data_path)

    t = floats(rows, "time_s")
    x = floats(rows, "x_k")
    S = floats(rows, "S_k")
    P = floats(rows, "P_k")
    F = floats(rows, "F_k")
    rho1 = floats(rows, "rho1_k")
    rho2 = floats(rows, "rho2_k")
    B1 = floats(rows, "B1_eff")
    B2 = floats(rows, "B2_eff")

    fault_t = next(float(r["time_s"]) for r in rows if float(r["damage_D2"]) > 0.0)

    plt.figure(figsize=(9, 4.8))
    plt.plot(t, x, label="x[k]")
    plt.axvline(fault_t, linestyle="--", label="irreversible damage")
    plt.xlabel("time [s]")
    plt.ylabel("state")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(out_dir / "state.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 4.8))
    plt.plot(t, rho1, label="rho1")
    plt.plot(t, rho2, label="rho2")
    plt.axvline(fault_t, linestyle="--", label="irreversible damage")
    plt.xlabel("time [s]")
    plt.ylabel("resource operability")
    plt.ylim(-0.05, 1.05)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(out_dir / "resources.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 4.8))
    plt.plot(t, S, label="S[k]")
    plt.plot(t, P, label="P[k]")
    plt.plot(t, F, label="F[k]")
    plt.axhline(0.8, linestyle=":", label="F_N")
    plt.axhline(0.3, linestyle=":", label="F_K")
    plt.axvline(fault_t, linestyle="--", label="irreversible damage")
    plt.xlabel("time [s]")
    plt.ylabel("integrity")
    plt.ylim(-0.05, 1.05)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(out_dir / "integrity.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 4.8))
    plt.plot(t, B1, label="B1_eff")
    plt.plot(t, B2, label="B2_eff")
    plt.axvline(fault_t, linestyle="--", label="irreversible damage")
    plt.xlabel("time [s]")
    plt.ylabel("effective actuator coefficient")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(out_dir / "effective_actuation.png", dpi=160)
    plt.close()

    print("Figures were generated from:", data_path)


if __name__ == "__main__":
    main()
