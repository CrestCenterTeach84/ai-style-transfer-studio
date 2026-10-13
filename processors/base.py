"""Processor base class. Every stage is a Processor[Frame] -> Frame."""
from __future__ import annotations

from abc import ABC, abstractmethod

from models.frame import Frame


class Processor(ABC):
    name: str = "processor"

    @abstractmethod
    def process(self, frame: Frame) -> Frame:
        ...

    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.name}>"