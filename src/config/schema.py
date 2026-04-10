from dataclasses import dataclass, field
from typing import Any, List, Optional

from omegaconf import DictConfig, OmegaConf


@dataclass
class TaskConfig:
    _target_: str = "src.tasks.MaterializeTask"
    name: str = "materialize"
    log_level: int = 1
    compute_exact_reference: bool = True


@dataclass
class DataConfig:
    _target_: str = "src.data.GraphTNData"
    name: str = "ring"
    generator: str = "ring"
    num_nodes: int = 6
    phys_dim: int = 3
    bond_dim: int = 4
    open_legs_per_node: int = 1
    seed: int = 0
    edge_prob: float = 0.45
    grid_shape: List[int] = field(default_factory=lambda: [2, 3])
    edge_file: Optional[str] = None
    custom_edges: List[List[int]] = field(default_factory=lambda: [[0, 1], [1, 2], [2, 3], [3, 0]])


@dataclass
class MethodConfig:
    _target_: str = "src.methods.ASTNCMaterialization"
    name: str = "astnc"
    optimize: str = "greedy"
    seed: int = 0
    rank_policy: str = "adaptive"
    leaf_tol: float = 1e-3
    merge_tol: float = 5e-3
    tol_schedule: str = "depth_open"
    tol_depth_decay: float = 1.5
    tol_open_power: float = 0.5
    target_rank: int = 2
    max_rank: int = 16
    randomized: bool = True
    oversample: int = 1
    n_power_iter: int = 0
    selective_threshold: int = 0
    compress_min_rank_product: int = 4
    compress_max_exact_size: int = 256
    compress_min_saving_ratio: float = 0.1
    implicit_merge_sketch: bool = True
    implicit_min_full_rank: int = 192
    adaptive_refine: bool = False
    refine_tol: float = 1e-3
    max_refine_steps: int = 0
    rank_growth_factor: int = 2
    cache_enabled: bool = True


@dataclass
class BlockConfig:
    _target_: str = "src.block.OutputBlocker"
    name: str = "default"
    enabled: bool = True
    block_labels: int = 2
    chunk_size: int = 1


@dataclass
class ExperimentConfig:
    name: str = "smoke"
    group: str = "dev"
    protocol: str = "single_run"


@dataclass
class RootConfig:
    seed: int = 0
    task: TaskConfig = field(default_factory=TaskConfig)
    data: DataConfig = field(default_factory=DataConfig)
    method: MethodConfig = field(default_factory=MethodConfig)
    block: BlockConfig = field(default_factory=BlockConfig)
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)
    hydra: Any = field(default_factory=dict)


def validate_config(cfg: DictConfig) -> DictConfig:
    schema = OmegaConf.structured(RootConfig)
    merged = OmegaConf.merge(schema, cfg)
    OmegaConf.resolve(merged)
    return merged
