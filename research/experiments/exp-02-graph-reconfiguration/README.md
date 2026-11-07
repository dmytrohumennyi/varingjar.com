# EXP-02 — Graph-Based Post-Failure Reconfiguration

Interactive prototype for Væringjar II.

## Purpose

Demonstrate the proposed post-failure reasoning chain using explicit stable-state graphs and matrices:

`residual resources -> feasible graph -> transition matrices -> reachable set -> path search -> degraded stable state`

## Current evidence level

The model structure and algorithms are executable in the browser, but the scenario values in `data/scenario.json` are synthetic. They are intended to validate the information structure and decision logic before plant-specific identification and HIL validation.

## Files

- `index.html` — interactive experiment page
- `data/scenario.json` — states, transition edges, resource vectors and costs
- `../../../assets/js/exp-02.js` — matrix rendering, Dijkstra search, graph rendering and animation
- `../../../assets/css/exp-02.css` — page-specific visual layer

## Scientific distinction

The transient failure point `q_f` is not treated as a stable-state node and therefore does not appear in the stable-state transition matrix. The search begins from the certified capture state V1 after the failure transient has been contained.
