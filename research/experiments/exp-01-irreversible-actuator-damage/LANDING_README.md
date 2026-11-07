# Væringjar II — EXP-01 Landing v2

This package contains the rebuilt landing page based on the validated mathematical EXP-01 dataset.

## Measured results

- irreversible actuator #2 damage: 5.00 s
- first K regime: 5.00 s, F=0.450898
- first SK regime: 5.03 s, F=0.298923
- F=0: 14.52 s
- samples: 1601

## Important

Figures embedded in `index.html` are generated from `data/exp01_baseline.csv`.
The numerical model is in `src/`; the plotter does not generate system state.

## Verify

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```


## Author

Dmytro Humennyi  
dmytro.humennyi@edu.kpi.ua

## Publication status

A publication covering this research direction has been submitted as a preprint and is currently under review.
The formal citation and public link will be added to the landing page after public release.
