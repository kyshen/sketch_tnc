from abc import ABC, abstractmethod
from typing import Any

from src.types import TNProblem


class BaseData(ABC):
    def __init__(self, **data_cfg: Any):
        self.cfg = data_cfg
        self._problem = self._make_problem()

    @abstractmethod
    def _make_problem(self) -> TNProblem:
        raise NotImplementedError

    def get_size(self) -> int:
        shape = self._problem.network.output_shape
        out = 1
        for s in shape:
            out *= int(s)
        return int(out)

    def get(self, split: str) -> TNProblem:
        if split not in {"fit", "eval"}:
            raise ValueError(f"Unsupported split: {split}")
        return self._problem
