import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from experiment import ExperimentConfig, run


def test_fault_occurs_once_and_is_permanent():
    rows = run(ExperimentConfig())
    damage_rows = [r for r in rows if r["damage_D2"] > 0.0]
    assert len(damage_rows) == 1

    fault_index = rows.index(damage_rows[0])
    assert damage_rows[0]["rho2_k"] == 0.0

    for row in rows[fault_index:]:
        assert row["rho2_k"] == 0.0
        assert row["B2_eff"] == 0.0


def test_plots_are_not_source_of_data():
    # The experiment produces numerical logs without importing matplotlib.
    rows = run(ExperimentConfig(t_end=5.1))
    assert len(rows) > 0
    assert "x_k1" in rows[0]
    assert "F_k" in rows[0]
