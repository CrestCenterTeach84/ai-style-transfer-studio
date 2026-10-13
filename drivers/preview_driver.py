"""Local preview server. Binds 127.0.0.1 only. Serves latest stylized frame."""
from __future__ import annotations

import io
import threading
from pathlib import Path

import numpy as np
import uvicorn
from fastapi import FastAPI
from fastapi.responses import Response
from PIL import Image

from utils.logging_setup import get_logger

log = get_logger(__name__)

app = FastAPI(title="ai-style-transfer-studio preview")
_latest: bytes | None = None
_lock = threading.Lock()


def push_frame(arr: np.ndarray) -> None:
    global _latest
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    with _lock:
        _latest = buf.getvalue()


@app.get("/frame.png")
def current_frame() -> Response:
    with _lock:
        if _latest is None:
            return Response(status_code=204)
        return Response(content=_latest, media_type="image/png")


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "has_frame": _latest is not None}


def main(host: str = "127.0.0.1", port: int = 8765) -> None:
    log.info("preview on http://%s:%d", host, port)
    uvicorn.run(app, host=host, port=port, log_level="warning")