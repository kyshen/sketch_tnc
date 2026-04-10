# Setup Notes (Experimental Setup & Benchmark Protocol)

## 1) Engineering Readiness Check

Checked on 2026-04-10 (Asia/Shanghai):

- Entry script: `run.py` works with Hydra overrides.
- Hydra/config stack: consistent (`configs/{data,method,task,block,experiment,hydra}`).
- Result export path: `outputs/<group>/<experiment>/<timestamp>/runs.csv|runs.parquet` is functional.
- Tests: `pytest -q` passed after minimal fixes (11/11).

## 2) Minimal Non-Algorithmic Fixes Applied

### Fix A: Extend run table schema and metric passthrough
- File: `src/runner/io.py`
- Problem:
  - Existing `runs.csv` only exported a narrow legacy column set and dropped many ASTNC internal stats needed by paper benchmarking.
  - Missing direct fields for `topology` and `size_description`.
- Change:
  - Expanded default columns to include requested accuracy/time/internal-stat fields.
  - Added `topology` and generated `size_description` from config.
  - Enabled scalar metric passthrough from `task.evaluate()` so additional internal counters are kept in table output.
  - Made CSV/Parquet column resolution dynamic (base columns + discovered scalar fields).
- Scope/safety:
  - No algorithm logic change.
  - Output-layer only.

### Fix B: Adaptive-refine argument mismatch (latent bug)
- File: `src/core/algorithms.py`
- Problem:
  - `_maybe_refine_block(...)` signature did not accept `depth_info`/`max_depth`, while call-site passed them.
  - This would fail if `adaptive_refine=true` was enabled.
- Change:
  - Added optional `depth_info` and `max_depth` args and forwarded them to `_build_state(...)` inside refine loop.
- Scope/safety:
  - No core algorithm policy change; only parameter plumbing.

### Fix C: test expectation update for expanded CSV header
- File: `src/tests/test_runner_outputs.py`
- Problem:
  - Test asserted old CSV prefix string.
- Change:
  - Updated assertion to the new leading header sequence.
- Scope/safety:
  - Test-only, no runtime effect.

## 3) Pilot Runner Utility (for this benchmark-protocol turn)

- Added helper script: `results/run_pilot.py`.
- Purpose: execute pilot matrix and export:
  - `results/pilot_raw_runs.csv`
  - `results/pilot_agg.csv`
- Notes:
  - Per-run timeout set to 180s for stress boundary screening.
  - Script reuses existing run outputs by experiment-name key when available.

## 4) Data/Metric Coverage vs Requested Fields

Requested core fields are now present in `pilot_raw_runs.csv`, including:

- basic: `topology`, `size_description`, `seed`, `method`
- accuracy: `rel_error`, `RMSE`, `NMSE`, `NMSE_dB`
- time: `contract_time_sec`, `emit_time_sec`, `total_time_sec`, `speedup_vs_exact`, `t_contract_ratio`
- ASTNC internals: `num_blocks`, `refined_blocks`, `mean_rank`, `max_rank`, `peak_rank`, `num_exact_merges`, `num_compressed_merges`, `num_exact_leaves`, `num_compressed_leaves`, `mean_leaf_residual_ratio`, `mean_merge_residual_ratio`, cache stats

## 5) Known Caveats (for interpretation)

- `speedup_vs_exact` on `method=exact` is not a strict 1.0 baseline because the pipeline separately computes exact reference in task evaluation; treat exact-row speedup only as diagnostic.
- Stress tier (`ring_10`, `grid2d_3x4`, `random_10`) hit timeout=180s in this pilot and is intentionally retained as boundary signal, not as final-table evidence.
- Pilot seeds use `{0,1}` for toy/main and `{0}` for stress to control runtime in this protocol-design round.
