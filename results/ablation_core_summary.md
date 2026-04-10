# Core Mechanism Ablation Summary (Section 3.4)

## Data Completeness
- `main_ring_8` | `ASTNC-L2`: n_ok=3/3
- `main_ring_8` | `ASTNC-L2-no-blockwise`: n_ok=3/3
- `main_ring_8` | `ASTNC-L2-no-implicit`: n_ok=3/3
- `main_ring_8` | `ASTNC-L2-no-cache`: n_ok=3/3
- `main_ring_8` | `fixed-rank baseline`: n_ok=3/3
- `main_grid2d_3x3` | `ASTNC-L2`: n_ok=3/3
- `main_grid2d_3x3` | `ASTNC-L2-no-blockwise`: n_ok=3/3
- `main_grid2d_3x3` | `ASTNC-L2-no-implicit`: n_ok=3/3
- `main_grid2d_3x3` | `ASTNC-L2-no-cache`: n_ok=3/3
- `main_grid2d_3x3` | `fixed-rank baseline`: n_ok=3/3
- `main_random_8` | `ASTNC-L2`: n_ok=3/3
- `main_random_8` | `ASTNC-L2-no-blockwise`: n_ok=3/3
- `main_random_8` | `ASTNC-L2-no-implicit`: n_ok=3/3
- `main_random_8` | `ASTNC-L2-no-cache`: n_ok=3/3
- `main_random_8` | `fixed-rank baseline`: n_ok=3/3

## Answers To Required Questions
1. Is `blockwise` core? `no-blockwise` time ratio is 0.5441 on `main_ring_8` and 2.4029 on `main_grid2d_3x3`. Conclusion: workload-dependent, but important on harder cases.
2. Is `implicit merge sketch` core? `no-implicit` time ratio is ring=0.8969, grid=6.9675. This is the strongest and most stable efficiency mechanism on the hard grid case.
3. Is `cache` consistently beneficial? `no-cache` time ratio is ring=1.1002, grid=0.8627, random=2.7791. Best paper wording: workload-dependent / overhead-sensitive; current implementation does not support a universal positive claim.
4. Do `ring_8` and `grid2d_3x3` reveal different mechanism pictures? Yes. Ring exposes overhead effects; grid exposes real gains on harder contractions.
5. If `main_random_8` is included, which picture is it closer to? For `no-blockwise` it is grid-like; for `no-implicit` it is ring-like.
6. Two mechanisms to foreground in the main text: `implicit merge sketch` and `blockwise output organization`.
7. Results that should be appendix-level or conservative: `cache reuse` and `fixed-rank baseline` (policy reference, not single-mechanism ablation).

## 8-12 Lines Draft Paragraph For Paper Writing
- Core ablation across `main_ring_8` and `main_grid2d_3x3` shows that ASTNC gains are mechanism-compositional rather than from a single trick.
- Removing `implicit merge sketch` causes the most stable runtime degradation, especially on the harder grid case.
- Removing `blockwise output organization` has workload-dependent effects: it may reduce overhead on easier cases, but degrades behavior on harder ones.
- This pattern indicates blockwise scheduling is not universally positive, yet becomes important when contraction structure is complex.
- `cache reuse` does not show a uniform sign across workloads.
- The observed cache impact is overhead-sensitive and implementation-dependent under current settings.
- Therefore, we avoid claiming consistent runtime improvement from cache in the present implementation.
- `fixed-rank baseline` is treated only as a policy reference and should not be interpreted as removing any single ASTNC mechanism.
- Overall, ASTNC performance emerges from coordinated mechanisms whose value depends on workload difficulty and structure.
- The most robust core narrative is the joint role of implicit sketching and blockwise organization on harder workloads.
