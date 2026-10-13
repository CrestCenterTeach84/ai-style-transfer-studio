"""Normalize frames to the mean/std the style model was trained with."""
from __future__ import annotations

import numpy as np

from core.pipeline import register_processor
from models.frame import Frame
from processors.base import Processor

_IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


@register_processor("preprocess_normalize")
class NormalizeProcessor(Processor):
    name = "preprocess_normalize"

    def __init__(self, mean: str = "imagenet", std: str = "imagenet"):
        self.mean = _IMAGENET_MEAN
        self.std = _IMAGENET_STD

    def process(self, frame: Frame) -> Frame:
        normed = (frame.data - self.mean) / self.std
        return frame.replace(data=normed.astype(np.float32))