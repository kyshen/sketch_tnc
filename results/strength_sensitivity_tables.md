# Strength Sensitivity Tables (Section 3.5)

Seeds: `[0, 1, 2]`; methods: `ASTNC-L1`, `ASTNC-L2`, `ASTNC-L3`.
Core cases: `main_ring_8, main_grid2d_3x3, main_random_8`.
Optional `main_tree_8` included: `False`.

## Table 1: Per-case Strength Sensitivity Main Table

### main_ring_8

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio (mean +/- std) | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L1 | 0.000000 +/- 0.000000 | -287.032 +/- 0.492 | 0.0478 +/- 0.0057 | 0.0478 +/- 0.0057 | 0.9993 +/- 0.0000 | 3/3 |
| ASTNC-L2 | 0.001827 +/- 0.003164 | -206.616 +/- 139.771 | 0.0534 +/- 0.0011 | 0.0534 +/- 0.0011 | 0.9993 +/- 0.0000 | 3/3 |
| ASTNC-L3 | 0.015534 +/- 0.004440 | -36.394 +/- 2.341 | 0.0494 +/- 0.0053 | 0.0495 +/- 0.0053 | 0.9984 +/- 0.0016 | 3/3 |

### main_grid2d_3x3

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio (mean +/- std) | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L1 | 0.000000 +/- 0.000000 | -265.308 +/- 13.637 | 0.1906 +/- 0.0068 | 0.1907 +/- 0.0068 | 0.9995 +/- 0.0001 | 3/3 |
| ASTNC-L2 | 0.004078 +/- 0.000417 | -47.823 +/- 0.902 | 0.4424 +/- 0.0310 | 0.4426 +/- 0.0310 | 0.9997 +/- 0.0001 | 3/3 |
| ASTNC-L3 | 0.018051 +/- 0.000644 | -34.874 +/- 0.310 | 0.3330 +/- 0.1237 | 0.3331 +/- 0.1237 | 0.9996 +/- 0.0001 | 3/3 |

### main_random_8

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio (mean +/- std) | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L1 | 0.000000 +/- 0.000000 | -282.555 +/- 6.115 | 0.0547 +/- 0.0337 | 0.0547 +/- 0.0337 | 0.9993 +/- 0.0003 | 3/3 |
| ASTNC-L2 | 0.000000 +/- 0.000000 | -280.042 +/- 13.126 | 0.0524 +/- 0.0302 | 0.0524 +/- 0.0302 | 0.9993 +/- 0.0003 | 3/3 |
| ASTNC-L3 | 0.012649 +/- 0.018338 | -115.789 +/- 134.299 | 0.0545 +/- 0.0345 | 0.0545 +/- 0.0345 | 0.9992 +/- 0.0003 | 3/3 |

## Table 2: Relative Change vs ASTNC-L2

### main_ring_8

| method | delta_rel_error | delta_contract_time | delta_total_time | contract_ratio_vs_L2 | time_ratio_vs_L2 |
|---|---:|---:|---:|---:|---:|
| ASTNC-L1 | -0.001827 | -0.0056 | -0.0056 | 0.8952 | 0.8952 |
| ASTNC-L3 | 0.013707 | -0.0040 | -0.0039 | 0.9256 | 0.9264 |

### main_grid2d_3x3

| method | delta_rel_error | delta_contract_time | delta_total_time | contract_ratio_vs_L2 | time_ratio_vs_L2 |
|---|---:|---:|---:|---:|---:|
| ASTNC-L1 | -0.004078 | -0.2519 | -0.2519 | 0.4307 | 0.4308 |
| ASTNC-L3 | 0.013973 | -0.1094 | -0.1095 | 0.7527 | 0.7527 |

### main_random_8

| method | delta_rel_error | delta_contract_time | delta_total_time | contract_ratio_vs_L2 | time_ratio_vs_L2 |
|---|---:|---:|---:|---:|---:|
| ASTNC-L1 | -0.000000 | 0.0023 | 0.0023 | 1.0445 | 1.0445 |
| ASTNC-L3 | 0.012649 | 0.0022 | 0.0022 | 1.0412 | 1.0412 |

## Table 3: Internal Statistics Changes

### main_ring_8

| method | mean_rank | peak_rank | num_compressed_merges | mean_merge_residual_ratio | num_implicit_merge_sketches | cache_hit_rate |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L1 | 1.000 | 16.000 | 36.000 | 0.000000 | 0.000 | 0.4444 |
| ASTNC-L2 | 1.000 | 16.000 | 36.000 | 0.000128 | 0.000 | 0.4444 |
| ASTNC-L3 | 1.000 | 16.000 | 37.000 | 0.001982 | 0.000 | 0.4444 |

### main_grid2d_3x3

| method | mean_rank | peak_rank | num_compressed_merges | mean_merge_residual_ratio | num_implicit_merge_sketches | cache_hit_rate |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L1 | 1.000 | 64.000 | 36.000 | 0.000000 | 18.000 | 0.4397 |
| ASTNC-L2 | 1.000 | 64.000 | 36.000 | 0.000403 | 13.667 | 0.4397 |
| ASTNC-L3 | 1.000 | 64.000 | 36.000 | 0.002646 | 8.000 | 0.4397 |

### main_random_8

| method | mean_rank | peak_rank | num_compressed_merges | mean_merge_residual_ratio | num_implicit_merge_sketches | cache_hit_rate |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L1 | 1.000 | 63.000 | 23.000 | 0.000000 | 2.000 | 0.4148 |
| ASTNC-L2 | 1.000 | 63.000 | 23.000 | 0.000000 | 2.000 | 0.4148 |
| ASTNC-L3 | 1.000 | 62.333 | 25.000 | 0.001417 | 2.000 | 0.4148 |

## Table 4: Cross-case Summary (Core Cases)

| method | avg rel_error | avg total_time_sec | avg delta_rel_error vs L2 | avg delta_total_time vs L2 | avg t_contract_ratio | gmean total_time_ratio_vs_L2 | gmean contract_ratio_vs_L2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| ASTNC-L1 | 0.000000 | 0.0977 | -0.001968 | -0.0851 | 0.9994 | 0.7385 | 0.7385 |
| ASTNC-L2 | 0.001968 | 0.1828 | 0.000000 | 0.0000 | 0.9994 | 1.0000 | 1.0000 |
| ASTNC-L3 | 0.015411 | 0.1457 | 0.013443 | -0.0371 | 0.9991 | 0.8988 | 0.8985 |

