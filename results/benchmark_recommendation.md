# Benchmark Recommendation (from Pilot)

## 1) Is the current repo ready for paper experiments?

Yes, **conditionally ready** after the minimal fixes in `results/setup_notes.md`.

What is now ready:

- batch execution via Hydra overrides
- stable per-run table export (`runs.csv`/`runs.parquet`)
- required benchmark fields exported for both accuracy/time and ASTNC internals

Remaining caution:

- stress tier currently times out under 180s (expected for boundary screening, not final main-table evidence).

## 2) Recommended default ASTNC level (L1/L2/L3)

Recommended default: **`ASTNC-L2`**.

Reason from pilot:

- Maintains strong speedup on main cases (roughly 15x to 100x+ vs exact) while keeping low-to-moderate error.
- `ASTNC-L1` is often near-exact but can be slower on difficult cases.
- `ASTNC-L3` consistently increases error and does not reliably reduce runtime further in this implementation.

## 3) Recommended cases for the main result table

Keep as core main-table set:

- `main_ring_8`
- `main_tree_8`
- `main_grid2d_3x3`
- `main_random_8`

Optional include:

- `main_chain_8` (only as easiest reference row, not as key discriminative evidence)

## 4) Cases recommended to drop from main claims (low information / instability)

Drop from primary claim tables:

- all toy cases (`toy_*`): mostly near-exact for all non-trivial methods, low discrimination
- `main_chain_8` as a required row: too easy; fixed-rank baseline already near-exact, weak contrast

Do not use stress cases for quantitative main-table claims yet:

- `stress_ring_10`, `stress_grid2d_3x4`, `stress_random_10` (all timeout in this pilot setting)

## 5) Top two next sections to prioritize

1. **Main result section (exact vs fixed-rank baseline vs ASTNC-L2)** on recommended main cases with seeds `{0,1,2}`.
2. **Mechanism ablation section** focused on `main_ring_8` and `main_grid2d_3x3`, prioritizing:
   - cache reuse on/off
   - blockwise on/off
   - implicit merge sketch on/off
   - fixed vs adaptive rank policy

## Pilot Snapshot (key signals)

- `t_contract_ratio` is ~0.999 across methods/cases: runtime is contraction-dominated.
- `main_grid2d_3x3` is the strongest discriminative case.
- Fixed-rank baseline is very fast but often severely degrades accuracy on nontrivial topologies.
- `ASTNC-L2` provides the most balanced default trajectory for paper narrative.
