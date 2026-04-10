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
OUT_GROUP = 'pilot_protocol'
RESULTS_DIR = ROOT / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

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
    'astnc_l1': {
        'external_method': 'ASTNC-L1',
        'overrides': {
            **COMMON_ASTNC,
            'method.rank_policy': 'adaptive',
            'method.target_rank': '2',
            'method.max_rank': '16',
            'method.leaf_tol': '0.0005',
            'method.merge_tol': '0.002',
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
    'astnc_l3': {
        'external_method': 'ASTNC-L3',
        'overrides': {
            **COMMON_ASTNC,
            'method.rank_policy': 'adaptive',
            'method.target_rank': '2',
            'method.max_rank': '16',
            'method.leaf_tol': '0.003',
            'method.merge_tol': '0.015',
        },
    },
    'ablate_no_cache': {
        'external_method': 'ASTNC-L2-no-cache',
        'overrides': {
            **COMMON_ASTNC,
            'method.rank_policy': 'adaptive',
            'method.target_rank': '2',
            'method.max_rank': '16',
            'method.leaf_tol': '0.001',
            'method.merge_tol': '0.005',
            'method.cache_enabled': 'false',
        },
    },
    'ablate_no_implicit': {
        'external_method': 'ASTNC-L2-no-implicit',
        'overrides': {
            **COMMON_ASTNC,
            'method.rank_policy': 'adaptive',
            'method.target_rank': '2',
            'method.max_rank': '16',
            'method.leaf_tol': '0.001',
            'method.merge_tol': '0.005',
            'method.implicit_merge_sketch': 'false',
        },
    },
    'ablate_no_blockwise': {
        'external_method': 'ASTNC-L2-no-blockwise',
        'overrides': {
            **COMMON_ASTNC,
            'method.rank_policy': 'adaptive',
            'method.target_rank': '2',
            'method.max_rank': '16',
            'method.leaf_tol': '0.001',
            'method.merge_tol': '0.005',
            'block.enabled': 'false',
        },
    },
}

CASES = [
    {
        'case_id': 'toy_chain_6',
        'tier': 'toy',
        'topology': 'chain',
        'size_description': 'num_nodes=6, phys_dim=2, bond_dim=3, open_legs_per_node=1',
        'overrides': {'data': 'chain', 'data.num_nodes': '6', 'data.phys_dim': '2', 'data.bond_dim': '3', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'fixed_rank', 'astnc_l2'],
        'seeds': [0, 1],
    },
    {
        'case_id': 'toy_ring_6',
        'tier': 'toy',
        'topology': 'ring',
        'size_description': 'num_nodes=6, phys_dim=2, bond_dim=3, open_legs_per_node=1',
        'overrides': {'data': 'ring', 'data.num_nodes': '6', 'data.phys_dim': '2', 'data.bond_dim': '3', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'fixed_rank', 'astnc_l2'],
        'seeds': [0, 1],
    },
    {
        'case_id': 'toy_tree_6',
        'tier': 'toy',
        'topology': 'tree',
        'size_description': 'num_nodes=6, phys_dim=2, bond_dim=3, open_legs_per_node=1',
        'overrides': {'data': 'tree', 'data.num_nodes': '6', 'data.phys_dim': '2', 'data.bond_dim': '3', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'fixed_rank', 'astnc_l2'],
        'seeds': [0, 1],
    },
    {
        'case_id': 'toy_grid2d_2x3',
        'tier': 'toy',
        'topology': 'grid2d',
        'size_description': 'grid_shape=[2,3], phys_dim=2, bond_dim=3, open_legs_per_node=1',
        'overrides': {'data': 'grid2d', 'data.grid_shape': '[2,3]', 'data.num_nodes': '6', 'data.phys_dim': '2', 'data.bond_dim': '3', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'fixed_rank', 'astnc_l2'],
        'seeds': [0, 1],
    },
    {
        'case_id': 'toy_random_6',
        'tier': 'toy',
        'topology': 'random_connected',
        'size_description': 'num_nodes=6, phys_dim=2, bond_dim=3, edge_prob=0.35, open_legs_per_node=1',
        'overrides': {'data': 'random_connected', 'data.num_nodes': '6', 'data.edge_prob': '0.35', 'data.phys_dim': '2', 'data.bond_dim': '3', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'fixed_rank', 'astnc_l2'],
        'seeds': [0, 1],
    },
    {
        'case_id': 'main_chain_8',
        'tier': 'main',
        'topology': 'chain',
        'size_description': 'num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {'data': 'chain', 'data.num_nodes': '8', 'data.phys_dim': '3', 'data.bond_dim': '4', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'fixed_rank', 'astnc_l2'],
        'seeds': [0, 1],
    },
    {
        'case_id': 'main_ring_8',
        'tier': 'main',
        'topology': 'ring',
        'size_description': 'num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {'data': 'ring', 'data.num_nodes': '8', 'data.phys_dim': '3', 'data.bond_dim': '4', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'fixed_rank', 'astnc_l1', 'astnc_l2', 'astnc_l3'],
        'seeds': [0, 1],
    },
    {
        'case_id': 'main_tree_8',
        'tier': 'main',
        'topology': 'tree',
        'size_description': 'num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {'data': 'tree', 'data.num_nodes': '8', 'data.phys_dim': '3', 'data.bond_dim': '4', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'fixed_rank', 'astnc_l2'],
        'seeds': [0, 1],
    },
    {
        'case_id': 'main_grid2d_3x3',
        'tier': 'main',
        'topology': 'grid2d',
        'size_description': 'grid_shape=[3,3], phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {'data': 'grid2d', 'data.grid_shape': '[3,3]', 'data.num_nodes': '9', 'data.phys_dim': '3', 'data.bond_dim': '4', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'fixed_rank', 'astnc_l1', 'astnc_l2', 'astnc_l3'],
        'seeds': [0, 1],
    },
    {
        'case_id': 'main_random_8',
        'tier': 'main',
        'topology': 'random_connected',
        'size_description': 'num_nodes=8, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1',
        'overrides': {'data': 'random_connected', 'data.num_nodes': '8', 'data.edge_prob': '0.35', 'data.phys_dim': '3', 'data.bond_dim': '4', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'fixed_rank', 'astnc_l1', 'astnc_l2', 'astnc_l3'],
        'seeds': [0, 1],
    },
    {
        'case_id': 'stress_ring_10',
        'tier': 'stress',
        'topology': 'ring',
        'size_description': 'num_nodes=10, phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {'data': 'ring', 'data.num_nodes': '10', 'data.phys_dim': '3', 'data.bond_dim': '4', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'astnc_l2', 'astnc_l3'],
        'seeds': [0],
    },
    {
        'case_id': 'stress_grid2d_3x4',
        'tier': 'stress',
        'topology': 'grid2d',
        'size_description': 'grid_shape=[3,4], phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {'data': 'grid2d', 'data.grid_shape': '[3,4]', 'data.num_nodes': '12', 'data.phys_dim': '3', 'data.bond_dim': '4', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['astnc_l2'],
        'seeds': [0],
    },
    {
        'case_id': 'stress_random_10',
        'tier': 'stress',
        'topology': 'random_connected',
        'size_description': 'num_nodes=10, phys_dim=3, bond_dim=4, edge_prob=0.35, open_legs_per_node=1',
        'overrides': {'data': 'random_connected', 'data.num_nodes': '10', 'data.edge_prob': '0.35', 'data.phys_dim': '3', 'data.bond_dim': '4', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['exact', 'astnc_l2'],
        'seeds': [0],
    },
    {
        'case_id': 'ablate_ring_8',
        'tier': 'ablation_probe',
        'topology': 'ring',
        'size_description': 'num_nodes=8, phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {'data': 'ring', 'data.num_nodes': '8', 'data.phys_dim': '3', 'data.bond_dim': '4', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['astnc_l2', 'ablate_no_cache', 'ablate_no_implicit', 'ablate_no_blockwise'],
        'seeds': [0],
    },
    {
        'case_id': 'ablate_grid2d_3x3',
        'tier': 'ablation_probe',
        'topology': 'grid2d',
        'size_description': 'grid_shape=[3,3], phys_dim=3, bond_dim=4, open_legs_per_node=1',
        'overrides': {'data': 'grid2d', 'data.grid_shape': '[3,3]', 'data.num_nodes': '9', 'data.phys_dim': '3', 'data.bond_dim': '4', 'data.open_legs_per_node': '1', 'block.enabled': 'true', 'block.block_labels': '2', 'block.chunk_size': '1'},
        'methods': ['astnc_l2', 'ablate_no_cache', 'ablate_no_implicit', 'ablate_no_blockwise'],
        'seeds': [0],
    },
]

NUMERIC_FIELDS = [
    'rel_error', 'RMSE', 'NMSE', 'NMSE_dB',
    'contract_time_sec', 'emit_time_sec', 'total_time_sec', 'speedup_vs_exact', 't_contract_ratio',
    'num_blocks', 'refined_blocks', 'mean_rank', 'max_rank', 'peak_rank',
    'num_exact_merges', 'num_compressed_merges', 'num_exact_leaves', 'num_compressed_leaves',
    'mean_leaf_residual_ratio', 'mean_merge_residual_ratio',
    'cache_requests', 'cache_hits', 'cache_misses', 'cache_hit_rate', 'num_cached_states',
]


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


def _to_float(x):
    if x is None:
        return None
    s = str(x).strip()
    if s == '' or s.lower() in {'none', 'nan'}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


raw_rows = []
plan_rows = []
for case in CASES:
    for method_key in case['methods']:
        for seed in case['seeds']:
            plan_rows.append((case, method_key, seed))

print(f"Planned runs: {len(plan_rows)}")

for idx, (case, method_key, seed) in enumerate(plan_rows, start=1):
    method_spec = METHODS[method_key]
    run_name = f"{case['case_id']}__{method_key}__s{seed}"
    overrides = {
        'seed': str(seed),
        'experiment.group': OUT_GROUP,
        'experiment.name': run_name,
        **case['overrides'],
        **method_spec['overrides'],
    }
    cmd = [str(PY), str(RUNPY)] + [f"{k}={v}" for k, v in overrides.items()]
    print(f"[{idx}/{len(plan_rows)}] {run_name}")

    status = 'ok'
    error_message = ''
    row = _read_run_row(run_name)
    reused = row is not None
    if not reused:
        try:
            subprocess.run(cmd, cwd=str(ROOT), check=True, timeout=180)
        except subprocess.TimeoutExpired:
            status = 'timeout'
            error_message = 'timeout>180s'
        except subprocess.CalledProcessError as exc:
            status = 'failed'
            error_message = f'nonzero_exit={exc.returncode}'
        row = _read_run_row(run_name)
    if row is None:
        row = {}

    merged = {
        'case_id': case['case_id'],
        'tier': case['tier'],
        'topology': case['topology'],
        'size_description': case['size_description'],
        'seed': seed,
        'method': method_spec['external_method'],
        'method_key': method_key,
        'planned_method_group': json.dumps(case['methods']),
        'status': row.get('status', status),
        'status_source': 'runner' if 'status' in row else 'driver',
        'driver_status': 'reused' if reused else status,
        'driver_error': error_message,
    }

    passthrough = [
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
    for k in passthrough:
        merged[k] = row.get(k)
    raw_rows.append(merged)

raw_columns = []
seen = set()
for r in raw_rows:
    for k in r.keys():
        if k not in seen:
            seen.add(k)
            raw_columns.append(k)

raw_path = RESULTS_DIR / 'pilot_raw_runs.csv'
with raw_path.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=raw_columns)
    writer.writeheader()
    writer.writerows(raw_rows)

agg_groups = defaultdict(list)
for r in raw_rows:
    key = (
        r['tier'],
        r['case_id'],
        r['topology'],
        r['size_description'],
        r['method'],
    )
    agg_groups[key].append(r)

agg_rows = []
for key, rows in agg_groups.items():
    tier, case_id, topology, size_description, method = key
    out = {
        'tier': tier,
        'case_id': case_id,
        'topology': topology,
        'size_description': size_description,
        'method': method,
        'n_runs': len(rows),
        'n_ok': sum(1 for r in rows if r.get('status') == 'ok'),
        'ok_rate': sum(1 for r in rows if r.get('status') == 'ok') / max(1, len(rows)),
    }
    for field in NUMERIC_FIELDS:
        vals = [_to_float(r.get(field)) for r in rows if r.get('status') == 'ok']
        vals = [v for v in vals if (v is not None and math.isfinite(v))]
        if vals:
            out[f'{field}_mean'] = mean(vals)
            out[f'{field}_std'] = stdev(vals) if len(vals) >= 2 else 0.0
        else:
            out[f'{field}_mean'] = ''
            out[f'{field}_std'] = ''
    agg_rows.append(out)

agg_rows.sort(key=lambda r: (r['tier'], r['case_id'], r['method']))
agg_columns = []
seen = set()
for r in agg_rows:
    for k in r.keys():
        if k not in seen:
            seen.add(k)
            agg_columns.append(k)

agg_path = RESULTS_DIR / 'pilot_agg.csv'
with agg_path.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=agg_columns)
    writer.writeheader()
    writer.writerows(agg_rows)

print(f"Wrote: {raw_path}")
print(f"Wrote: {agg_path}")
