#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Web Vitals Preload, Speculation Rules, bfcache & LCP Subpart Diagnostics
(Integrated from AgriciDaniel/claude-seo: preload_check.py & lcp_subparts.py).

Provides:
  - analyse_preload_and_bfcache(html, headers=None) -> dict
  - decompose_lcp_subparts(crux_record, url="", form_factor="PHONE") -> dict
"""

from __future__ import annotations

import json
import re
from typing import Optional

_SPECULATION_BLOCK_RE = re.compile(
    r'<script\b[^>]*\btype\s*=\s*["\']speculationrules["\'][^>]*>(?P<body>.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
_PRELOAD_LINK_RE = re.compile(
    r'<link\b[^>]*\brel\s*=\s*["\']preload["\'][^>]*>', re.IGNORECASE,
)
_PRERENDER_LINK_RE = re.compile(
    r'<link\b[^>]*\brel\s*=\s*["\']prerender["\'][^>]*>', re.IGNORECASE,
)
_FETCHPRIORITY_HIGH_RE = re.compile(
    r'\bfetchpriority\s*=\s*["\']high["\']', re.IGNORECASE,
)
_LCP_IMG_HINT_RE = re.compile(
    r'<(?:img|video|source)\b[^>]*\bfetchpriority\s*=\s*["\']high["\']',
    re.IGNORECASE,
)
_UNLOAD_LISTENER_RE = re.compile(
    r'\b(?:addEventListener|on)\s*\(\s*["\']?unload["\']?', re.IGNORECASE,
)
_BEFOREUNLOAD_LISTENER_RE = re.compile(
    r'\b(?:addEventListener|on)\s*\(\s*["\']?beforeunload["\']?', re.IGNORECASE,
)


def _extract_speculation_actions(body: str) -> list[str]:
    actions: set[str] = set()
    try:
        payload = json.loads((body or "").strip())
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, dict):
        return []
    for action_kind in ("prefetch", "prerender"):
        if isinstance(payload.get(action_kind), list):
            actions.add(action_kind)
    return sorted(actions)


def analyse_preload_and_bfcache(html: str, headers: Optional[dict] = None) -> dict:
    """Audit Speculation Rules, bfcache eligibility signals, and LCP fetchpriority hints."""
    html = html or ""
    headers = headers or {}
    speculation_blocks = list(_SPECULATION_BLOCK_RE.finditer(html))
    actions: set[str] = set()
    for m in speculation_blocks:
        for a in _extract_speculation_actions(m.group("body")):
            actions.add(a)
    speculation_header = "speculation-rules" in {k.lower() for k in headers}

    preload_count = len(_PRELOAD_LINK_RE.findall(html))
    prerender_count = len(_PRERENDER_LINK_RE.findall(html))
    fetchpriority_count = len(_FETCHPRIORITY_HIGH_RE.findall(html))
    lcp_img_hint = bool(_LCP_IMG_HINT_RE.search(html))

    cc_value = ""
    for key, value in headers.items():
        if key.lower() == "cache-control":
            cc_value = value or ""
            break
    cache_control_no_store = "no-store" in cc_value.lower()

    has_unload = bool(_UNLOAD_LISTENER_RE.search(html))
    has_beforeunload = bool(_BEFOREUNLOAD_LISTENER_RE.search(html))

    score = 0
    recs: list[str] = []
    if speculation_blocks or speculation_header:
        score += 25
    else:
        recs.append(
            "Add <script type=\"speculationrules\"> for prefetch+prerender on top user-paths."
        )

    if lcp_img_hint:
        score += 25
    else:
        recs.append(
            "Mark the LCP hero image with fetchpriority=\"high\" so the browser preloads it ahead of other resources."
        )

    if not cache_control_no_store and not has_unload:
        score += 25
    else:
        if cache_control_no_store:
            recs.append(
                "Cache-Control: no-store disqualifies the page from bfcache. Remove it on public routes."
            )
        if has_unload:
            recs.append(
                "An unload listener disqualifies the page from bfcache. Switch to pagehide or visibilitychange."
            )

    if prerender_count == 0:
        score += 25
    else:
        recs.append(
            f"Found {prerender_count} <link rel=\"prerender\"> (deprecated). Migrate to Speculation Rules."
        )

    return {
        "speculation_rules": {
            "inline_blocks": len(speculation_blocks),
            "header_present": speculation_header,
            "actions": sorted(actions),
        },
        "preload_hints": preload_count,
        "prerender_links": prerender_count,
        "bfcache_signals": {
            "cache_control_no_store": cache_control_no_store,
            "unload_listener": has_unload,
            "beforeunload_listener": has_beforeunload,
        },
        "lcp_resource_hints": {
            "preload_lcp_candidate": lcp_img_hint,
            "fetchpriority_high": fetchpriority_count,
        },
        "score": score,
        "recommendations": recs,
    }


_LCP_SUBPART_METRICS = [
    "largest_contentful_paint_image_time_to_first_byte",
    "largest_contentful_paint_image_resource_load_delay",
    "largest_contentful_paint_image_resource_load_duration",
    "largest_contentful_paint_image_element_render_delay",
]


def _percentile(metric: dict) -> float | None:
    p = (metric or {}).get("percentiles", {}).get("p75")
    if p is None:
        return None
    try:
        return float(p)
    except (TypeError, ValueError):
        return None


def decompose_lcp_subparts(crux_record: dict, url: str = "", form_factor: str = "PHONE") -> dict:
    """Decompose a CrUX API record into its 4 LCP subparts and surface dominant bottlenecks (>=40% share)."""
    metrics = (crux_record or {}).get("record", {}).get("metrics", {})
    breakdown: dict[str, float | None] = {}
    for key in _LCP_SUBPART_METRICS:
        m = metrics.get(key)
        breakdown[key] = _percentile(m) if m else None

    overall_lcp = (
        _percentile(metrics.get("largest_contentful_paint", {}))
        if metrics.get("largest_contentful_paint")
        else None
    )

    dominant: list[dict] = []
    if overall_lcp:
        for key, val in breakdown.items():
            if val is None:
                continue
            share = val / overall_lcp
            if share >= 0.40:
                dominant.append({
                    "metric": key,
                    "p75_ms": val,
                    "share": round(share, 2),
                })

    recommendations: list[str] = []
    for d in dominant:
        if d["metric"].endswith("time_to_first_byte"):
            recommendations.append(
                "TTFB dominates LCP. Check origin response time, server-side compute, and CDN edge cache hit rate. Aim for TTFB < 0.8s."
            )
        elif d["metric"].endswith("resource_load_delay"):
            recommendations.append(
                "Resource load delay dominates. Preload the hero image with fetchpriority=high or move it ahead of blocking resources."
            )
        elif d["metric"].endswith("resource_load_duration"):
            recommendations.append(
                "Resource load duration dominates. Serve responsive sizes (srcset), modern formats (AVIF/WebP), and async decoding."
            )
        elif d["metric"].endswith("element_render_delay"):
            recommendations.append(
                "Element render delay dominates. Reduce render-blocking CSS/JS above the fold and avoid font-blocking layout shifts."
            )

    return {
        "url": url,
        "form_factor": form_factor,
        "p75_lcp_ms": overall_lcp,
        "subparts_p75_ms": breakdown,
        "dominant_subparts": dominant,
        "recommendations": recommendations,
    }
