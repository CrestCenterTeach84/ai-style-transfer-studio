"""Entry point for ai-style-transfer-studio.

Boots config, builds the pipeline graph, and dispatches a job from the
CLI or the desktop shell. This module is intentionally thin — all real
work lives in core/ and processors/.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from core.pipeline import Pipeline
from core.scheduler import JobScheduler
from services.style_catalog import StyleCatalog
from services.model_registry import ModelRegistry
from utils.logging_setup import get_logger

log = get_logger(__name__)


def build_pipeline(profile: str) -> Pipeline:
    """Construct the default style transfer pipeline for a profile."""
    catalog = StyleCatalog.load()
    registry = ModelRegistry.load()
    return Pipeline.from_profile(profile, catalog=catalog, registry=registry)


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aistyle", description="AI style transfer generator")
    parser.add_argument("input", type=Path, help="input image or video path")
    parser.add_argument("-s", "--style", default="candy", help="style id from the catalog")
    parser.add_argument("-o", "--out", type=Path, default=Path("runtime/outputs"), help="output dir")
    parser.add_argument("--profile", default="config/default.yaml", help="pipeline profile yaml")
    parser.add_argument("--strict", action="store_true", help="fail hard on any processor error")
    args = parser.parse_args(argv)

    pipeline = build_pipeline(args.profile)
    scheduler = JobScheduler(pipeline, strict=args.strict)
    job = scheduler.submit(input_path=args.input, style_id=args.style, out_dir=args.out)
    log.info("job %s finished: %s", job.id, job.status)
    return 0 if job.status == "done" else 1


if __name__ == "__main__":
    sys.exit(cli())