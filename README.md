# ASTNC Paper Reproduction (CSV Only)

## Install

```bash
pip install -r requirements.txt
```

## Reproduce Current Paper Tables

Run one command from repository root:

```bash
python reproduce/run_paper_experiments.py
```

CSV outputs are written to:

`reproduce/csv/`

Generated files:

- `raw_runs.csv`
- `main_results.csv`
- `stage_breakdown.csv`
- `mechanism_ablation.csv`
- `strength_sensitivity.csv`
