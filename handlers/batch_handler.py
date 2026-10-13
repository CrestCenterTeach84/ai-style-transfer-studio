"""Batch folder ingest: walk a directory and yield frames tagged with src."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from handlers.image_handler import ImageIngestHandler
from models.frame import Frame
from utils.logging_setup import get_logger

log = get_logger(__name__)

_SUPPORTED = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


class BatchIngestHandler:
    def __init__(self, recursive: bool = True):
        self.recursive = recursive
        self._img = ImageIngestHandler()

    def ingest(self, path: Path) -> Iterator[Frame]:
        pattern = "**/*" if self.recursive else "*"
        files = [p for p in sorted(path.glob(pattern)) if p.suffix.lower() in _SUPPORTED]
        log.info("batch: %d images under %s", len(files), path)
        for i, f in enumerate(files):
            for frame in self._img.ingest(f):
                frame.index = i
                yield frame

    def emit(self, frame: Frame, out_dir: Path, *, style_id: str) -> Path:
        return self._img.emit(frame, out_dir, style_id=style_id)