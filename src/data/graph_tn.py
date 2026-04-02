from typing import Any

from src.data.base import BaseData
from src.types import TNProblem
from src.core.generators import generate_tensor_network


class GraphTNData(BaseData):
    def __init__(self, **data_cfg: Any):
        super().__init__(**data_cfg)

    def _make_problem(self) -> TNProblem:
        network = generate_tensor_network(self.cfg, seed=int(self.cfg.get("seed", 0)))
        return TNProblem(network=network)
