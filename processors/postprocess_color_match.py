"""Match the stylized output's luminance stats back to the source frame."""
from __future__ import annotations

import numpy as np

from core.pipeline import register_processor
from models.frame import Frame
from processors.base import Processor


@register_processor("postprocess_color_match")
class ColorMatch(Processor):
    name = "postprocess_color_match"

    def __init__(self, blend: float = 0.5):
        self.blend = float(np.clip(blend, 0.0, 1.0))

    def process(self, frame: Frame) -> Frame:
        src_mean, src_std = frame.meta.get("src_stats", (None, None))
        if src_mean is None:
            return frame
        out = frame.data
        out_mean = out.mean(axis=(0, 1), keepdims=True)
        out_std = out.std(axis=(0, 1), keepdims=True) + 1e-6
        matched = (out - out_mean) / out_std * src_std + src_mean
        blended = (1.0 - self.blend) * out + self.blend * matched
        return frame.replace(data=np.clip(blended, 0.0, 1.0).astype(np.float32))