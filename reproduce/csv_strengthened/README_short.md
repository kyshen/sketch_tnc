# Strengthened small-network CSVs

- `raw_runs.csv`: all per-seed runs collected by the strengthened script; best for debugging and custom regrouping.
- `main_results.csv`: main table compatible with the paper body; best for the main text.
- `stage_breakdown.csv`: contraction vs emit stage breakdown; best for the main text.
- `mechanism_ablation.csv`: compact Grid 3x3 mechanism ablation; best for the main text.
- `strength_sensitivity.csv`: L1/L2/L3 strength sensitivity with Tree-8 added; fits either main text or appendix.
- `pareto_sweep.csv`: continuous ASTNC tolerance sweep; best for a main-text Pareto figure or appendix support.
- `blockwise_sensitivity.csv`: blockwise / chunk sensitivity; better suited for the appendix.
- `mechanism_internal_ablation.csv`: internal mechanism evidence table; better suited for the appendix or an expanded paper table.
- Grid 3x3 paper default is the `core` ASTNC-L2 run with `block_labels=2`, `chunk_size=1`, `cache_enabled=true`, `implicit_merge_sketch=true`; sweep tables now mark whether an entry is that paper default or only a candidate setting.

## Honest notes
- The tolerance sweep exposes multiple operating points, but speedup is not strictly monotone in tolerance, so the Pareto front should be drawn from the non-dominated points rather than read as a monotone curve.
- No additional failure mode stood out beyond that non-monotonicity, but Grid 3x3 remains the most sensitive case.
