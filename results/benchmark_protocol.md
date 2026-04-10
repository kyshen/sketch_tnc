# Experimental Setup and Benchmark Protocol (ASTNC)

## 1. Benchmark Design Principles

1. Protocol is designed from paper claims, not from existing demo commands.
2. Use layered cases (`toy/main/stress`) to separate sanity checks, main evidence, and boundary behavior.
3. Keep exact-computable main cases so accuracy and speedup are interpretable.
4. Separate method groups by question:
   - main result comparison
   - approximation-strength sensitivity
   - mechanism ablation probes
5. All outward-facing method names follow:
   - `ASTNC`
   - `ASTNC-L1`
   - `ASTNC-L2`
   - `ASTNC-L3`

## 2. Case Layers

## 2.1 Toy / Sanity

| case_id | topology | config | role |
|---|---|---|---|
| toy_chain_6 | chain | num_nodes=6, phys_dim=2, bond_dim=3 | correctness + trivial trend check |
| toy_ring_6 | ring | num_nodes=6, phys_dim=2, bond_dim=3 | correctness + small-cycle sanity |
| toy_tree_6 | tree | num_nodes=6, phys_dim=2, bond_dim=3 | acyclic sanity |
| toy_grid2d_2x3 | grid2d | grid_shape=[2,3], phys_dim=2, bond_dim=3 | mesh sanity |
| toy_random_6 | random_connected | num_nodes=6, phys_dim=2, bond_dim=3, edge_prob=0.35 | random-topology sanity |

## 2.2 Main Benchmark (paper core tables)

| case_id | topology | config | pilot signal |
|---|---|---|---|
| main_chain_8 | chain | num_nodes=8, phys_dim=3, bond_dim=4 | easy; limited discrimination |
| main_ring_8 | ring | num_nodes=8, phys_dim=3, bond_dim=4 | strong time gain + sensitivity signal |
| main_tree_8 | tree | num_nodes=8, phys_dim=3, bond_dim=4 | moderate approximation error, useful |
| main_grid2d_3x3 | grid2d | grid_shape=[3,3], phys_dim=3, bond_dim=4 | highest discrimination and challenge |
| main_random_8 | random_connected | num_nodes=8, phys_dim=3, bond_dim=4, edge_prob=0.35 | topology robustness with stable runs |

## 2.3 Stress / Boundary

| case_id | topology | config | pilot result |
|---|---|---|---|
| stress_ring_10 | ring | num_nodes=10, phys_dim=3, bond_dim=4 | timeout at 180s |
| stress_grid2d_3x4 | grid2d | grid_shape=[3,4], phys_dim=3, bond_dim=4 | timeout at 180s |
| stress_random_10 | random_connected | num_nodes=10, phys_dim=3, bond_dim=4 | timeout at 180s |

## 3. Method Groups by Experimental Question

## 3.1 Main Results (Q1, Q4)

Run on main benchmark cases:

- `exact`
- `fixed-rank baseline` (internal: ASTNC fixed policy)
- `ASTNC-L2`

Purpose: show time-accuracy tradeoff under full dense materialization with a practical default setting.

## 3.2 Approximation-Strength Sensitivity (Q1)

Run on representative medium-hard cases (`main_ring_8`, `main_grid2d_3x3`, `main_random_8`):

- `ASTNC-L1`
- `ASTNC-L2`
- `ASTNC-L3`

Purpose: characterize whether stronger approximation gives useful additional speed and how much accuracy is sacrificed.

## 3.3 Mechanism Ablation Probes (Q2, Q3)

Pilot mechanism interface points (already executable):

- no cache: `cache_enabled=false`
- no implicit merge sketch: `implicit_merge_sketch=false`
- no blockwise output organization: `block.enabled=false`
- fixed vs adaptive rank: `rank_policy=fixed` baseline vs `ASTNC-L2`

Pilot ablation cases:

- `ablate_ring_8`
- `ablate_grid2d_3x3`

## 4. Seed and Protocol Controls

- Pilot seeds:
  - toy/main: `{0,1}`
  - stress: `{0}`
- Reason for not using seed=2 in this round:
  - This round targets protocol design + screening; seed expansion is deferred to final-table phase after case pruning.

## 5. Metrics to Keep as Primary Table Fields

Primary fields (stable and informative in pilot):

- identification: `topology`, `size_description`, `seed`, `method`
- accuracy: `rel_error`, `RMSE`, `NMSE`, `NMSE_dB`
- time: `contract_time_sec`, `emit_time_sec`, `total_time_sec`, `speedup_vs_exact`, `t_contract_ratio`
- ASTNC internals:
  - `num_blocks`, `refined_blocks`, `mean_rank`, `max_rank`, `peak_rank`
  - `num_exact_merges`, `num_compressed_merges`
  - `num_exact_leaves`, `num_compressed_leaves`
  - `mean_leaf_residual_ratio`, `mean_merge_residual_ratio`
  - `cache_enabled`, `cache_requests`, `cache_hits`, `cache_misses`, `cache_hit_rate`, `num_cached_states`

## 6. Mapping to Paper Subsections

- Claim 1 (time-accuracy tradeoff):
  - main cases + methods (`exact`, `fixed-rank baseline`, `ASTNC-L2`) and L1/L2/L3 sensitivity subset.
- Claim 2 (gain source is contraction-side saving):
  - use `contract_time_sec`, `emit_time_sec`, `t_contract_ratio`, plus no-blockwise and no-cache probes.
- Claim 3 (core mechanism effectiveness):
  - dedicated ablation section using ring/grid representative cases.
- Claim 4 (topology + scale universality):
  - topology coverage in toy/main + timeout-marked stress layer for boundary narrative.
