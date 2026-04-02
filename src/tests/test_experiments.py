import json

import numpy as np

from omegaconf import OmegaConf

from src.config import validate_config
from src.core.state import SeparatorState, merge_states
from src.experiments.aggregate import aggregate_runs


def test_validate_config_keeps_global_seed_consistent():
    cfg = OmegaConf.create({
        "seed": 9,
        "task": {"name": "materialize"},
        "data": {"name": "ring", "generator": "ring", "seed": 9},
        "method": {"name": "boss", "seed": 9},
        "block": {"name": "default"},
        "experiment": {"name": "unit", "group": "tests"},
        "hydra": {"job": {"num": 0}},
    })
    validated = validate_config(cfg)
    assert int(validated.seed) == 9
    assert int(validated.data.seed) == 9
    assert int(validated.method.seed) == 9


def test_aggregate_runs_writes_summary_files(tmp_path):
    run_dir = tmp_path / "outputs" / "paper" / "demo" / "run_0"
    run_dir.mkdir(parents=True)
    (run_dir / "metrics.json").write_text(
        json.dumps({"reference_available": True, "NMSE_dB": -3.0, "total_time_sec": 1.25, "cache_hit_rate": 0.5}),
        encoding="utf-8",
    )
    (run_dir / "manifest.json").write_text(
        json.dumps({"seed": 3, "experiment": {"name": "demo", "group": "paper"}}),
        encoding="utf-8",
    )
    (run_dir / "resolved_config.yaml").write_text(
        "seed: 3\nmethod:\n  name: boss\ndata:\n  generator: ring\n",
        encoding="utf-8",
    )

    outputs = aggregate_runs(tmp_path / "outputs")

    assert outputs["csv"].exists()
    assert outputs["jsonl"].exists()
    csv_text = outputs["csv"].read_text(encoding="utf-8")
    assert "reference_available" in csv_text
    assert "cache_hit_rate" in csv_text


def test_merge_states_can_skip_compression_for_small_merges():
    left = SeparatorState(
        open_labels=[0],
        open_dims=[2],
        boundary_labels=[10],
        boundary_dims=[2],
        A=np.array([[1.0, 0.0], [0.0, 1.0]]),
        B=np.array([[1.0, 2.0], [3.0, 4.0]]),
    )
    right = SeparatorState(
        open_labels=[1],
        open_dims=[2],
        boundary_labels=[10],
        boundary_dims=[2],
        A=np.array([[1.0, 1.0], [0.5, -0.5]]),
        B=np.array([[2.0, 1.0], [0.0, 1.0]]),
    )

    state, info = merge_states(
        left,
        right,
        cut_labels=[10],
        parent_boundary_labels=[],
        label_dims={10: 2},
        target_rank=1,
        randomized=False,
        compress_min_rank_product=8,
        compress_max_exact_size=0,
        compress_min_saving_ratio=0.0,
    )

    assert info.compressed is False
    assert info.reason == "rank_product_too_small"
    assert state.rank == 4


def test_merge_states_compresses_when_savings_are_large():
    left = SeparatorState(
        open_labels=[0],
        open_dims=[2],
        boundary_labels=[10],
        boundary_dims=[2],
        A=np.array([[1.0, 0.0], [0.0, 1.0]]),
        B=np.array([[1.0, 2.0], [3.0, 4.0]]),
    )
    right = SeparatorState(
        open_labels=[1],
        open_dims=[2],
        boundary_labels=[10],
        boundary_dims=[2],
        A=np.array([[1.0, 1.0], [0.5, -0.5]]),
        B=np.array([[2.0, 1.0], [0.0, 1.0]]),
    )

    state, info = merge_states(
        left,
        right,
        cut_labels=[10],
        parent_boundary_labels=[],
        label_dims={10: 2},
        target_rank=1,
        randomized=False,
        compress_min_rank_product=0,
        compress_max_exact_size=0,
        compress_min_saving_ratio=0.1,
    )

    assert info.compressed is True
    assert info.reason == "compressed"
    assert state.rank == 1


def test_validate_config_enables_implicit_merge_sketch_by_default():
    cfg = OmegaConf.create({
        "seed": 3,
        "task": {"name": "materialize"},
        "data": {"name": "ring", "generator": "ring", "seed": 3},
        "method": {"name": "boss", "seed": 3},
        "block": {"name": "default"},
        "experiment": {"name": "unit", "group": "tests"},
        "hydra": {"job": {"num": 0}},
    })
    validated = validate_config(cfg)
    assert bool(validated.method.implicit_merge_sketch) is True
