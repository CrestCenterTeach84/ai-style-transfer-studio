"""Runtime bootstrap: device selection, thread pools, cache warmup."""
from __future__ import annotations

import os
from dataclasses import dataclass

from utils.logging_setup import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class RuntimeEnv:
    device: str
    num_workers: int
    cache_dir: str
    preview_port: int


def detect_device() -> str:
    """Pick cuda if torch sees a GPU, else cpu. Never raises."""
    try:
        import torch

        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            log.info("cuda device: %s", name)
            return "cuda"
    except Exception as exc:  # pragma: no cover - torch missing is a soft fail
        log.warning("torch device probe failed: %s", exc)
    return "cpu"


def bootstrap(cache_dir: str = "runtime/cache", preview_port: int = 8765) -> RuntimeEnv:
    workers = max(2, (os.cpu_count() or 4) // 2)
    env = RuntimeEnv(
        device=detect_device(),
        num_workers=workers,
        cache_dir=cache_dir,
        preview_port=preview_port,
    )
    log.info("bootstrap: device=%s workers=%d", env.device, env.num_workers)
    return env