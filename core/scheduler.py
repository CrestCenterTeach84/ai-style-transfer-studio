"""Job scheduler: turns a submit() call into an ordered job record."""
from __future__ import annotations

import time
import uuid
from pathlib import Path

from core.pipeline import Pipeline
from handlers.image_handler import ImageIngestHandler
from handlers.video_handler import VideoIngestHandler
from models.job import Job, JobStatus
from utils.logging_setup import get_logger

log = get_logger(__name__)

_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
_VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


class JobScheduler:
    def __init__(self, pipeline: Pipeline, *, strict: bool = False):
        self.pipeline = pipeline
        self.strict = strict

    def submit(self, *, input_path: Path, style_id: str, out_dir: Path) -> Job:
        job = Job(id=uuid.uuid4().hex[:12], style_id=style_id, input_path=input_path, out_dir=out_dir)
        job.status = JobStatus.RUNNING
        started = time.perf_counter()
        try:
            handler = self._pick_handler(input_path)
            frames = handler.ingest(input_path)
            for frame in frames:
                stylized = self.pipeline.run(frame)
                handler.emit(stylized, out_dir, style_id=style_id)
            job.status = JobStatus.DONE
        except Exception as exc:
            log.exception("job %s failed", job.id)
            job.error = str(exc)
            job.status = JobStatus.FAILED
            if self.strict:
                raise
        finally:
            job.elapsed_ms = int((time.perf_counter() - started) * 1000)
        return job

    @staticmethod
    def _pick_handler(path: Path):
        suffix = path.suffix.lower()
        if suffix in _IMAGE_EXT:
            return ImageIngestHandler()
        if suffix in _VIDEO_EXT:
            return VideoIngestHandler()
        raise ValueError(f"unsupported input type: {suffix}")