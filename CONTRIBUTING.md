# Contributing to ai-style-transfer-studio

Thanks for wanting to push pixels through a neural blender with us. This
repo is a Windows desktop tool that runs AI style transfer generation —
ingest an image or frame, pick a style model, run it through the pipeline,
get stylized output. Contributions that make that loop faster, cleaner,
or more controllable are welcome.

## Ground rules

- Python 3.11+ is the target runtime. Type hints required on new modules.
- One concern per PR. A pipeline processor and a UI tweak are two PRs.
- Every new processor must ship with a unit test under `tests/`.
- Don't commit model checkpoints. They go in `models/checkpoints/` and are
  gitignored. Use `scripts/fetch_models.py` to pull them.
- Native code (C++/C#) lives under `native/`. Keep the Python binding thin.

## Repo layout at a glance

```
app/          entry point, bootstrap, config loading
core/         pipeline graph, job scheduler, worker pool
handlers/     ingest handlers (image, video, batch, clipboard)
processors/   per-stage transform logic (preprocess, infer, postprocess)
drivers/      output drivers (file, preview, stream, webhook)
services/     model registry, style catalog, telemetry, cache
models/       type defs and dataclasses for jobs, styles, frames
utils/        image ops, tensors, timing, logging
config/       yaml profiles and default settings
native/       optional C++/C# acceleration kernels
tests/        pytest suite
scripts/      dev + build helpers
```

## Development setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest tests/ -q
python -m app.main --profile config/default.yaml
```

## Style of code

- Prefer small composable processors over one god-function.
- Processors receive a `Frame` and return a `Frame`. No global state.
- Logging via `utils.logging_setup.get_logger(__name__)`.
- Fail loud in dev, fail soft in production (`--strict` flag).

## Commit messages

`pipeline: add temporal smoothing processor`
`drivers: fix webhook retry backoff`
`native: expose fast bilinear resize to python`

## Reporting issues

Open an issue with: style model used, input resolution, GPU/CPU, the
profile yaml, and the last 50 lines of the log. Screenshots of the
stylized output help a lot.