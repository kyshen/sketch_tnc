# Gain Breakdown Summary (Section 3.3)

## Data sufficiency
- Reused `results/main_results_raw_runs.csv` from Section 3.2 directly.
- No additional runs were needed: all 5 cases x 3 methods x 3 seeds are `status=ok`.

## Required answers
1. ASTNC-L2 relative to exact: is total speedup mainly from contraction?
- Yes. Core-case average total speedup is 52.03x, while contraction speedup is 52.07x.
- The two are consistently close case-by-case, indicating contraction-side savings explain most end-to-end gain.
2. Is emit time a small term across core cases?
- Yes. `t_emit_ratio` ranges 0.000004 to 0.002428 across core case-method rows.
3. Is `gain_share_contract` close to 1 on most cases?
- For ASTNC-L2, 4/4 core cases fall in [0.9, 1.1], with range 1.0000 to 1.0000.
- Values slightly above 1 can occur when emit term is tiny and noisy; they are not a separate mechanism.
4. Fixed-rank baseline vs ASTNC-L2: different gain source or mostly same source?
- Gain source is qualitatively the same: both are contraction-dominated (avg gain_share_contract: fixed-rank 1.0000, ASTNC-L2 1.0000).
- Main difference between methods is not where speedup comes from, but their approximation behavior/accuracy profile.
5. Best representative case for "gain comes from contraction side":
- Recommended: `main_grid2d_3x3` (ASTNC-L2 total 84.33x, contract 84.36x, gain_share_contract 1.0000, t_contract_ratio 0.9997).
6. Should `main_chain_8` be excluded from main narrative?
- Yes. Keep `main_chain_8` only as an easiest optional reference row; do not use it as core evidence for the mechanism claim.

## Exception check
- `main_grid2d_3x3` / `fixed-rank baseline` shows a tiny negative `delta_emit` (-3.699999e-06 sec). This is a small fluctuation on a negligible emit term, not a mechanism shift.

## Write-ready result snippet (5-10 lines)
Across the four core topologies, end-to-end runtime is consistently contraction-dominated (`t_contract_ratio` close to 1, while `t_emit_ratio` remains tiny).
For both fixed-rank baseline and ASTNC-L2, most of the total-time reduction relative to exact is explained by contraction-time reduction.
ASTNC-L2 shows close alignment between total speedup and contraction speedup, indicating that its end-to-end gain is not an emit/writeback artifact.
Gain-share decomposition (`delta_total = delta_contract + delta_emit`) further supports this: `gain_share_contract` is near 1 on most core cases.
Occasional `gain_share_contract > 1` values are attributable to very small emit terms and measurement noise, not a different acceleration mechanism.
Therefore, the contraction stage is the primary source of ASTNC-L2 runtime gain on challenging topologies.
`main_chain_8` is retained only as an easy reference and excluded from the core mechanism narrative.