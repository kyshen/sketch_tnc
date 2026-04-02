from typing import Any, Dict
import math

import numpy as np


def _sq_abs(x: np.ndarray) -> np.ndarray:
    return np.abs(x) ** 2


def val_rel_error(reference: np.ndarray, reconstructed: np.ndarray) -> float:
    return float(np.linalg.norm(reference - reconstructed) / (np.linalg.norm(reference) + 1e-12))


def val_NMSE(reference: np.ndarray, reconstructed: np.ndarray) -> float:
    mse = float(np.mean(_sq_abs(reference - reconstructed)))
    denom = float(np.mean(_sq_abs(reference)))
    if denom <= 1e-12:
        return float("inf")
    return float(mse / denom)


def val_NMSE_dB(reference: np.ndarray, reconstructed: np.ndarray) -> float:
    nmse = val_NMSE(reference, reconstructed)
    if nmse == 0:
        return float("-inf")
    return float(10.0 * np.log10(nmse))


def val_RMSE(reference: np.ndarray, reconstructed: np.ndarray) -> float:
    return float(np.sqrt(np.mean(_sq_abs(reference - reconstructed))))


def val_t_contract_ratio(contract_time_sec: float, emit_time_sec: float) -> float:
    total = float(contract_time_sec + emit_time_sec)
    return float(contract_time_sec / (total + 1e-12))


def REL(reference: np.ndarray, reconstructed: np.ndarray) -> Dict[str, Any]:
    return {"rel_error": val_rel_error(reference, reconstructed)}


def RMSE(reference: np.ndarray, reconstructed: np.ndarray) -> Dict[str, Any]:
    return {"RMSE": val_RMSE(reference, reconstructed)}


def NMSE(reference: np.ndarray, reconstructed: np.ndarray) -> Dict[str, Any]:
    return {"NMSE": val_NMSE(reference, reconstructed)}


def NMSE_dB(reference: np.ndarray, reconstructed: np.ndarray) -> Dict[str, Any]:
    return {"NMSE_dB": val_NMSE_dB(reference, reconstructed)}


def TIMES(contract_time_sec: float, emit_time_sec: float, exact_total_time_sec: float | None) -> Dict[str, Any]:
    total = float(contract_time_sec + emit_time_sec)
    out = {
        "contract_time_sec": float(contract_time_sec),
        "emit_time_sec": float(emit_time_sec),
        "total_time_sec": total,
        "t_contract_ratio": val_t_contract_ratio(contract_time_sec, emit_time_sec),
    }
    if exact_total_time_sec is not None:
        out["exact_total_time_sec"] = float(exact_total_time_sec)
        out["speedup_vs_exact"] = float(exact_total_time_sec / (total + 1e-12))
    return out
