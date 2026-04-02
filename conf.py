from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from omegaconf import MISSING
from hydra.conf import HydraConf, JobConf, RunDir, SweepDir
from hydra.core.config_store import ConfigStore


# --------- group: task ----------
@dataclass
class TaskCfg:
    _target_: str = MISSING
    _name: str = MISSING
    _group: str = "task"


@dataclass
class MaterializeTaskCfg(TaskCfg):
    _target_: str = "src.tasks.MaterializeTask"
    _name: str = "materialize"
    log_level: int = 1
    compute_exact_reference: bool = True
    save_output_dense: bool = True


# --------- group: data ----------
@dataclass
class DataCfg:
    _target_: str = MISSING
    _name: str = MISSING
    _group: str = "data"
    generator: str = MISSING
    num_nodes: int = 6
    phys_dim: int = 3
    bond_dim: int = 4
    open_legs_per_node: int = 1
    seed: int = 0


@dataclass
class RandomConnectedGraphDataCfg(DataCfg):
    _target_: str = "src.data.GraphTNData"
    _name: str = "random_connected"
    generator: str = "random_connected"
    edge_prob: float = 0.45


@dataclass
class RingGraphDataCfg(DataCfg):
    _target_: str = "src.data.GraphTNData"
    _name: str = "ring"
    generator: str = "ring"


@dataclass
class TreeGraphDataCfg(DataCfg):
    _target_: str = "src.data.GraphTNData"
    _name: str = "tree"
    generator: str = "tree"


@dataclass
class Grid2DGraphDataCfg(DataCfg):
    _target_: str = "src.data.GraphTNData"
    _name: str = "grid2d"
    generator: str = "grid2d"
    grid_shape: Tuple[int, int] = (2, 3)


@dataclass
class CustomEdgesGraphDataCfg(DataCfg):
    _target_: str = "src.data.GraphTNData"
    _name: str = "custom_edges"
    generator: str = "custom_edges"
    edge_file: Optional[str] = None
    custom_edges: Tuple[Tuple[int, int], ...] = ((0, 1), (1, 2), (2, 3), (3, 0))


# --------- group: block ----------
@dataclass
class BlockCfg:
    _target_: str = MISSING
    _name: str = MISSING
    _group: str = "block"


@dataclass
class OutputBlockCfg(BlockCfg):
    _target_: str = "src.block.OutputBlocker"
    _name: str = "default"
    enabled: bool = True
    block_labels: int = 2
    chunk_size: int = 1


# --------- group: method ----------
@dataclass
class MethodCfg:
    _target_: str = MISSING
    _name: str = MISSING
    _group: str = "method"


@dataclass
class ExactMaterializationCfg(MethodCfg):
    _target_: str = "src.methods.ExactMaterialization"
    _name: str = "exact"
    optimize: str = "optimal"


@dataclass
class BossMaterializationCfg(MethodCfg):
    _target_: str = "src.methods.BOSSMaterialization"
    _name: str = "boss"
    optimize: str = "greedy"
    target_rank: int = 2
    max_rank: int = 16
    randomized: bool = True
    oversample: int = 4
    n_power_iter: int = 1
    selective_threshold: int = 0
    adaptive_refine: bool = False
    refine_tol: float = 1e-3
    max_refine_steps: int = 0
    rank_growth_factor: int = 2


# --------- top-level config ----------
@dataclass
class Config:
    defaults: List[Any] = field(default_factory=lambda: [
        {"task": "materialize"},
        {"data": "ring"},
        {"method": "boss"},
        {"block": "default"},
        "_self_",
    ])

    exp: str = MISSING
    seed: int = 0
    task: TaskCfg = MISSING
    data: DataCfg = MISSING
    method: MethodCfg = MISSING
    block: BlockCfg = MISSING

    hydra: HydraConf = field(default_factory=lambda: HydraConf(
        run=RunDir(dir="outputs/${exp}/${now:%Y-%m-%d_%H-%M-%S}"),
        sweep=SweepDir(
            dir="multirun/${exp}/${now:%Y-%m-%d_%H-%M-%S}",
            subdir="${hydra.job.num}",
        ),
        output_subdir=".hydra",
        job=JobConf(chdir=False),
    ))


def register_configs():
    cs = ConfigStore.instance()
    cs.store(name="config", node=Config)
    cfg_list = [
        MaterializeTaskCfg,
        RandomConnectedGraphDataCfg, RingGraphDataCfg, TreeGraphDataCfg, Grid2DGraphDataCfg, CustomEdgesGraphDataCfg,
        OutputBlockCfg,
        ExactMaterializationCfg, BossMaterializationCfg,
    ]
    for cfg in cfg_list:
        cs.store(group=cfg._group, name=cfg._name, node=cfg)
