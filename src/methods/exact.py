from typing import Any, Dict, List

import numpy as np

from src.core.algorithms import materialize_exact
from src.core.blocking import OutputBlock
from src.methods.base import BaseMethod
from src.types import LogCallback, TNProblem


class ExactMaterialization(BaseMethod):
    def __init__(self, **method_cfg: Any) -> None:
        super().__init__()
        self.cfg = method_cfg
        self._dense: np.ndarray | None = None
        self._meta: Dict[str, Any] | None = None
        self._contract_time_sec: float = 0.0
        self._emit_time_sec: float = 0.0

    def fit(self, problem: TNProblem, blocks: List[OutputBlock], logcallback: LogCallback) -> None:
        self.problem = problem
        self.blocks = blocks
        result = materialize_exact(problem.network, blocks, optimize=str(self.cfg.get("optimize", "optimal")))
        self._dense = result.dense
        self._meta = result.meta
        self._contract_time_sec = float(result.contract_time_sec)
        self._emit_time_sec = float(result.emit_time_sec)
        logcallback.addlog({
            "method": "exact",
            "num_blocks": len(blocks),
            "contract_time_sec": self._contract_time_sec,
            "emit_time_sec": self._emit_time_sec,
        })

    def reconstruct(self):
        if self._dense is None:
            raise ValueError("Method must be fit before reconstruct.")
        return self._dense

    def get_num_params(self) -> int:
        if self.problem is None:
            return 0
        return int(sum(node.tensor.size for node in self.problem.network.nodes))

    def get_state_dict(self) -> Dict[str, Any]:
        return {
            "dense_hat": self._dense,
            "contract_time_sec": self._contract_time_sec,
            "emit_time_sec": self._emit_time_sec,
            "meta": self._meta or {},
        }
