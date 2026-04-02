from dataclasses import dataclass

import numpy as np


@dataclass
class LowRankFactors:
    left: np.ndarray
    right: np.ndarray


def _resolve_rng(rng: np.random.Generator | None) -> np.random.Generator:
    return rng if rng is not None else np.random.default_rng()


def orth(x: np.ndarray) -> np.ndarray:
    if x.size == 0:
        return x
    q, _ = np.linalg.qr(x, mode="reduced")
    return q


def compress_matrix(
    M: np.ndarray,
    target_rank: int,
    randomized: bool = True,
    oversample: int = 4,
    n_power_iter: int = 1,
    rng: np.random.Generator | None = None,
) -> LowRankFactors:
    m, n = M.shape
    if target_rank <= 0 or target_rank >= min(m, n):
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        r = min(m, n)
        return LowRankFactors(left=U[:, :r] * s[:r], right=Vt[:r, :].T)
    if not randomized:
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        r = min(target_rank, len(s))
        return LowRankFactors(left=U[:, :r] * s[:r], right=Vt[:r, :].T)
    rng = _resolve_rng(rng)
    l = min(n, max(target_rank + oversample, target_rank + 1))
    Omega = rng.standard_normal((n, l))
    Y = M @ Omega
    for _ in range(max(0, int(n_power_iter))):
        Y = M @ (M.T @ Y)
    Q = orth(Y)
    B = Q.T @ M
    Uh, s, Vt = np.linalg.svd(B, full_matrices=False)
    r = min(target_rank, len(s))
    U = Q @ Uh[:, :r]
    return LowRankFactors(left=U * s[:r], right=Vt[:r, :].T)


def compress_from_factors(
    A: np.ndarray,
    B: np.ndarray,
    target_rank: int,
    randomized: bool = True,
    oversample: int = 4,
    n_power_iter: int = 1,
    rng: np.random.Generator | None = None,
) -> LowRankFactors:
    m, ra = A.shape
    n, rb = B.shape
    assert ra == rb
    r0 = ra
    if target_rank <= 0 or target_rank >= r0:
        return LowRankFactors(left=A, right=B)
    if not randomized:
        Qa, Ra = np.linalg.qr(A, mode="reduced")
        Qb, Rb = np.linalg.qr(B, mode="reduced")
        core = Ra @ Rb.T
        U, s, Vt = np.linalg.svd(core, full_matrices=False)
        r = min(target_rank, len(s))
        left = Qa @ U[:, :r] * s[:r]
        right = Qb @ Vt[:r, :].T
        return LowRankFactors(left=left, right=right)
    rng = _resolve_rng(rng)
    l = max(target_rank + oversample, target_rank + 1)
    Omega = rng.standard_normal((n, l))
    Y = A @ (B.T @ Omega)
    for _ in range(max(0, int(n_power_iter))):
        Y = A @ (B.T @ (B @ (A.T @ Y)))
    Q = orth(Y)
    small = (Q.T @ A) @ B.T
    Uh, s, Vt = np.linalg.svd(small, full_matrices=False)
    r = min(target_rank, len(s))
    U = Q @ Uh[:, :r]
    return LowRankFactors(left=U * s[:r], right=Vt[:r, :].T)


def compress_from_implicit_factors(
    *,
    num_rows: int,
    num_cols: int,
    latent_rank: int,
    apply_A,
    apply_AT,
    apply_B,
    apply_BT,
    target_rank: int,
    randomized: bool = True,
    oversample: int = 4,
    n_power_iter: int = 1,
    rng: np.random.Generator | None = None,
) -> LowRankFactors:
    if target_rank <= 0 or target_rank >= latent_rank or target_rank >= min(num_rows, num_cols):
        raise ValueError("Implicit compression expects a strictly reducing target rank.")
    if not randomized:
        raise ValueError("Implicit compression path currently requires randomized=True.")
    rng = _resolve_rng(rng)
    sketch_cols = max(int(target_rank) + int(oversample), int(target_rank) + 1)
    Omega = rng.standard_normal((int(num_cols), sketch_cols))
    Y = apply_A(apply_BT(Omega))
    for _ in range(max(0, int(n_power_iter))):
        Y = apply_A(apply_BT(apply_B(apply_AT(Y))))
    Q = orth(Y)
    small = apply_B(apply_AT(Q)).T
    Uh, s, Vt = np.linalg.svd(small, full_matrices=False)
    r = min(int(target_rank), len(s))
    U = Q @ Uh[:, :r]
    return LowRankFactors(left=U * s[:r], right=Vt[:r, :].T)
