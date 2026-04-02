from typing import Any, List

from src.core.blocking import OutputBlock, make_blocks
from src.types import TNProblem


class OutputBlocker:
    def __init__(self, **block_cfg: Any):
        self.cfg = block_cfg

    def make(self, problem: TNProblem) -> List[OutputBlock]:
        if not bool(self.cfg.get("enabled", True)):
            return make_blocks(problem.network, block_label_count=0, chunk_size=1)
        return make_blocks(
            problem.network,
            block_label_count=int(self.cfg.get("block_labels", 2)),
            chunk_size=int(self.cfg.get("chunk_size", 1)),
        )
