"""Write stylized frames to disk. The default output driver."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from utils.logging_setup import get_logger

log = get_logger(__name__)


class FileDriver:
    def __init__(self, root: Path, fmt: str = "png", quality: int = 95):
        self.root = Path(root).resolve()
        self.fmt = fmt
        self.quality = quality

    def write(self, name: str, arr: np.ndarray) -> Path:
        target = (self.root / f"{name}.{self.fmt}").resolve()
        if not str(target).startswith(str(self.root)):
            raise ValueError("path traversal blocked")
        target.parent.mkdir(parents=True, exist_ok=True)
        img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
        img.save(target, quality=self.quality)
        log.debug("file driver wrote %s", target)
        return target