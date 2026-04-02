from typing import Any, Dict

from src.block import OutputBlocker
from src.core.algorithms import materialize_exact
from src.data import BaseData
from src.methods.base import BaseMethod
from src.metrics import NMSE, NMSE_dB, REL, RMSE, TIMES
from src.tasks.base import BaseTask
from src.types import LogCallback, Result


class MaterializeTask(BaseTask):
    def __init__(self, **task_cfg: Any) -> None:
        super().__init__()
        self.cfg = task_cfg
        self.logcallback = LogCallback(log_level=int(self.cfg.get("log_level", 1)))
        self._exact_reference = None
        self._exact_total_time_sec = None

    def setup(self, data: BaseData, method: BaseMethod, blocker: OutputBlocker) -> None:
        self.data = data
        self.method = method
        self.blocker = blocker

    def run(self) -> Result:
        if self.method is None or self.data is None or self.blocker is None:
            raise ValueError("Task setup is incomplete.")

        problem = self.data.get(split="fit")
        blocks = self.blocker.make(problem)

        if bool(self.cfg.get("compute_exact_reference", True)):
            exact = materialize_exact(problem.network, blocks, optimize="optimal")
            self._exact_reference = exact.dense
            self._exact_total_time_sec = float(exact.contract_time_sec + exact.emit_time_sec)
            self.logcallback.addlog({
                "reference": "exact",
                "exact_contract_time_sec": float(exact.contract_time_sec),
                "exact_emit_time_sec": float(exact.emit_time_sec),
            })

        self.method.fit(problem, blocks, self.logcallback)
        state_dict = self.method.get_state_dict()
        if not bool(self.cfg.get("save_output_dense", True)) and "dense_hat" in state_dict:
            state_dict = dict(state_dict)
            state_dict.pop("dense_hat", None)
        eval_dict = self.evaluate()
        logs = self.logcallback.logs
        return Result(state_dict=state_dict, eval=eval_dict, logs=logs)

    def evaluate(self) -> Dict[str, Any]:
        if self.method is None:
            raise ValueError("Method is not set.")
        dense_hat = self.method.reconstruct()
        state = self.method.get_state_dict()
        eval_dict: Dict[str, Any] = {
            "reference_available": bool(self._exact_reference is not None),
            "num_method_params": int(self.method.get_num_params()),
        }
        if self._exact_reference is not None:
            eval_dict.update(REL(self._exact_reference, dense_hat))
            eval_dict.update(RMSE(self._exact_reference, dense_hat))
            eval_dict.update(NMSE(self._exact_reference, dense_hat))
            eval_dict.update(NMSE_dB(self._exact_reference, dense_hat))
        else:
            eval_dict["reference_metric_status"] = "skipped_without_exact_reference"
        eval_dict.update(TIMES(
            contract_time_sec=float(state.get("contract_time_sec", 0.0)),
            emit_time_sec=float(state.get("emit_time_sec", 0.0)),
            exact_total_time_sec=self._exact_total_time_sec,
        ))
        meta = state.get("meta", {})
        if isinstance(meta, dict):
            for key, value in meta.items():
                if isinstance(value, (bool, int, float, str)):
                    eval_dict[key] = value
        return eval_dict
