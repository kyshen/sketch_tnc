import itertools
from dataclasses import dataclass
from typing import Dict, List

from src.core.network import TensorNetwork


@dataclass
class OutputBlock:
    block_id: int
    slice_map: Dict[int, List[int]]


def make_blocks(tn: TensorNetwork, block_label_count: int, chunk_size: int) -> List[OutputBlock]:
    labels = tn.open_label_order[: int(block_label_count)]
    if len(labels) == 0:
        return [OutputBlock(block_id=0, slice_map={})]
    per_label_chunks: List[List[List[int]]] = []
    for lbl in labels:
        dim = int(tn.label_dims[lbl])
        chunks = [list(range(i, min(i + int(chunk_size), dim))) for i in range(0, dim, int(chunk_size))]
        per_label_chunks.append(chunks)
    out: List[OutputBlock] = []
    for bid, combo in enumerate(itertools.product(*per_label_chunks)):
        slice_map = {lbl: idxs for lbl, idxs in zip(labels, combo)}
        out.append(OutputBlock(block_id=bid, slice_map=slice_map))
    return out
