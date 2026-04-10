from __future__ import annotations

from pathlib import Path
from typing import Any

import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig, open_dict

from src.config import validate_config
from src.runner.io import build_run_row, write_run_outputs


def _apply_global_seed(cfg: DictConfig) -> None:
    with open_dict(cfg):
        cfg.data.seed = int(cfg.seed)
        cfg.method.seed = int(cfg.seed)


def _instantiate_experiment_parts(cfg: DictConfig) -> tuple[Any, Any, Any, Any]:
    dataset = hydra.utils.instantiate(cfg.data)
    method = hydra.utils.instantiate(cfg.method)
    task = hydra.utils.instantiate(cfg.task)
    block = hydra.utils.instantiate(cfg.block)
    return dataset, method, task, block


def _status_from_exception(exc: BaseException) -> str:
    if isinstance(exc, TimeoutError):
        return "timeout"
    if isinstance(exc, MemoryError):
        return "oom"
    return "failed"


def run_experiment(raw_cfg: DictConfig) -> Path:
    cfg = validate_config(raw_cfg)
    _apply_global_seed(cfg)
    out_dir = Path(HydraConfig.get().runtime.output_dir)
    status = "ok"
    metrics: dict[str, Any] = {}
    error_message: str | None = None
    error: BaseException | None = None
    try:
        dataset, method, task, block = _instantiate_experiment_parts(cfg)
        task.setup(dataset, method, block)
        result = task.run()
        metrics = dict(result.eval)
    except BaseException as exc:
        error = exc
        status = _status_from_exception(exc)
        error_message = f"{type(exc).__name__}: {exc}"
    row = build_run_row(cfg, metrics=metrics, status=status, error_message=error_message)
    write_run_outputs(out_dir, cfg, rows=[row])
    if error is not None:
        raise RuntimeError(f"Experiment ended with status={status}.") from error
    return out_dir
