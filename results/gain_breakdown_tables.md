# Gain Breakdown Tables (Section 3.3)

Data source: `results/main_results_raw_runs.csv` from Section 3.2. No extra runs were executed for this analysis.

## Table 1: Stage Time Decomposition (Core Cases)

### main_ring_8

| method | contract_time_sec (mean +/- std) | emit_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio | t_emit_ratio | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| exact | 3.0072 +/- 0.1122 | 0.000063 +/- 0.000002 | 3.0072 +/- 0.1122 | 1.0000 +/- 0.0000 | 0.000021 +/- 0.000000 | 3/3 |
| fixed-rank baseline | 0.0243 +/- 0.0012 | 0.000035 +/- 0.000004 | 0.0244 +/- 0.0012 | 0.9986 +/- 0.0001 | 0.001438 +/- 0.000084 | 3/3 |
| ASTNC-L2 | 0.0534 +/- 0.0011 | 0.000037 +/- 0.000000 | 0.0534 +/- 0.0011 | 0.9993 +/- 0.0000 | 0.000694 +/- 0.000020 | 3/3 |

### main_tree_8

| method | contract_time_sec (mean +/- std) | emit_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio | t_emit_ratio | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| exact | 1.1068 +/- 0.1835 | 0.000051 +/- 0.000007 | 1.1068 +/- 0.1835 | 1.0000 +/- 0.0000 | 0.000046 +/- 0.000005 | 3/3 |
| fixed-rank baseline | 0.0191 +/- 0.0046 | 0.000037 +/- 0.000003 | 0.0192 +/- 0.0046 | 0.9980 +/- 0.0004 | 0.001985 +/- 0.000382 | 3/3 |
| ASTNC-L2 | 0.0223 +/- 0.0041 | 0.000032 +/- 0.000005 | 0.0224 +/- 0.0041 | 0.9985 +/- 0.0003 | 0.001454 +/- 0.000307 | 3/3 |

### main_grid2d_3x3

| method | contract_time_sec (mean +/- std) | emit_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio | t_emit_ratio | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| exact | 37.1994 +/- 4.2547 | 0.000155 +/- 0.000031 | 37.1995 +/- 4.2548 | 1.0000 +/- 0.0000 | 0.000004 +/- 0.000000 | 3/3 |
| fixed-rank baseline | 0.0656 +/- 0.0019 | 0.000158 +/- 0.000054 | 0.0657 +/- 0.0019 | 0.9976 +/- 0.0009 | 0.002428 +/- 0.000897 | 3/3 |
| ASTNC-L2 | 0.4424 +/- 0.0310 | 0.000147 +/- 0.000042 | 0.4426 +/- 0.0310 | 0.9997 +/- 0.0001 | 0.000333 +/- 0.000088 | 3/3 |

### main_random_8

| method | contract_time_sec (mean +/- std) | emit_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio | t_emit_ratio | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| exact | 0.7325 +/- 0.4783 | 0.000038 +/- 0.000004 | 0.7326 +/- 0.4783 | 0.9999 +/- 0.0001 | 0.000076 +/- 0.000061 | 3/3 |
| fixed-rank baseline | 0.0337 +/- 0.0281 | 0.000035 +/- 0.000003 | 0.0337 +/- 0.0281 | 0.9984 +/- 0.0011 | 0.001587 +/- 0.001058 | 3/3 |
| ASTNC-L2 | 0.0524 +/- 0.0302 | 0.000032 +/- 0.000003 | 0.0524 +/- 0.0302 | 0.9993 +/- 0.0003 | 0.000722 +/- 0.000310 | 3/3 |

Optional reference only: `main_chain_8` (easiest case; excluded from core conclusion).

| method | contract_time_sec (mean +/- std) | emit_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio | t_emit_ratio | n_ok/3 |
|---|---:|---:|---:|---:|---:|---:|
| exact | 0.9851 +/- 0.0514 | 0.000048 +/- 0.000000 | 0.9851 +/- 0.0514 | 1.0000 +/- 0.0000 | 0.000049 +/- 0.000002 | 3/3 |
| fixed-rank baseline | 0.0145 +/- 0.0027 | 0.000047 +/- 0.000029 | 0.0146 +/- 0.0027 | 0.9969 +/- 0.0013 | 0.003072 +/- 0.001291 | 3/3 |
| ASTNC-L2 | 0.0216 +/- 0.0006 | 0.000035 +/- 0.000002 | 0.0216 +/- 0.0006 | 0.9984 +/- 0.0001 | 0.001608 +/- 0.000057 | 3/3 |

## Table 2: Stage Speedup vs Exact (Core Cases)

### main_ring_8

| method | contract_speedup_vs_exact | emit_speedup_vs_exact | total_speedup_vs_exact |
|---|---:|---:|---:|
| fixed-rank baseline | 123.76x | 1.82x | 123.58x |
| ASTNC-L2 | 56.37x | 1.71x | 56.33x |

### main_tree_8

| method | contract_speedup_vs_exact | emit_speedup_vs_exact | total_speedup_vs_exact |
|---|---:|---:|---:|
| fixed-rank baseline | 60.53x | 1.39x | 60.40x |
| ASTNC-L2 | 50.65x | 1.62x | 50.58x |

### main_grid2d_3x3

| method | contract_speedup_vs_exact | emit_speedup_vs_exact | total_speedup_vs_exact |
|---|---:|---:|---:|
| fixed-rank baseline | 567.76x | 1.06x | 566.38x |
| ASTNC-L2 | 84.36x | 1.11x | 84.33x |

### main_random_8

| method | contract_speedup_vs_exact | emit_speedup_vs_exact | total_speedup_vs_exact |
|---|---:|---:|---:|
| fixed-rank baseline | 32.31x | 1.09x | 32.25x |
| ASTNC-L2 | 16.92x | 1.22x | 16.91x |

## Table 3: Gain Share Decomposition (Core Cases)

`gain_share_*` is only reported when `delta_total > 0`; otherwise NA.

### main_ring_8

| method | delta_total | delta_contract | delta_emit | gain_share_contract | gain_share_emit |
|---|---:|---:|---:|---:|---:|
| fixed-rank baseline | 2.9828 | 2.9828 | 0.000028 | 1.0000 | 0.000009 |
| ASTNC-L2 | 2.9538 | 2.9538 | 0.000026 | 1.0000 | 0.000009 |

### main_tree_8

| method | delta_total | delta_contract | delta_emit | gain_share_contract | gain_share_emit |
|---|---:|---:|---:|---:|---:|
| fixed-rank baseline | 1.0876 | 1.0876 | 0.000014 | 1.0000 | 0.000013 |
| ASTNC-L2 | 1.0844 | 1.0844 | 0.000019 | 1.0000 | 0.000017 |

### main_grid2d_3x3

| method | delta_total | delta_contract | delta_emit | gain_share_contract | gain_share_emit |
|---|---:|---:|---:|---:|---:|
| fixed-rank baseline | 37.1338 | 37.1338 | -0.000004 | 1.0000 | -0.000000 |
| ASTNC-L2 | 36.7569 | 36.7569 | 0.000007 | 1.0000 | 0.000000 |

### main_random_8

| method | delta_total | delta_contract | delta_emit | gain_share_contract | gain_share_emit |
|---|---:|---:|---:|---:|---:|
| fixed-rank baseline | 0.6989 | 0.6989 | 0.000003 | 1.0000 | 0.000004 |
| ASTNC-L2 | 0.6802 | 0.6802 | 0.000007 | 1.0000 | 0.000010 |

## Table 4: Cross-case Aggregate (Core Cases Only)

| method | avg t_contract_ratio | avg t_emit_ratio | avg contract_speedup_vs_exact | avg total_speedup_vs_exact | geo contract_speedup_vs_exact | geo total_speedup_vs_exact | avg gain_share_contract | avg gain_share_emit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| exact | 1.0000 | 0.000037 | 1.00x | 1.00x | 1.00x | 1.00x | NA | NA |
| fixed-rank baseline | 0.9981 | 0.001860 | 196.09x | 195.65x | 108.27x | 108.06x | 1.0000 | 0.000007 |
| ASTNC-L2 | 0.9992 | 0.000801 | 52.07x | 52.03x | 44.93x | 44.89x | 1.0000 | 0.000009 |

## Supplement: Log-scale Time Magnitude (Core Cases)

| method | avg log10(contract_time_sec) | avg log10(emit_time_sec) | avg gap (contract - emit) |
|---|---:|---:|---:|
| exact | 0.4692 | -4.1824 | 4.6516 |
| fixed-rank baseline | -1.5233 | -4.2902 | 2.7670 |
| ASTNC-L2 | -1.1522 | -4.3189 | 3.1667 |
