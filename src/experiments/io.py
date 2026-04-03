from __future__ import annotations

from datetime import datetime, timezone
import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, List

from omegaconf import DictConfig, OmegaConf

from src.utils import _dump_json

if TYPE_CHECKING:
    from src.types import Result


METRICS_FILENAME = "metrics.json"
LEGACY_METRICS_FILENAME = "eval.json"
MANIFEST_FILENAME = "manifest.json"
RESOLVED_CONFIG_FILENAME = "resolved_config.yaml"
SUMMARY_JSONL_FILENAME = "summary.jsonl"
SUMMARY_CSV_FILENAME = "summary.csv"
PREFERRED_SUMMARY_FIELDS = [
    "run_dir",
    "reference_available",
    "reference_metric_status",
    "rel_error",
    "RMSE",
    "NMSE",
    "NMSE_dB",
    "total_time_sec",
    "contract_time_sec",
    "emit_time_sec",
    "speedup_vs_exact",
    "cache_hit_rate",
    "cache_hits",
    "cache_misses",
    "num_cached_states",
    "num_exact_merges",
    "num_compressed_merges",
    "num_implicit_merge_sketches",
    "num_explicit_merge_compressions",
    "num_exact_leaves",
    "num_compressed_leaves",
    "mean_leaf_residual_ratio",
    "mean_merge_residual_ratio",
    "skipped_small_rank_merges",
    "skipped_small_state_merges",
    "skipped_low_saving_merges",
    "num_blocks",
    "peak_rank",
    "max_rank",
    "mean_rank",
    "cfg.seed",
    "cfg.data.name",
    "cfg.data.generator",
    "cfg.method.name",
    "cfg.method.rank_policy",
    "cfg.method.leaf_tol",
    "cfg.method.merge_tol",
    "cfg.method.target_rank",
    "cfg.block.block_labels",
    "cfg.block.chunk_size",
]


def save_experiment_run(
    out_dir: Path,
    cfg: DictConfig,
    result: "Result",
    manifest: Dict[str, Any],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    result.save(out_dir)
    if bool(cfg.experiment.write_metrics_json):
        _dump_json(out_dir / METRICS_FILENAME, result.eval)
    if bool(cfg.experiment.save_manifest):
        _dump_json(out_dir / MANIFEST_FILENAME, manifest)
    if bool(cfg.experiment.save_resolved_config):
        (out_dir / RESOLVED_CONFIG_FILENAME).write_text(
            OmegaConf.to_yaml(cfg, resolve=True),
            encoding="utf-8",
        )


def build_manifest(cfg: DictConfig, out_dir: Path) -> Dict[str, Any]:
    hydra_cfg = cfg.get("hydra")
    job_num = None
    if hydra_cfg is not None:
        job = hydra_cfg.get("job")
        if job is not None:
            job_num = job.get("num")
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(out_dir),
        "experiment": OmegaConf.to_container(cfg.experiment, resolve=True),
        "seed": int(cfg.seed),
        "task_name": str(cfg.task.name),
        "data_name": str(cfg.data.name),
        "method_name": str(cfg.method.name),
        "block_name": str(cfg.block.name),
        "hydra_job_num": job_num,
    }


def flatten_mapping(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    flat: Dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            flat.update(flatten_mapping(value, prefix=full_key))
        elif isinstance(value, list):
            flat[full_key] = json.dumps(value, ensure_ascii=False)
        else:
            flat[full_key] = value
    return flat


def load_run_record(run_dir: Path) -> Dict[str, Any] | None:
    metrics_path = run_dir / METRICS_FILENAME
    if not metrics_path.exists():
        legacy_metrics = run_dir / LEGACY_METRICS_FILENAME
        if not legacy_metrics.exists():
            return None
        metrics_path = legacy_metrics
    record: Dict[str, Any] = {"run_dir": str(run_dir)}
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    record.update(metrics)
    resolved_config_path = run_dir / RESOLVED_CONFIG_FILENAME
    if resolved_config_path.exists():
        resolved = OmegaConf.to_container(
            OmegaConf.load(resolved_config_path),
            resolve=True,
        )
        if isinstance(resolved, dict):
            record.update(flatten_mapping(resolved, prefix="cfg"))
    manifest_path = run_dir / MANIFEST_FILENAME
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        record.update(flatten_mapping(manifest, prefix="manifest"))
    return record


def write_summary(records: Iterable[Dict[str, Any]], output_dir: Path) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = list(records)
    jsonl_path = output_dir / SUMMARY_JSONL_FILENAME
    csv_path = output_dir / SUMMARY_CSV_FILENAME
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    fieldnames: List[str] = [name for name in PREFERRED_SUMMARY_FIELDS if any(name in row for row in rows)]
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return {"jsonl": jsonl_path, "csv": csv_path}
