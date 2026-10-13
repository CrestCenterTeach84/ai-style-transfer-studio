"""Pipeline graph for style transfer jobs.

A Pipeline is an ordered list of Processor stages. Each stage takes a
Frame in and returns a Frame out. The graph is built from a profile yaml
so users can reorder or swap stages without touching code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml

from models.frame import Frame
from processors.base import Processor
from utils.logging_setup import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class Pipeline:
    stages: list[Processor] = field(default_factory=list)
    name: str = "default"

    @classmethod
    def from_profile(cls, profile_path: str | Path, *, catalog, registry) -> "Pipeline":
        path = Path(profile_path)
        if not path.exists():
            raise FileNotFoundError(f"profile not found: {path}")
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        stages: list[Processor] = []
        for entry in raw.get("stages", []):
            name = entry["name"]
            proc_cls = _resolve_processor(name)
            stages.append(proc_cls(**entry.get("params", {})))
            log.debug("loaded stage %s", name)
        return cls(stages=stages, name=raw.get("name", "default"))

    def run(self, frame: Frame) -> Frame:
        """Pass a frame through every stage in order."""
        for stage in self.stages:
            frame = stage.process(frame)
        return frame


_REGISTRY: dict[str, type[Processor]] = {}


def register_processor(name: str):
    def deco(cls: type[Processor]) -> type[Processor]:
        _REGISTRY[name] = cls
        return cls
    return deco


def _resolve_processor(name: str) -> type[Processor]:
    if name not in _REGISTRY:
        raise KeyError(f"unknown processor: {name}. registered={sorted(_REGISTRY)}")
    return _REGISTRY[name]