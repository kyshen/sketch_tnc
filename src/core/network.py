from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

import networkx as nx
import numpy as np
import opt_einsum as oe


@dataclass
class TensorNode:
    node_id: int
    tensor: np.ndarray
    labels: List[int]
    open_labels: List[int]
    internal_labels: List[int]


class TensorNetwork:
    def __init__(self, nodes: Sequence[TensorNode], label_dims: Dict[int, int], open_label_order: List[int], label_to_nodes: Dict[int, List[int]]):
        self.nodes = list(nodes)
        self.label_dims = dict(label_dims)
        self.open_label_order = list(open_label_order)
        self.label_to_nodes = {int(k): list(v) for k, v in label_to_nodes.items()}
        self.node_map = {n.node_id: n for n in self.nodes}

    @property
    def num_open(self) -> int:
        return len(self.open_label_order)

    @property
    def output_shape(self) -> Tuple[int, ...]:
        return tuple(int(self.label_dims[l]) for l in self.open_label_order)

    def interaction_graph(self) -> nx.Graph:
        g = nx.Graph()
        for node in self.nodes:
            g.add_node(node.node_id)
        for label, attached in self.label_to_nodes.items():
            if len(attached) == 2:
                u, v = attached
                w = float(self.label_dims[label])
                if g.has_edge(u, v):
                    g[u][v]["weight"] += w
                    g[u][v]["labels"].append(label)
                else:
                    g.add_edge(u, v, weight=w, labels=[label])
        return g

    def _prepared_operands(self, node_ids: Iterable[int], slice_map: Dict[int, Sequence[int]] | None = None):
        operands = []
        slice_map = slice_map or {}
        node_ids_set = set(node_ids)
        for nid in node_ids_set:
            node = self.node_map[nid]
            tensor = node.tensor
            labels = list(node.labels)
            for axis, label in enumerate(labels):
                if label in slice_map:
                    idx = np.asarray(slice_map[label], dtype=int)
                    tensor = np.take(tensor, idx, axis=axis)
            operands.append((tensor, labels))
        return operands

    def contract_subnetwork(self, node_ids: Iterable[int], output_labels: Sequence[int], slice_map: Dict[int, Sequence[int]] | None = None, optimize: str = "optimal") -> np.ndarray:
        operands = self._prepared_operands(node_ids, slice_map=slice_map)
        args = []
        for tensor, labels in operands:
            args.append(tensor)
            args.append(labels)
        args.append(list(output_labels))
        return oe.contract(*args, optimize=optimize)

    def contract_full(self, slice_map: Dict[int, Sequence[int]] | None = None, optimize: str = "optimal") -> np.ndarray:
        return self.contract_subnetwork(
            [n.node_id for n in self.nodes],
            self.open_label_order,
            slice_map=slice_map,
            optimize=optimize,
        )
