"""POST stylized frames to a configured webhook. HTTPS enforced by default."""
from __future__ import annotations

import base64
import io
import time
from urllib.parse import urlparse

import httpx
import numpy as np
from PIL import Image

from utils.logging_setup import get_logger

log = get_logger(__name__)


class WebhookDriver:
    def __init__(self, url: str, *, allow_http: bool = False, timeout: float = 10.0, retries: int = 3):
        parsed = urlparse(url)
        if parsed.scheme != "https" and not allow_http:
            raise ValueError("webhook must be https unless --allow-http is set")
        self.url = url
        self.timeout = timeout
        self.retries = retries

    def write(self, name: str, arr: np.ndarray) -> None:
        img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        payload = {"name": name, "png_b64": base64.b64encode(buf.getvalue()).decode()}
        for attempt in range(self.retries):
            try:
                r = httpx.post(self.url, json=payload, timeout=self.timeout)
                r.raise_for_status()
                return
            except Exception as exc:
                backoff = 0.5 * (2 ** attempt)
                log.warning("webhook attempt %d failed: %s (retry in %.1fs)", attempt + 1, exc, backoff)
                time.sleep(backoff)
        raise RuntimeError(f"webhook failed after {self.retries} attempts")