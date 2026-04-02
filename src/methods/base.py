from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.core.blocking import OutputBlock
from src.types import LogCallback, TNProblem


class BaseMethod(ABC):
    def __init__(self) -> None:
        self.problem: TNProblem | None = None
        self.blocks: List[OutputBlock] | None = None

    @abstractmethod
    def fit(self, problem: TNProblem, blocks: List[OutputBlock], logcallback: LogCallback) -> None:
        raise NotImplementedError

    @abstractmethod
    def reconstruct(self):
        raise NotImplementedError

    @abstractmethod
    def get_num_params(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_state_dict(self) -> Dict[str, Any]:
        raise NotImplementedError
