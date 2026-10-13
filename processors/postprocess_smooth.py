"""Temporal smoothing for video: blend current frame with previous output."""
from __future__ import annotations

import numpy as np

from core.pipeline import register_processor
from models.frame import Frame
from processors.base import Processor


@register_processor("postprocess_smooth")
class TemporalSmooth(Processor):
    name = "postprocess_smooth"

    def __init__(self, strength: float = 0.25):
        self.strength = float(np.clip(strength, 0.0, 1.0))
        self._prev: np.ndarray | None = None

    def process(self, frame: Frame) -> Frame:
        if self._prev is None or self._prev.shape != frame.data.shape:
            self._prev = frame.data
            return frame
        blended = (1.0 - self.strength) * frame.data + self.strength * self._prev
        self._prev = blended
        return frame.replace(data=blended.astype(np.float32))