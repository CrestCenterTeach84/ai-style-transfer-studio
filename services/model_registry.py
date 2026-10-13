"""Registry of style transfer model checkpoints on disk."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
import yaml

from utils.logging_setup import get_logger

log = get_logger(__name__)

_MODELS_DIR = Path("models/checkpoints")
_INDEX = Path("config/models.yaml")


@dataclass(slots=True)
class ModelEntry:
    id: str
    path: Path
    arch: str
    scale: int = 1

    def load(self) -> torch.nn.Module:
        if not self.path.exists():
            raise FileNotFoundError(f"checkpoint missing: {self.path}")
        # weights_only=True blocks arbitrary pickle execution in .pth
        state = torch.load(self.path, map_location="cpu", weights_only=True)
        model = _build_arch(self.arch)
        model.load_state_dict(state, strict=False)
        return model


def _build_arch(name: str) -> torch.nn.Module:
    if name == "fast_neural":
        from services.arch_fast_neural import FastNeuralStyleNet
        return FastNeuralStyleNet()
    raise KeyError(f"unknown arch {name}")


class ModelRegistry:
    def __init__(self, entries: dict[str, ModelEntry]):
        self._entries = entries

    @classmethod
    def load(cls, index: Path = _INDEX) -> "ModelRegistry":
        if not index.exists():
            log.warning("no model index at %s, registry empty", index)
            return cls({})
        raw = yaml.safe_load(index.read_text(encoding="utf-8")) or {}
        entries = {
            m["id"]: ModelEntry(id=m["id"], path=_MODELS_DIR / m["file"], arch=m["arch"], scale=m.get("scale",