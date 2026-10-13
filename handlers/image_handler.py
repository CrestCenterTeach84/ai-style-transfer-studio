"""Static image ingest + emit handler."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

import numpy as np
from PIL import Image

from handlers.base_handler import IngestHandler
from models.frame import Frame
from utils.image_ops import to_float01
from utils.logging_setup import get_logger

log = get_logger(__name__)


class ImageIngestHandler(IngestHandler):
    def ingest(self, path: Path) -> Iterator[Frame]:
        img = Image.open(path).convert("RGB")
        arr = np.asarray(img, dtype=np.uint8)
        log.debug("ingested image %s %s", path.name, arr.shape)
        yield Frame(index=0, data=to_float01(arr), meta={"src": str(path)})

    def emit(self, frame: Frame, out_dir: Path, *, style_id: str) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(frame.meta.get("src", "out")).stem
        out_path = out_dir / f"{stem}_{style_id}.png"
        arr = (np.clip(frame.data, 0.0, 1.0) * 255.0).astype(np.uint8)
        Image.fromarray(arr).save(out_path)
        log.info("wrote %s", out_path)
        return out_path