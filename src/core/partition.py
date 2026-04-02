from dataclasses import dataclass
from typing import FrozenSet, List, Optional, Set

import networkx as nx

from src.core.network import TensorNetwork


@dataclass
class PartitionNode:
    node_ids: FrozenSet[int]
    children: Optional[List["PartitionNode"]]
    boundary_labels: List[int]
    open_labels: List[int]
    cut_labels: List[int]

    @property
    def is_leaf(self) -> bool:
        return not self.children

    @property
    def node_key(self) -> tuple[int, ...]:
        return tuple(sorted(self.node_ids))


def _subtree_boundary_labels(tn: TensorNetwork, node_ids: Set[int]) -> List[int]:
    out: List[int] = []
    for label, attached in tn.label_to_nodes.items():
        inside = sum(1 for n in attached if n in node_ids)
        if inside == 1 and len(attached) == 2:
            out.append(label)
    return sorted(out)


def _subtree_open_labels(tn: TensorNetwork, node_ids: Set[int]) -> List[int]:
    labs: List[int] = []
    for nid in sorted(node_ids):
        labs.extend(tn.node_map[nid].open_labels)
    order = {l: i for i, l in enumerate(tn.open_label_order)}
    return sorted(labs, key=lambda x: order[x])


def _cut_labels_between(tn: TensorNetwork, a: Set[int], b: Set[int]) -> List[int]:
    out: List[int] = []
    for label, attached in tn.label_to_nodes.items():
        if len(attached) == 2:
            x, y = attached
            if (x in a and y in b) or (x in b and y in a):
                out.append(label)
    return sorted(out)


def _recursive_build(tn: TensorNetwork, node_ids: Set[int]) -> PartitionNode:
    boundary_labels = _subtree_boundary_labels(tn, node_ids)
    open_labels = _subtree_open_labels(tn, node_ids)
    if len(node_ids) == 1:
        return PartitionNode(frozenset(node_ids), None, boundary_labels, open_labels, [])

    sub = tn.interaction_graph().subgraph(node_ids).copy()
    if sub.number_of_edges() == 0:
        items = list(node_ids)
        left_nodes, right_nodes = {items[0]}, set(items[1:])
    else:
        _, parts = nx.stoer_wagner(sub, weight="weight")
        left_nodes = set(parts[0])
        right_nodes = set(parts[1])
        if not left_nodes or not right_nodes:
            items = list(node_ids)
            left_nodes, right_nodes = {items[0]}, set(items[1:])
    cut_labels = _cut_labels_between(tn, left_nodes, right_nodes)
    left = _recursive_build(tn, left_nodes)
    right = _recursive_build(tn, right_nodes)
    return PartitionNode(frozenset(node_ids), [left, right], boundary_labels, open_labels, cut_labels)


def build_partition_tree(tn: TensorNetwork) -> PartitionNode:
    return _recursive_build(tn, set(n.node_id for n in tn.nodes))
