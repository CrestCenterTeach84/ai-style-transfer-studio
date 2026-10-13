"""Bounded worker pool for parallel frame processing.

Uses a thread pool because the heavy lifting is in torch (which releases
the GIL) and cv2. For CPU-only tiny frames, threads are still fine.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable

from models.frame import Frame
from utils.logging_setup import get_logger

log = get_logger(__name__)


class FrameWorkerPool:
    def __init__(self, workers: int = 4, max_queue: int = 64):
        self.workers = workers
        self.max_queue = max_queue
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="frame")

    def map_frames(self, frames: Iterable[Frame], fn: Callable[[Frame], Frame]) -> list[Frame]:
        futures = [self._pool.submit(fn, f) for f in frames]
        return [fut.result() for fut in futures]

    def shutdown(self) -> None:
        self._pool.shutdown(wait=True)

    def __enter__(self) -> "FrameWorkerPool":
        return self

    def __exit__(self, *exc) -> None:
        self.shutdown()