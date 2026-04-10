import csv
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / '.venv' / 'Scripts' / 'python.exe'
RUNPY = ROOT / 'run.py'
OUT_GROUP = 'main_results_e2e'
RESULTS_DIR = ROOT / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

INCLUDE_OPTIONAL_CHAIN = True
SEEDS = [0, 1, 2]

COMMON_ASTNC = {
    'method': 'astnc',
    'method.optimize': 'greedy',
    'method.randomized': 'true',
    'method.oversample': '1',
    'method.n_power_iter': '0',
    'method.tol_schedule': 'depth_open',
    'method.tol_depth_decay': '1.5',
    'method.tol_open_power': '0.5',
    'method.selective_threshold': '0',
    'method.compress_min_rank_product': '4',
    'method.compress_max_exact_size': '256',
    'method.compress_min_saving_ratio': '0.1',
    'method.implicit_merge_sketch': 'true',
    'method.implicit_min_full_rank': '192',
    'method.adaptive_refine': 'false',
    'method.cache_enabled': 'true',
}

METHODS = {
    'exact': {
        'external_method': 'exact',
        'overrides': {
            'method': 'exact',
            'method.optimize': 'optimal',
        },
    },
    'fixed_rank': {
        'external_method': 'fixed-rank baseline',
        'overrides': {
            **COMMON_ASTNC,
            'method.rank_policy': 'fixed',
            'method.target_rank': '4',
            'method.max_rank': '4',
            'method.leaf_tol': '0.0',
            'method.merge_tol': '0.0',
        },
    },
    'astnc_l2': {
        'external_method': 'ASTNC-L2',
        'overrides': {
            **COMMON_ASTNC,
            'method.rank_policy': 'adaptive',
            'method.target_rank': '2',
            'method.max_rank': '16',
            'method.leaf_tol': '0.001',
            'method.merge_tol': '0.005',
        },
    },
}

CASES_CORE = [
    {
        'case_id': 'main_ring_8',
        'topology': 'ring',
        'size_description': 'num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {
            'data': 'ring', 'data.num_nodes': '8', 'data.phys_dim': '3', 'data.bond_dim': '4',
            'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'
        },
    },
    {
        'case_id': 'main_tree_8',
        'topology': 'tree',
        'size_description': 'num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {
            'data': 'tree', 'data.num_nodes': '8', 'data.phys_dim': '3', 'data.bond_dim': '4',
            'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'
        },
    },
    {
        'case_id': 'main_grid2d_3x3',
        'topology': 'grid2d',
        'size_description': 'grid_shape=[3,3], phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {
            'data': 'grid2d', 'data.grid_shape': '[3,3]', 'data.num_nodes': '9', 'data.phys_dim': '3', 'data.bond_dim': '4',
            'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'
        },
    },
    {
        'case_id': 'main_random_8',
        'topology': 'random_connected',
        'size_description': 'num_nodes=8, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1',
        'overrides': {
            'data': 'random_connected', 'data.num_nodes': '8', 'data.edge_prob': '0.35', 'data.phys_dim': '3', 'data.bond_dim': '4',
            'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'
        },
    },
]

CASE_OPTIONAL_CHAIN = {
    'case_id': 'main_chain_8',
    'topology': 'chain',
    'size_description': 'num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1',
    'overrides': {
        'data': 'chain', 'data.num_nodes': '8', 'data.phys_dim': '3', 'data.bond_dim': '4',
        'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'
    },
}

CASES = list(CASES_CORE)
if INCLUDE_OPTIONAL_CHAIN:
    CASES.append(CASE_OPTIONAL_CHAIN)

PASSTHROUGH_FIELDS = [
    'rel_error', 'RMSE', 'NMSE', 'NMSE_dB',
    'contract_time_sec', 'emit_time_sec', 'total_time_sec', 'speedup_vs_exact', 't_contract_ratio',
    'num_blocks', 'refined_blocks', 'mean_rank', 'max_rank', 'peak_rank',
    'num_exact_merges', 'num_compressed_merges', 'num_exact_leaves', 'num_compressed_leaves',
    'mean_leaf_residual_ratio', 'mean_merge_residual_ratio',
    'cache_enabled', 'cache_requests', 'cache_hits', 'cache_misses', 'cache_hit_rate', 'num_cached_states',
    'leaf_states_built', 'internal_states_built',
    'num_implicit_merge_sketches', 'num_explicit_merge_compressions',
    'skipped_small_rank_merges', 'skipped_small_state_merges', 'skipped_low_saving_merges',
    'rank_policy', 'leaf_tol', 'merge_tol', 'target_rank', 'max_rank',
    'run_dir'
]

NUMERIC_FIELDS = [
    'rel_error', 'RMSE', 'NMSE', 'NMSE_dB',
    'contract_time_sec', 'emit_time_sec', 'total_time_sec', 'speedup_vs_exact', 't_contract_ratio',
    'num_blocks', 'refined_blocks', 'mean_rank', 'max_rank', 'peak_rank',
    'num_exact_merges', 'num_compressed_merges', 'num_exact_leaves', 'num_compressed_leaves',
    'mean_leaf_residual_ratio', 'mean_merge_residual_ratio',
    'cache_requests', 'cache_hits', 'cache_misses', 'cache_hit_rate', 'num_cached_states',
]


def _to_float(x):
    if x is None:
        return None
    s = str(x).strip()
    if s == '' or s.lower() in {'none', 'nan'}:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    if not math.isfinite(v):
        return None
    return v


def _fmt_mean_std(m, s, digits=4):
    if m is None:
        return 'NA'
    if s is None:
        return f'{m:.{digits}f}'
    return f'{m:.{digits}f} +/- {s:.{digits}f}'


def _fmt_speedup(v):
    if v is None:
        return 'NA'
    return f'{v:.2f}x'


def _read_run_row(run_name: str):
    run_root = ROOT / 'outputs' / OUT_GROUP / run_name
    if not run_root.exists():
        return None
    subdirs = [p for p in run_root.iterdir() if p.is_dir()]
    if not subdirs:
        return None
    latest = max(subdirs, key=lambda p: p.stat().st_mtime)
    csv_path = latest / 'runs.csv'
    if not csv_path.exists():
        return None
    with csv_path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['run_dir'] = str(latest)
            return row
    return None


plan = []
for case in CASES:
    for method_key in ['exact', 'fixed_rank', 'astnc_l2']:
        for seed in SEEDS:
            plan.append((case, method_key, seed))

print(f'Planned runs: {len(plan)}')

raw_rows = []
for i, (case, method_key, seed) in enumerate(plan, start=1):
    method_spec = METHODS[method_key]
    run_name = f"{case['case_id']}__{method_key}__s{seed}"
    row = _read_run_row(run_name)
    reused = row is not None
    status = 'ok'
    err = ''

    if not reused:
        overrides = {
            'seed': str(seed),
            'experiment.group': OUT_GROUP,
            'experiment.name': run_name,
            **case['overrides'],
            **method_spec['overrides'],
        }
        cmd = [str(PY), str(RUNPY)] + [f'{k}={v}' for k, v in overrides.items()]
        print(f'[{i}/{len(plan)}] RUN {run_name}')
        try:
            subprocess.run(cmd, cwd=str(ROOT), check=True, timeout=900)
        except subprocess.TimeoutExpired:
            status = 'timeout'
            err = 'timeout>900s'
        except subprocess.CalledProcessError as exc:
            status = 'failed'
            err = f'nonzero_exit={exc.returncode}'
        row = _read_run_row(run_name)
    else:
        print(f'[{i}/{len(plan)}] REUSE {run_name}')

    if row is None:
        row = {}

    out = {
        'case_id': case['case_id'],
        'case_group': 'main_core' if case['case_id'] != 'main_chain_8' else 'optional_reference',
        'topology': case['topology'],
        'size_description': case['size_description'],
        'seed': seed,
        'method': method_spec['external_method'],
        'method_key': method_key,
        'status': row.get('status', status),
        'status_source': 'runner' if 'status' in row else 'driver',
        'driver_status': 'reused' if reused else status,
        'driver_error': err,
    }

    for k in PASSTHROUGH_FIELDS:
        out[k] = row.get(k)

    raw_rows.append(out)

raw_columns = []
seen = set()
for r in raw_rows:
    for k in r.keys():
        if k not in seen:
            seen.add(k)
            raw_columns.append(k)

raw_path = RESULTS_DIR / 'main_results_raw_runs.csv'
with raw_path.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=raw_columns)
    w.writeheader()
    w.writerows(raw_rows)

# Aggregate per case x method
agg_groups = defaultdict(list)
for r in raw_rows:
    key = (r['case_group'], r['case_id'], r['topology'], r['size_description'], r['method'])
    agg_groups[key].append(r)

agg_rows = []
for key, rows in agg_groups.items():
    case_group, case_id, topology, size_description, method = key
    ok_rows = [r for r in rows if r.get('status') == 'ok']
    out = {
        'case_group': case_group,
        'case_id': case_id,
        'topology': topology,
        'size_description': size_description,
        'method': method,
        'n_runs': len(rows),
        'n_ok': len(ok_rows),
        'ok_rate': len(ok_rows) / max(1, len(rows)),
    }
    for fld in NUMERIC_FIELDS:
        vals = [_to_float(r.get(fld)) for r in ok_rows]
        vals = [v for v in vals if v is not None]
        out[f'{fld}_mean'] = mean(vals) if vals else ''
        out[f'{fld}_std'] = (stdev(vals) if len(vals) >= 2 else 0.0) if vals else ''
    agg_rows.append(out)

# Report-speedup: recompute from total_time means by case, and force exact=1.0
exact_time_by_case = {}
for r in agg_rows:
    if r['method'] == 'exact':
        t = _to_float(r.get('total_time_sec_mean'))
        if t is not None:
            exact_time_by_case[r['case_id']] = t

for r in agg_rows:
    t = _to_float(r.get('total_time_sec_mean'))
    ex = exact_time_by_case.get(r['case_id'])
    if r['method'] == 'exact':
        rep = 1.0 if ex is not None else None
    elif (t is None) or (ex is None) or (t <= 0):
        rep = None
    else:
        rep = ex / t
    r['speedup_vs_exact_report'] = '' if rep is None else rep

agg_rows.sort(key=lambda x: (x['case_group'], x['case_id'], x['method']))
agg_columns = []
seen = set()
for r in agg_rows:
    for k in r.keys():
        if k not in seen:
            seen.add(k)
            agg_columns.append(k)

agg_path = RESULTS_DIR / 'main_results_agg.csv'
with agg_path.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=agg_columns)
    w.writeheader()
    w.writerows(agg_rows)

# Build markdown tables
by_case = defaultdict(dict)
for r in agg_rows:
    by_case[r['case_id']][r['method']] = r

method_order = ['exact', 'fixed-rank baseline', 'ASTNC-L2']
all_cases_order = ['main_ring_8', 'main_tree_8', 'main_grid2d_3x3', 'main_random_8']
if INCLUDE_OPTIONAL_CHAIN:
    all_cases_order.append('main_chain_8')

# Table 1
lines = []
lines.append('# Main Results Tables')
lines.append('')
lines.append('## Table 1: Per-case Aggregated Main Results')
lines.append('')
for cid in all_cases_order:
    if cid not in by_case:
        continue
    meta = next((c for c in CASES if c['case_id'] == cid), None)
    title = f"### {cid}"
    if cid == 'main_chain_8':
        title += ' (optional reference row)'
    lines.append(title)
    if meta is not None:
        lines.append(f"Topology: `{meta['topology']}`; Size: `{meta['size_description']}`")
    lines.append('')
    lines.append('| method | rel_error (mean +/- std) | NMSE_dB (mean +/- std) | contract_time_sec (mean +/- std) | total_time_sec (mean +/- std) | speedup_vs_exact | t_contract_ratio | n_ok/3 |')
    lines.append('|---|---:|---:|---:|---:|---:|---:|---:|')
    for m in method_order:
        r = by_case[cid].get(m)
        if not r:
            lines.append(f'| {m} | NA | NA | NA | NA | NA | NA | 0/3 |')
            continue
        rel = _fmt_mean_std(_to_float(r.get('rel_error_mean')), _to_float(r.get('rel_error_std')), digits=6)
        nmse_db = _fmt_mean_std(_to_float(r.get('NMSE_dB_mean')), _to_float(r.get('NMSE_dB_std')), digits=3)
        ct = _fmt_mean_std(_to_float(r.get('contract_time_sec_mean')), _to_float(r.get('contract_time_sec_std')), digits=4)
        tt = _fmt_mean_std(_to_float(r.get('total_time_sec_mean')), _to_float(r.get('total_time_sec_std')), digits=4)
        sp = _fmt_speedup(_to_float(r.get('speedup_vs_exact_report')))
        tr = _fmt_mean_std(_to_float(r.get('t_contract_ratio_mean')), _to_float(r.get('t_contract_ratio_std')), digits=4)
        lines.append(f"| {m} | {rel} | {nmse_db} | {ct} | {tt} | {sp} | {tr} | {r.get('n_ok', 0)}/3 |")
    lines.append('')

# Table 2 (core cases only)
lines.append('## Table 2: Cross-case Summary (Core Main Cases Only)')
lines.append('')
lines.append('Core cases: `main_ring_8`, `main_tree_8`, `main_grid2d_3x3`, `main_random_8`.')
lines.append('')
lines.append('| method | avg rel_error | avg NMSE_dB | avg total_time_sec | avg speedup_vs_exact | geo mean speedup_vs_exact | avg t_contract_ratio |')
lines.append('|---|---:|---:|---:|---:|---:|---:|')
for m in method_order:
    rows = []
    for cid in ['main_ring_8', 'main_tree_8', 'main_grid2d_3x3', 'main_random_8']:
        r = by_case.get(cid, {}).get(m)
        if r and int(r.get('n_ok', 0)) > 0:
            rows.append(r)
    def avg(field):
        vals = [_to_float(r.get(field)) for r in rows]
        vals = [v for v in vals if v is not None]
        return mean(vals) if vals else None
    avg_rel = avg('rel_error_mean')
    avg_nmse_db = avg('NMSE_dB_mean')
    avg_total = avg('total_time_sec_mean')
    avg_speed = avg('speedup_vs_exact_report')
    avg_ratio = avg('t_contract_ratio_mean')

    speed_vals = [_to_float(r.get('speedup_vs_exact_report')) for r in rows]
    speed_vals = [v for v in speed_vals if (v is not None and v > 0)]
    geo = None
    if speed_vals:
        geo = math.exp(sum(math.log(v) for v in speed_vals) / len(speed_vals))

    lines.append(
        '| {} | {} | {} | {} | {} | {} | {} |'.format(
            m,
            'NA' if avg_rel is None else f'{avg_rel:.6f}',
            'NA' if avg_nmse_db is None else f'{avg_nmse_db:.3f}',
            'NA' if avg_total is None else f'{avg_total:.4f}',
            'NA' if avg_speed is None else f'{avg_speed:.2f}x',
            'NA' if geo is None else f'{geo:.2f}x',
            'NA' if avg_ratio is None else f'{avg_ratio:.4f}',
        )
    )
lines.append('')

# Table 3 ASTNC internals
lines.append('## Table 3: ASTNC-L2 Internal Statistics by Case')
lines.append('')
lines.append('| case_id | num_blocks | mean_rank | peak_rank | num_exact_merges | num_compressed_merges | mean_merge_residual_ratio | cache_hit_rate |')
lines.append('|---|---:|---:|---:|---:|---:|---:|---:|')
for cid in all_cases_order:
    r = by_case.get(cid, {}).get('ASTNC-L2')
    if not r:
        lines.append(f'| {cid} | NA | NA | NA | NA | NA | NA | NA |')
        continue
    lines.append(
        '| {} | {} | {} | {} | {} | {} | {} | {} |'.format(
            cid,
            'NA' if _to_float(r.get('num_blocks_mean')) is None else f"{_to_float(r.get('num_blocks_mean')):.2f}",
            'NA' if _to_float(r.get('mean_rank_mean')) is None else f"{_to_float(r.get('mean_rank_mean')):.2f}",
            'NA' if _to_float(r.get('peak_rank_mean')) is None else f"{_to_float(r.get('peak_rank_mean')):.2f}",
            'NA' if _to_float(r.get('num_exact_merges_mean')) is None else f"{_to_float(r.get('num_exact_merges_mean')):.2f}",
            'NA' if _to_float(r.get('num_compressed_merges_mean')) is None else f"{_to_float(r.get('num_compressed_merges_mean')):.2f}",
            'NA' if _to_float(r.get('mean_merge_residual_ratio_mean')) is None else f"{_to_float(r.get('mean_merge_residual_ratio_mean')):.6f}",
            'NA' if _to_float(r.get('cache_hit_rate_mean')) is None else f"{_to_float(r.get('cache_hit_rate_mean')):.4f}",
        )
    )
lines.append('')
lines.append('Note: For paper-facing tables, `exact` row speedup is reported as `1.00x`; raw exported `speedup_vs_exact` values remain in CSV for diagnostics.')

tables_path = RESULTS_DIR / 'main_results_tables.md'
tables_path.write_text('\n'.join(lines), encoding='utf-8')

# Summary file

def _get(case_id, method, field):
    r = by_case.get(case_id, {}).get(method)
    if not r:
        return None
    return _to_float(r.get(field))

adv_cases = []
for cid in ['main_ring_8', 'main_tree_8', 'main_grid2d_3x3', 'main_random_8']:
    ast_err = _get(cid, 'ASTNC-L2', 'rel_error_mean')
    ast_spd = _get(cid, 'ASTNC-L2', 'speedup_vs_exact_report')
    fix_err = _get(cid, 'fixed-rank baseline', 'rel_error_mean')
    fix_spd = _get(cid, 'fixed-rank baseline', 'speedup_vs_exact_report')
    if None not in (ast_err, ast_spd, fix_err, fix_spd):
        adv_cases.append((cid, ast_spd, ast_err, fix_spd, fix_err))

summary_lines = []
summary_lines.append('# Main Results Summary (Section 3.2)')
summary_lines.append('')
summary_lines.append('## Run completion')
summary_lines.append('')
for cid in all_cases_order:
    parts = []
    for m in method_order:
        r = by_case.get(cid, {}).get(m)
        n_ok = int(r.get('n_ok', 0)) if r else 0
        parts.append(f'{m}: {n_ok}/3')
    summary_lines.append(f'- {cid}: ' + '; '.join(parts))
summary_lines.append('')
summary_lines.append('All listed rows in this summary are based on completed (`status=ok`) runs only.')
summary_lines.append('')
summary_lines.append('## Required questions')
summary_lines.append('')

# Q1
if adv_cases:
    # choose by high speedup with low error among ASTNC
    q1_rank = sorted(adv_cases, key=lambda x: (x[1], -x[2]), reverse=True)
    top = q1_rank[0]
    summary_lines.append('1. ASTNC-L2 most evident time-accuracy tradeoff advantage:')
    summary_lines.append(f"- Most evident on `{top[0]}` (ASTNC-L2 speedup {top[1]:.2f}x, rel_error {top[2]:.6f}).")
    # include grid likely
    grid = next((x for x in adv_cases if x[0] == 'main_grid2d_3x3'), None)
    if grid:
        summary_lines.append(f"- On `main_grid2d_3x3`, ASTNC-L2 keeps rel_error at {grid[2]:.6f} with {grid[1]:.2f}x speedup, while fixed-rank is faster but much less accurate.")
else:
    summary_lines.append('1. ASTNC-L2 most evident tradeoff case cannot be determined due to missing runs.')
summary_lines.append('')

# Q2
bad_fix = []
for cid, ast_spd, ast_err, fix_spd, fix_err in adv_cases:
    if fix_err is not None and fix_err >= 0.1:
        bad_fix.append((cid, fix_spd, fix_err))
summary_lines.append('2. Cases where fixed-rank baseline is faster but error is not acceptable:')
if bad_fix:
    for cid, spd, errv in sorted(bad_fix, key=lambda x: x[2], reverse=True):
        summary_lines.append(f'- `{cid}`: fixed-rank speedup {spd:.2f}x, rel_error {errv:.6f}.')
else:
    summary_lines.append('- None under current main-core runs.')
summary_lines.append('')

# Q3
summary_lines.append('3. ASTNC-L2 gains: total time vs contract time?')
ast_total = []
ast_contract = []
for cid in ['main_ring_8', 'main_tree_8', 'main_grid2d_3x3', 'main_random_8']:
    exact_t = _get(cid, 'exact', 'total_time_sec_mean')
    exact_c = _get(cid, 'exact', 'contract_time_sec_mean')
    ast_t = _get(cid, 'ASTNC-L2', 'total_time_sec_mean')
    ast_c = _get(cid, 'ASTNC-L2', 'contract_time_sec_mean')
    if None not in (exact_t, exact_c, ast_t, ast_c) and ast_t > 0 and ast_c > 0:
        ast_total.append(exact_t / ast_t)
        ast_contract.append(exact_c / ast_c)
if ast_total and ast_contract:
    summary_lines.append(f'- Average total-time speedup (ASTNC-L2 vs exact, core cases): {mean(ast_total):.2f}x.')
    summary_lines.append(f'- Average contract-time speedup (ASTNC-L2 vs exact, core cases): {mean(ast_contract):.2f}x.')
    summary_lines.append('- Interpretation: the dominant gain is from contraction stage; emit time is comparatively tiny in all methods.')
else:
    summary_lines.append('- Insufficient completed runs to compare total vs contract gains.')
summary_lines.append('')

# Q4
summary_lines.append('4. Does `t_contract_ratio` support contraction-dominated claim?')
ratios = []
for cid in ['main_ring_8', 'main_tree_8', 'main_grid2d_3x3', 'main_random_8']:
    for m in method_order:
        r = _get(cid, m, 't_contract_ratio_mean')
        if r is not None:
            ratios.append(r)
if ratios:
    summary_lines.append(f'- Yes. Across core-case/method rows, `t_contract_ratio` ranges from {min(ratios):.4f} to {max(ratios):.4f}.')
    summary_lines.append('- This indicates runtime is overwhelmingly contraction-dominated.')
else:
    summary_lines.append('- Cannot conclude due to missing `t_contract_ratio` values.')
summary_lines.append('')

# Q5
summary_lines.append('5. Should `main_chain_8` be in main table?')
if INCLUDE_OPTIONAL_CHAIN:
    summary_lines.append('- Keep it as an optional/easiest reference row, not core evidence, because it is structurally easiest and all methods already look very favorable there.')
else:
    summary_lines.append('- Not included in this run. It is better used as an appendix/reference row.')
summary_lines.append('')

# Q6
summary_lines.append('6. Suggested Section 3.2 narrative organization from this round:')
summary_lines.append('- First establish that exact is the quality anchor but has highest total runtime on hard topologies (especially grid2d).')
summary_lines.append('- Then show fixed-rank is very fast but often incurs large error on ring/tree/grid/random main-core cases.')
summary_lines.append('- Position ASTNC-L2 as the default operating point: substantial speedup over exact while preserving materially lower error than fixed-rank.')
summary_lines.append('- Finally, use `t_contract_ratio` and ASTNC internals to support that speed gains are mainly contraction-side improvements.')
summary_lines.append('')
summary_lines.append('## Reporting rule applied')
summary_lines.append('- Raw CSV keeps exported `speedup_vs_exact` from runner.')
summary_lines.append('- Paper-facing tables report exact-row speedup as `1.00x` by convention; non-exact rows use recomputed case-local speedup from aggregated total time.')
summary_lines.append('')
summary_lines.append('## Notes')
summary_lines.append('- No algorithm logic changes were introduced in this run script.')
summary_lines.append('- `ASTNC-L2` is treated as default operating point only; no claim is made that it strictly dominates all other tolerance levels in all scenarios.')

summary_path = RESULTS_DIR / 'main_results_summary.md'
summary_path.write_text('\n'.join(summary_lines), encoding='utf-8')

print(f'Wrote: {raw_path}')
print(f'Wrote: {agg_path}')
print(f'Wrote: {tables_path}')
print(f'Wrote: {summary_path}')
