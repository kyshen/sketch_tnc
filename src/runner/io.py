from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable

from omegaconf import DictConfig, OmegaConf

RESULT_COLUMNS = [
    "family",
    "instance",
    "topology",
    "size_description",
    "method",
    "method_variant",
    "status",
    "seed",
    "rel_error",
    "RMSE",
    "NMSE",
    "NMSE_dB",
    "contract_time_sec",
    "emit_time_sec",
    "total_time_sec",
    "speedup_vs_exact",
    "t_contract_ratio",
    "num_blocks",
    "refined_blocks",
    "mean_rank",
    "max_rank",
    "peak_rank",
    "num_exact_merges",
    "num_compressed_merges",
    "num_exact_leaves",
    "num_compressed_leaves",
    "mean_leaf_residual_ratio",
    "mean_merge_residual_ratio",
    "cache_enabled",
    "cache_requests",
    "cache_hits",
    "cache_misses",
    "cache_hit_rate",
    "num_cached_states",
    "leaf_states_built",
    "internal_states_built",
    "num_implicit_merge_sketches",
    "num_explicit_merge_compressions",
    "skipped_small_rank_merges",
    "skipped_small_state_merges",
    "skipped_low_saving_merges",
    "exact_total_time_sec",
    "reference_available",
    "num_method_params",
    "nmse",
    "total_time",
    "contraction_time",
    "emission_time",
    "speedup",
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
    "topology": "Topology generator label.",
    "size_description": "Human-readable size metadata for this case.",
    "method": "Method/baseline name.",
    "method_variant": "External method variant label used in reporting.",
    "status": "Run status: ok, timeout, oom, or failed.",
    "seed": "Global random seed.",
    "rel_error": "Relative reconstruction error against exact reference.",
    "RMSE": "Root mean-squared error against exact reference.",
    "NMSE": "Normalized mean squared error against exact reference.",
    "NMSE_dB": "NMSE in dB.",
    "contract_time_sec": "Contraction stage runtime in seconds.",
    "emit_time_sec": "Emission/writeback stage runtime in seconds.",
    "total_time_sec": "Total runtime in seconds.",
    "speedup_vs_exact": "Speedup versus exact baseline when available.",
    "t_contract_ratio": "Contraction time ratio over total time.",
    "num_blocks": "Number of output blocks.",
    "refined_blocks": "Blocks refined by adaptive refinement.",
    "mean_rank": "Mean effective rank used across blocks.",
    "max_rank": "Maximum effective rank used across blocks.",
    "peak_rank": "Peak intermediate separator rank.",
    "num_exact_merges": "Internal merges executed exactly.",
    "num_compressed_merges": "Internal merges executed in compressed mode.",
    "num_exact_leaves": "Leaf states kept exact.",
    "num_compressed_leaves": "Leaf states compressed.",
    "mean_leaf_residual_ratio": "Mean residual ratio from leaf compression decisions.",
    "mean_merge_residual_ratio": "Mean residual ratio from merge compression decisions.",
    "cache_enabled": "Whether separator state cache was enabled.",
    "cache_requests": "Number of cache lookup requests.",
    "cache_hits": "Number of cache hits.",
    "cache_misses": "Number of cache misses.",
    "cache_hit_rate": "Cache hit rate.",
    "num_cached_states": "Number of cached states stored.",
    "leaf_states_built": "Leaf states built in ASTNC recursion.",
    "internal_states_built": "Internal states built in ASTNC recursion.",
    "num_implicit_merge_sketches": "Number of implicit randomized merge sketches.",
    "num_explicit_merge_compressions": "Number of explicit merge compressions.",
    "skipped_small_rank_merges": "Exact merges forced by small rank product.",
    "skipped_small_state_merges": "Exact merges forced by small exact state size.",
    "skipped_low_saving_merges": "Exact merges forced by low estimated saving.",
    "exact_total_time_sec": "Exact-reference runtime used for speedup.",
    "reference_available": "Whether exact reference was computed.",
    "num_method_params": "Method parameter count proxy.",
    "nmse": "Normalized mean squared error against exact reference.",
    "total_time": "Total runtime in seconds.",
    "contraction_time": "Contraction stage runtime in seconds.",
    "emission_time": "Emission/writeback stage runtime in seconds.",
    "speedup": "Speedup versus exact baseline when available.",
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


def _size_description(cfg: DictConfig) -> str:
    topology = str(_select(cfg, "data.generator", _select(cfg, "data.name", "unknown")))
    num_nodes = _select(cfg, "data.num_nodes")
    phys_dim = _select(cfg, "data.phys_dim")
    bond_dim = _select(cfg, "data.bond_dim")
    open_legs = _select(cfg, "data.open_legs_per_node")
    if topology == "grid2d":
        grid_shape = _select(cfg, "data.grid_shape")
        if grid_shape is not None:
            return f"grid_shape={list(grid_shape)}, phys_dim={phys_dim}, bond_dim={bond_dim}, open_legs_per_node={open_legs}"
    parts = []
    if num_nodes is not None:
        parts.append(f"num_nodes={int(num_nodes)}")
    if phys_dim is not None:
        parts.append(f"phys_dim={int(phys_dim)}")
    if bond_dim is not None:
        parts.append(f"bond_dim={int(bond_dim)}")
    if open_legs is not None:
        parts.append(f"open_legs_per_node={int(open_legs)}")
    return ", ".join(parts)


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
    method_variant = method_name
    if is_astnc and str(rank_policy) == "fixed":
        method_variant = "fixed-rank"
    tau = _select(cfg, "method.tau") if is_astnc else None
    if tau is None and is_astnc:
        tau = _select(cfg, "method.leaf_tol")
    if tau is None and is_astnc:
        tau = _select(cfg, "method.merge_tol")
    row = {
        "family": _select(cfg, "data.generator", _select(cfg, "data.name", "")),
        "instance": _select(cfg, "experiment.name", _select(cfg, "data.name", "run")),
        "topology": topology,
        "size_description": _size_description(cfg),
        "method": method_name,
        "method_variant": method_variant,
        "status": status,
        "seed": _select(cfg, "seed"),
        "rel_error": metrics.get("rel_error"),
        "RMSE": metrics.get("RMSE"),
        "NMSE": metrics.get("NMSE"),
        "NMSE_dB": metrics.get("NMSE_dB"),
        "contract_time_sec": metrics.get("contract_time_sec"),
        "emit_time_sec": metrics.get("emit_time_sec"),
        "total_time_sec": metrics.get("total_time_sec"),
        "speedup_vs_exact": metrics.get("speedup_vs_exact"),
        "t_contract_ratio": metrics.get("t_contract_ratio"),
        "num_blocks": metrics.get("num_blocks"),
        "refined_blocks": metrics.get("refined_blocks"),
        "mean_rank": metrics.get("mean_rank"),
        "max_rank": metrics.get("max_rank"),
        "peak_rank": metrics.get("peak_rank"),
        "num_exact_merges": metrics.get("num_exact_merges"),
        "num_compressed_merges": metrics.get("num_compressed_merges"),
        "num_exact_leaves": metrics.get("num_exact_leaves"),
        "num_compressed_leaves": metrics.get("num_compressed_leaves"),
        "mean_leaf_residual_ratio": metrics.get("mean_leaf_residual_ratio"),
        "mean_merge_residual_ratio": metrics.get("mean_merge_residual_ratio"),
        "cache_enabled": metrics.get("cache_enabled"),
        "cache_requests": metrics.get("cache_requests"),
        "cache_hits": metrics.get("cache_hits"),
        "cache_misses": metrics.get("cache_misses"),
        "cache_hit_rate": metrics.get("cache_hit_rate"),
        "num_cached_states": metrics.get("num_cached_states"),
        "leaf_states_built": metrics.get("leaf_states_built"),
        "internal_states_built": metrics.get("internal_states_built"),
        "num_implicit_merge_sketches": metrics.get("num_implicit_merge_sketches"),
        "num_explicit_merge_compressions": metrics.get("num_explicit_merge_compressions"),
        "skipped_small_rank_merges": metrics.get("skipped_small_rank_merges"),
        "skipped_small_state_merges": metrics.get("skipped_small_state_merges"),
        "skipped_low_saving_merges": metrics.get("skipped_low_saving_merges"),
        "exact_total_time_sec": metrics.get("exact_total_time_sec"),
        "reference_available": metrics.get("reference_available"),
        "num_method_params": metrics.get("num_method_params"),
        "nmse": metrics.get("NMSE"),
        "total_time": metrics.get("total_time_sec"),
        "contraction_time": metrics.get("contract_time_sec"),
        "emission_time": metrics.get("emit_time_sec"),
        "speedup": metrics.get("speedup_vs_exact"),
        "tau": tau,
        "fixed_rank": target_rank if is_astnc and str(rank_policy) == "fixed" else None,
        "oversampling": _select(cfg, "method.oversample", _select(cfg, "method.oversampling")) if is_astnc else None,
        "power_iter": _select(cfg, "method.n_power_iter", _select(cfg, "method.power_iter")) if is_astnc else None,
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


def _write_parquet(rows: list[dict[str, Any]], path: Path, columns: list[str]) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise ImportError("Writing runs.parquet requires pyarrow. Please install pyarrow.") from exc
    normalized = [{column: row.get(column) for column in columns} for row in rows]
    table = pa.Table.from_pylist(normalized)
    pq.write_table(table, path)


def _write_csv(rows: list[dict[str, Any]], path: Path, columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})


def _write_results_readme(path: Path, columns: list[str]) -> None:
    lines = [
        "Result table files:",
        "- runs.parquet",
        "- runs.csv",
        "",
        "Column definitions:",
    ]
    for column in columns:
        description = RESULT_DESCRIPTIONS.get(column, "Auto-exported scalar metric field.")
        lines.append(f"- {column}: {description}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_run_outputs(
    out_dir: Path,
    cfg: DictConfig,
    rows: Iterable[dict[str, Any]],
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_list = list(rows)
    columns = _resolved_columns(rows_list)
    normalized_rows = [{column: row.get(column) for column in columns} for row in rows_list]
    parquet_path = out_dir / "runs.parquet"
    csv_path = out_dir / "runs.csv"
    config_snapshot_path = out_dir / "config_snapshot.yaml"
    readme_path = out_dir / "README_results.txt"
    _write_parquet(normalized_rows, parquet_path, columns)
    _write_csv(normalized_rows, csv_path, columns)
    config_snapshot_path.write_text(OmegaConf.to_yaml(cfg, resolve=True), encoding="utf-8")
    _write_results_readme(readme_path, columns)
    return {
        "runs_parquet": parquet_path,
        "runs_csv": csv_path,
        "config_snapshot": config_snapshot_path,
        "readme_results": readme_path,
    }
