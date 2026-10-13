"""Resize input frames to the model's expected working resolution."""
from __future__ import annotations

import cv2

from core.pipeline import register_processor
from models.frame import Frame
from processors.base import Processor


@register_processor("preprocess_resize")
class ResizeProcessor(Processor):
    name = "preprocess_resize"

    def __init__(self, long_edge: int = 1024, interp: str = "cubic"):
        self.long_edge = long_edge
        self._interp = {"cubic": cv2.INTER_CUBIC, "linear": cv2.INTER_LINEAR}[interp]

    def process(self, frame: Frame) -> Frame:
        h, w = frame.data.shape[:2]
        scale = self.long_edge / max(h, w)
        if scale == 1.0:
            return frame
        nw, nh = int(round(w * scale)), int(round(h * scale))
        resized = cv2.resize(frame.data, (nw, nh), interpolation=self._interp)
        frame.meta["orig_size"] = (w, h)
        return frame.replace(data=resized)