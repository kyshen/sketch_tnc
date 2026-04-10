# Main Results Tables

## Table 1: Per-case Aggregated Main Results

### main_ring_8
Topology: `ring`; Size: `num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1`

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | speedup_vs_exact | t_contract_ratio | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| exact | 0.000000 +/- 0.000000 | NA | 3.0072 +/- 0.1122 | 3.0072 +/- 0.1122 | 1.00x | 1.0000 +/- 0.0000 | 3/3 |
| fixed-rank baseline | 0.805755 +/- 0.027809 | -1.879 +/- 0.300 | 0.0243 +/- 0.0012 | 0.0244 +/- 0.0012 | 123.39x | 0.9986 +/- 0.0001 | 3/3 |
| ASTNC-L2 | 0.001827 +/- 0.003164 | -206.616 +/- 139.771 | 0.0534 +/- 0.0011 | 0.0534 +/- 0.0011 | 56.31x | 0.9993 +/- 0.0000 | 3/3 |

### main_tree_8
Topology: `tree`; Size: `num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1`

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | speedup_vs_exact | t_contract_ratio | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| exact | 0.000000 +/- 0.000000 | NA | 1.1068 +/- 0.1835 | 1.1068 +/- 0.1835 | 1.00x | 1.0000 +/- 0.0000 | 3/3 |
| fixed-rank baseline | 0.652428 +/- 0.017929 | -3.712 +/- 0.237 | 0.0191 +/- 0.0046 | 0.0192 +/- 0.0046 | 57.69x | 0.9980 +/- 0.0004 | 3/3 |
| ASTNC-L2 | 0.004810 +/- 0.006255 | -126.696 +/- 141.335 | 0.0223 +/- 0.0041 | 0.0224 +/- 0.0041 | 49.45x | 0.9985 +/- 0.0003 | 3/3 |

### main_grid2d_3x3
Topology: `grid2d`; Size: `grid_shape=[3,3], phys_dim=3, bond_dim=4, open_legs_per_node=1`

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | speedup_vs_exact | t_contract_ratio | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| exact | 0.000000 +/- 0.000000 | NA | 37.1994 +/- 4.2547 | 37.1995 +/- 4.2548 | 1.00x | 1.0000 +/- 0.0000 | 3/3 |
| fixed-rank baseline | 0.978913 +/- 0.001771 | -0.185 +/- 0.016 | 0.0656 +/- 0.0019 | 0.0657 +/- 0.0019 | 566.07x | 0.9976 +/- 0.0009 | 3/3 |
| ASTNC-L2 | 0.004078 +/- 0.000417 | -47.823 +/- 0.902 | 0.4424 +/- 0.0310 | 0.4426 +/- 0.0310 | 84.05x | 0.9997 +/- 0.0001 | 3/3 |

### main_random_8
Topology: `random_connected`; Size: `num_nodes=8, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1`

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | speedup_vs_exact | t_contract_ratio | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| exact | 0.000000 +/- 0.000000 | NA | 0.7325 +/- 0.4783 | 0.7326 +/- 0.4783 | 1.00x | 0.9999 +/- 0.0001 | 3/3 |
| fixed-rank baseline | 0.928319 +/- 0.063717 | -0.660 +/- 0.601 | 0.0337 +/- 0.0281 | 0.0337 +/- 0.0281 | 21.72x | 0.9984 +/- 0.0011 | 3/3 |
| ASTNC-L2 | 0.000000 +/- 0.000000 | -280.042 +/- 13.126 | 0.0524 +/- 0.0302 | 0.0524 +/- 0.0302 | 13.98x | 0.9993 +/- 0.0003 | 3/3 |

### main_chain_8 (optional reference row)
Topology: `chain`; Size: `num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1`

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | speedup_vs_exact | t_contract_ratio | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| exact | 0.000000 +/- 0.000000 | NA | 0.9851 +/- 0.0514 | 0.9851 +/- 0.0514 | 1.00x | 1.0000 +/- 0.0000 | 3/3 |
| fixed-rank baseline | 0.000000 +/- 0.000000 | -290.989 +/- 2.511 | 0.0145 +/- 0.0027 | 0.0146 +/- 0.0027 | 67.51x | 0.9969 +/- 0.0013 | 3/3 |
| ASTNC-L2 | 0.000000 +/- 0.000000 | -291.827 +/- 0.835 | 0.0216 +/- 0.0006 | 0.0216 +/- 0.0006 | 45.63x | 0.9984 +/- 0.0001 | 3/3 |

## Table 2: Cross-case Summary (Core Main Cases Only)

Core cases: `main_ring_8`, `main_tree_8`, `main_grid2d_3x3`, `main_random_8`.

| method | avg rel_error | avg NMSE_dB | avg total_time_sec | avg speedup_vs_exact | geo mean speedup_vs_exact | avg t_contract_ratio |
|---|---:|---:|---:|---:|---:|---:|
| exact | 0.000000 | NA | 10.5115 | 1.00x | 1.00x | 1.0000 |
| fixed-rank baseline | 0.841354 | -1.609 | 0.0357 | 192.22x | 96.73x | 0.9981 |
| ASTNC-L2 | 0.002679 | -165.295 | 0.1427 | 50.95x | 42.53x | 0.9992 |

## Table 3: ASTNC-L2 Internal Statistics by Case

| case_id | num_blocks | mean_rank | peak_rank | num_exact_merges | num_compressed_merges | mean_merge_residual_ratio | cache_hit_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| main_ring_8 | 9.00 | 1.00 | 16.00 | 27.00 | 36.00 | 0.000128 | 0.4444 |
| main_tree_8 | 9.00 | 1.00 | 14.67 | 18.00 | 35.00 | 0.000222 | 0.4341 |
| main_grid2d_3x3 | 9.00 | 1.00 | 64.00 | 30.00 | 36.00 | 0.000403 | 0.4397 |
| main_random_8 | 9.00 | 1.00 | 63.00 | 20.00 | 23.00 | 0.000000 | 0.4148 |
| main_chain_8 | 9.00 | 1.00 | 4.00 | 18.00 | 45.00 | 0.000000 | 0.4444 |

Note: For paper-facing tables, `exact` row speedup is reported as `1.00x`; raw exported `speedup_vs_exact` values remain in CSV for diagnostics.