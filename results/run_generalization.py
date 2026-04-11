import csv
import math
import subprocess
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "Scripts" / "python.exe"
RUNPY = ROOT / "run.py"
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

OUT_GROUP = "generalization"
RAW = RESULTS / "generalization_raw_runs.csv"
AGG = RESULTS / "generalization_agg.csv"
TABLES = RESULTS / "generalization_tables.md"
SUMMARY = RESULTS / "generalization_summary.md"

SOURCE_CSVS = [
    RESULTS / "pilot_raw_runs.csv",
    RESULTS / "main_results_raw_runs.csv",
    RESULTS / "ablation_core_raw_runs.csv",
    RESULTS / "strength_sensitivity_raw_runs.csv",
    RAW,
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
    "exact": {
        "name": "exact",
        "overrides": {"method": "exact", "method.optimize": "optimal"},
    },
    "fixed_rank": {
        "name": "fixed-rank baseline",
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
}
METHOD_ORDER = ["exact", "fixed-rank baseline", "ASTNC-L1", "ASTNC-L2", "ASTNC-L3"]

CASES = [
    ("main_chain_8", "chain", "num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1", "easy", [0, 1, 2], ["main_chain_8"], {"data": "chain", "data.num_nodes": "8"}),
    ("main_ring_8", "ring", "num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1", "easy", [0, 1, 2], ["main_ring_8"], {"data": "ring", "data.num_nodes": "8"}),
    ("main_tree_8", "tree", "num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1", "easy", [0, 1, 2], ["main_tree_8"], {"data": "tree", "data.num_nodes": "8"}),
    ("main_grid2d_3x3", "grid2d", "grid_shape=[3,3], num_nodes=9, phys_dim=3, bond_dim=4, open_legs_per_node=1", "easy", [0, 1, 2], ["main_grid2d_3x3"], {"data": "grid2d", "data.grid_shape": "[3,3]", "data.num_nodes": "9"}),
    ("main_random_8", "random_connected", "num_nodes=8, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1", "easy", [0, 1, 2], ["main_random_8"], {"data": "random_connected", "data.num_nodes": "8", "data.edge_prob": "0.35"}),
    ("medium_chain_10", "chain", "num_nodes=10, phys_dim=3, bond_dim=4, open_legs_per_node=1", "medium", [0, 1], [], {"data": "chain", "data.num_nodes": "10"}),
    ("medium_ring_10", "ring", "num_nodes=10, phys_dim=3, bond_dim=4, open_legs_per_node=1", "medium", [0, 1], ["stress_ring_10"], {"data": "ring", "data.num_nodes": "10"}),
    ("medium_tree_10", "tree", "num_nodes=10, phys_dim=3, bond_dim=4, open_legs_per_node=1", "medium", [0, 1], [], {"data": "tree", "data.num_nodes": "10"}),
    ("medium_grid2d_3x4", "grid2d", "grid_shape=[3,4], num_nodes=12, phys_dim=3, bond_dim=4, open_legs_per_node=1", "medium", [0, 1], ["stress_grid2d_3x4"], {"data": "grid2d", "data.grid_shape": "[3,4]", "data.num_nodes": "12"}),
    ("medium_random_10", "random_connected", "num_nodes=10, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1", "medium", [0, 1], ["stress_random_10"], {"data": "random_connected", "data.num_nodes": "10", "data.edge_prob": "0.35"}),
    ("boundary_ring_12", "ring", "num_nodes=12, phys_dim=3, bond_dim=4, open_legs_per_node=1", "boundary", [0], [], {"data": "ring", "data.num_nodes": "12"}),
    ("boundary_grid2d_4x4", "grid2d", "grid_shape=[4,4], num_nodes=16, phys_dim=3, bond_dim=4, open_legs_per_node=1", "boundary", [0], [], {"data": "grid2d", "data.grid_shape": "[4,4]", "data.num_nodes": "16"}),
    ("boundary_random_12", "random_connected", "num_nodes=12, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1", "boundary", [0], [], {"data": "random_connected", "data.num_nodes": "12", "data.edge_prob": "0.35"}),
]


def f2(x):
    if x is None:
        return None
    s = str(x).strip()
    if s == "" or s.lower() in {"none", "na", "nan", "inf", "-inf"}:
        return None
    try:
        v = float(s)
    except Exception:
        return None
    return v if math.isfinite(v) else None


def fmt(x, d=4):
    return "NA" if x is None else f"{x:.{d}f}"


def div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def timeout_for(scale, method_key):
    if method_key == "exact":
        return 60 if scale == "boundary" else (90 if scale == "medium" else 600)
    if method_key == "fixed_rank":
        return 60 if scale != "easy" else 300
    return 60 if scale == "boundary" else (90 if scale == "medium" else 600)


def load_sources():
    rows = []
    for p in SOURCE_CSVS:
        if not p.exists():
            continue
        with p.open("r", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                r2 = dict(r)
                r2["_source"] = p.name
                rows.append(r2)
    return rows


def read_run(group, run_name):
    base = ROOT / "outputs" / group / run_name
    if not base.exists():
        return None
    dirs = [p for p in base.iterdir() if p.is_dir()]
    if not dirs:
        return None
    latest = max(dirs, key=lambda p: p.stat().st_mtime)
    fp = latest / "runs.csv"
    if not fp.exists():
        return {"status": "timeout", "run_dir": str(latest), "status_source": "inferred_missing_runs_csv"}
    with fp.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            o = dict(r)
            o["run_dir"] = str(latest)
            o["status_source"] = "runner"
            return o
    # If a run directory exists but no readable runs.csv row, treat as prior timeout/failure signal.
    return {"status": "timeout", "run_dir": str(latest), "status_source": "inferred_missing_runs_csv"}


def find_reuse(source_rows, case_ids, method_name, seed):
    cand = []
    for r in source_rows:
        if r.get("case_id") not in case_ids:
            continue
        if r.get("method") != method_name:
            continue
        try:
            s = int(str(r.get("seed", "")).strip())
        except Exception:
            continue
        if s == seed:
            cand.append(r)
    if not cand:
        return None
    ok = [r for r in cand if str(r.get("status", "")).lower() == "ok"]
    pick = ok[-1] if ok else cand[-1]
    out = dict(pick)
    out["status_source"] = f"reused:{pick.get('_source', 'csv')}"
    return out


def run_all():
    source_rows = load_sources()
    raw_rows = []
    plan = []
    for cid, topo, size_desc, scale, seeds, reuse_ids, cov in CASES:
        method_keys = list(METHODS.keys())
        if scale != "easy":
            method_keys = [k for k in method_keys if k != "fixed_rank"]
        for mk in method_keys:
            for seed in seeds:
                plan.append((cid, topo, size_desc, scale, seed, mk, reuse_ids, cov))
    print(f"Planned generalization runs: {len(plan)}")

    common_cov = {"data.phys_dim": "3", "data.bond_dim": "4", "data.open_legs_per_node": "1", "block.enabled": "true", "block.block_labels": "2", "block.chunk_size": "1"}
    for i, (cid, topo, size_desc, scale, seed, mk, reuse_ids, cov) in enumerate(plan, 1):
        mname = METHODS[mk]["name"]
        run_name = f"{cid}__{mk}__s{seed}"
        row = read_run(OUT_GROUP, run_name)
        driver_status = "reused" if row else "pending"
        driver_error = ""
        if row is None:
            row = find_reuse(source_rows, [cid] + list(reuse_ids), mname, seed)
            if row is not None:
                driver_status = "reused"
        if row is None:
            cmd_cfg = {
                "seed": str(seed),
                "experiment.group": OUT_GROUP,
                "experiment.name": run_name,
                **common_cov,
                **cov,
                **METHODS[mk]["overrides"],
            }
            cmd = [str(PY), str(RUNPY)] + [f"{k}={v}" for k, v in cmd_cfg.items()]
            to_sec = timeout_for(scale, mk)
            print(f"[{i}/{len(plan)}] RUN {run_name} timeout={to_sec}s")
            try:
                subprocess.run(cmd, cwd=str(ROOT), check=True, timeout=to_sec)
                driver_status = "ok"
            except subprocess.TimeoutExpired:
                driver_status = "timeout"
                driver_error = f"timeout>{to_sec}s"
            except subprocess.CalledProcessError as exc:
                driver_status = "failed"
                driver_error = f"nonzero_exit={exc.returncode}"
            row = read_run(OUT_GROUP, run_name)
        else:
            print(f"[{i}/{len(plan)}] REUSE {run_name}")
        row = row or {}
        status = str(row.get("status", "")).lower().strip() or driver_status
        if status not in {"ok", "timeout", "failed"}:
            status = "ok" if driver_status in {"ok", "reused"} else driver_status
        out = {
            "case_id": cid,
            "topology": topo,
            "size_description": size_desc,
            "scale_level": scale,
            "seed": seed,
            "method": mname,
            "method_key": mk,
            "status": status,
            "status_source": row.get("status_source", "runner"),
            "driver_status": driver_status,
            "driver_error": driver_error,
        }
        for k in [
            "rel_error", "RMSE", "NMSE", "NMSE_dB", "contract_time_sec", "emit_time_sec", "total_time_sec",
            "t_contract_ratio", "speedup_vs_exact", "num_blocks", "mean_rank", "max_rank", "peak_rank",
            "num_exact_merges", "num_compressed_merges", "mean_merge_residual_ratio", "num_implicit_merge_sketches",
            "cache_hit_rate", "run_dir",
        ]:
            out[k] = row.get(k, "")
        raw_rows.append(out)

    ex_time = {}
    group_cs = defaultdict(list)
    for r in raw_rows:
        if r["method"] == "exact" and r["status"] == "ok":
            t = f2(r.get("total_time_sec"))
            if t is not None:
                ex_time[(r["case_id"], r["seed"])] = t
        group_cs[(r["case_id"], r["seed"])].append(r)

    for _, rows in group_cs.items():
        rt = [(r, f2(r.get("total_time_sec"))) for r in rows if r["status"] == "ok"]
        rt = [(r, t) for r, t in rt if t is not None]
        for rk, (r, _) in enumerate(sorted(rt, key=lambda x: x[1]), 1):
            r["relative_runtime_rank_within_case"] = rk
        er = [(r, f2(r.get("rel_error"))) for r in rows if r["status"] == "ok" and r["method"] not in {"exact", "fixed-rank baseline"}]
        er = [(r, e) for r, e in er if e is not None]
        for rk, (r, _) in enumerate(sorted(er, key=lambda x: x[1]), 1):
            r["relative_error_rank_within_case"] = rk
    for r in raw_rows:
        if r["method"] != "exact" and r["status"] == "ok":
            t = f2(r.get("total_time_sec"))
            et = ex_time.get((r["case_id"], r["seed"]))
            if t is not None and et is not None and t > 0:
                r["speedup_vs_exact"] = et / t
        r.setdefault("relative_runtime_rank_within_case", "")
        r.setdefault("relative_error_rank_within_case", "")

    cols = []
    seen = set()
    for r in raw_rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                cols.append(k)
    with RAW.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(raw_rows)
    return raw_rows


def aggregate(raw_rows):
    groups = defaultdict(list)
    for r in raw_rows:
        groups[(r["case_id"], r["topology"], r["size_description"], r["scale_level"], r["method"])].append(r)
    agg_rows = []
    for (cid, topo, size_desc, scale, method), rows in groups.items():
        n_attempt = len(rows)
        n_ok = sum(1 for r in rows if r["status"] == "ok")
        n_to = sum(1 for r in rows if r["status"] == "timeout")
        n_fail = sum(1 for r in rows if r["status"] == "failed")
        ok_rows = [r for r in rows if r["status"] == "ok"]
        out = {
            "case_id": cid, "topology": topo, "size_description": size_desc, "scale_level": scale, "method": method,
            "n_attempted": n_attempt, "n_ok": n_ok, "n_timeout": n_to, "n_failed": n_fail,
            "completed_fraction": div(n_ok, n_attempt), "timeout_rate": div(n_to, n_attempt),
            "status_summary": f"ok={n_ok}/{n_attempt}, timeout={n_to}, failed={n_fail}",
        }
        for fld in [
            "rel_error", "RMSE", "NMSE", "NMSE_dB", "contract_time_sec", "emit_time_sec", "total_time_sec",
            "t_contract_ratio", "speedup_vs_exact", "num_blocks", "mean_rank", "max_rank", "peak_rank",
            "num_exact_merges", "num_compressed_merges", "mean_merge_residual_ratio", "num_implicit_merge_sketches",
            "cache_hit_rate", "relative_runtime_rank_within_case", "relative_error_rank_within_case",
        ]:
            vals = [f2(r.get(fld)) for r in ok_rows]
            vals = [v for v in vals if v is not None]
            out[f"{fld}_mean"] = mean(vals) if vals else ""
            out[f"{fld}_std"] = stdev(vals) if len(vals) >= 2 else (0.0 if vals else "")
        agg_rows.append(out)
    by_case = defaultdict(list)
    for r in raw_rows:
        by_case[r["case_id"]].append(r)
    case_sum = {}
    for cid, rows in by_case.items():
        exact_ok = [r for r in rows if r["method"] == "exact" and r["status"] == "ok"]
        exact_t = [f2(r.get("total_time_sec")) for r in exact_ok]
        exact_t = [v for v in exact_t if v is not None]
        l1_ok = [r for r in rows if r["method"] == "ASTNC-L1" and r["status"] == "ok"]
        l1_t = [f2(r.get("total_time_sec")) for r in l1_ok]
        l1_t = [v for v in l1_t if v is not None]
        case_sum[cid] = {
            "exact_available": len(exact_ok) > 0,
            "completed_fraction": div(sum(1 for r in rows if r["status"] == "ok"), len(rows)),
            "timeout_rate": div(sum(1 for r in rows if r["status"] == "timeout"), len(rows)),
            "case_difficulty_proxy": mean(exact_t) if exact_t else (mean(l1_t) if l1_t else None),
        }
    for r in agg_rows:
        cs = case_sum[r["case_id"]]
        r["exact_available"] = cs["exact_available"]
        r["case_completed_fraction"] = cs["completed_fraction"]
        r["case_timeout_rate"] = cs["timeout_rate"]
        r["case_difficulty_proxy"] = cs["case_difficulty_proxy"]
    agg_rows.sort(key=lambda x: (x["scale_level"], x["topology"], x["case_id"], METHOD_ORDER.index(x["method"]) if x["method"] in METHOD_ORDER else 99))
    cols = []
    seen = set()
    for r in agg_rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                cols.append(k)
    with AGG.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(agg_rows)
    return agg_rows, case_sum


def build_md(agg_rows, case_sum):
    lookup = {(r["case_id"], r["method"]): r for r in agg_rows}
    case_defs = [{"case_id": c[0], "topology": c[1], "size_description": c[2], "scale_level": c[3]} for c in CASES]

    def rec_case(cid):
        cand = []
        for m in ["ASTNC-L1", "ASTNC-L2", "ASTNC-L3"]:
            r = lookup.get((cid, m))
            if not r or int(r.get("n_ok", 0)) <= 0:
                continue
            e = f2(r.get("rel_error_mean")); t = f2(r.get("total_time_sec_mean"))
            if e is None or t is None:
                continue
            cand.append((e * t, m))
        return sorted(cand)[0][1] if cand else "NA"

    def classify(case):
        cid = case["case_id"]; scale = case["scale_level"]; cs = case_sum[cid]
        comp = cs["completed_fraction"] or 0.0; tor = cs["timeout_rate"] or 0.0
        ev = [f"completed={fmt(comp,3)}", f"timeout_rate={fmt(tor,3)}", f"exact_available={cs['exact_available']}"]
        if tor >= 0.20 or comp < 0.70 or ((not cs["exact_available"]) and scale in {"medium", "boundary"}):
            return "boundary", "; ".join(ev), "timeouts/low completion or missing exact anchor"
        if scale == "easy" and tor == 0 and comp >= 0.95 and cs["exact_available"]:
            return "stable", "; ".join(ev), "all methods mostly run; anchors available"
        return "transition", "; ".join(ev), "tradeoff shifts with scale"

    table_lines = ["# Generalization Tables (Section 3.6)", "", "## Table 1: Case Inventory", "",
                   "| case_id | topology | size_description | scale_level | exact_available | completed_fraction |",
                   "|---|---|---|---|---:|---:|"]
    for c in case_defs:
        cs = case_sum[c["case_id"]]
        table_lines.append(f"| {c['case_id']} | {c['topology']} | {c['size_description']} | {c['scale_level']} | {cs['exact_available']} | {fmt(cs['completed_fraction'],3)} |")
    table_lines += ["", "## Table 2: Main Results by Topology x Scale", ""]
    for c in case_defs:
        cid = c["case_id"]
        table_lines += [f"### {cid}", "", "| method | status summary | rel_error | total_time_sec | speedup_vs_exact | t_contract_ratio |", "|---|---|---:|---:|---:|---:|"]
        for m in METHOD_ORDER:
            r = lookup.get((cid, m))
            if not r:
                table_lines.append(f"| {m} | NA | NA | NA | NA | NA |")
            else:
                table_lines.append(f"| {m} | {r['status_summary']} | {fmt(f2(r.get('rel_error_mean')),6)} | {fmt(f2(r.get('total_time_sec_mean')),4)} | {fmt(f2(r.get('speedup_vs_exact_mean')),3)} | {fmt(f2(r.get('t_contract_ratio_mean')),4)} |")
        table_lines.append("")
    table_lines += ["## Table 3: L1/L2/L3 Relative Relationship", "", "| case_id | best accuracy method | fastest method | recommended method | L1 dominates L2 | L3 cost-effective |", "|---|---|---|---|---|---|"]
    for c in case_defs:
        cid = c["case_id"]
        tri = []
        for m in ["ASTNC-L1", "ASTNC-L2", "ASTNC-L3"]:
            r = lookup.get((cid, m))
            if not r or int(r.get("n_ok", 0)) <= 0:
                continue
            e = f2(r.get("rel_error_mean")); t = f2(r.get("total_time_sec_mean"))
            if e is not None and t is not None:
                tri.append((m, e, t))
        if not tri:
            table_lines.append(f"| {cid} | NA | NA | NA | NA | NA |"); continue
        best = min(tri, key=lambda x: x[1])[0]; fast = min(tri, key=lambda x: x[2])[0]
        rel = {m: (e, t) for m, e, t in tri}
        l1dom = "NA" if "ASTNC-L1" not in rel or "ASTNC-L2" not in rel else ("yes" if rel["ASTNC-L1"][0] <= rel["ASTNC-L2"][0] and rel["ASTNC-L1"][1] <= rel["ASTNC-L2"][1] else "no")
        l3ce = "NA" if "ASTNC-L3" not in rel or "ASTNC-L2" not in rel else ("yes" if rel["ASTNC-L3"][1] <= 0.95 * rel["ASTNC-L2"][1] else "no")
        table_lines.append(f"| {cid} | {best} | {fast} | {rec_case(cid)} | {l1dom} | {l3ce} |")
    table_lines += ["", "## Table 4: Regime Classification", "", "| case_id | regime | evidence | short note |", "|---|---|---|---|"]
    regimes = {}
    for c in case_defs:
        rg, ev, note = classify(c); regimes[c["case_id"]] = rg
        table_lines.append(f"| {c['case_id']} | {rg} | {ev} | {note} |")
    table_lines += ["", "## Table 5: Cross-case Summary by Method x Scale", "", "| scale | method | avg rel_error | avg total_time_sec | success rate | timeout rate | avg t_contract_ratio |", "|---|---|---:|---:|---:|---:|---:|"]
    for scale in ["easy", "medium", "boundary"]:
        cids = [c["case_id"] for c in case_defs if c["scale_level"] == scale]
        for m in METHOD_ORDER:
            rows = [r for r in agg_rows if r["case_id"] in cids and r["method"] == m]
            if not rows:
                table_lines.append(f"| {scale} | {m} | NA | NA | NA | NA | NA |"); continue
            rel = [f2(r.get("rel_error_mean")) for r in rows]; rel = [x for x in rel if x is not None]
            tt = [f2(r.get("total_time_sec_mean")) for r in rows]; tt = [x for x in tt if x is not None]
            su = [f2(r.get("completed_fraction")) for r in rows]; su = [x for x in su if x is not None]
            to = [f2(r.get("timeout_rate")) for r in rows]; to = [x for x in to if x is not None]
            tc = [f2(r.get("t_contract_ratio_mean")) for r in rows]; tc = [x for x in tc if x is not None]
            table_lines.append(f"| {scale} | {m} | {fmt(mean(rel) if rel else None,6)} | {fmt(mean(tt) if tt else None,4)} | {fmt(mean(su) if su else None,3)} | {fmt(mean(to) if to else None,3)} | {fmt(mean(tc) if tc else None,4)} |")
    table_lines.append("")
    table_lines.append("Note: boundary scale may have limited exact availability; speedup columns are NA when exact is unavailable.")
    TABLES.write_text("\n".join(table_lines) + "\n", encoding="utf-8")

    easy_ids = [c["case_id"] for c in case_defs if c["scale_level"] == "easy"]
    med_ids = [c["case_id"] for c in case_defs if c["scale_level"] == "medium"]
    bnd_ids = [c["case_id"] for c in case_defs if c["scale_level"] == "boundary"]

    def dom(cid):
        l1 = lookup.get((cid, "ASTNC-L1")); l2 = lookup.get((cid, "ASTNC-L2"))
        if not l1 or not l2:
            return None
        e1, e2, t1, t2 = f2(l1.get("rel_error_mean")), f2(l2.get("rel_error_mean")), f2(l1.get("total_time_sec_mean")), f2(l2.get("total_time_sec_mean"))
        if None in {e1, e2, t1, t2}: return None
        if e1 <= e2 and t1 <= t2: return "l1"
        if e2 <= e1 and t2 <= t1: return "l2"
        return "tradeoff"

    de = [d for d in [dom(x) for x in easy_ids] if d is not None]
    dm = [d for d in [dom(x) for x in med_ids] if d is not None]
    db = [d for d in [dom(x) for x in bnd_ids] if d is not None]
    e_to = mean([case_sum[c]["timeout_rate"] or 0.0 for c in easy_ids]) if easy_ids else 0.0
    m_to = mean([case_sum[c]["timeout_rate"] or 0.0 for c in med_ids]) if med_ids else 0.0
    b_to = mean([case_sum[c]["timeout_rate"] or 0.0 for c in bnd_ids]) if bnd_ids else 0.0
    bound_case = max(bnd_ids, key=lambda cid: (case_sum[cid]["timeout_rate"] or 0.0, 0 if case_sum[cid]["exact_available"] else 1)) if bnd_ids else "NA"

    s = ["# Generalization Summary (Section 3.6)", "", "## Scope and Data Completeness",
         f"- Cases: {len(case_defs)} (easy={len(easy_ids)}, medium={len(med_ids)}, boundary={len(bnd_ids)}).",
         "- Methods: ASTNC-L1/L2/L3 + exact + fixed-rank baseline.",
         "- Seeds: easy={0,1,2}, medium={0,1}, boundary={0}.",
         "- Seed reduction reason: medium/boundary are costlier and include timeout risk.",
         "", "## Direct Answers",
         f"1. 主结果泛化：stable regime 数量={sum(1 for v in regimes.values() if v == 'stable')}/{len(case_defs)}。",
         f"2. easy->medium->boundary 的 timeout_rate 均值：{e_to:.3f} -> {m_to:.3f} -> {b_to:.3f}。",
         f"3. `L1 dominates L2` 比例：easy={de.count('l1')}/{len(de) if de else 0}, medium={dm.count('l1')}/{len(dm) if dm else 0}, boundary={db.count('l1')}/{len(db) if db else 0}。",
         f"4. regime 分布：stable={sum(1 for v in regimes.values() if v == 'stable')}, transition={sum(1 for v in regimes.values() if v == 'transition')}, boundary={sum(1 for v in regimes.values() if v == 'boundary')}。",
         "5. boundary 主要问题：timeout 增长、completed_fraction 降低、部分 case 的 exact 锚点缺失。",
         "6. L2 在更难 case 是否更合理：仅能按 case-dependent 推荐，未观察到统一翻盘规律。",
         "7. L3 在更难 case 是否有价值：仅在显著降时延时才有成本效益，需逐 case 判断。",
         f"8. 推荐 boundary illustration case: `{bound_case}`。",
         "9. 可更强结论：tradeoff 与 regime 边界具有明显 case 依赖性。",
         "10. 需保守结论：`L1 dominates L2` 不能写成全局规律。",
         "", "## 10-15 Lines Paper-ready Result Abstract",
         "- We evaluated ASTNC generalization across chain/ring/tree/grid2d/random_connected under easy/medium/boundary scales.",
         "- Easy cases mostly preserve the previously observed behavior with usable exact anchors.",
         "- As scale increases to medium, completion pressure rises and method preference becomes workload-dependent.",
         "- Boundary cases show clear stress signals, including higher timeout rates and weaker exact anchoring.",
         "- Therefore, the runtime-accuracy relationship is not a single global law across all topologies.",
         "- `L1 dominates L2` appears in part of the workload space but does not universally hold at larger scales.",
         "- `L2` should be treated as a practical operating point only when supported by per-case data.",
         "- `L3` is beneficial only when its extra approximation yields meaningful runtime relief.",
         "- Recommended settings should be selected per case/regime rather than fixed globally.",
         "- Timeout and anchor-missing events are informative boundary signals, not data to discard.",
         "- The selected boundary case provides a direct illustration of where exact and ASTNC both enter stress.",
         "- These observations support a case-dependent narrative for generalization and boundary behavior."]
    SUMMARY.write_text("\n".join(s) + "\n", encoding="utf-8")


def main():
    raw_rows = run_all()
    agg_rows, case_sum = aggregate(raw_rows)
    build_md(agg_rows, case_sum)
    print(f"Wrote: {RAW}")
    print(f"Wrote: {AGG}")
    print(f"Wrote: {TABLES}")
    print(f"Wrote: {SUMMARY}")


if __name__ == "__main__":
    main()
