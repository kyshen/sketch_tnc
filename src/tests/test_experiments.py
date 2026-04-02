import json

from omegaconf import OmegaConf

from src.config import validate_config
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
    (run_dir / "metrics.json").write_text(json.dumps({"NMSE_dB": -3.0, "total_time_sec": 1.25}), encoding="utf-8")
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
