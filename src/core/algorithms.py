import copy
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from src.core.blocking import OutputBlock
from src.core.network import TensorNetwork
from src.core.partition import PartitionNode, build_partition_tree
from src.core.state import SeparatorState, compressed_state_from_tensor, exact_state_from_tensor, merge_states


@dataclass
class MaterializationResult:
    dense: np.ndarray
    contract_time_sec: float
    emit_time_sec: float
    meta: Dict[str, float]


@dataclass
class BossResult:
    dense: np.ndarray
    contract_time_sec: float
    emit_time_sec: float
    meta: Dict[str, float]


def materialize_exact(tn: TensorNetwork, blocks: List[OutputBlock], optimize: str = "optimal") -> MaterializationResult:
    import time

    dense = np.zeros(tn.output_shape, dtype=np.float64)
    t_contract = 0.0
    t_emit = 0.0
    block_labels = list(blocks[0].slice_map.keys()) if blocks else []
    suffix_labels = tn.open_label_order[len(block_labels):]
    for block in blocks:
        t0 = time.perf_counter()
        block_tensor = tn.contract_full(slice_map=block.slice_map, optimize=optimize)
        t_contract += time.perf_counter() - t0
        if block_labels:
            row_slices = tuple(slice(min(v), max(v) + 1) for _, v in sorted(block.slice_map.items(), key=lambda kv: tn.open_label_order.index(kv[0])))
            target = row_slices + tuple(slice(None) for _ in suffix_labels)
        else:
            target = tuple(slice(None) for _ in tn.open_label_order)
        t1 = time.perf_counter()
        dense[target] = block_tensor
        t_emit += time.perf_counter() - t1
    return MaterializationResult(dense=dense, contract_time_sec=t_contract, emit_time_sec=t_emit, meta={"num_blocks": len(blocks)})


def _leaf_state(tn: TensorNetwork, part: PartitionNode, slice_map, cfg, rng: np.random.Generator | None = None) -> SeparatorState:
    nid = next(iter(part.node_ids))
    output_labels = list(part.open_labels) + list(part.boundary_labels)
    T = tn.contract_subnetwork([nid], output_labels, slice_map=slice_map, optimize=getattr(cfg, "optimize", "greedy"))
    open_dims = [len(slice_map[l]) if l in slice_map else tn.label_dims[l] for l in part.open_labels]
    boundary_dims = [tn.label_dims[l] for l in part.boundary_labels]
    if getattr(cfg, "target_rank", 0) <= 0:
        return exact_state_from_tensor(T, part.open_labels, open_dims, part.boundary_labels, boundary_dims)
    target_rank = min(int(getattr(cfg, "target_rank", 1)), max(1, int(np.prod(open_dims)) if open_dims else 1), max(1, int(np.prod(boundary_dims)) if boundary_dims else 1))
    return compressed_state_from_tensor(
        T,
        part.open_labels,
        open_dims,
        part.boundary_labels,
        boundary_dims,
        target_rank=target_rank,
        randomized=bool(getattr(cfg, "randomized", True)),
        oversample=int(getattr(cfg, "oversample", 4)),
        n_power_iter=int(getattr(cfg, "n_power_iter", 1)),
        rng=rng,
    )


def _build_state(tn: TensorNetwork, part: PartitionNode, slice_map, cfg, rng: np.random.Generator | None = None) -> SeparatorState:
    if part.is_leaf:
        return _leaf_state(tn, part, slice_map, cfg, rng=rng)
    left, right = part.children
    s_left = _build_state(tn, left, slice_map, cfg, rng=rng)
    s_right = _build_state(tn, right, slice_map, cfg, rng=rng)
    rank = min(int(getattr(cfg, "target_rank", 1)), int(getattr(cfg, "max_rank", getattr(cfg, "target_rank", 1))))
    return merge_states(
        s_left,
        s_right,
        cut_labels=part.cut_labels,
        parent_boundary_labels=part.boundary_labels,
        label_dims=tn.label_dims,
        target_rank=rank,
        randomized=bool(getattr(cfg, "randomized", True)),
        oversample=int(getattr(cfg, "oversample", 4)),
        n_power_iter=int(getattr(cfg, "n_power_iter", 1)),
        selective_threshold=int(getattr(cfg, "selective_threshold", 0)),
        rng=rng,
    )


def _state_to_dense(state: SeparatorState) -> np.ndarray:
    if len(state.boundary_labels) != 0:
        raise ValueError("Root state must have empty boundary")
    if state.A.ndim == 1:
        return np.array(np.dot(state.A, state.B), dtype=np.float64)
    return np.tensordot(state.A, state.B, axes=([-1], [0]))


def _maybe_refine_block(
    tn: TensorNetwork,
    block: OutputBlock,
    approx_block: np.ndarray,
    cfg,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, int]:
    if not bool(getattr(cfg, "adaptive_refine", False)):
        return approx_block, int(getattr(cfg, "target_rank", 1))
    target_rank = int(getattr(cfg, "target_rank", 1))
    tol = float(getattr(cfg, "refine_tol", 1e-3))
    max_steps = int(getattr(cfg, "max_refine_steps", 0))
    max_rank = int(getattr(cfg, "max_rank", target_rank))
    growth = int(getattr(cfg, "rank_growth_factor", 2))
    refine_steps = 0
    current = approx_block
    while refine_steps < max_steps:
        ref = tn.contract_full(slice_map=block.slice_map, optimize="greedy")
        err = float(np.linalg.norm(ref - current) / (np.linalg.norm(ref) + 1e-12))
        if err <= tol or target_rank >= max_rank:
            return current, target_rank
        target_rank = min(max_rank, max(target_rank + 1, target_rank * growth))
        refine_steps += 1
        local_cfg = copy.deepcopy(cfg)
        setattr(local_cfg, "target_rank", target_rank)
        part = build_partition_tree(tn)
        state = _build_state(tn, part, block.slice_map, local_cfg, rng=rng)
        current = _state_to_dense(state)
    return current, target_rank


def materialize_boss(tn: TensorNetwork, blocks: List[OutputBlock], cfg) -> BossResult:
    import time

    part = build_partition_tree(tn)
    run_rng = np.random.default_rng(int(getattr(cfg, "seed", 0)))
    dense = np.zeros(tn.output_shape, dtype=np.float64)
    t_contract = 0.0
    t_emit = 0.0
    refined_blocks = 0
    used_ranks: List[int] = []
    block_labels = list(blocks[0].slice_map.keys()) if blocks else []
    suffix_labels = tn.open_label_order[len(block_labels):]

    for block in blocks:
        block_rng = np.random.default_rng(int(run_rng.integers(0, 2**32 - 1)))
        t0 = time.perf_counter()
        state = _build_state(tn, part, block.slice_map, cfg, rng=block_rng)
        perm = [state.open_labels.index(lbl) for lbl in tn.open_label_order]
        block_tensor = _state_to_dense(state)
        if list(range(len(perm))) != perm:
            block_tensor = np.transpose(block_tensor, perm)
        if bool(getattr(cfg, "adaptive_refine", False)):
            old_rank = int(getattr(cfg, "target_rank", 1))
            block_tensor, used_rank = _maybe_refine_block(tn, block, block_tensor, cfg, rng=block_rng)
            if used_rank != old_rank:
                refined_blocks += 1
            used_ranks.append(int(used_rank))
        else:
            used_ranks.append(int(getattr(cfg, "target_rank", 1)))
        t_contract += time.perf_counter() - t0
        if block_labels:
            row_slices = tuple(slice(min(v), max(v) + 1) for _, v in sorted(block.slice_map.items(), key=lambda kv: tn.open_label_order.index(kv[0])))
            target = row_slices + tuple(slice(None) for _ in suffix_labels)
        else:
            target = tuple(slice(None) for _ in tn.open_label_order)
        t1 = time.perf_counter()
        dense[target] = block_tensor
        t_emit += time.perf_counter() - t1

    return BossResult(dense=dense, contract_time_sec=t_contract, emit_time_sec=t_emit, meta={
        "num_blocks": len(blocks),
        "refined_blocks": refined_blocks,
        "mean_rank": float(np.mean(used_ranks)) if used_ranks else float(getattr(cfg, "target_rank", 1)),
        "max_rank": max(used_ranks) if used_ranks else int(getattr(cfg, "target_rank", 1)),
    })
