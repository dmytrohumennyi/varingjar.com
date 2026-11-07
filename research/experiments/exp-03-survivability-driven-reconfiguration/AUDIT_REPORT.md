# EXP-03 independent numerical audit

Status: **PASS**

The audit intentionally does not import `equations.py`, `selector.py`,
or `experiment.py` for numerical recomputation.

Checked:

- 1601 supervised time-series rows;
- 1601 frozen-baseline time-series rows;
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
