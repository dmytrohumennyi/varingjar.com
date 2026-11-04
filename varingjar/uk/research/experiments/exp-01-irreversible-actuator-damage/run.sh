#!/usr/bin/env bash
set -euo pipefail

python3 -m pytest -q
python3 src/experiment.py
python3 src/plot_results.py
