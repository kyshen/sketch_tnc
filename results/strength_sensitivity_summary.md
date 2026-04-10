# Strength Sensitivity Summary (Section 3.5)

## Data Completeness
- `main_ring_8` | `ASTNC-L1`: n_ok=3/3
- `main_ring_8` | `ASTNC-L2`: n_ok=3/3
- `main_ring_8` | `ASTNC-L3`: n_ok=3/3
- `main_grid2d_3x3` | `ASTNC-L1`: n_ok=3/3
- `main_grid2d_3x3` | `ASTNC-L2`: n_ok=3/3
- `main_grid2d_3x3` | `ASTNC-L3`: n_ok=3/3
- `main_random_8` | `ASTNC-L1`: n_ok=3/3
- `main_random_8` | `ASTNC-L2`: n_ok=3/3
- `main_random_8` | `ASTNC-L3`: n_ok=3/3
- Optional `main_tree_8` not included (kept scope to required 3 core cases).

## Direct Answers To Core Questions
1. L1->L2->L3 total time monotonic decrease holds in 0/3 core cases (by mean `total_time_sec`).
2. L1->L2->L3 error monotonic increase holds in 3/3 core cases (by mean `rel_error`).
3. Non-monotonic exceptions: time=['main_ring_8', 'main_grid2d_3x3', 'main_random_8'], error=none.
4. Do L1/L2/L3 form a speed-accuracy frontier? Judgment: partial (error axis clear, time axis not monotonic).
5. Cases where `ASTNC-L1` may be preferable over L2: main_ring_8, main_grid2d_3x3
6. Cases where `ASTNC-L3` looks not cost-effective (higher error with little/no extra speed): main_random_8
7. Is `ASTNC-L2` supported as a default operating point? Evidence strength: weak. L2 is dominated by L1 on: main_ring_8, main_grid2d_3x3. Use as a default only as a pragmatic middle preset, not as a universally optimal choice.
8. Topology dependence: `main_grid2d_3x3` shows the strongest separation; `main_ring_8` and `main_random_8` respond differently in runtime, confirming workload dependence.
9. Most representative case for paper main text: `main_grid2d_3x3`.
10. Most cautious claim: avoid saying stronger approximation is always faster; in this run set, time monotonicity fails on all core cases.

## Topology-level Pattern
- `main_grid2d_3x3` (harder topology) is the primary discriminator for speed-accuracy tension.
- `main_ring_8` and `main_random_8` do not share the same timing profile as grid, even though error still increases with strength.
- Cross-case behavior is workload-dependent; avoid claiming a fully uniform law.

## Auxiliary Indicator
- Auxiliary metric used: `error_time_product = rel_error * total_time_sec`; interpret only as secondary evidence.
- Core-case averages (error/time): L1=0.000000/0.0977, L2=0.001968/0.1828, L3=0.015411/0.1457.

## 8-12 Lines Draft Result Paragraph
- We ran a strength-sensitivity study on `main_ring_8`, `main_grid2d_3x3`, and `main_random_8` with seeds `{0,1,2}`.
- Error is monotonic with strength (L1 <= L2 <= L3 in all core cases), but runtime is not monotonic across cases.
- On `main_grid2d_3x3`, L1 is both faster and more accurate than L2, while L3 trades additional error for partial speed recovery.
- On `main_ring_8`, L1 again dominates L2 on both error and runtime; L3 improves time vs L2 but remains less accurate.
- On `main_random_8`, L1 and L2 are both near-exact in error, and L3 mainly increases error without time gain.
- These results indicate a workload-dependent frontier rather than a single monotonic speed-accuracy curve.
- `ASTNC-L2` should be described as a default operating point only in a pragmatic sense.
- It is not universally optimal in this dataset and can be dominated by L1 on specific workloads.
- `main_grid2d_3x3` is the best representative case for paper main text because it most clearly exposes the tradeoff structure.
- Claims that stronger approximation is always faster should be explicitly avoided.
