# Generalization Tables (Section 3.6)

## Table 1: Case Inventory

| case_id | topology | size_description | scale_level | exact_available | completed_fraction |
|---|---|---|---|---:|---:|
| main_chain_8 | chain | num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1 | easy | True | 1.000 |
| main_ring_8 | ring | num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1 | easy | True | 1.000 |
| main_tree_8 | tree | num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1 | easy | True | 1.000 |
| main_grid2d_3x3 | grid2d | grid_shape=[3,3], num_nodes=9, phys_dim=3, bond_dim=4, open_legs_per_node=1 | easy | True | 1.000 |
| main_random_8 | random_connected | num_nodes=8, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1 | easy | True | 1.000 |
| medium_chain_10 | chain | num_nodes=10, phys_dim=3, bond_dim=4, open_legs_per_node=1 | medium | False | 0.125 |
| medium_ring_10 | ring | num_nodes=10, phys_dim=3, bond_dim=4, open_legs_per_node=1 | medium | False | 0.000 |
| medium_tree_10 | tree | num_nodes=10, phys_dim=3, bond_dim=4, open_legs_per_node=1 | medium | False | 0.000 |
| medium_grid2d_3x4 | grid2d | grid_shape=[3,4], num_nodes=12, phys_dim=3, bond_dim=4, open_legs_per_node=1 | medium | False | 0.000 |
| medium_random_10 | random_connected | num_nodes=10, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1 | medium | False | 0.250 |
| boundary_ring_12 | ring | num_nodes=12, phys_dim=3, bond_dim=4, open_legs_per_node=1 | boundary | False | 0.000 |
| boundary_grid2d_4x4 | grid2d | grid_shape=[4,4], num_nodes=16, phys_dim=3, bond_dim=4, open_legs_per_node=1 | boundary | False | 0.000 |
| boundary_random_12 | random_connected | num_nodes=12, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1 | boundary | False | 0.000 |

## Table 2: Main Results by Topology x Scale

### main_chain_8

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=3/3, timeout=0, failed=0 | 0.000000 | 0.9851 | 0.973 | 1.0000 |
| fixed-rank baseline | ok=3/3, timeout=0, failed=0 | 0.000000 | 0.0146 | 69.255 | 0.9969 |
| ASTNC-L1 | ok=3/3, timeout=0, failed=0 | 0.000000 | 0.0713 | 13.824 | 0.9994 |
| ASTNC-L2 | ok=3/3, timeout=0, failed=0 | 0.000000 | 0.0216 | 45.689 | 0.9984 |
| ASTNC-L3 | ok=3/3, timeout=0, failed=0 | 0.002476 | 0.1101 | 8.946 | 0.9996 |

### main_ring_8

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=3/3, timeout=0, failed=0 | 0.000000 | 3.0072 | 0.647 | 1.0000 |
| fixed-rank baseline | ok=3/3, timeout=0, failed=0 | 0.805755 | 0.0244 | 123.704 | 0.9986 |
| ASTNC-L1 | ok=3/3, timeout=0, failed=0 | 0.000000 | 0.0478 | 63.575 | 0.9993 |
| ASTNC-L2 | ok=3/3, timeout=0, failed=0 | 0.001827 | 0.0534 | 56.321 | 0.9993 |
| ASTNC-L3 | ok=3/3, timeout=0, failed=0 | 0.015534 | 0.0495 | 61.364 | 0.9984 |

### main_tree_8

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=3/3, timeout=0, failed=0 | 0.000000 | 1.1068 | 0.978 | 1.0000 |
| fixed-rank baseline | ok=3/3, timeout=0, failed=0 | 0.652428 | 0.0192 | 62.266 | 0.9980 |
| ASTNC-L1 | ok=3/3, timeout=0, failed=0 | 0.000000 | 0.1004 | 11.773 | 0.9996 |
| ASTNC-L2 | ok=3/3, timeout=0, failed=0 | 0.004810 | 0.0224 | 51.540 | 0.9985 |
| ASTNC-L3 | ok=3/3, timeout=0, failed=0 | 0.048607 | 0.0996 | 12.186 | 0.9996 |

### main_grid2d_3x3

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=3/3, timeout=0, failed=0 | 0.000000 | 37.1995 | 0.982 | 1.0000 |
| fixed-rank baseline | ok=3/3, timeout=0, failed=0 | 0.978913 | 0.0657 | 567.407 | 0.9976 |
| ASTNC-L1 | ok=3/3, timeout=0, failed=0 | 0.000000 | 0.1907 | 194.885 | 0.9995 |
| ASTNC-L2 | ok=3/3, timeout=0, failed=0 | 0.004078 | 0.4426 | 83.910 | 0.9997 |
| ASTNC-L3 | ok=3/3, timeout=0, failed=0 | 0.018051 | 0.3331 | 120.307 | 0.9996 |

### main_random_8

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=3/3, timeout=0, failed=0 | 0.000000 | 0.7326 | 1.001 | 0.9999 |
| fixed-rank baseline | ok=3/3, timeout=0, failed=0 | 0.928319 | 0.0337 | 26.406 | 0.9984 |
| ASTNC-L1 | ok=3/3, timeout=0, failed=0 | 0.000000 | 0.0547 | 13.272 | 0.9993 |
| ASTNC-L2 | ok=3/3, timeout=0, failed=0 | 0.000000 | 0.0524 | 13.561 | 0.9993 |
| ASTNC-L3 | ok=3/3, timeout=0, failed=0 | 0.012649 | 0.0545 | 13.443 | 0.9992 |

### medium_chain_10

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| fixed-rank baseline | NA | NA | NA | NA | NA |
| ASTNC-L1 | ok=1/2, timeout=1, failed=0 | 0.000000 | 0.0415 | 22852.072 | 0.9956 |
| ASTNC-L2 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| ASTNC-L3 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |

### medium_ring_10

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| fixed-rank baseline | NA | NA | NA | NA | NA |
| ASTNC-L1 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| ASTNC-L2 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| ASTNC-L3 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |

### medium_tree_10

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| fixed-rank baseline | NA | NA | NA | NA | NA |
| ASTNC-L1 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| ASTNC-L2 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| ASTNC-L3 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |

### medium_grid2d_3x4

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| fixed-rank baseline | NA | NA | NA | NA | NA |
| ASTNC-L1 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| ASTNC-L2 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| ASTNC-L3 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |

### medium_random_10

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| fixed-rank baseline | NA | NA | NA | NA | NA |
| ASTNC-L1 | ok=1/2, timeout=1, failed=0 | 0.003337 | 4.7850 | 59.894 | 0.9999 |
| ASTNC-L2 | ok=0/2, timeout=2, failed=0 | NA | NA | NA | NA |
| ASTNC-L3 | ok=1/2, timeout=1, failed=0 | 0.046085 | 4.4098 | 66.133 | 0.9999 |

### boundary_ring_12

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |
| fixed-rank baseline | NA | NA | NA | NA | NA |
| ASTNC-L1 | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |
| ASTNC-L2 | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |
| ASTNC-L3 | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |

### boundary_grid2d_4x4

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |
| fixed-rank baseline | NA | NA | NA | NA | NA |
| ASTNC-L1 | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |
| ASTNC-L2 | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |
| ASTNC-L3 | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |

### boundary_random_12

| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |
|---|---|---:|---:|---:|---:|
| exact | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |
| fixed-rank baseline | NA | NA | NA | NA | NA |
| ASTNC-L1 | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |
| ASTNC-L2 | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |
| ASTNC-L3 | ok=0/1, timeout=1, failed=0 | NA | NA | NA | NA |

## Table 3: L1/L2/L3 Relative Relationship

| case_id | best accuracy method | fastest method | recommended method | L1 dominates L2 | L3 cost-effective |
|---|---|---|---|---|---|
| main_chain_8 | ASTNC-L1 | ASTNC-L2 | ASTNC-L2 | no | no |
| main_ring_8 | ASTNC-L1 | ASTNC-L1 | ASTNC-L1 | yes | yes |
| main_tree_8 | ASTNC-L1 | ASTNC-L2 | ASTNC-L1 | no | no |
| main_grid2d_3x3 | ASTNC-L1 | ASTNC-L1 | ASTNC-L1 | yes | yes |
| main_random_8 | ASTNC-L1 | ASTNC-L2 | ASTNC-L1 | no | no |
| medium_chain_10 | ASTNC-L1 | ASTNC-L1 | ASTNC-L1 | NA | NA |
| medium_ring_10 | NA | NA | NA | NA | NA |
| medium_tree_10 | NA | NA | NA | NA | NA |
| medium_grid2d_3x4 | NA | NA | NA | NA | NA |
| medium_random_10 | ASTNC-L1 | ASTNC-L3 | ASTNC-L1 | NA | NA |
| boundary_ring_12 | NA | NA | NA | NA | NA |
| boundary_grid2d_4x4 | NA | NA | NA | NA | NA |
| boundary_random_12 | NA | NA | NA | NA | NA |

## Table 4: Regime Classification

| case_id | regime | evidence | short note |
|---|---|---|---|
| main_chain_8 | stable | completed=1.000; timeout_rate=0.000; exact_available=True | all methods mostly run; anchors available |
| main_ring_8 | stable | completed=1.000; timeout_rate=0.000; exact_available=True | all methods mostly run; anchors available |
| main_tree_8 | stable | completed=1.000; timeout_rate=0.000; exact_available=True | all methods mostly run; anchors available |
| main_grid2d_3x3 | stable | completed=1.000; timeout_rate=0.000; exact_available=True | all methods mostly run; anchors available |
| main_random_8 | stable | completed=1.000; timeout_rate=0.000; exact_available=True | all methods mostly run; anchors available |
| medium_chain_10 | boundary | completed=0.125; timeout_rate=0.875; exact_available=False | timeouts/low completion or missing exact anchor |
| medium_ring_10 | boundary | completed=0.000; timeout_rate=1.000; exact_available=False | timeouts/low completion or missing exact anchor |
| medium_tree_10 | boundary | completed=0.000; timeout_rate=1.000; exact_available=False | timeouts/low completion or missing exact anchor |
| medium_grid2d_3x4 | boundary | completed=0.000; timeout_rate=1.000; exact_available=False | timeouts/low completion or missing exact anchor |
| medium_random_10 | boundary | completed=0.250; timeout_rate=0.750; exact_available=False | timeouts/low completion or missing exact anchor |
| boundary_ring_12 | boundary | completed=0.000; timeout_rate=1.000; exact_available=False | timeouts/low completion or missing exact anchor |
| boundary_grid2d_4x4 | boundary | completed=0.000; timeout_rate=1.000; exact_available=False | timeouts/low completion or missing exact anchor |
| boundary_random_12 | boundary | completed=0.000; timeout_rate=1.000; exact_available=False | timeouts/low completion or missing exact anchor |

## Table 5: Cross-case Summary by Method x Scale

| scale | method | avg rel_error | avg total_time_sec | success rate | timeout rate | avg t_contract_ratio |
|---|---|---:|---:|---:|---:|---:|
| easy | exact | 0.000000 | 8.6062 | 1.000 | 0.000 | 1.0000 |
| easy | fixed-rank baseline | 0.673083 | 0.0315 | 1.000 | 0.000 | 0.9979 |
| easy | ASTNC-L1 | 0.000000 | 0.0930 | 1.000 | 0.000 | 0.9994 |
| easy | ASTNC-L2 | 0.002143 | 0.1185 | 1.000 | 0.000 | 0.9990 |
| easy | ASTNC-L3 | 0.019463 | 0.1294 | 1.000 | 0.000 | 0.9993 |
| medium | exact | NA | NA | 0.000 | 1.000 | NA |
| medium | fixed-rank baseline | NA | NA | NA | NA | NA |
| medium | ASTNC-L1 | 0.001668 | 2.4133 | 0.200 | 0.800 | 0.9978 |
| medium | ASTNC-L2 | NA | NA | 0.000 | 1.000 | NA |
| medium | ASTNC-L3 | 0.046085 | 4.4098 | 0.100 | 0.900 | 0.9999 |
| boundary | exact | NA | NA | 0.000 | 1.000 | NA |
| boundary | fixed-rank baseline | NA | NA | NA | NA | NA |
| boundary | ASTNC-L1 | NA | NA | 0.000 | 1.000 | NA |
| boundary | ASTNC-L2 | NA | NA | 0.000 | 1.000 | NA |
| boundary | ASTNC-L3 | NA | NA | 0.000 | 1.000 | NA |

Note: boundary scale may have limited exact availability; speedup columns are NA when exact is unavailable.
