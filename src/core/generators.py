from typing import Dict, List, Tuple

import networkx as nx
import numpy as np

from src.core.network import TensorNetwork, TensorNode


def _ensure_connected_random(num_nodes: int, edge_prob: float, rng: np.random.Generator) -> nx.Graph:
    while True:
        g = nx.erdos_renyi_graph(num_nodes, edge_prob, seed=int(rng.integers(0, 1_000_000)))
        if nx.is_connected(g):
            return g


def make_graph(cfg, rng: np.random.Generator) -> nx.Graph:
    gen = cfg["generator"] if isinstance(cfg, dict) else cfg.generator
    if gen == "random_connected":
        return _ensure_connected_random(int(cfg["num_nodes"] if isinstance(cfg, dict) else cfg.num_nodes), float(cfg.get("edge_prob", 0.45) if isinstance(cfg, dict) else cfg.edge_prob), rng)
    if gen == "ring":
        return nx.cycle_graph(int(cfg["num_nodes"] if isinstance(cfg, dict) else cfg.num_nodes))
    if gen == "tree":
        num_nodes = int(cfg["num_nodes"] if isinstance(cfg, dict) else cfg.num_nodes)
        return nx.random_labeled_tree(num_nodes, seed=int(rng.integers(0, 1_000_000)))
    if gen == "grid2d":
        grid_shape = cfg.get("grid_shape", (2, 3)) if isinstance(cfg, dict) else cfg.grid_shape
        rows, cols = map(int, grid_shape)
        base = nx.grid_2d_graph(rows, cols)
        mapping = {node: i for i, node in enumerate(base.nodes())}
        return nx.relabel_nodes(base, mapping)
    raise ValueError(f"Unknown generator: {gen}")


def generate_tensor_network(cfg, seed: int = 0) -> TensorNetwork:
    rng = np.random.default_rng(seed)
    g = make_graph(cfg, rng)
    phys_dim = int(cfg["phys_dim"] if isinstance(cfg, dict) else cfg.phys_dim)
    bond_dim = int(cfg["bond_dim"] if isinstance(cfg, dict) else cfg.bond_dim)
    open_legs_per_node = int(cfg.get("open_legs_per_node", 1) if isinstance(cfg, dict) else cfg.open_legs_per_node)

    next_label = 0
    label_dims: Dict[int, int] = {}
    label_to_nodes: Dict[int, List[int]] = {}
    open_label_order: List[int] = []
    internal_edge_to_label: Dict[Tuple[int, int], int] = {}

    for u, v in g.edges():
        key = tuple(sorted((int(u), int(v))))
        lbl = next_label
        next_label += 1
        internal_edge_to_label[key] = lbl
        label_dims[lbl] = bond_dim
        label_to_nodes[lbl] = [int(u), int(v)]

    nodes: List[TensorNode] = []
    for nid in sorted(g.nodes()):
        labels: List[int] = []
        open_labels: List[int] = []
        internal_labels: List[int] = []
        for _ in range(open_legs_per_node):
            lbl = next_label
            next_label += 1
            labels.append(lbl)
            open_labels.append(lbl)
            open_label_order.append(lbl)
            label_dims[lbl] = phys_dim
            label_to_nodes[lbl] = [int(nid)]
        for nbr in sorted(g.neighbors(nid)):
            lbl = internal_edge_to_label[tuple(sorted((int(nid), int(nbr))))]
            labels.append(lbl)
            internal_labels.append(lbl)
        shape = tuple(label_dims[l] for l in labels)
        tensor = rng.standard_normal(shape).astype(np.float64) / np.sqrt(max(1, np.prod(shape)))
        nodes.append(TensorNode(node_id=int(nid), tensor=tensor, labels=labels, open_labels=open_labels, internal_labels=internal_labels))

    return TensorNetwork(nodes=nodes, label_dims=label_dims, open_label_order=open_label_order, label_to_nodes=label_to_nodes)
