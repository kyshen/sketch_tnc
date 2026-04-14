import argparse
import csv
import math
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNPY = ROOT / "run.py"


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    display_name: str
    topology: str
    overrides: dict[str, str]


@dataclass(frozen=True)
class RunSpec:
    case_id: str
    method_key: str
    seed: int
    run_name: str
    tag: str
    extra: dict[str, Any]


COMMON_ASTNC: dict[str, str] = {
    "method": "astnc",
    "method.optimize": "greedy",
    "method.randomized": "true",
    "method.oversample": "1",
    "method.n_power_iter": "0",
    "method.tol_schedule": "depth_open",
    "method.tol_depth_decay": "1.5",
    "method.tol_open_power": "0.5",
    "method.selective_threshold": "0",
    "method.compress_min_rank_product": "4",
    "method.compress_max_exact_size": "256",
    "method.compress_min_saving_ratio": "0.1",
    "method.implicit_merge_sketch": "true",
    "method.implicit_min_full_rank": "192",
    "method.adaptive_refine": "false",
    "method.cache_enabled": "true",
}

METHODS: dict[str, dict[str, Any]] = {
    "exact": {
        "name": "exact",
        "overrides": {
            "method": "exact",
            "method.optimize": "optimal",
        },
    },
    "fixed_rank": {
        "name": "fixed-rank",
        "overrides": {
            **COMMON_ASTNC,
            "method.rank_policy": "fixed",
            "method.target_rank": "4",
            "method.max_rank": "4",
            "method.leaf_tol": "0.0",
            "method.merge_tol": "0.0",
        },
    },
    "astnc_l1": {
        "name": "ASTNC-L1",
        "overrides": {
            **COMMON_ASTNC,
            "method.rank_policy": "adaptive",
            "method.target_rank": "2",
            "method.max_rank": "16",
            "method.leaf_tol": "0.0005",
            "method.merge_tol": "0.002",
        },
    },
    "astnc_l2": {
        "name": "ASTNC-L2",
        "overrides": {
            **COMMON_ASTNC,
            "method.rank_policy": "adaptive",
            "method.target_rank": "2",
            "method.max_rank": "16",
            "method.leaf_tol": "0.001",
            "method.merge_tol": "0.005",
        },
    },
    "astnc_l3": {
        "name": "ASTNC-L3",
        "overrides": {
            **COMMON_ASTNC,
            "method.rank_policy": "adaptive",
            "method.target_rank": "2",
            "method.max_rank": "16",
            "method.leaf_tol": "0.003",
            "method.merge_tol": "0.015",
        },
    },
    "no_blockwise": {
        "name": "no-blockwise",
        "overrides": {
            **COMMON_ASTNC,
            "method.rank_policy": "adaptive",
            "method.target_rank": "2",
            "method.max_rank": "16",
            "method.leaf_tol": "0.001",
            "method.merge_tol": "0.005",
            "block.enabled": "false",
        },
    },
    "no_implicit": {
        "name": "no-implicit",
        "overrides": {
            **COMMON_ASTNC,
            "method.rank_policy": "adaptive",
            "method.target_rank": "2",
            "method.max_rank": "16",
            "method.leaf_tol": "0.001",
            "method.merge_tol": "0.005",
            "method.implicit_merge_sketch": "false",
        },
    },
    "no_cache": {
        "name": "no-cache",
        "overrides": {
            **COMMON_ASTNC,
            "method.rank_policy": "adaptive",
            "method.target_rank": "2",
            "method.max_rank": "16",
            "method.leaf_tol": "0.001",
            "method.merge_tol": "0.005",
            "method.cache_enabled": "false",
        },
    },
}

PARETO_LEVELS: list[dict[str, Any]] = [
    {"level_id": "P1", "leaf_tol": 0.00025, "merge_tol": 0.00125},
    {"level_id": "P2", "leaf_tol": 0.00050, "merge_tol": 0.00250},
    {"level_id": "P3", "leaf_tol": 0.00075, "merge_tol": 0.00375},
    {"level_id": "P4", "leaf_tol": 0.00100, "merge_tol": 0.00500},
    {"level_id": "P5", "leaf_tol": 0.00200, "merge_tol": 0.01000},
    {"level_id": "P6", "leaf_tol": 0.00300, "merge_tol": 0.01500},
    {"level_id": "P7", "leaf_tol": 0.00450, "merge_tol": 0.02250},
]

BLOCKWISE_SETTINGS: list[dict[str, Any]] = [
    {"setting_id": "block_disabled", "block_enabled": False, "block_labels": 0, "chunk_size": 0},
    {"setting_id": "b1_c1", "block_enabled": True, "block_labels": 1, "chunk_size": 1},
    {"setting_id": "b1_c2", "block_enabled": True, "block_labels": 1, "chunk_size": 2},
    {"setting_id": "b1_c3", "block_enabled": True, "block_labels": 1, "chunk_size": 3},
    {"setting_id": "b2_c1", "block_enabled": True, "block_labels": 2, "chunk_size": 1},
    {"setting_id": "b2_c2", "block_enabled": True, "block_labels": 2, "chunk_size": 2},
    {"setting_id": "b2_c3", "block_enabled": True, "block_labels": 2, "chunk_size": 3},
    {"setting_id": "b3_c1", "block_enabled": True, "block_labels": 3, "chunk_size": 1},
    {"setting_id": "b3_c3", "block_enabled": True, "block_labels": 3, "chunk_size": 3},
]

DIFFICULTY_TREND_CASES = [
    CaseSpec(
        case_id="difficulty_grid2d_2x3",
        display_name="Grid 2x3",
        topology="grid2d",
        overrides={
            "data": "grid2d",
            "data.grid_shape": "[2,3]",
            "data.num_nodes": "6",
            "data.phys_dim": "3",
            "data.bond_dim": "4",
            "data.open_legs_per_node": "1",
            "block.enabled": "true",
            "block.block_labels": "2",
            "block.chunk_size": "1",
        },
    ),
    CaseSpec(
        case_id="difficulty_grid2d_2x4",
        display_name="Grid 2x4",
        topology="grid2d",
        overrides={
            "data": "grid2d",
            "data.grid_shape": "[2,4]",
            "data.num_nodes": "8",
            "data.phys_dim": "3",
            "data.bond_dim": "4",
            "data.open_legs_per_node": "1",
            "block.enabled": "true",
            "block.block_labels": "2",
            "block.chunk_size": "1",
        },
    ),
]

DIFFICULTY_TREND_SETTINGS: list[dict[str, str]] = [
    {"case_id": "difficulty_grid2d_2x3", "case_family": "grid_shape", "size_or_difficulty_setting": "2x3", "display_name": "Grid 2x3"},
    {"case_id": "difficulty_grid2d_2x4", "case_family": "grid_shape", "size_or_difficulty_setting": "2x4", "display_name": "Grid 2x4"},
    {"case_id": "main_grid2d_3x3", "case_family": "grid_shape", "size_or_difficulty_setting": "3x3", "display_name": "Grid 3x3"},
]

CACHE_REUSE_SETTINGS: list[dict[str, Any]] = [
    {"setting_id": "b2_c1", "block_enabled": True, "block_labels": 2, "chunk_size": 1},
    {"setting_id": "b2_c2", "block_enabled": True, "block_labels": 2, "chunk_size": 2},
]

MAIN_CASES = [
    CaseSpec(
        case_id="main_ring_8",
        display_name="Ring-8",
        topology="ring",
        overrides={
            "data": "ring",
            "data.num_nodes": "8",
            "data.phys_dim": "3",
            "data.bond_dim": "4",
            "data.open_legs_per_node": "1",
            "block.enabled": "true",
            "block.block_labels": "2",
            "block.chunk_size": "1",
        },
    ),
    CaseSpec(
        case_id="main_tree_8",
        display_name="Tree-8",
        topology="tree",
        overrides={
            "data": "tree",
            "data.num_nodes": "8",
            "data.phys_dim": "3",
            "data.bond_dim": "4",
            "data.open_legs_per_node": "1",
            "block.enabled": "true",
            "block.block_labels": "2",
            "block.chunk_size": "1",
        },
    ),
    CaseSpec(
        case_id="main_grid2d_3x3",
        display_name="Grid 3x3",
        topology="grid2d",
        overrides={
            "data": "grid2d",
            "data.grid_shape": "[3,3]",
            "data.num_nodes": "9",
            "data.phys_dim": "3",
            "data.bond_dim": "4",
            "data.open_legs_per_node": "1",
            "block.enabled": "true",
            "block.block_labels": "2",
            "block.chunk_size": "1",
        },
    ),
    CaseSpec(
        case_id="main_random_8",
        display_name="Random-8",
        topology="random_connected",
        overrides={
            "data": "random_connected",
            "data.num_nodes": "8",
            "data.edge_prob": "0.35",
            "data.phys_dim": "3",
            "data.bond_dim": "4",
            "data.open_legs_per_node": "1",
            "block.enabled": "true",
            "block.block_labels": "2",
            "block.chunk_size": "1",
        },
    ),
]

MAIN_CASE_IDS = {case.case_id for case in MAIN_CASES}
PARETO_CASE_IDS = {"main_grid2d_3x3", "main_random_8"}
BLOCKWISE_CASE_IDS = {"main_grid2d_3x3", "main_random_8"}


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() in {"none", "nan", "na"}:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    return number


def _to_int(value: Any) -> int | None:
    number = _to_float(value)
    if number is None:
        return None
    return int(number)


def _to_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def _safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or b == 0:
        return None
    return a / b


def _avg(values: list[float | None]) -> float | None:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return mean(nums)


def _first(values: list[Any]) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def _gmean(values: list[float | None]) -> float | None:
    nums = [v for v in values if v is not None and v > 0]
    if not nums:
        return None
    return math.exp(sum(math.log(v) for v in nums) / len(nums))


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in columns})


def _read_single_run_row(group: str, run_name: str) -> dict[str, Any] | None:
    run_root = ROOT / "outputs" / group / run_name
    if not run_root.exists():
        return None
    subdirs = [p for p in run_root.iterdir() if p.is_dir()]
    if not subdirs:
        return None
    latest = max(subdirs, key=lambda p: p.stat().st_mtime)
    csv_path = latest / "runs.csv"
    if not csv_path.exists():
        return None
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out = dict(row)
            out["run_dir"] = str(latest)
            return out
    return None


def _execute_one(case: CaseSpec, spec: RunSpec, group: str, force: bool) -> dict[str, Any]:
    row = None if force else _read_single_run_row(group, spec.run_name)
    if row is None:
        overrides = {
            "seed": str(spec.seed),
            "experiment.group": group,
            "experiment.name": spec.run_name,
            **case.overrides,
            **METHODS[spec.method_key]["overrides"],
        }
        for key, value in spec.extra.items():
            if key.startswith("override."):
                overrides[key.removeprefix("override.")] = str(value)
        cmd = [sys.executable, str(RUNPY)] + [f"{k}={v}" for k, v in overrides.items()]
        try:
            subprocess.run(cmd, cwd=str(ROOT), check=True, timeout=1800)
        except subprocess.CalledProcessError:
            row = _read_single_run_row(group, spec.run_name)
            if row is None:
                return {
                    "case_id": case.case_id,
                    "case": case.display_name,
                    "topology": case.topology,
                    "seed": spec.seed,
                    "method_key": spec.method_key,
                    "method": METHODS[spec.method_key]["name"],
                    "run_name": spec.run_name,
                    "tag": spec.tag,
                    "status": "failed",
                    **{k: v for k, v in spec.extra.items() if not k.startswith("override.")},
                }
        row = _read_single_run_row(group, spec.run_name)

    if row is None:
        return {
            "case_id": case.case_id,
            "case": case.display_name,
            "topology": case.topology,
            "seed": spec.seed,
            "method_key": spec.method_key,
            "method": METHODS[spec.method_key]["name"],
            "run_name": spec.run_name,
            "tag": spec.tag,
            "status": "failed",
            **{k: v for k, v in spec.extra.items() if not k.startswith("override.")},
        }

    clean_extra = {k: v for k, v in spec.extra.items() if not k.startswith("override.")}
    return {
        "case_id": case.case_id,
        "case": case.display_name,
        "topology": case.topology,
        "seed": spec.seed,
        "method_key": spec.method_key,
        "method": METHODS[spec.method_key]["name"],
        "run_name": spec.run_name,
        "tag": spec.tag,
        "status": row.get("status", "failed"),
        "rel_error": _to_float(row.get("rel_error")),
        "contract_time_sec": _to_float(row.get("contract_time_sec")),
        "emit_time_sec": _to_float(row.get("emit_time_sec")),
        "total_time_sec": _to_float(row.get("total_time_sec")),
        "speedup_vs_exact": _to_float(row.get("speedup_vs_exact")),
        "t_contract_ratio": _to_float(row.get("t_contract_ratio")),
        "rank_policy": row.get("rank_policy"),
        "leaf_tol": _to_float(row.get("leaf_tol")),
        "merge_tol": _to_float(row.get("merge_tol")),
        "target_rank": _to_int(row.get("target_rank")),
        "max_rank": _to_int(row.get("max_rank")),
        "mean_rank": _to_float(row.get("mean_rank")),
        "peak_rank": _to_float(row.get("peak_rank")),
        "num_implicit_merge_sketches": _to_float(row.get("num_implicit_merge_sketches")),
        "num_exact_merges": _to_float(row.get("num_exact_merges")),
        "num_compressed_merges": _to_float(row.get("num_compressed_merges")),
        "cache_enabled": _to_bool(row.get("cache_enabled")),
        "cache_requests": _to_float(row.get("cache_requests")),
        "cache_hits": _to_float(row.get("cache_hits")),
        "cache_misses": _to_float(row.get("cache_misses")),
        "cache_hit_rate": _to_float(row.get("cache_hit_rate")),
        "num_cached_states": _to_float(row.get("num_cached_states")),
        "num_blocks": _to_float(row.get("num_blocks")),
        "mean_merge_residual_ratio": _to_float(row.get("mean_merge_residual_ratio")),
        "run_dir": row.get("run_dir"),
        **clean_extra,
    }


def _case_open_label_count(case: CaseSpec) -> int:
    num_nodes = int(case.overrides.get("data.num_nodes", "0"))
    open_legs = int(case.overrides.get("data.open_legs_per_node", "1"))
    return num_nodes * open_legs


def _case_phys_dim(case: CaseSpec) -> int:
    return int(case.overrides.get("data.phys_dim", "1"))


def _blockwise_setting_is_valid(case: CaseSpec, setting: dict[str, Any]) -> bool:
    if not setting["block_enabled"]:
        return True
    if int(setting["block_labels"]) <= 0 or int(setting["chunk_size"]) <= 0:
        return False
    if int(setting["block_labels"]) > _case_open_label_count(case):
        return False
    if int(setting["chunk_size"]) > _case_phys_dim(case):
        return False
    return True


def _build_required_specs(seeds: list[int]) -> list[RunSpec]:
    specs: list[RunSpec] = []

    for case in MAIN_CASES:
        for method_key in ["exact", "fixed_rank", "astnc_l1", "astnc_l2", "astnc_l3"]:
            for seed in seeds:
                specs.append(
                    RunSpec(
                        case_id=case.case_id,
                        method_key=method_key,
                        seed=seed,
                        run_name=f"{case.case_id}__{method_key}__s{seed}",
                        tag="core",
                        extra={},
                    )
                )

    for seed in seeds:
        for method_key in ["no_blockwise", "no_implicit", "no_cache"]:
            specs.append(
                RunSpec(
                    case_id="main_grid2d_3x3",
                    method_key=method_key,
                    seed=seed,
                    run_name=f"main_grid2d_3x3__{method_key}__s{seed}",
                    tag="mechanism",
                    extra={},
                )
            )

    for case in MAIN_CASES:
        if case.case_id not in PARETO_CASE_IDS:
            continue
        for level in PARETO_LEVELS:
            method_key = f"pareto_{level['level_id'].lower()}"
            METHODS[method_key] = {
                "name": f"ASTNC-{level['level_id']}",
                "overrides": {
                    **COMMON_ASTNC,
                    "method.rank_policy": "adaptive",
                    "method.target_rank": "2",
                    "method.max_rank": "16",
                    "method.leaf_tol": str(level["leaf_tol"]),
                    "method.merge_tol": str(level["merge_tol"]),
                },
            }
            for seed in seeds:
                specs.append(
                    RunSpec(
                        case_id=case.case_id,
                        method_key=method_key,
                        seed=seed,
                        run_name=f"{case.case_id}__pareto_{level['level_id'].lower()}__s{seed}",
                        tag="pareto",
                        extra={
                            "level_id": level["level_id"],
                            "leaf_tol_nominal": level["leaf_tol"],
                            "merge_tol_nominal": level["merge_tol"],
                        },
                    )
                )

    for case in MAIN_CASES:
        if case.case_id not in BLOCKWISE_CASE_IDS:
            continue
        for setting in BLOCKWISE_SETTINGS:
            if not _blockwise_setting_is_valid(case, setting):
                continue
            for seed in seeds:
                specs.append(
                    RunSpec(
                        case_id=case.case_id,
                        method_key="astnc_l2",
                        seed=seed,
                        run_name=f"{case.case_id}__block_{setting['setting_id']}__s{seed}",
                        tag="blockwise",
                        extra={
                            "block_enabled": setting["block_enabled"],
                            "block_labels": setting["block_labels"],
                            "chunk_size": setting["chunk_size"],
                            "override.block.enabled": str(setting["block_enabled"]).lower(),
                            "override.block.block_labels": setting["block_labels"],
                            "override.block.chunk_size": 1 if not setting["block_enabled"] else setting["chunk_size"],
                        },
                    )
                )

    for case in DIFFICULTY_TREND_CASES:
        for method_key in ["exact", "astnc_l2"]:
            for seed in seeds:
                specs.append(
                    RunSpec(
                        case_id=case.case_id,
                        method_key=method_key,
                        seed=seed,
                        run_name=f"{case.case_id}__{method_key}__s{seed}",
                        tag="difficulty",
                        extra={},
                    )
                )

    for seed in seeds:
        specs.extend(
            [
                RunSpec(
                    case_id="main_grid2d_3x3",
                    method_key="astnc_l2",
                    seed=seed,
                    run_name=f"main_grid2d_3x3__block_b1_c1__s{seed}",
                    tag="cache_reuse",
                    extra={
                        "setting_id": "b1_c1",
                        "block_enabled": True,
                        "block_labels": 1,
                        "chunk_size": 1,
                        "cache_enabled_requested": True,
                    },
                ),
                RunSpec(
                    case_id="main_grid2d_3x3",
                    method_key="astnc_l2",
                    seed=seed,
                    run_name=f"main_grid2d_3x3__cache_off_b1_c1__s{seed}",
                    tag="cache_reuse",
                    extra={
                        "setting_id": "b1_c1",
                        "block_enabled": True,
                        "block_labels": 1,
                        "chunk_size": 1,
                        "cache_enabled_requested": False,
                        "override.method.cache_enabled": "false",
                        "override.block.enabled": "true",
                        "override.block.block_labels": 1,
                        "override.block.chunk_size": 1,
                    },
                ),
                RunSpec(
                    case_id="main_grid2d_3x3",
                    method_key="astnc_l2",
                    seed=seed,
                    run_name=f"main_grid2d_3x3__astnc_l2__s{seed}",
                    tag="cache_reuse",
                    extra={
                        "setting_id": "b2_c1",
                        "block_enabled": True,
                        "block_labels": 2,
                        "chunk_size": 1,
                        "cache_enabled_requested": True,
                    },
                ),
                RunSpec(
                    case_id="main_grid2d_3x3",
                    method_key="no_cache",
                    seed=seed,
                    run_name=f"main_grid2d_3x3__no_cache__s{seed}",
                    tag="cache_reuse",
                    extra={
                        "setting_id": "b2_c1",
                        "block_enabled": True,
                        "block_labels": 2,
                        "chunk_size": 1,
                        "cache_enabled_requested": False,
                    },
                ),
                RunSpec(
                    case_id="main_grid2d_3x3",
                    method_key="astnc_l2",
                    seed=seed,
                    run_name=f"main_grid2d_3x3__block_b2_c2__s{seed}",
                    tag="cache_reuse",
                    extra={
                        "setting_id": "b2_c2",
                        "block_enabled": True,
                        "block_labels": 2,
                        "chunk_size": 2,
                        "cache_enabled_requested": True,
                    },
                ),
                RunSpec(
                    case_id="main_grid2d_3x3",
                    method_key="astnc_l2",
                    seed=seed,
                    run_name=f"main_grid2d_3x3__cache_off_b2_c2__s{seed}",
                    tag="cache_reuse",
                    extra={
                        "setting_id": "b2_c2",
                        "block_enabled": True,
                        "block_labels": 2,
                        "chunk_size": 2,
                        "cache_enabled_requested": False,
                        "override.method.cache_enabled": "false",
                        "override.block.enabled": "true",
                        "override.block.block_labels": 2,
                        "override.block.chunk_size": 2,
                    },
                ),
            ]
        )

    return specs


def _collect_runs(group: str, seeds: list[int], force: bool) -> list[dict[str, Any]]:
    case_lookup = {case.case_id: case for case in [*MAIN_CASES, *DIFFICULTY_TREND_CASES]}
    rows: list[dict[str, Any]] = []
    for spec in _build_required_specs(seeds):
        rows.append(_execute_one(case_lookup[spec.case_id], spec, group=group, force=force))
    return rows


def _ok(rows: list[dict[str, Any]], *, case_id: str | None = None, method_key: str | None = None, tag: str | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if row.get("status") != "ok":
            continue
        if case_id is not None and row.get("case_id") != case_id:
            continue
        if method_key is not None and row.get("method_key") != method_key:
            continue
        if tag is not None and row.get("tag") != tag:
            continue
        out.append(row)
    return out


def _build_main_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    ast_errors: list[float | None] = []
    ast_speedups: list[float | None] = []

    for case in MAIN_CASES:
        exact_rows = _ok(rows, case_id=case.case_id, method_key="exact")
        fixed_rows = _ok(rows, case_id=case.case_id, method_key="fixed_rank")
        ast_rows = _ok(rows, case_id=case.case_id, method_key="astnc_l2")

        exact_time = _avg([_to_float(r.get("total_time_sec")) for r in exact_rows])
        fixed_time = _avg([_to_float(r.get("total_time_sec")) for r in fixed_rows])
        ast_time = _avg([_to_float(r.get("total_time_sec")) for r in ast_rows])
        fixed_rel = _avg([_to_float(r.get("rel_error")) for r in fixed_rows])
        ast_rel = _avg([_to_float(r.get("rel_error")) for r in ast_rows])
        fixed_speed = _safe_div(exact_time, fixed_time)
        ast_speed = _safe_div(exact_time, ast_time)

        ast_errors.append(ast_rel)
        ast_speedups.append(ast_speed)
        out.append(
            {
                "case": case.display_name,
                "exact_time_sec": exact_time,
                "fixed_rank_rel_error": fixed_rel,
                "fixed_rank_speedup": fixed_speed,
                "astnc_l2_rel_error": ast_rel,
                "astnc_l2_speedup": ast_speed,
            }
        )

    out.append(
        {
            "case": "summary",
            "exact_time_sec": None,
            "fixed_rank_rel_error": None,
            "fixed_rank_speedup": None,
            "astnc_l2_rel_error": _avg(ast_errors),
            "astnc_l2_speedup": _gmean(ast_speedups),
        }
    )
    return out


def _build_stage_breakdown(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for case in MAIN_CASES:
        exact_rows = _ok(rows, case_id=case.case_id, method_key="exact")
        ast_rows = _ok(rows, case_id=case.case_id, method_key="astnc_l2")
        exact_contract = _avg([_to_float(r.get("contract_time_sec")) for r in exact_rows])
        exact_total = _avg([_to_float(r.get("total_time_sec")) for r in exact_rows])
        ast_contract = _avg([_to_float(r.get("contract_time_sec")) for r in ast_rows])
        ast_emit = _avg([_to_float(r.get("emit_time_sec")) for r in ast_rows])
        ast_total = _avg([_to_float(r.get("total_time_sec")) for r in ast_rows])
        t_contract_ratio = _avg([_to_float(r.get("t_contract_ratio")) for r in ast_rows])
        t_emit_ratio = _safe_div(ast_emit, ast_total)
        out.append(
            {
                "case": case.display_name,
                "t_contract_ratio": t_contract_ratio,
                "t_emit_ratio": t_emit_ratio,
                "contraction_speedup": _safe_div(exact_contract, ast_contract),
                "total_speedup": _safe_div(exact_total, ast_total),
            }
        )

    out.append(
        {
            "case": "Average",
            "t_contract_ratio": _avg([_to_float(r.get("t_contract_ratio")) for r in out]),
            "t_emit_ratio": _avg([_to_float(r.get("t_emit_ratio")) for r in out]),
            "contraction_speedup": _avg([_to_float(r.get("contraction_speedup")) for r in out]),
            "total_speedup": _avg([_to_float(r.get("total_speedup")) for r in out]),
        }
    )
    return out


def _build_mechanism_ablation(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    case_id = "main_grid2d_3x3"
    default_rows = _ok(rows, case_id=case_id, method_key="astnc_l2")
    default_total = _avg([_to_float(r.get("total_time_sec")) for r in default_rows])
    method_order = ["astnc_l2", "no_blockwise", "no_implicit"]
    label_map = {
        "astnc_l2": "ASTNC (default)",
        "no_blockwise": "no-blockwise",
        "no_implicit": "no-implicit",
    }
    out: list[dict[str, Any]] = []
    for method_key in method_order:
        method_rows = _ok(rows, case_id=case_id, method_key=method_key)
        total_time = _avg([_to_float(r.get("total_time_sec")) for r in method_rows])
        out.append(
            {
                "case": "Grid 3x3",
                "setting": label_map[method_key],
                "rel_error": _avg([_to_float(r.get("rel_error")) for r in method_rows]),
                "total_time_sec": total_time,
                "time_ratio_vs_default": _safe_div(total_time, default_total),
            }
        )
    return out


def _build_strength_sensitivity(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for case in MAIN_CASES:
        out.append(
            {
                "case": case.display_name,
                "l1_rel_error": _avg([_to_float(r.get("rel_error")) for r in _ok(rows, case_id=case.case_id, method_key="astnc_l1")]),
                "l2_rel_error": _avg([_to_float(r.get("rel_error")) for r in _ok(rows, case_id=case.case_id, method_key="astnc_l2")]),
                "l3_rel_error": _avg([_to_float(r.get("rel_error")) for r in _ok(rows, case_id=case.case_id, method_key="astnc_l3")]),
            }
        )

    out.append(
        {
            "case": "Average rel. error",
            "l1_rel_error": _avg([_to_float(r.get("l1_rel_error")) for r in out]),
            "l2_rel_error": _avg([_to_float(r.get("l2_rel_error")) for r in out]),
            "l3_rel_error": _avg([_to_float(r.get("l3_rel_error")) for r in out]),
        }
    )
    return out


def _build_pareto_sweep(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for case in MAIN_CASES:
        if case.case_id not in PARETO_CASE_IDS:
            continue
        for level in PARETO_LEVELS:
            method_key = f"pareto_{level['level_id'].lower()}"
            level_rows = _ok(rows, case_id=case.case_id, method_key=method_key)
            if not level_rows:
                continue
            out.append(
                {
                    "case": case.display_name,
                    "level_id": level["level_id"],
                    "leaf_tol": _first([_to_float(r.get("leaf_tol")) for r in level_rows]) or level["leaf_tol"],
                    "merge_tol": _first([_to_float(r.get("merge_tol")) for r in level_rows]) or level["merge_tol"],
                    "rel_error": _avg([_to_float(r.get("rel_error")) for r in level_rows]),
                    "contract_time_sec": _avg([_to_float(r.get("contract_time_sec")) for r in level_rows]),
                    "emit_time_sec": _avg([_to_float(r.get("emit_time_sec")) for r in level_rows]),
                    "total_time_sec": _avg([_to_float(r.get("total_time_sec")) for r in level_rows]),
                    "speedup_vs_exact": _avg([_to_float(r.get("speedup_vs_exact")) for r in level_rows]),
                    "t_contract_ratio": _avg([_to_float(r.get("t_contract_ratio")) for r in level_rows]),
                    "mean_rank": _avg([_to_float(r.get("mean_rank")) for r in level_rows]),
                    "peak_rank": _avg([_to_float(r.get("peak_rank")) for r in level_rows]),
                    "num_implicit_merge_sketches": _avg([_to_float(r.get("num_implicit_merge_sketches")) for r in level_rows]),
                    "cache_hit_rate": _avg([_to_float(r.get("cache_hit_rate")) for r in level_rows]),
                }
            )
    return out


def _build_blockwise_sensitivity(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for case in MAIN_CASES:
        if case.case_id not in BLOCKWISE_CASE_IDS:
            continue
        for setting in BLOCKWISE_SETTINGS:
            setting_rows = [
                row
                for row in rows
                if row.get("status") == "ok"
                and row.get("case_id") == case.case_id
                and row.get("tag") == "blockwise"
                and _to_bool(row.get("block_enabled")) == setting["block_enabled"]
                and _to_int(row.get("block_labels")) == setting["block_labels"]
                and _to_int(row.get("chunk_size")) == setting["chunk_size"]
            ]
            if not setting_rows:
                continue
            out.append(
                {
                    "case": case.display_name,
                    "block_enabled": setting["block_enabled"],
                    "block_labels": setting["block_labels"],
                    "chunk_size": setting["chunk_size"],
                    "rel_error": _avg([_to_float(r.get("rel_error")) for r in setting_rows]),
                    "contract_time_sec": _avg([_to_float(r.get("contract_time_sec")) for r in setting_rows]),
                    "emit_time_sec": _avg([_to_float(r.get("emit_time_sec")) for r in setting_rows]),
                    "total_time_sec": _avg([_to_float(r.get("total_time_sec")) for r in setting_rows]),
                    "t_contract_ratio": _avg([_to_float(r.get("t_contract_ratio")) for r in setting_rows]),
                    "speedup_vs_exact": _avg([_to_float(r.get("speedup_vs_exact")) for r in setting_rows]),
                    "cache_hit_rate": _avg([_to_float(r.get("cache_hit_rate")) for r in setting_rows]),
                    "num_cached_states": _avg([_to_float(r.get("num_cached_states")) for r in setting_rows]),
                    "mean_rank": _avg([_to_float(r.get("mean_rank")) for r in setting_rows]),
                    "peak_rank": _avg([_to_float(r.get("peak_rank")) for r in setting_rows]),
                }
            )
    return out


def _build_mechanism_internal_ablation(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    case_id = "main_grid2d_3x3"
    method_order = ["astnc_l2", "no_blockwise", "no_implicit", "no_cache"]
    label_map = {
        "astnc_l2": "ASTNC default",
        "no_blockwise": "no-blockwise",
        "no_implicit": "no-implicit",
        "no_cache": "no-cache",
    }
    out: list[dict[str, Any]] = []
    for method_key in method_order:
        method_rows = _ok(rows, case_id=case_id, method_key=method_key)
        if not method_rows:
            continue
        out.append(
            {
                "case": "Grid 3x3",
                "setting": label_map[method_key],
                "rel_error": _avg([_to_float(r.get("rel_error")) for r in method_rows]),
                "contract_time_sec": _avg([_to_float(r.get("contract_time_sec")) for r in method_rows]),
                "emit_time_sec": _avg([_to_float(r.get("emit_time_sec")) for r in method_rows]),
                "total_time_sec": _avg([_to_float(r.get("total_time_sec")) for r in method_rows]),
                "t_contract_ratio": _avg([_to_float(r.get("t_contract_ratio")) for r in method_rows]),
                "mean_rank": _avg([_to_float(r.get("mean_rank")) for r in method_rows]),
                "peak_rank": _avg([_to_float(r.get("peak_rank")) for r in method_rows]),
                "num_implicit_merge_sketches": _avg([_to_float(r.get("num_implicit_merge_sketches")) for r in method_rows]),
                "num_exact_merges": _avg([_to_float(r.get("num_exact_merges")) for r in method_rows]),
                "num_compressed_merges": _avg([_to_float(r.get("num_compressed_merges")) for r in method_rows]),
                "cache_hit_rate": _avg([_to_float(r.get("cache_hit_rate")) for r in method_rows]),
                "num_cached_states": _avg([_to_float(r.get("num_cached_states")) for r in method_rows]),
                "mean_merge_residual_ratio": _avg([_to_float(r.get("mean_merge_residual_ratio")) for r in method_rows]),
            }
        )
    return out


def _build_difficulty_trend(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for setting in DIFFICULTY_TREND_SETTINGS:
        case_id = setting["case_id"]
        exact_rows = _ok(rows, case_id=case_id, method_key="exact")
        ast_rows = _ok(rows, case_id=case_id, method_key="astnc_l2")
        if not exact_rows or not ast_rows:
            continue
        exact_total = _avg([_to_float(r.get("total_time_sec")) for r in exact_rows])
        ast_total = _avg([_to_float(r.get("total_time_sec")) for r in ast_rows])
        out.append(
            {
                "case_family": setting["case_family"],
                "size_or_difficulty_setting": setting["size_or_difficulty_setting"],
                "case": setting["display_name"],
                "topology": _first([r.get("topology") for r in ast_rows]),
                "exact_total_time_sec": exact_total,
                "rel_error": _avg([_to_float(r.get("rel_error")) for r in ast_rows]),
                "contract_time_sec": _avg([_to_float(r.get("contract_time_sec")) for r in ast_rows]),
                "total_time_sec": ast_total,
                "speedup_vs_exact": _safe_div(exact_total, ast_total),
                "t_contract_ratio": _avg([_to_float(r.get("t_contract_ratio")) for r in ast_rows]),
                "mean_rank": _avg([_to_float(r.get("mean_rank")) for r in ast_rows]),
                "peak_rank": _avg([_to_float(r.get("peak_rank")) for r in ast_rows]),
            }
        )
    return out


def _build_cache_reuse_evidence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for setting in CACHE_REUSE_SETTINGS:
        for cache_enabled in [True, False]:
            setting_rows = [
                row
                for row in rows
                if row.get("status") == "ok"
                and row.get("case_id") == "main_grid2d_3x3"
                and row.get("tag") == "cache_reuse"
                and row.get("setting_id") == setting["setting_id"]
                and row.get("cache_enabled_requested") == cache_enabled
            ]
            if not setting_rows:
                continue
            out.append(
                {
                    "case": "Grid 3x3",
                    "setting_id": setting["setting_id"],
                    "block_enabled": setting["block_enabled"],
                    "block_labels": setting["block_labels"],
                    "chunk_size": setting["chunk_size"],
                    "cache_enabled": cache_enabled,
                    "cache_requests": _avg([_to_float(r.get("cache_requests")) for r in setting_rows]),
                    "cache_hits": _avg([_to_float(r.get("cache_hits")) for r in setting_rows]),
                    "cache_hit_rate": _avg([_to_float(r.get("cache_hit_rate")) for r in setting_rows]),
                    "num_cached_states": _avg([_to_float(r.get("num_cached_states")) for r in setting_rows]),
                    "num_blocks": _avg([_to_float(r.get("num_blocks")) for r in setting_rows]),
                    "rel_error": _avg([_to_float(r.get("rel_error")) for r in setting_rows]),
                    "contract_time_sec": _avg([_to_float(r.get("contract_time_sec")) for r in setting_rows]),
                    "total_time_sec": _avg([_to_float(r.get("total_time_sec")) for r in setting_rows]),
                    "speedup_vs_exact": _avg([_to_float(r.get("speedup_vs_exact")) for r in setting_rows]),
                    "t_contract_ratio": _avg([_to_float(r.get("t_contract_ratio")) for r in setting_rows]),
                    "mean_rank": _avg([_to_float(r.get("mean_rank")) for r in setting_rows]),
                    "peak_rank": _avg([_to_float(r.get("peak_rank")) for r in setting_rows]),
                }
            )
    return out


def _write_short_readme(output_dir: Path, rows: list[dict[str, Any]]) -> None:
    pareto = _build_pareto_sweep(rows)
    mechanism_internal = _build_mechanism_internal_ablation(rows)
    weak_notes: list[str] = []

    if pareto:
        by_case: dict[str, tuple[float | None, float | None]] = {}
        for row in pareto:
            case = str(row["case"])
            rel = _to_float(row.get("rel_error"))
            speed = _to_float(row.get("speedup_vs_exact"))
            if case not in by_case:
                by_case[case] = (rel, speed)
                continue
            best_rel, best_speed = by_case[case]
            rel_candidates = [v for v in [best_rel, rel] if v is not None]
            speed_candidates = [v for v in [best_speed, speed] if v is not None]
            by_case[case] = (
                min(rel_candidates) if rel_candidates else None,
                max(speed_candidates) if speed_candidates else None,
            )
        for case, (best_rel, best_speed) in by_case.items():
            if best_rel is not None and best_speed is not None and best_rel > 1e-2:
                weak_notes.append(f"- `{case}` pareto sweep remains relatively high-error even at the strict end.")

    if mechanism_internal:
        default_row = next((row for row in mechanism_internal if row["setting"] == "ASTNC default"), None)
        no_imp_row = next((row for row in mechanism_internal if row["setting"] == "no-implicit"), None)
        if default_row and no_imp_row:
            default_err = _to_float(default_row.get("rel_error"))
            no_imp_err = _to_float(no_imp_row.get("rel_error"))
            if default_err is not None and no_imp_err is not None and abs(default_err - no_imp_err) > 5e-3:
                weak_notes.append("- `no-implicit` changed error more than expected, so the speed-only story is weaker than hoped.")

    weak_notes.append("- The tolerance sweep exposes multiple operating points, but speedup is not strictly monotone in tolerance, so the Pareto front should be drawn from the non-dominated points rather than read as a monotone curve.")
    if len(weak_notes) == 1:
        weak_notes.append("- No additional failure mode stood out beyond that non-monotonicity, but Grid 3x3 remains the most sensitive case.")

    readme = "\n".join(
        [
            "# Strengthened small-network CSVs",
            "",
            "- `raw_runs.csv`: all per-seed runs collected by the strengthened script; best for debugging and custom regrouping.",
            "- `main_results.csv`: main table compatible with the paper body; best for the main text.",
            "- `stage_breakdown.csv`: contraction vs emit stage breakdown; best for the main text.",
            "- `mechanism_ablation.csv`: compact Grid 3x3 mechanism ablation; best for the main text.",
            "- `strength_sensitivity.csv`: L1/L2/L3 strength sensitivity with Tree-8 added; fits either main text or appendix.",
            "- `pareto_sweep.csv`: continuous ASTNC tolerance sweep; best for a main-text Pareto figure or appendix support.",
            "- `blockwise_sensitivity.csv`: blockwise / chunk sensitivity; better suited for the appendix.",
            "- `mechanism_internal_ablation.csv`: internal mechanism evidence table; better suited for the appendix or an expanded paper table.",
            "",
            "## Honest notes",
            *weak_notes,
            "",
        ]
    )
    (output_dir / "README_short.md").write_text(readme, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run strengthened small-network experiments and export CSV assets.")
    parser.add_argument("--group", default="paper_strengthened")
    parser.add_argument("--output-dir", default="reproduce/csv_strengthened")
    parser.add_argument("--seeds", default="0,1,2")
    parser.add_argument("--force", action="store_true", help="Force rerun even if cached outputs exist.")
    args = parser.parse_args()

    seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]
    rows = _collect_runs(group=args.group, seeds=seeds, force=args.force)
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_csv(
        output_dir / "raw_runs.csv",
        rows,
        [
            "case_id",
            "case",
            "topology",
            "seed",
            "method_key",
            "method",
            "run_name",
            "tag",
            "status",
            "rel_error",
            "contract_time_sec",
            "emit_time_sec",
            "total_time_sec",
            "speedup_vs_exact",
            "t_contract_ratio",
            "rank_policy",
            "leaf_tol",
            "merge_tol",
            "target_rank",
            "max_rank",
            "mean_rank",
            "peak_rank",
            "num_implicit_merge_sketches",
            "num_exact_merges",
            "num_compressed_merges",
            "cache_enabled",
            "cache_requests",
            "cache_hits",
            "cache_misses",
            "cache_hit_rate",
            "num_cached_states",
            "num_blocks",
            "mean_merge_residual_ratio",
            "block_enabled",
            "block_labels",
            "chunk_size",
            "level_id",
            "leaf_tol_nominal",
            "merge_tol_nominal",
            "setting_id",
            "cache_enabled_requested",
            "run_dir",
        ],
    )

    _write_csv(
        output_dir / "main_results.csv",
        _build_main_results(rows),
        [
            "case",
            "exact_time_sec",
            "fixed_rank_rel_error",
            "fixed_rank_speedup",
            "astnc_l2_rel_error",
            "astnc_l2_speedup",
        ],
    )

    _write_csv(
        output_dir / "stage_breakdown.csv",
        _build_stage_breakdown(rows),
        ["case", "t_contract_ratio", "t_emit_ratio", "contraction_speedup", "total_speedup"],
    )

    _write_csv(
        output_dir / "mechanism_ablation.csv",
        _build_mechanism_ablation(rows),
        ["case", "setting", "rel_error", "total_time_sec", "time_ratio_vs_default"],
    )

    _write_csv(
        output_dir / "strength_sensitivity.csv",
        _build_strength_sensitivity(rows),
        ["case", "l1_rel_error", "l2_rel_error", "l3_rel_error"],
    )

    _write_csv(
        output_dir / "pareto_sweep.csv",
        _build_pareto_sweep(rows),
        [
            "case",
            "level_id",
            "leaf_tol",
            "merge_tol",
            "rel_error",
            "contract_time_sec",
            "emit_time_sec",
            "total_time_sec",
            "speedup_vs_exact",
            "t_contract_ratio",
            "mean_rank",
            "peak_rank",
            "num_implicit_merge_sketches",
            "cache_hit_rate",
        ],
    )

    _write_csv(
        output_dir / "blockwise_sensitivity.csv",
        _build_blockwise_sensitivity(rows),
        [
            "case",
            "block_enabled",
            "block_labels",
            "chunk_size",
            "rel_error",
            "contract_time_sec",
            "emit_time_sec",
            "total_time_sec",
            "t_contract_ratio",
            "speedup_vs_exact",
            "cache_hit_rate",
            "num_cached_states",
            "mean_rank",
            "peak_rank",
        ],
    )

    _write_csv(
        output_dir / "mechanism_internal_ablation.csv",
        _build_mechanism_internal_ablation(rows),
        [
            "case",
            "setting",
            "rel_error",
            "contract_time_sec",
            "emit_time_sec",
            "total_time_sec",
            "t_contract_ratio",
            "mean_rank",
            "peak_rank",
            "num_implicit_merge_sketches",
            "num_exact_merges",
            "num_compressed_merges",
            "cache_hit_rate",
            "num_cached_states",
            "mean_merge_residual_ratio",
        ],
    )

    _write_csv(
        output_dir / "difficulty_trend.csv",
        _build_difficulty_trend(rows),
        [
            "case_family",
            "size_or_difficulty_setting",
            "case",
            "topology",
            "exact_total_time_sec",
            "rel_error",
            "contract_time_sec",
            "total_time_sec",
            "speedup_vs_exact",
            "t_contract_ratio",
            "mean_rank",
            "peak_rank",
        ],
    )

    _write_csv(
        output_dir / "cache_reuse_evidence.csv",
        _build_cache_reuse_evidence(rows),
        [
            "case",
            "setting_id",
            "block_enabled",
            "block_labels",
            "chunk_size",
            "cache_enabled",
            "cache_requests",
            "cache_hits",
            "cache_hit_rate",
            "num_cached_states",
            "num_blocks",
            "rel_error",
            "contract_time_sec",
            "total_time_sec",
            "speedup_vs_exact",
            "t_contract_ratio",
            "mean_rank",
            "peak_rank",
        ],
    )

    _write_short_readme(output_dir, rows)


if __name__ == "__main__":
    main()
