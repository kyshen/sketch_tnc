from abc import ABC, abstractmethod
from typing import Optional

from src.block import OutputBlocker
from src.data import BaseData
from src.methods.base import BaseMethod
from src.types import Result


class BaseTask(ABC):
    def __init__(self) -> None:
        self.method: Optional[BaseMethod] = None
        self.data: Optional[BaseData] = None
        self.blocker: Optional[OutputBlocker] = None

    @abstractmethod
    def run(self) -> Result:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self) -> dict:
        raise NotImplementedError
