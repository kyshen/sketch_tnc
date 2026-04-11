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
}

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

STRENGTH_CASE_IDS = {"main_ring_8", "main_grid2d_3x3", "main_random_8"}


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


def _safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or b == 0:
        return None
    return a / b


def _avg(values: list[float | None]) -> float | None:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return mean(nums)


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


def _execute_one(
    *,
    case: CaseSpec,
    method_key: str,
    seed: int,
    group: str,
    force: bool,
) -> dict[str, Any]:
    run_name = f"{case.case_id}__{method_key}__s{seed}"
    row = None if force else _read_single_run_row(group, run_name)
    if row is None:
        overrides = {
            "seed": str(seed),
            "experiment.group": group,
            "experiment.name": run_name,
            **case.overrides,
            **METHODS[method_key]["overrides"],
        }
        cmd = [sys.executable, str(RUNPY)] + [f"{k}={v}" for k, v in overrides.items()]
        subprocess.run(cmd, cwd=str(ROOT), check=True, timeout=1800)
        row = _read_single_run_row(group, run_name)
    if row is None:
        return {
            "case_id": case.case_id,
            "case": case.display_name,
            "topology": case.topology,
            "seed": seed,
            "method_key": method_key,
            "method": METHODS[method_key]["name"],
            "status": "failed",
        }

    return {
        "case_id": case.case_id,
        "case": case.display_name,
        "topology": case.topology,
        "seed": seed,
        "method_key": method_key,
        "method": METHODS[method_key]["name"],
        "status": row.get("status", "failed"),
        "rel_error": _to_float(row.get("rel_error")),
        "contract_time_sec": _to_float(row.get("contract_time_sec")),
        "emit_time_sec": _to_float(row.get("emit_time_sec")),
        "total_time_sec": _to_float(row.get("total_time_sec")),
        "t_contract_ratio": _to_float(row.get("t_contract_ratio")),
        "rank_policy": row.get("rank_policy"),
        "leaf_tol": _to_float(row.get("leaf_tol")),
        "merge_tol": _to_float(row.get("merge_tol")),
        "cache_enabled": row.get("cache_enabled"),
        "num_implicit_merge_sketches": _to_float(row.get("num_implicit_merge_sketches")),
        "run_dir": row.get("run_dir"),
    }


def _collect_runs(group: str, seeds: list[int], force: bool) -> list[dict[str, Any]]:
    required_specs: set[tuple[str, str, int]] = set()

    for case in MAIN_CASES:
        for method_key in ["exact", "fixed_rank", "astnc_l2"]:
            for seed in seeds:
                required_specs.add((case.case_id, method_key, seed))

    grid_case_id = "main_grid2d_3x3"
    for method_key in ["astnc_l2", "no_blockwise", "no_implicit"]:
        for seed in seeds:
            required_specs.add((grid_case_id, method_key, seed))

    for case in MAIN_CASES:
        if case.case_id not in STRENGTH_CASE_IDS:
            continue
        for method_key in ["astnc_l1", "astnc_l2", "astnc_l3"]:
            for seed in seeds:
                required_specs.add((case.case_id, method_key, seed))

    case_lookup = {case.case_id: case for case in MAIN_CASES}
    rows: list[dict[str, Any]] = []
    for case_id, method_key, seed in sorted(required_specs):
        rows.append(
            _execute_one(
                case=case_lookup[case_id],
                method_key=method_key,
                seed=seed,
                group=group,
                force=force,
            )
        )
    return rows


def _ok(rows: list[dict[str, Any]], case_id: str, method_key: str) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row["case_id"] == case_id and row["method_key"] == method_key and row.get("status") == "ok"
    ]


def _build_main_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    ast_errors: list[float | None] = []
    ast_speedups: list[float | None] = []

    for case in MAIN_CASES:
        exact_rows = _ok(rows, case.case_id, "exact")
        fixed_rows = _ok(rows, case.case_id, "fixed_rank")
        ast_rows = _ok(rows, case.case_id, "astnc_l2")

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
        exact_rows = _ok(rows, case.case_id, "exact")
        ast_rows = _ok(rows, case.case_id, "astnc_l2")

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
    default_rows = _ok(rows, case_id, "astnc_l2")
    default_total = _avg([_to_float(r.get("total_time_sec")) for r in default_rows])

    method_order = ["astnc_l2", "no_blockwise", "no_implicit"]
    label_map = {
        "astnc_l2": "ASTNC (default)",
        "no_blockwise": "no-blockwise",
        "no_implicit": "no-implicit",
    }

    out: list[dict[str, Any]] = []
    for method_key in method_order:
        method_rows = _ok(rows, case_id, method_key)
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
        if case.case_id not in STRENGTH_CASE_IDS:
            continue
        l1 = _avg([_to_float(r.get("rel_error")) for r in _ok(rows, case.case_id, "astnc_l1")])
        l2 = _avg([_to_float(r.get("rel_error")) for r in _ok(rows, case.case_id, "astnc_l2")])
        l3 = _avg([_to_float(r.get("rel_error")) for r in _ok(rows, case.case_id, "astnc_l3")])
        out.append(
            {
                "case": case.display_name,
                "l1_rel_error": l1,
                "l2_rel_error": l2,
                "l3_rel_error": l3,
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run minimal paper experiment reproduction and export CSV only.")
    parser.add_argument("--group", default="paper_reproduce")
    parser.add_argument("--output-dir", default="reproduce/csv")
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
            "status",
            "rel_error",
            "contract_time_sec",
            "emit_time_sec",
            "total_time_sec",
            "t_contract_ratio",
            "rank_policy",
            "leaf_tol",
            "merge_tol",
            "cache_enabled",
            "num_implicit_merge_sketches",
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


if __name__ == "__main__":
    main()
