# Main Results Summary (Section 3.2)

## Run completion

- main_ring_8: exact: 3/3; fixed-rank baseline: 3/3; ASTNC-L2: 3/3
- main_tree_8: exact: 3/3; fixed-rank baseline: 3/3; ASTNC-L2: 3/3
- main_grid2d_3x3: exact: 3/3; fixed-rank baseline: 3/3; ASTNC-L2: 3/3
- main_random_8: exact: 3/3; fixed-rank baseline: 3/3; ASTNC-L2: 3/3
- main_chain_8: exact: 3/3; fixed-rank baseline: 3/3; ASTNC-L2: 3/3

All listed rows in this summary are based on completed (`status=ok`) runs only.

## Required questions

1. ASTNC-L2 most evident time-accuracy tradeoff advantage:
- Most evident on `main_grid2d_3x3` (ASTNC-L2 speedup 84.05x, rel_error 0.004078).
- On `main_grid2d_3x3`, ASTNC-L2 keeps rel_error at 0.004078 with 84.05x speedup, while fixed-rank is faster but much less accurate.

2. Cases where fixed-rank baseline is faster but error is not acceptable:
- `main_grid2d_3x3`: fixed-rank speedup 566.07x, rel_error 0.978913.
- `main_random_8`: fixed-rank speedup 21.72x, rel_error 0.928319.
- `main_ring_8`: fixed-rank speedup 123.39x, rel_error 0.805755.
- `main_tree_8`: fixed-rank speedup 57.69x, rel_error 0.652428.

3. ASTNC-L2 gains: total time vs contract time?
- Average total-time speedup (ASTNC-L2 vs exact, core cases): 50.95x.
- Average contract-time speedup (ASTNC-L2 vs exact, core cases): 50.99x.
- Interpretation: the dominant gain is from contraction stage; emit time is comparatively tiny in all methods.

4. Does `t_contract_ratio` support contraction-dominated claim?
- Yes. Across core-case/method rows, `t_contract_ratio` ranges from 0.9976 to 1.0000.
- This indicates runtime is overwhelmingly contraction-dominated.

5. Should `main_chain_8` be in main table?
- Keep it as an optional/easiest reference row, not core evidence, because it is structurally easiest and all methods already look very favorable there.

6. Suggested Section 3.2 narrative organization from this round:
- First establish that exact is the quality anchor but has highest total runtime on hard topologies (especially grid2d).
- Then show fixed-rank is very fast but often incurs large error on ring/tree/grid/random main-core cases.
- Position ASTNC-L2 as the default operating point: substantial speedup over exact while preserving materially lower error than fixed-rank.
- Finally, use `t_contract_ratio` and ASTNC internals to support that speed gains are mainly contraction-side improvements.

## Reporting rule applied
- Raw CSV keeps exported `speedup_vs_exact` from runner.
- Paper-facing tables report exact-row speedup as `1.00x` by convention; non-exact rows use recomputed case-local speedup from aggregated total time.

## Notes
- No algorithm logic changes were introduced in this run script.
- `ASTNC-L2` is treated as default operating point only; no claim is made that it strictly dominates all other tolerance levels in all scenarios.