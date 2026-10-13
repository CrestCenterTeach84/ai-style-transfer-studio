"""Base ingest handler contract."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator

from models.frame import Frame


class IngestHandler(ABC):
    """Reads input into Frames, and writes stylized Frames back out."""

    @abstractmethod
    def ingest(self, path: Path) -> Iterator[Frame]:
        ...

    @abstractmethod
    def emit(self, frame: Frame, out_dir: Path, *, style_id: str) -> Path:
        ...