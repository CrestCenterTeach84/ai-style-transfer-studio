"""Video ingest + emit handler. Streams frames, no full decode in RAM."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterator

import cv2
import numpy as np

from handlers.base_handler import IngestHandler
from models.frame import Frame
from utils.image_ops import to_float01
from utils.logging_setup import get_logger

log = get_logger(__name__)


class VideoIngestHandler(IngestHandler):
    def __init__(self, max_frames: int | None = None):
        self.max_frames = max_frames

    def ingest(self, path: Path) -> Iterator[Frame]:
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            raise IOError(f"cannot open video: {path}")
        idx = 0
        try:
            while True:
                ok, bgr = cap.read()
                if not ok:
                    break
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                yield Frame(index=idx, data=to_float01(rgb), meta={"src": str(path)})
                idx += 1
                if self.max_frames and idx >= self.max_frames:
                    break
        finally:
            cap.release()
        log.info("ingested %d frames from %s", idx, path.name)

    def emit(self, frame: Frame, out_dir: Path, *, style_id: str) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(frame.meta.get("src", "out")).stem
        out_path = out_dir / f"{stem}_{style_id}_f{frame.index:06d}.png"
        arr = (np.clip(frame.data, 0.0, 1.0) * 255.0).astype(np.uint8)
        cv2.imwrite(str(out_path), cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
        return out_path

    @staticmethod
    def mux_frames(frame_dir: Path, out_video: Path, fps: int = 24) -> Path:
        """Reassemble emitted frames back into a video. Kept here for symmetry."""
        frames = sorted(frame_dir.glob("*.png"))
        if not frames:
            raise ValueError(f"no frames in {frame_dir}")
        first = cv2.imread(str(frames[0]))
        h, w = first.shape[:2]
        writer = cv2.VideoWriter(str(out_video), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        for f in frames:
            writer.write(cv2.imread(str(f)))
        writer.release()
        log.info("muxed %d frames -> %s", len(frames), out_video)
        return out_video