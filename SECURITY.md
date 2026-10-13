# Security Policy

## Scope

ai-style-transfer-studio is a local Windows desktop tool. It reads image
and video files you point it at, runs style transfer models, and writes
stylized output. It can optionally expose a local preview server and an
outbound webhook driver.

The relevant attack surface:

- Image/video decoders (Pillow, OpenCV, ffmpeg bindings)
- Model checkpoint loading (PyTorch `.pth`, ONNX, safetensors)
- The optional local preview HTTP server (`drivers/preview_driver.py`)
- The optional webhook driver (`drivers/webhook_driver.py`)
- Plugin-style custom processors loaded from `processors/custom/`

## Supported versions

Only the latest minor release receives security fixes. As of 2026 that's
the 1.x line.

## What we consider a vulnerability

- Arbitrary code execution from a crafted image, video, or checkpoint file
- Path traversal in output drivers (writing outside the configured root)
- SSRF or credential leak in the webhook driver
- Privilege escalation via the native kernel loader

## What we don't

- Your own machine running your own models on your own files
- Output that "looks bad" because you picked the wrong style model
- The preview server being reachable on localhost — bind to 127.0.0.1

## Hardening defaults

- The preview server binds `127.0.0.1` only, never `0.0.0.0`.
- Checkpoint loading runs with `weights_only=True` where the format allows.
- The webhook driver refuses non-HTTPS URLs unless `--allow-http` is set.
- Custom processors from `processors/custom/` require `--enable-plugins`.

## Reporting

Email the maintainer listed in `pyproject.toml` with a reproducer. If
it's a decoder RCE, include the minimal file. We'll confirm within 72h
and coordinate a fix + advisory.