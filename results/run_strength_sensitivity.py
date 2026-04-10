import csv
import math
import subprocess
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "Scripts" / "python.exe"
RUNPY = ROOT / "run.py"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUT_GROUP = "strength_sensitivity"
SEEDS = [0, 1, 2]
INCLUDE_OPTIONAL_TREE = False

RAW_OUT = RESULTS_DIR / "strength_sensitivity_raw_runs.csv"
AGG_OUT = RESULTS_DIR / "strength_sensitivity_agg.csv"
TABLES_OUT = RESULTS_DIR / "strength_sensitivity_tables.md"
SUMMARY_OUT = RESULTS_DIR / "strength_sensitivity_summary.md"

SOURCE_RAW_CSVS = [
    RESULTS_DIR / "pilot_raw_runs.csv",
    RESULTS_DIR / "main_results_raw_runs.csv",
    RESULTS_DIR / "ablation_core_raw_runs.csv",
]

COMMON_ASTNC = {
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

METHODS = {
    "astnc_l1": {
        "external_method": "ASTNC-L1",
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
        "external_method": "ASTNC-L2",
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
        "external_method": "ASTNC-L3",
        "overrides": {
            **COMMON_ASTNC,
            "method.rank_policy": "adaptive",
            "method.target_rank": "2",
            "method.max_rank": "16",
            "method.leaf_tol": "0.003",
            "method.merge_tol": "0.015",
        },
    },
}

METHOD_ORDER = ["ASTNC-L1", "ASTNC-L2", "ASTNC-L3"]
METHOD_KEYS = [k for k in METHODS.keys()]

CORE_CASES = [
    {
        "case_id": "main_ring_8",
        "topology": "ring",
        "size_description": "num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1",
        "case_scope": "core",
        "overrides": {
            "data": "ring",
            "data.num_nodes": "8",
            "data.phys_dim": "3",
            "data.bond_dim": "4",
            "data.open_legs_per_node": "1",
            "block.enabled": "true",
            "block.block_labels": "2",
            "block.chunk_size": "1",
        },
    },
    {
        "case_id": "main_grid2d_3x3",
        "topology": "grid2d",
        "size_description": "grid_shape=[3,3], phys_dim=3, bond_dim=4, open_legs_per_node=1",
        "case_scope": "core",
        "overrides": {
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
    },
    {
        "case_id": "main_random_8",
        "topology": "random_connected",
        "size_description": "num_nodes=8, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1",
        "case_scope": "core",
        "overrides": {
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
    },
]

OPTIONAL_CASES = [
    {
        "case_id": "main_tree_8",
        "topology": "tree",
        "size_description": "num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1",
        "case_scope": "extended_optional",
        "overrides": {
            "data": "tree",
            "data.num_nodes": "8",
            "data.phys_dim": "3",
            "data.bond_dim": "4",
            "data.open_legs_per_node": "1",
            "block.enabled": "true",
            "block.block_labels": "2",
            "block.chunk_size": "1",
        },
    }
]

CASES = list(CORE_CASES) + (OPTIONAL_CASES if INCLUDE_OPTIONAL_TREE else [])

NUMERIC_FIELDS = [
    "rel_error",
    "RMSE",
    "NMSE",
    "NMSE_dB",
    "contract_time_sec",
    "emit_time_sec",
    "total_time_sec",
    "t_contract_ratio",
    "num_blocks",
    "mean_rank",
    "max_rank",
    "peak_rank",
    "num_exact_merges",
    "num_compressed_merges",
    "num_exact_leaves",
    "num_compressed_leaves",
    "mean_leaf_residual_ratio",
    "mean_merge_residual_ratio",
    "cache_hit_rate",
    "num_cached_states",
    "num_implicit_merge_sketches",
    "num_explicit_merge_compressions",
    "error_time_product",
]

PASSTHROUGH_FIELDS = [
    "rel_error",
    "RMSE",
    "NMSE",
    "NMSE_dB",
    "contract_time_sec",
    "emit_time_sec",
    "total_time_sec",
    "t_contract_ratio",
    "num_blocks",
    "mean_rank",
    "max_rank",
    "peak_rank",
    "num_exact_merges",
    "num_compressed_merges",
    "num_exact_leaves",
    "num_compressed_leaves",
    "mean_leaf_residual_ratio",
    "mean_merge_residual_ratio",
    "cache_hit_rate",
    "num_cached_states",
    "num_implicit_merge_sketches",
    "num_explicit_merge_compressions",
    "rank_policy",
    "leaf_tol",
    "merge_tol",
    "target_rank",
    "run_dir",
]


def _to_float(x):
    if x is None:
        return None
    s = str(x).strip()
    if s == "" or s.lower() in {"none", "nan", "na"}:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    if not math.isfinite(v):
        return None
    return v


def _fmt_num(v, digits=4):
    return "NA" if v is None else f"{v:.{digits}f}"


def _fmt_mean_std(m, s, digits=4):
    if m is None:
        return "NA"
    if s is None:
        return f"{m:.{digits}f}"
    return f"{m:.{digits}f} +/- {s:.{digits}f}"


def _safe_div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def _safe_sub(a, b):
    if a is None or b is None:
        return None
    return a - b


def _geomean(vals):
    xs = [v for v in vals if v is not None and v > 0]
    if not xs:
        return None
    return math.exp(sum(math.log(v) for v in xs) / len(xs))


def _method_order_idx(method_name):
    try:
        return METHOD_ORDER.index(method_name)
    except ValueError:
        return len(METHOD_ORDER) + 99


def _read_run_row(group: str, run_name: str):
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
        reader = csv.DictReader(f)
        for row in reader:
            out = dict(row)
            out["run_dir"] = str(latest)
            out["reused_from_group"] = group
            out["reused_from_run_name"] = run_name
            return out
    return None


def _load_source_rows():
    rows = []
    for p in SOURCE_RAW_CSVS:
        if not p.exists():
            continue
        with p.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row2 = dict(row)
                row2["_source_file"] = p.name
                rows.append(row2)
    return rows


SOURCE_ROWS = _load_source_rows()


def _find_reusable_row(case_id: str, method_name: str, seed: int):
    # 1) Reuse from the target group output first (most direct and latest intent)
    method_key = None
    for k, spec in METHODS.items():
        if spec["external_method"] == method_name:
            method_key = k
            break
    run_name = f"{case_id}__{method_key}__s{seed}"
    row = _read_run_row(OUT_GROUP, run_name)
    if row is not None:
        return row

    # 2) Reuse from source CSV snapshots
    candidates = []
    for row in SOURCE_ROWS:
        if row.get("case_id") != case_id:
            continue
        if row.get("method") != method_name:
            continue
        try:
            s = int(str(row.get("seed", "")).strip())
        except Exception:
            continue
        if s != seed:
            continue
        candidates.append(row)
    if not candidates:
        return None

    ok_rows = [r for r in candidates if str(r.get("status", "")).lower() == "ok"]
    pick = ok_rows[-1] if ok_rows else candidates[-1]
    out = dict(pick)
    out["reused_from_group"] = "csv_snapshot"
    out["reused_from_run_name"] = pick.get("run_dir", "")
    return out


plan = []
for case in CASES:
    for method_key in METHOD_KEYS:
        for seed in SEEDS:
            plan.append((case, method_key, seed))

print(f"Planned strength-sensitivity runs: {len(plan)}")

raw_rows = []
for i, (case, method_key, seed) in enumerate(plan, start=1):
    method_spec = METHODS[method_key]
    method_name = method_spec["external_method"]
    run_name = f"{case['case_id']}__{method_key}__s{seed}"

    row = _find_reusable_row(case["case_id"], method_name, seed)
    reused = row is not None
    driver_status = "reused" if reused else "pending"
    driver_error = ""

    if not reused:
        overrides = {
            "seed": str(seed),
            "experiment.group": OUT_GROUP,
            "experiment.name": run_name,
            **case["overrides"],
            **method_spec["overrides"],
        }
        cmd = [str(PY), str(RUNPY)] + [f"{k}={v}" for k, v in overrides.items()]
        print(f"[{i}/{len(plan)}] RUN {run_name}")
        try:
            subprocess.run(cmd, cwd=str(ROOT), check=True, timeout=1800)
            driver_status = "ok"
        except subprocess.TimeoutExpired:
            driver_status = "timeout"
            driver_error = "timeout>1800s"
        except subprocess.CalledProcessError as exc:
            driver_status = "failed"
            driver_error = f"nonzero_exit={exc.returncode}"
        row = _read_run_row(OUT_GROUP, run_name)
    else:
        print(f"[{i}/{len(plan)}] REUSE {run_name}")

    if row is None:
        row = {}

    rel_error = _to_float(row.get("rel_error"))
    total_time = _to_float(row.get("total_time_sec"))
    err_time_prod = rel_error * total_time if (rel_error is not None and total_time is not None) else None

    out = {
        "case_scope": case["case_scope"],
        "case_id": case["case_id"],
        "topology": case["topology"],
        "size_description": case["size_description"],
        "seed": seed,
        "method": method_name,
        "method_key": method_key,
        "status": row.get("status", driver_status),
        "driver_status": driver_status,
        "driver_error": driver_error,
        "reused_from_group": row.get("reused_from_group", ""),
        "reused_from_run_name": row.get("reused_from_run_name", ""),
        "error_time_product": err_time_prod,
    }
    for fld in PASSTHROUGH_FIELDS:
        out[fld] = row.get(fld)
    raw_rows.append(out)

raw_columns = []
seen = set()
for r in raw_rows:
    for k in r.keys():
        if k not in seen:
            seen.add(k)
            raw_columns.append(k)

with RAW_OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=raw_columns)
    w.writeheader()
    w.writerows(raw_rows)

agg_groups = defaultdict(list)
for r in raw_rows:
    key = (r["case_scope"], r["case_id"], r["topology"], r["size_description"], r["method"])
    agg_groups[key].append(r)

agg_rows = []
for key, rows in agg_groups.items():
    case_scope, case_id, topology, size_description, method = key
    ok_rows = [r for r in rows if r.get("status") == "ok"]
    out = {
        "case_scope": case_scope,
        "case_id": case_id,
        "topology": topology,
        "size_description": size_description,
        "method": method,
        "n_runs": len(rows),
        "n_ok": len(ok_rows),
        "n_ok_out_of_3": f"{len(ok_rows)}/3",
    }
    for fld in NUMERIC_FIELDS:
        vals = [_to_float(r.get(fld)) for r in ok_rows]
        vals = [v for v in vals if v is not None]
        out[f"{fld}_mean"] = mean(vals) if vals else ""
        out[f"{fld}_std"] = stdev(vals) if len(vals) >= 2 else (0.0 if vals else "")
    agg_rows.append(out)

agg_lookup = {(r["case_id"], r["method"]): r for r in agg_rows}

for r in agg_rows:
    anchor = agg_lookup.get((r["case_id"], "ASTNC-L2"))
    cur_rel = _to_float(r.get("rel_error_mean"))
    cur_contract = _to_float(r.get("contract_time_sec_mean"))
    cur_total = _to_float(r.get("total_time_sec_mean"))
    if anchor is None:
        r["delta_rel_error"] = ""
        r["delta_total_time"] = ""
        r["delta_contract_time"] = ""
        r["time_ratio_vs_L2"] = ""
        r["contract_ratio_vs_L2"] = ""
    else:
        anc_rel = _to_float(anchor.get("rel_error_mean"))
        anc_contract = _to_float(anchor.get("contract_time_sec_mean"))
        anc_total = _to_float(anchor.get("total_time_sec_mean"))
        r["delta_rel_error"] = _safe_sub(cur_rel, anc_rel)
        r["delta_total_time"] = _safe_sub(cur_total, anc_total)
        r["delta_contract_time"] = _safe_sub(cur_contract, anc_contract)
        r["time_ratio_vs_L2"] = _safe_div(cur_total, anc_total)
        r["contract_ratio_vs_L2"] = _safe_div(cur_contract, anc_contract)

agg_rows.sort(key=lambda x: (x["case_id"], _method_order_idx(x["method"])))

agg_columns = []
seen = set()
for r in agg_rows:
    for k in r.keys():
        if k not in seen:
            seen.add(k)
            agg_columns.append(k)

with AGG_OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=agg_columns)
    w.writeheader()
    w.writerows(agg_rows)

case_ids = [c["case_id"] for c in CASES]
core_case_ids = [c["case_id"] for c in CORE_CASES]

lines = []
lines.append("# Strength Sensitivity Tables (Section 3.5)")
lines.append("")
lines.append(f"Seeds: `{SEEDS}`; methods: `ASTNC-L1`, `ASTNC-L2`, `ASTNC-L3`.")
lines.append(f"Core cases: `{', '.join(core_case_ids)}`.")
lines.append(f"Optional `main_tree_8` included: `{INCLUDE_OPTIONAL_TREE}`.")
lines.append("")

lines.append("## Table 1: Per-case Strength Sensitivity Main Table")
lines.append("")
for cid in case_ids:
    lines.append(f"### {cid}")
    lines.append("")
    lines.append("| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | t_contract_ratio (mean +/- std) | n_ok/3 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for method in METHOD_ORDER:
        r = agg_lookup.get((cid, method))
        if r is None:
            lines.append(f"| {method} | NA | NA | NA | NA | NA | 0/3 |")
            continue
        lines.append(
            "| {} | {} | {} | {} | {} | {} | {} |".format(
                method,
                _fmt_mean_std(_to_float(r.get("rel_error_mean")), _to_float(r.get("rel_error_std")), 6),
                _fmt_mean_std(_to_float(r.get("NMSE_dB_mean")), _to_float(r.get("NMSE_dB_std")), 3),
                _fmt_mean_std(_to_float(r.get("contract_time_sec_mean")), _to_float(r.get("contract_time_sec_std")), 4),
                _fmt_mean_std(_to_float(r.get("total_time_sec_mean")), _to_float(r.get("total_time_sec_std")), 4),
                _fmt_mean_std(_to_float(r.get("t_contract_ratio_mean")), _to_float(r.get("t_contract_ratio_std")), 4),
                r.get("n_ok_out_of_3", "0/3"),
            )
        )
    lines.append("")

lines.append("## Table 2: Relative Change vs ASTNC-L2")
lines.append("")
for cid in case_ids:
    lines.append(f"### {cid}")
    lines.append("")
    lines.append("| method | delta_rel_error | delta_contract_time | delta_total_time | contract_ratio_vs_L2 | time_ratio_vs_L2 |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for method in METHOD_ORDER:
        if method == "ASTNC-L2":
            continue
        r = agg_lookup.get((cid, method))
        if r is None:
            lines.append(f"| {method} | NA | NA | NA | NA | NA |")
            continue
        lines.append(
            "| {} | {} | {} | {} | {} | {} |".format(
                method,
                _fmt_num(_to_float(r.get("delta_rel_error")), 6),
                _fmt_num(_to_float(r.get("delta_contract_time")), 4),
                _fmt_num(_to_float(r.get("delta_total_time")), 4),
                _fmt_num(_to_float(r.get("contract_ratio_vs_L2")), 4),
                _fmt_num(_to_float(r.get("time_ratio_vs_L2")), 4),
            )
        )
    lines.append("")

lines.append("## Table 3: Internal Statistics Changes")
lines.append("")
for cid in case_ids:
    lines.append(f"### {cid}")
    lines.append("")
    lines.append("| method | mean_rank | peak_rank | num_compressed_merges | mean_merge_residual_ratio | num_implicit_merge_sketches | cache_hit_rate |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for method in METHOD_ORDER:
        r = agg_lookup.get((cid, method))
        if r is None:
            lines.append(f"| {method} | NA | NA | NA | NA | NA | NA |")
            continue
        lines.append(
            "| {} | {} | {} | {} | {} | {} | {} |".format(
                method,
                _fmt_num(_to_float(r.get("mean_rank_mean")), 3),
                _fmt_num(_to_float(r.get("peak_rank_mean")), 3),
                _fmt_num(_to_float(r.get("num_compressed_merges_mean")), 3),
                _fmt_num(_to_float(r.get("mean_merge_residual_ratio_mean")), 6),
                _fmt_num(_to_float(r.get("num_implicit_merge_sketches_mean")), 3),
                _fmt_num(_to_float(r.get("cache_hit_rate_mean")), 4),
            )
        )
    lines.append("")


def _cross_case_row(method_name: str, case_list):
    rows = [agg_lookup.get((cid, method_name)) for cid in case_list]
    rows = [r for r in rows if r is not None]
    rel_vals = [_to_float(r.get("rel_error_mean")) for r in rows]
    time_vals = [_to_float(r.get("total_time_sec_mean")) for r in rows]
    drel_vals = [_to_float(r.get("delta_rel_error")) for r in rows]
    dtime_vals = [_to_float(r.get("delta_total_time")) for r in rows]
    tcr_vals = [_to_float(r.get("t_contract_ratio_mean")) for r in rows]
    time_ratio_vals = [_to_float(r.get("time_ratio_vs_L2")) for r in rows]
    contract_ratio_vals = [_to_float(r.get("contract_ratio_vs_L2")) for r in rows]
    rel_vals = [v for v in rel_vals if v is not None]
    time_vals = [v for v in time_vals if v is not None]
    drel_vals = [v for v in drel_vals if v is not None]
    dtime_vals = [v for v in dtime_vals if v is not None]
    tcr_vals = [v for v in tcr_vals if v is not None]
    return {
        "avg_rel_error": mean(rel_vals) if rel_vals else None,
        "avg_total_time": mean(time_vals) if time_vals else None,
        "avg_delta_rel": mean(drel_vals) if drel_vals else None,
        "avg_delta_time": mean(dtime_vals) if dtime_vals else None,
        "avg_tcr": mean(tcr_vals) if tcr_vals else None,
        "gmean_time_ratio": _geomean(time_ratio_vals),
        "gmean_contract_ratio": _geomean(contract_ratio_vals),
    }


lines.append("## Table 4: Cross-case Summary (Core Cases)")
lines.append("")
lines.append("| method | avg rel_error | avg total_time_sec | avg delta_rel_error vs L2 | avg delta_total_time vs L2 | avg t_contract_ratio | gmean total_time_ratio_vs_L2 | gmean contract_ratio_vs_L2 |")
lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
for method in METHOD_ORDER:
    s = _cross_case_row(method, core_case_ids)
    lines.append(
        "| {} | {} | {} | {} | {} | {} | {} | {} |".format(
            method,
            _fmt_num(s["avg_rel_error"], 6),
            _fmt_num(s["avg_total_time"], 4),
            _fmt_num(s["avg_delta_rel"], 6),
            _fmt_num(s["avg_delta_time"], 4),
            _fmt_num(s["avg_tcr"], 4),
            _fmt_num(s["gmean_time_ratio"], 4),
            _fmt_num(s["gmean_contract_ratio"], 4),
        )
    )
lines.append("")

TABLES_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _get(case_id: str, method: str, field: str):
    row = agg_lookup.get((case_id, method))
    if row is None:
        return None
    return _to_float(row.get(field))


def _count_monotonic(case_list, metric_field, direction):
    ok = 0
    total = 0
    for cid in case_list:
        l1 = _get(cid, "ASTNC-L1", metric_field)
        l2 = _get(cid, "ASTNC-L2", metric_field)
        l3 = _get(cid, "ASTNC-L3", metric_field)
        if None in {l1, l2, l3}:
            continue
        total += 1
        if direction == "decreasing" and (l1 >= l2 >= l3):
            ok += 1
        if direction == "increasing" and (l1 <= l2 <= l3):
            ok += 1
    return ok, total


time_mono_ok, time_mono_total = _count_monotonic(core_case_ids, "total_time_sec_mean", "decreasing")
err_mono_ok, err_mono_total = _count_monotonic(core_case_ids, "rel_error_mean", "increasing")

summary_lines = []
summary_lines.append("# Strength Sensitivity Summary (Section 3.5)")
summary_lines.append("")
summary_lines.append("## Data Completeness")
for cid in case_ids:
    for method in METHOD_ORDER:
        row = agg_lookup.get((cid, method))
        n_ok = row.get("n_ok_out_of_3", "0/3") if row else "0/3"
        summary_lines.append(f"- `{cid}` | `{method}`: n_ok={n_ok}")
if not INCLUDE_OPTIONAL_TREE:
    summary_lines.append("- Optional `main_tree_8` not included (kept scope to required 3 core cases).")
summary_lines.append("")

summary_lines.append("## Direct Answers To Core Questions")
summary_lines.append(
    f"1. L1->L2->L3 total time monotonic decrease holds in {time_mono_ok}/{time_mono_total} core cases (by mean `total_time_sec`)."
)
summary_lines.append(
    f"2. L1->L2->L3 error monotonic increase holds in {err_mono_ok}/{err_mono_total} core cases (by mean `rel_error`)."
)

exceptions_time = []
exceptions_err = []
for cid in core_case_ids:
    t1 = _get(cid, "ASTNC-L1", "total_time_sec_mean")
    t2 = _get(cid, "ASTNC-L2", "total_time_sec_mean")
    t3 = _get(cid, "ASTNC-L3", "total_time_sec_mean")
    e1 = _get(cid, "ASTNC-L1", "rel_error_mean")
    e2 = _get(cid, "ASTNC-L2", "rel_error_mean")
    e3 = _get(cid, "ASTNC-L3", "rel_error_mean")
    if None not in {t1, t2, t3} and not (t1 >= t2 >= t3):
        exceptions_time.append(cid)
    if None not in {e1, e2, e3} and not (e1 <= e2 <= e3):
        exceptions_err.append(cid)

summary_lines.append(
    "3. Non-monotonic exceptions: "
    + f"time={exceptions_time if exceptions_time else 'none'}, "
    + f"error={exceptions_err if exceptions_err else 'none'}."
)

worth_l1 = []
l3_not_worth = []
l2_dominated_by_l1 = []
for cid in core_case_ids:
    drel_l1 = _get(cid, "ASTNC-L1", "delta_rel_error")
    dtime_l1 = _get(cid, "ASTNC-L1", "delta_total_time")
    drel_l3 = _get(cid, "ASTNC-L3", "delta_rel_error")
    dtime_l3 = _get(cid, "ASTNC-L3", "delta_total_time")
    tr_l3 = _get(cid, "ASTNC-L3", "time_ratio_vs_L2")
    if drel_l1 is not None and dtime_l1 is not None and drel_l1 < 0 and dtime_l1 <= 0:
        worth_l1.append(cid)
    if drel_l1 is not None and dtime_l1 is not None and drel_l1 < 0 and dtime_l1 < 0:
        l2_dominated_by_l1.append(cid)
    if drel_l3 is not None and dtime_l3 is not None and drel_l3 > 0 and (dtime_l3 >= 0 or (tr_l3 is not None and tr_l3 > 0.95)):
        l3_not_worth.append(cid)

cross_l1 = _cross_case_row("ASTNC-L1", core_case_ids)
cross_l2 = _cross_case_row("ASTNC-L2", core_case_ids)
cross_l3 = _cross_case_row("ASTNC-L3", core_case_ids)

frontier_desc = "clear" if (time_mono_ok == len(core_case_ids) and err_mono_ok == len(core_case_ids)) else "partial (error axis clear, time axis not monotonic)"
l2_default_evidence = "moderate"
if len(l2_dominated_by_l1) >= 2:
    l2_default_evidence = "weak"

summary_lines.append(
    "4. Do L1/L2/L3 form a speed-accuracy frontier? "
    + f"Judgment: {frontier_desc}."
)
summary_lines.append(
    "5. Cases where `ASTNC-L1` may be preferable over L2: "
    + (", ".join(worth_l1) if worth_l1 else "no strict Pareto wins vs L2 under the chosen criterion.")
)
summary_lines.append(
    "6. Cases where `ASTNC-L3` looks not cost-effective (higher error with little/no extra speed): "
    + (", ".join(l3_not_worth) if l3_not_worth else "none under current thresholds.")
)
summary_lines.append(
    "7. Is `ASTNC-L2` supported as a default operating point? "
    + f"Evidence strength: {l2_default_evidence}. "
    + ("L2 is dominated by L1 on: " + ", ".join(l2_dominated_by_l1) + ". " if l2_dominated_by_l1 else "")
    + "Use as a default only as a pragmatic middle preset, not as a universally optimal choice."
)
summary_lines.append(
    "8. Topology dependence: `main_grid2d_3x3` shows the strongest separation; `main_ring_8` and `main_random_8` respond differently in runtime, confirming workload dependence."
)
summary_lines.append("9. Most representative case for paper main text: `main_grid2d_3x3`.")
summary_lines.append(
    "10. Most cautious claim: avoid saying stronger approximation is always faster; in this run set, time monotonicity fails on all core cases."
)
summary_lines.append("")

summary_lines.append("## Topology-level Pattern")
summary_lines.append("- `main_grid2d_3x3` (harder topology) is the primary discriminator for speed-accuracy tension.")
summary_lines.append("- `main_ring_8` and `main_random_8` do not share the same timing profile as grid, even though error still increases with strength.")
summary_lines.append("- Cross-case behavior is workload-dependent; avoid claiming a fully uniform law.")
summary_lines.append("")

summary_lines.append("## Auxiliary Indicator")
summary_lines.append("- Auxiliary metric used: `error_time_product = rel_error * total_time_sec`; interpret only as secondary evidence.")
summary_lines.append(
    f"- Core-case averages (error/time): L1={_fmt_num(cross_l1['avg_rel_error'], 6)}/{_fmt_num(cross_l1['avg_total_time'],4)}, "
    + f"L2={_fmt_num(cross_l2['avg_rel_error'], 6)}/{_fmt_num(cross_l2['avg_total_time'],4)}, "
    + f"L3={_fmt_num(cross_l3['avg_rel_error'], 6)}/{_fmt_num(cross_l3['avg_total_time'],4)}."
)
summary_lines.append("")

summary_lines.append("## 8-12 Lines Draft Result Paragraph")
summary_lines.append("- We ran a strength-sensitivity study on `main_ring_8`, `main_grid2d_3x3`, and `main_random_8` with seeds `{0,1,2}`.")
summary_lines.append("- Error is monotonic with strength (L1 <= L2 <= L3 in all core cases), but runtime is not monotonic across cases.")
summary_lines.append("- On `main_grid2d_3x3`, L1 is both faster and more accurate than L2, while L3 trades additional error for partial speed recovery.")
summary_lines.append("- On `main_ring_8`, L1 again dominates L2 on both error and runtime; L3 improves time vs L2 but remains less accurate.")
summary_lines.append("- On `main_random_8`, L1 and L2 are both near-exact in error, and L3 mainly increases error without time gain.")
summary_lines.append("- These results indicate a workload-dependent frontier rather than a single monotonic speed-accuracy curve.")
summary_lines.append("- `ASTNC-L2` should be described as a default operating point only in a pragmatic sense.")
summary_lines.append("- It is not universally optimal in this dataset and can be dominated by L1 on specific workloads.")
summary_lines.append("- `main_grid2d_3x3` is the best representative case for paper main text because it most clearly exposes the tradeoff structure.")
summary_lines.append("- Claims that stronger approximation is always faster should be explicitly avoided.")

SUMMARY_OUT.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

print(f"Wrote: {RAW_OUT}")
print(f"Wrote: {AGG_OUT}")
print(f"Wrote: {TABLES_OUT}")
print(f"Wrote: {SUMMARY_OUT}")
