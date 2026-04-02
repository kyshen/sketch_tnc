from __future__ import annotations

from pathlib import Path
from typing import Any

import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig, open_dict

from src.config import validate_config
from src.experiments.io import build_manifest, save_experiment_run


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


def run_experiment(raw_cfg: DictConfig) -> Path:
    cfg = validate_config(raw_cfg)
    _apply_global_seed(cfg)
    out_dir = Path(HydraConfig.get().runtime.output_dir)
    dataset, method, task, block = _instantiate_experiment_parts(cfg)
    task.setup(dataset, method, block)
    result = task.run()
    manifest = build_manifest(cfg, out_dir)
    save_experiment_run(out_dir, cfg, result, manifest)
    return out_dir
