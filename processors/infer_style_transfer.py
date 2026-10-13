"""Run the style transfer model on a normalized frame.

Expects model to accept a CHW float32 tensor. Handles device placement
and returns a de-normalized HWC float32 frame in [0,1].
"""
from __future__ import annotations

import numpy as np
import torch

from core.pipeline import register_processor
from models.frame import Frame
from processors.base import Processor
from services.model_registry import ModelRegistry
from utils.logging_setup import get_logger

log = get_logger(__name__)


@register_processor("infer_style_transfer")
class StyleTransferInfer(Processor):
    name = "infer_style_transfer"

    def __init__(self, model_id: str, device: str = "cuda", denorm: bool = True):
        self.model_id = model_id
        self.device = device if (device == "cpu" or torch.cuda.is_available()) else "cpu"
        self.denorm = denorm
        self._model = None

    def _load(self):
        if self._model is None:
            self._model = ModelRegistry.load().get(self.model_id).to(self.device).eval()
            log.info("loaded style model %s on %s", self.model_id, self.device)
        return self._model

    @torch.inference_mode()
    def process(self, frame: Frame) -> Frame:
        model = self._load()
        chw = np.transpose(frame.data, (2, 0, 1))[None, ...]
        tensor = torch.from_numpy(chw).to(self.device, dtype=torch.float32)
        out = model(tensor)[0].clamp(0, 1).cpu().numpy()
        hwc = np.transpose(out, (1, 2, 0))
        return frame.replace(data=hwc.astype(np.float32))