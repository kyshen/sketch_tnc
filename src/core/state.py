from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np
import opt_einsum as oe

from src.core.linalg import compress_from_factors, compress_matrix


@dataclass
class SeparatorState:
    open_labels: List[int]
    open_dims: List[int]
    boundary_labels: List[int]
    boundary_dims: List[int]
    A: np.ndarray
    B: np.ndarray

    @property
    def rank(self) -> int:
        return int(self.A.shape[-1])

    def to_matrix(self) -> Tuple[np.ndarray, List[int], List[int]]:
        open_flat = int(np.prod(self.open_dims)) if self.open_dims else 1
        boundary_flat = int(np.prod(self.boundary_dims)) if self.boundary_dims else 1
        A = self.A.reshape(open_flat, self.rank)
        B = self.B.reshape(boundary_flat, self.rank)
        M = A @ B.T
        return M, self.open_labels, self.boundary_labels


def exact_state_from_tensor(T: np.ndarray, open_labels: Sequence[int], open_dims: Sequence[int], boundary_labels: Sequence[int], boundary_dims: Sequence[int]) -> SeparatorState:
    open_flat = int(np.prod(open_dims)) if open_dims else 1
    boundary_flat = int(np.prod(boundary_dims)) if boundary_dims else 1
    M = T.reshape(open_flat, boundary_flat)
    factors = compress_matrix(M, target_rank=min(open_flat, boundary_flat), randomized=False)
    A = factors.left.reshape(*open_dims, factors.left.shape[-1]) if open_dims else factors.left.reshape(factors.left.shape[-1])
    if boundary_dims:
        B = factors.right.reshape(*boundary_dims, factors.right.shape[-1])
    else:
        B = factors.right.reshape(factors.right.shape[-1])
    return SeparatorState(list(open_labels), list(open_dims), list(boundary_labels), list(boundary_dims), A, B)


def compressed_state_from_tensor(
    T: np.ndarray,
    open_labels: Sequence[int],
    open_dims: Sequence[int],
    boundary_labels: Sequence[int],
    boundary_dims: Sequence[int],
    target_rank: int,
    randomized: bool = True,
    oversample: int = 4,
    n_power_iter: int = 1,
    rng: np.random.Generator | None = None,
) -> SeparatorState:
    open_flat = int(np.prod(open_dims)) if open_dims else 1
    boundary_flat = int(np.prod(boundary_dims)) if boundary_dims else 1
    M = T.reshape(open_flat, boundary_flat)
    factors = compress_matrix(
        M,
        target_rank=target_rank,
        randomized=randomized,
        oversample=oversample,
        n_power_iter=n_power_iter,
        rng=rng,
    )
    r = factors.left.shape[-1]
    A = factors.left.reshape(*open_dims, r) if open_dims else factors.left.reshape(r)
    if boundary_dims:
        B = factors.right.reshape(*boundary_dims, r)
    else:
        B = factors.right.reshape(r)
    return SeparatorState(list(open_labels), list(open_dims), list(boundary_labels), list(boundary_dims), A, B)


def merge_states(
    left: SeparatorState,
    right: SeparatorState,
    cut_labels: Sequence[int],
    parent_boundary_labels: Sequence[int],
    label_dims: Dict[int, int],
    target_rank: int,
    randomized: bool = True,
    oversample: int = 4,
    n_power_iter: int = 1,
    selective_threshold: int = 0,
    rng: np.random.Generator | None = None,
) -> SeparatorState:
    open_labels = list(left.open_labels) + list(right.open_labels)
    open_dims = list(left.open_dims) + list(right.open_dims)
    parent_boundary_labels = list(parent_boundary_labels)
    parent_boundary_dims = [label_dims[l] for l in parent_boundary_labels]

    rL = left.rank
    rR = right.rank

    A_outer = np.tensordot(left.A, right.A, axes=0)
    num_openL = len(left.open_dims)
    num_openR = len(right.open_dims)
    perm = list(range(num_openL)) + list(range(num_openL + 1, num_openL + 1 + num_openR)) + [num_openL, num_openL + 1 + num_openR]
    A_outer = np.transpose(A_outer, perm)
    A_mat = A_outer.reshape(int(np.prod(open_dims)) if open_dims else 1, rL * rR)

    B_L = left.B.reshape(rL) if len(left.boundary_labels) == 0 else left.B
    B_R = right.B.reshape(rR) if len(right.boundary_labels) == 0 else right.B
    rank_label_left = -1
    rank_label_right = -2
    left_labels = [-(100000 + i) for i in range(len(left.boundary_labels))] + [rank_label_left]
    right_labels = [-(200000 + i) for i in range(len(right.boundary_labels))] + [rank_label_right]
    for idx, lbl in enumerate(left.boundary_labels):
        if lbl in cut_labels or lbl in parent_boundary_labels:
            left_labels[idx] = lbl
    for idx, lbl in enumerate(right.boundary_labels):
        if lbl in cut_labels or lbl in parent_boundary_labels:
            right_labels[idx] = lbl
    output_labels = list(parent_boundary_labels) + [rank_label_left, rank_label_right]
    left_args = [B_L, [rank_label_left]] if len(left.boundary_labels) == 0 else [B_L, left_labels]
    right_args = [B_R, [rank_label_right]] if len(right.boundary_labels) == 0 else [B_R, right_labels]
    C = oe.contract(*left_args, *right_args, output_labels, optimize="greedy")
    B_mat = C.reshape(int(np.prod(parent_boundary_dims)) if parent_boundary_dims else 1, rL * rR)

    estimated_cost = int(A_mat.shape[0] * A_mat.shape[1] + B_mat.shape[0] * B_mat.shape[1])
    if selective_threshold and estimated_cost < int(selective_threshold):
        target_rank = A_mat.shape[1]
    factors = compress_from_factors(
        A_mat,
        B_mat,
        target_rank=target_rank,
        randomized=randomized,
        oversample=oversample,
        n_power_iter=n_power_iter,
        rng=rng,
    )
    r = factors.left.shape[-1]
    A_new = factors.left.reshape(*open_dims, r) if open_dims else factors.left.reshape(r)
    if parent_boundary_dims:
        B_new = factors.right.reshape(*parent_boundary_dims, r)
    else:
        B_new = factors.right.reshape(r)
    return SeparatorState(
        open_labels=open_labels,
        open_dims=open_dims,
        boundary_labels=parent_boundary_labels,
        boundary_dims=parent_boundary_dims,
        A=A_new,
        B=B_new,
    )
