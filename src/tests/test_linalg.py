import numpy as np

from src.core.linalg import compress_from_factors, compress_from_implicit_factors


def test_compress_from_implicit_factors_matches_explicit_shapes():
    rng = np.random.default_rng(0)
    A = rng.standard_normal((6, 5))
    B = rng.standard_normal((4, 5))
    target_rank = 2

    def apply_A(x: np.ndarray) -> np.ndarray:
        return A @ x

    def apply_AT(y: np.ndarray) -> np.ndarray:
        return A.T @ y

    def apply_B(x: np.ndarray) -> np.ndarray:
        return B @ x

    def apply_BT(y: np.ndarray) -> np.ndarray:
        return B.T @ y

    implicit = compress_from_implicit_factors(
        num_rows=A.shape[0],
        num_cols=B.shape[0],
        latent_rank=A.shape[1],
        apply_A=apply_A,
        apply_AT=apply_AT,
        apply_B=apply_B,
        apply_BT=apply_BT,
        target_rank=target_rank,
        randomized=True,
        oversample=3,
        n_power_iter=1,
        rng=np.random.default_rng(123),
    )
    explicit = compress_from_factors(
        A,
        B,
        target_rank=target_rank,
        randomized=True,
        oversample=3,
        n_power_iter=1,
        rng=np.random.default_rng(123),
    )

    implicit_M = implicit.left @ implicit.right.T
    explicit_M = explicit.left @ explicit.right.T

    assert implicit.left.shape == explicit.left.shape == (6, target_rank)
    assert implicit.right.shape == explicit.right.shape == (4, target_rank)
    assert np.linalg.norm(implicit_M - explicit_M) < 1e-6
