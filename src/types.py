from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from src.core.network import TensorNetwork

Float = np.float32
Array = np.ndarray


@dataclass
class TNProblem:
    network: TensorNetwork


class LogCallback:
    def __init__(self, log_level: int) -> None:
        self.log_level = int(log_level)
        self.logs: Optional[List[Dict[str, Any]]] = None

    def addlog(self, log: Dict[str, Any]) -> None:
        if self.logs is None:
            self.logs = []
        self.logs.append(log)

@dataclass
class Result:
    state_dict: Dict[str, Any]
    eval: Dict[str, Any]
    logs: Optional[List[Dict[str, Any]]]
