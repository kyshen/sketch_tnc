# Core Mechanism Ablation Tables (Section 3.4)

Seeds: `[0, 1, 2]`. Core cases: `main_ring_8`, `main_grid2d_3x3`. Extended optional case included: `True`.

`fixed-rank baseline` is reported as a policy reference (not a single-mechanism ablation).

## Table 1: Per-case Core Ablation Main Table

### main_ring_8

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio (mean +/- std) | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L2 | 0.001827 +/- 0.003164 | -206.616 +/- 139.771 | 0.0534 +/- 0.0011 | 0.0534 +/- 0.0011 | 0.9993 +/- 0.0000 | 3/3 |
| ASTNC-L2-no-blockwise | 0.000000 +/- 0.000000 | -284.696 +/- 2.619 | 0.0290 +/- 0.0019 | 0.0291 +/- 0.0019 | 0.9995 +/- 0.0000 | 3/3 |
| ASTNC-L2-no-implicit | 0.001827 +/- 0.003164 | -206.616 +/- 139.771 | 0.0479 +/- 0.0046 | 0.0479 +/- 0.0046 | 0.9993 +/- 0.0000 | 3/3 |
| ASTNC-L2-no-cache | 0.001827 +/- 0.003164 | -206.616 +/- 139.771 | 0.0587 +/- 0.0017 | 0.0588 +/- 0.0017 | 0.9994 +/- 0.0000 | 3/3 |
| fixed-rank baseline | 0.805755 +/- 0.027809 | -1.879 +/- 0.300 | 0.0243 +/- 0.0012 | 0.0244 +/- 0.0012 | 0.9986 +/- 0.0001 | 3/3 |

### main_grid2d_3x3

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio (mean +/- std) | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L2 | 0.004078 +/- 0.000417 | -47.823 +/- 0.902 | 0.4424 +/- 0.0310 | 0.4426 +/- 0.0310 | 0.9997 +/- 0.0001 | 3/3 |
| ASTNC-L2-no-blockwise | 0.010640 +/- 0.000735 | -39.475 +/- 0.590 | 1.0635 +/- 0.0866 | 1.0635 +/- 0.0866 | 0.9999 +/- 0.0000 | 3/3 |
| ASTNC-L2-no-implicit | 0.004078 +/- 0.000417 | -47.823 +/- 0.902 | 3.0837 +/- 0.2757 | 3.0838 +/- 0.2757 | 1.0000 +/- 0.0000 | 3/3 |
| ASTNC-L2-no-cache | 0.004078 +/- 0.000417 | -47.823 +/- 0.902 | 0.3817 +/- 0.1626 | 0.3818 +/- 0.1627 | 0.9996 +/- 0.0001 | 3/3 |
| fixed-rank baseline | 0.978913 +/- 0.001771 | -0.185 +/- 0.016 | 0.0656 +/- 0.0019 | 0.0657 +/- 0.0019 | 0.9976 +/- 0.0009 | 3/3 |

### main_random_8

| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio (mean +/- std) | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L2 | 0.000000 +/- 0.000000 | -280.042 +/- 13.126 | 0.0524 +/- 0.0302 | 0.0524 +/- 0.0302 | 0.9993 +/- 0.0003 | 3/3 |
| ASTNC-L2-no-blockwise | 0.003501 +/- 0.003296 | -125.546 +/- 138.028 | 0.0968 +/- 0.1079 | 0.0969 +/- 0.1079 | 0.9997 +/- 0.0003 | 3/3 |
| ASTNC-L2-no-implicit | 0.000000 +/- 0.000000 | -286.951 +/- 2.035 | 0.0618 +/- 0.0352 | 0.0618 +/- 0.0352 | 0.9993 +/- 0.0003 | 3/3 |
| ASTNC-L2-no-cache | 0.000000 +/- 0.000000 | -280.042 +/- 13.126 | 0.1456 +/- 0.1276 | 0.1456 +/- 0.1276 | 0.9996 +/- 0.0004 | 3/3 |
| fixed-rank baseline | 0.928319 +/- 0.063717 | -0.660 +/- 0.601 | 0.0337 +/- 0.0281 | 0.0337 +/- 0.0281 | 0.9984 +/- 0.0011 | 3/3 |

## Table 2: Relative Change vs ASTNC-L2 (Case-wise)

### main_ring_8

| method | delta_rel_error | delta_contract_time | delta_total_time | contract_ratio_vs_ASTNC | time_ratio_vs_ASTNC |
|---|---:|---:|---:|---:|---:|
| ASTNC-L2-no-blockwise | -0.001827 | -0.0243 | -0.0243 | 0.5442 | 0.5441 |
| ASTNC-L2-no-implicit | 0.000000 | -0.0055 | -0.0055 | 0.8969 | 0.8969 |
| ASTNC-L2-no-cache | 0.000000 | 0.0054 | 0.0053 | 1.1003 | 1.1002 |
| fixed-rank baseline | 0.803929 | -0.0290 | -0.0290 | 0.4560 | 0.4564 |

### main_grid2d_3x3

| method | delta_rel_error | delta_contract_time | delta_total_time | contract_ratio_vs_ASTNC | time_ratio_vs_ASTNC |
|---|---:|---:|---:|---:|---:|
| ASTNC-L2-no-blockwise | 0.006562 | 0.6210 | 0.6209 | 2.4036 | 2.4029 |
| ASTNC-L2-no-implicit | 0.000000 | 2.6412 | 2.6412 | 6.9695 | 6.9675 |
| ASTNC-L2-no-cache | 0.000000 | -0.0608 | -0.0607 | 0.8627 | 0.8627 |
| fixed-rank baseline | 0.974835 | -0.3769 | -0.3769 | 0.1482 | 0.1485 |

### main_random_8

| method | delta_rel_error | delta_contract_time | delta_total_time | contract_ratio_vs_ASTNC | time_ratio_vs_ASTNC |
|---|---:|---:|---:|---:|---:|
| ASTNC-L2-no-blockwise | 0.003501 | 0.0445 | 0.0445 | 1.8496 | 1.8488 |
| ASTNC-L2-no-implicit | -0.000000 | 0.0094 | 0.0094 | 1.1803 | 1.1803 |
| ASTNC-L2-no-cache | 0.000000 | 0.0932 | 0.0932 | 2.7800 | 2.7791 |
| fixed-rank baseline | 0.928319 | -0.0187 | -0.0187 | 0.6435 | 0.6438 |

## Table 3: Internal Statistics Change (Case-wise)

### main_ring_8

| method | num_blocks | peak_rank | num_compressed_merges | num_implicit_merge_sketches | cache_hit_rate | num_cached_states |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L2 | 9.00 | 16.00 | 36.00 | 0.00 | 0.4444 | 75.00 |
| ASTNC-L2-no-blockwise | 1.00 | 16.00 | 6.00 | 0.00 | 0.0000 | 15.00 |
| ASTNC-L2-no-implicit | 9.00 | 16.00 | 36.00 | 0.00 | 0.4444 | 75.00 |
| ASTNC-L2-no-cache | 9.00 | 16.00 | 36.00 | 0.00 | 0.0000 | 0.00 |
| fixed-rank baseline | 9.00 | 9.00 | 36.00 | 27.00 | 0.4444 | 75.00 |

### main_grid2d_3x3

| method | num_blocks | peak_rank | num_compressed_merges | num_implicit_merge_sketches | cache_hit_rate | num_cached_states |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L2 | 9.00 | 64.00 | 36.00 | 13.67 | 0.4397 | 79.00 |
| ASTNC-L2-no-blockwise | 1.00 | 222.00 | 5.00 | 4.00 | 0.0000 | 17.00 |
| ASTNC-L2-no-implicit | 9.00 | 64.00 | 36.00 | 0.00 | 0.4397 | 79.00 |
| ASTNC-L2-no-cache | 9.00 | 64.00 | 36.00 | 13.67 | 0.0000 | 0.00 |
| fixed-rank baseline | 9.00 | 4.00 | 54.00 | 45.00 | 0.4397 | 79.00 |

### main_random_8

| method | num_blocks | peak_rank | num_compressed_merges | num_implicit_merge_sketches | cache_hit_rate | num_cached_states |
|---|---:|---:|---:|---:|---:|---:|
| ASTNC-L2 | 9.00 | 63.00 | 23.00 | 2.00 | 0.4148 | 55.00 |
| ASTNC-L2-no-blockwise | 1.00 | 142.67 | 4.33 | 1.33 | 0.0000 | 15.00 |
| ASTNC-L2-no-implicit | 9.00 | 63.00 | 23.00 | 0.00 | 0.4148 | 55.00 |
| ASTNC-L2-no-cache | 9.00 | 63.00 | 27.00 | 6.00 | 0.0000 | 0.00 |
| fixed-rank baseline | 9.00 | 7.33 | 25.00 | 13.00 | 0.4148 | 55.00 |

## Table 4: Cross-case Summary

### 2-case core summary (`main_ring_8`, `main_grid2d_3x3`)

| method | avg rel_error | avg total_time_sec | avg delta_total_time vs ASTNC-L2 | avg delta_rel_error vs ASTNC-L2 | avg t_contract_ratio |
|---|---:|---:|---:|---:|---:|
| ASTNC-L2 | 0.002952 | 0.2480 | 0.0000 | 0.000000 | 0.9995 |
| ASTNC-L2-no-blockwise | 0.005320 | 0.5463 | 0.2983 | 0.002368 | 0.9997 |
| ASTNC-L2-no-implicit | 0.002952 | 1.5659 | 1.3179 | 0.000000 | 0.9996 |
| ASTNC-L2-no-cache | 0.002952 | 0.2203 | -0.0277 | 0.000000 | 0.9995 |
| fixed-rank baseline | 0.892334 | 0.0450 | -0.2030 | 0.889382 | 0.9981 |

### 3-case extended summary (`main_ring_8`, `main_grid2d_3x3`, `main_random_8`)

| method | avg rel_error | avg total_time_sec | avg delta_total_time vs ASTNC-L2 | avg delta_rel_error vs ASTNC-L2 | avg t_contract_ratio |
|---|---:|---:|---:|---:|---:|
| ASTNC-L2 | 0.001968 | 0.1828 | 0.0000 | 0.000000 | 0.9994 |
| ASTNC-L2-no-blockwise | 0.004713 | 0.3965 | 0.2137 | 0.002745 | 0.9997 |
| ASTNC-L2-no-implicit | 0.001968 | 1.0645 | 0.8817 | -0.000000 | 0.9995 |
| ASTNC-L2-no-cache | 0.001968 | 0.1954 | 0.0126 | 0.000000 | 0.9995 |
| fixed-rank baseline | 0.904329 | 0.0413 | -0.1415 | 0.902361 | 0.9982 |

