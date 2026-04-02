__all__ = [
    "GraphTNData",
    "ExactMaterialization",
    "BOSSMaterialization",
    "MaterializeTask",
    "OutputBlocker",
]


def __getattr__(name: str):
    if name == "GraphTNData":
        from .data import GraphTNData

        return GraphTNData
    if name == "ExactMaterialization":
        from .methods import ExactMaterialization

        return ExactMaterialization
    if name == "BOSSMaterialization":
        from .methods import BOSSMaterialization

        return BOSSMaterialization
    if name == "MaterializeTask":
        from .tasks import MaterializeTask

        return MaterializeTask
    if name == "OutputBlocker":
        from .block import OutputBlocker

        return OutputBlocker
    raise AttributeError(name)
