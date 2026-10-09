"""Mandatory junk-content gate. Import `enforce_publish_payload` before any WP publish."""
from .gate import (  # noqa: F401
    JunkContentError,
    GateResult,
    check_post,
    enforce_publish_payload,
    normalize_slug,
    strip_geo_hallucinations,
)
