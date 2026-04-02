from dataclasses import dataclass, field
from typing import Any, List, Optional

from omegaconf import DictConfig, OmegaConf


@dataclass
class TaskConfig:
    _target_: str = "src.tasks.MaterializeTask"
    name: str = "materialize"
    log_level: int = 1
    compute_exact_reference: bool = True
    save_output_dense: bool = True


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
    _target_: str = "src.methods.BOSSMaterialization"
    name: str = "boss"
    optimize: str = "greedy"
    seed: int = 0
    target_rank: int = 2
    max_rank: int = 16
    randomized: bool = True
    oversample: int = 4
    n_power_iter: int = 1
    selective_threshold: int = 0
    compress_min_rank_product: int = 4
    compress_max_exact_size: int = 256
    compress_min_saving_ratio: float = 0.1
    implicit_merge_sketch: bool = True
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
    tags: List[str] = field(default_factory=list)
    save_resolved_config: bool = True
    save_manifest: bool = True
    write_metrics_json: bool = True


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
