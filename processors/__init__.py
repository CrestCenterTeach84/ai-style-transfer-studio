"""Pipeline processors. Import side effect registers them by name."""

from processors import (  # noqa: F401
    preprocess_resize,
    preprocess_normalize,
    infer_style_transfer,
    postprocess_smooth,
    postprocess_color_match,
)