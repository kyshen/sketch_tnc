from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable

from omegaconf import DictConfig, OmegaConf

RESULT_COLUMNS = [
    "family",
    "instance",
    "method",
    "status",
    "rel_error",
    "nmse",
    "total_time",
    "contraction_time",
    "emission_time",
    "speedup",
    "seed",
    "tau",
    "fixed_rank",
    "oversampling",
    "power_iter",
    "rank_policy",
    "leaf_tol",
    "merge_tol",
    "target_rank",
    "max_rank",
    "error_message",
]

RESULT_DESCRIPTIONS = {
    "family": "Problem family, usually the graph generator name.",
    "instance": "Instance identifier for this run.",
    "method": "Method/baseline name.",
    "status": "Run status: ok, timeout, oom, or failed.",
    "rel_error": "Relative reconstruction error against exact reference.",
    "nmse": "Normalized mean squared error against exact reference.",
    "total_time": "Total runtime in seconds.",
    "contraction_time": "Contraction stage runtime in seconds.",
    "emission_time": "Emission/writeback stage runtime in seconds.",
    "speedup": "Speedup versus exact baseline when available.",
    "seed": "Global random seed.",
    "tau": "Primary tolerance hyperparameter (tau/leaf_tol/merge_tol).",
    "fixed_rank": "Fixed rank used when rank_policy is fixed.",
    "oversampling": "Randomized sketch oversampling parameter.",
    "power_iter": "Randomized sketch power iterations.",
    "rank_policy": "Rank policy (fixed/adaptive).",
    "leaf_tol": "Leaf compression tolerance.",
    "merge_tol": "Merge compression tolerance.",
    "target_rank": "Configured target rank.",
    "max_rank": "Configured max rank.",
    "error_message": "Error text when status is not ok.",
}


def _select(cfg: DictConfig, key: str, default: Any = None) -> Any:
    value = OmegaConf.select(cfg, key, default=default)
    return value


def build_run_row(
    cfg: DictConfig,
    *,
    metrics: dict[str, Any],
    status: str,
    error_message: str | None = None,
) -> dict[str, Any]:
    method_name = str(_select(cfg, "method.name", ""))
    is_boss = method_name == "boss"
    rank_policy = _select(cfg, "method.rank_policy") if is_boss else None
    target_rank = _select(cfg, "method.target_rank") if is_boss else None
    tau = _select(cfg, "method.tau") if is_boss else None
    if tau is None and is_boss:
        tau = _select(cfg, "method.leaf_tol")
    if tau is None and is_boss:
        tau = _select(cfg, "method.merge_tol")
    row = {
        "family": _select(cfg, "data.generator", _select(cfg, "data.name", "")),
        "instance": _select(cfg, "experiment.name", _select(cfg, "data.name", "run")),
        "method": method_name,
        "status": status,
        "rel_error": metrics.get("rel_error"),
        "nmse": metrics.get("NMSE"),
        "total_time": metrics.get("total_time_sec"),
        "contraction_time": metrics.get("contract_time_sec"),
        "emission_time": metrics.get("emit_time_sec"),
        "speedup": metrics.get("speedup_vs_exact"),
        "seed": _select(cfg, "seed"),
        "tau": tau,
        "fixed_rank": target_rank if is_boss and str(rank_policy) == "fixed" else None,
        "oversampling": _select(cfg, "method.oversample", _select(cfg, "method.oversampling")) if is_boss else None,
        "power_iter": _select(cfg, "method.n_power_iter", _select(cfg, "method.power_iter")) if is_boss else None,
        "rank_policy": rank_policy,
        "leaf_tol": _select(cfg, "method.leaf_tol") if is_boss else None,
        "merge_tol": _select(cfg, "method.merge_tol") if is_boss else None,
        "target_rank": target_rank,
        "max_rank": _select(cfg, "method.max_rank") if is_boss else None,
        "error_message": error_message,
    }
    return {column: row.get(column) for column in RESULT_COLUMNS}


def _write_parquet(rows: list[dict[str, Any]], path: Path) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise ImportError("Writing runs.parquet requires pyarrow. Please install pyarrow.") from exc
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, path)


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in RESULT_COLUMNS})


def _write_results_readme(path: Path) -> None:
    lines = [
        "Result table files:",
        "- runs.parquet",
        "- runs.csv",
        "",
        "Column definitions:",
    ]
    for column in RESULT_COLUMNS:
        lines.append(f"- {column}: {RESULT_DESCRIPTIONS[column]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_run_outputs(
    out_dir: Path,
    cfg: DictConfig,
    rows: Iterable[dict[str, Any]],
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    normalized_rows = [{column: row.get(column) for column in RESULT_COLUMNS} for row in rows]
    parquet_path = out_dir / "runs.parquet"
    csv_path = out_dir / "runs.csv"
    config_snapshot_path = out_dir / "config_snapshot.yaml"
    readme_path = out_dir / "README_results.txt"
    _write_parquet(normalized_rows, parquet_path)
    _write_csv(normalized_rows, csv_path)
    config_snapshot_path.write_text(OmegaConf.to_yaml(cfg, resolve=True), encoding="utf-8")
    _write_results_readme(readme_path)
    return {
        "runs_parquet": parquet_path,
        "runs_csv": csv_path,
        "config_snapshot": config_snapshot_path,
        "readme_results": readme_path,
    }
