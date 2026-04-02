__all__ = [
    "TensorNetwork",
    "TensorNode",
    "OutputBlock",
    "make_blocks",
    "PartitionNode",
    "build_partition_tree",
]


def __getattr__(name: str):
    if name in {"TensorNetwork", "TensorNode"}:
        from .network import TensorNetwork, TensorNode

        return {"TensorNetwork": TensorNetwork, "TensorNode": TensorNode}[name]
    if name in {"OutputBlock", "make_blocks"}:
        from .blocking import OutputBlock, make_blocks

        return {"OutputBlock": OutputBlock, "make_blocks": make_blocks}[name]
    if name in {"PartitionNode", "build_partition_tree"}:
        from .partition import PartitionNode, build_partition_tree

        return {"PartitionNode": PartitionNode, "build_partition_tree": build_partition_tree}[name]
    raise AttributeError(name)
