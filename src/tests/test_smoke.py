from src.block import OutputBlocker
from src.data import GraphTNData
from src.methods import BOSSMaterialization, ExactMaterialization
from src.tasks import MaterializeTask


def test_ring_exact_smoke():
    data = GraphTNData(generator="ring", num_nodes=5, phys_dim=2, bond_dim=3, open_legs_per_node=1, seed=0)
    method = ExactMaterialization(optimize="greedy")
    task = MaterializeTask(log_level=1, compute_exact_reference=True, save_output_dense=False)
    block = OutputBlocker(enabled=True, block_labels=2, chunk_size=1)
    task.setup(data, method, block)
    result = task.run()
    assert "rel_error" in result.eval
    assert abs(result.eval["rel_error"]) < 1e-12


def test_ring_boss_smoke():
    data = GraphTNData(generator="ring", num_nodes=5, phys_dim=2, bond_dim=3, open_legs_per_node=1, seed=0)
    method = BOSSMaterialization(target_rank=2, max_rank=8, randomized=True, oversample=2, n_power_iter=1, selective_threshold=0, adaptive_refine=False)
    task = MaterializeTask(log_level=1, compute_exact_reference=True, save_output_dense=False)
    block = OutputBlocker(enabled=True, block_labels=2, chunk_size=1)
    task.setup(data, method, block)
    result = task.run()
    assert "NMSE_dB" in result.eval
    assert result.eval["total_time_sec"] >= 0.0


def test_custom_graph_data_smoke():
    data = GraphTNData(generator="custom_edges", num_nodes=4, phys_dim=2, bond_dim=3, custom_edges=((0,1),(1,2),(2,3),(3,0)), open_legs_per_node=1, seed=0)
    problem = data.get("fit")
    assert len(problem.network.nodes) == 4


def test_chain_graph_data_smoke():
    data = GraphTNData(generator="chain", num_nodes=6, phys_dim=2, bond_dim=3, open_legs_per_node=1, seed=0)
    problem = data.get("fit")
    graph = problem.network.interaction_graph()
    assert len(problem.network.nodes) == 6
    assert graph.number_of_edges() == 5


def test_tree_graph_data_smoke():
    data = GraphTNData(generator="tree", num_nodes=6, phys_dim=2, bond_dim=3, open_legs_per_node=1, seed=0)
    problem = data.get("fit")
    graph = problem.network.interaction_graph()
    assert len(problem.network.nodes) == 6
    assert graph.number_of_edges() == 5
