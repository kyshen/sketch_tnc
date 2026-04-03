from typing import Any, Dict, List

import numpy as np

from src.core.algorithms import materialize_boss
from src.core.blocking import OutputBlock
from src.methods.base import BaseMethod
from src.types import LogCallback, TNProblem


class BOSSMaterialization(BaseMethod):
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
        result = materialize_boss(problem.network, blocks, self)
        self._dense = result.dense
        self._meta = result.meta
        self._contract_time_sec = float(result.contract_time_sec)
        self._emit_time_sec = float(result.emit_time_sec)
        logcallback.addlog({
            "method": "boss",
            "num_blocks": len(blocks),
            "contract_time_sec": self._contract_time_sec,
            "emit_time_sec": self._emit_time_sec,
            "rank_policy": str(self.cfg.get("rank_policy", "fixed")),
            "target_rank": int(self.cfg.get("target_rank", 0)),
            "leaf_tol": float(self.cfg.get("leaf_tol", 0.0)),
            "merge_tol": float(self.cfg.get("merge_tol", 0.0)),
            "tol_schedule": str(self.cfg.get("tol_schedule", "flat")),
            "meta": self._meta,
        })

    # attribute-style access for core algorithm compatibility
    def __getattr__(self, name: str):
        if name in self.cfg:
            return self.cfg[name]
        raise AttributeError(name)

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
