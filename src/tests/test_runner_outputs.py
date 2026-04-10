from omegaconf import OmegaConf

from src.config import validate_config
from src.runner.io import RESULT_COLUMNS, build_run_row, write_run_outputs


def test_validate_config_keeps_global_seed_consistent():
    cfg = OmegaConf.create({
        "seed": 9,
        "task": {"name": "materialize"},
        "data": {"name": "ring", "generator": "ring", "seed": 9},
        "method": {"name": "astnc", "seed": 9},
        "block": {"name": "default"},
        "experiment": {"name": "unit", "group": "tests"},
        "hydra": {"job": {"num": 0}},
    })
    validated = validate_config(cfg)
    assert int(validated.seed) == 9
    assert int(validated.data.seed) == 9
    assert int(validated.method.seed) == 9
    assert str(validated.method.rank_policy) == "adaptive"


def test_build_run_row_contains_required_columns():
    cfg = OmegaConf.create({
        "seed": 3,
        "experiment": {"name": "ring_demo"},
        "data": {"name": "ring", "generator": "ring"},
        "method": {"name": "astnc", "rank_policy": "fixed", "target_rank": 5, "oversample": 2, "n_power_iter": 1},
    })
    row = build_run_row(
        cfg,
        metrics={"rel_error": 0.1, "NMSE": 0.2, "total_time_sec": 1.5, "contract_time_sec": 1.0, "emit_time_sec": 0.5},
        status="ok",
    )
    for key in RESULT_COLUMNS:
        assert key in row
    assert row["fixed_rank"] == 5
    assert row["status"] == "ok"


def test_write_run_outputs_writes_required_files(tmp_path):
    cfg = OmegaConf.create({
        "seed": 7,
        "experiment": {"name": "smoke"},
        "data": {"name": "ring", "generator": "ring"},
        "method": {"name": "exact"},
    })
    row = build_run_row(
        cfg,
        metrics={"rel_error": 0.0, "NMSE": 0.0, "total_time_sec": 0.1, "contract_time_sec": 0.08, "emit_time_sec": 0.02},
        status="ok",
    )
    outputs = write_run_outputs(tmp_path, cfg, [row])
    assert outputs["runs_parquet"].exists()
    assert outputs["runs_csv"].exists()
    assert outputs["config_snapshot"].exists()
    assert outputs["readme_results"].exists()
    csv_text = outputs["runs_csv"].read_text(encoding="utf-8")
    assert "family,instance,topology,size_description,method,method_variant,status" in csv_text
