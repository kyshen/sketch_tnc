from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable

from omegaconf import DictConfig, OmegaConf

RESULT_COLUMNS = [
    "family",
    "instance",
    "topology",
    "method",
    "status",
    "seed",
    "rel_error",
    "contract_time_sec",
    "emit_time_sec",
    "total_time_sec",
    "speedup_vs_exact",
    "t_contract_ratio",
    "tau",
    "rank_policy",
    "leaf_tol",
    "merge_tol",
    "target_rank",
    "max_rank",
    "num_implicit_merge_sketches",
    "cache_enabled",
    "error_message",
]


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
    is_astnc = method_name == "astnc"
    rank_policy = _select(cfg, "method.rank_policy") if is_astnc else None
    target_rank = _select(cfg, "method.target_rank") if is_astnc else None
    topology = str(_select(cfg, "data.generator", _select(cfg, "data.name", "")))
    tau = _select(cfg, "method.tau") if is_astnc else None
    if tau is None and is_astnc:
        tau = _select(cfg, "method.leaf_tol")
    if tau is None and is_astnc:
        tau = _select(cfg, "method.merge_tol")
    row = {
        "family": _select(cfg, "data.generator", _select(cfg, "data.name", "")),
        "instance": _select(cfg, "experiment.name", _select(cfg, "data.name", "run")),
        "topology": topology,
        "method": method_name,
        "status": status,
        "seed": _select(cfg, "seed"),
        "rel_error": metrics.get("rel_error"),
        "contract_time_sec": metrics.get("contract_time_sec"),
        "emit_time_sec": metrics.get("emit_time_sec"),
        "total_time_sec": metrics.get("total_time_sec"),
        "speedup_vs_exact": metrics.get("speedup_vs_exact"),
        "t_contract_ratio": metrics.get("t_contract_ratio"),
        "cache_enabled": metrics.get("cache_enabled"),
        "num_implicit_merge_sketches": metrics.get("num_implicit_merge_sketches"),
        "tau": tau,
        "rank_policy": rank_policy,
        "leaf_tol": _select(cfg, "method.leaf_tol") if is_astnc else None,
        "merge_tol": _select(cfg, "method.merge_tol") if is_astnc else None,
        "target_rank": target_rank,
        "max_rank": _select(cfg, "method.max_rank") if is_astnc else None,
        "error_message": error_message,
    }
    for key, value in metrics.items():
        if key in row:
            continue
        if isinstance(value, (bool, int, float, str)):
            row[key] = value
    return row


def _resolved_columns(rows: list[dict[str, Any]]) -> list[str]:
    ordered = list(RESULT_COLUMNS)
    seen = set(ordered)
    extra = []
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                extra.append(key)
    return ordered + sorted(extra)


def _write_csv(rows: list[dict[str, Any]], path: Path, columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})


def write_run_outputs(
    out_dir: Path,
    cfg: DictConfig,
    rows: Iterable[dict[str, Any]],
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_list = list(rows)
    columns = _resolved_columns(rows_list)
    normalized_rows = [{column: row.get(column) for column in columns} for row in rows_list]
    csv_path = out_dir / "runs.csv"
    config_snapshot_path = out_dir / "config_snapshot.yaml"
    _write_csv(normalized_rows, csv_path, columns)
    config_snapshot_path.write_text(OmegaConf.to_yaml(cfg, resolve=True), encoding="utf-8")
    return {
        "runs_csv": csv_path,
        "config_snapshot": config_snapshot_path,
    }
