#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Primary-Source Google Updates Ledger Query Tool
(Integrated from AgriciDaniel/claude-seo: seo_updates.py + google-updates.json).

Reads `modules/search_console_sentinel/google-updates.json` and surfaces filtered views
of confirmed Google ranking / spam / QRG / product / schema / CWV / Discover updates.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

_DATA_FILE = Path(__file__).resolve().parent / "google-updates.json"

KNOWN_KINDS = (
    "core", "spam", "core+spam", "policy", "qrg", "product", "schema", "cwv",
    "discover", "documentation",
)

STALE_AFTER_DAYS = 30
_STATUS_URL = "https://status.search.google.com/"


def freshness(
    last_verified: Optional[str],
    today: Optional[date] = None,
    max_age: int = STALE_AFTER_DAYS,
) -> dict:
    today = today or date.today()
    try:
        verified = date.fromisoformat(str(last_verified))
    except ValueError:
        return {
            "age_days": None,
            "stale": True,
            "warning": "last_verified is missing or not an ISO date.",
        }
    age = (today - verified).days
    stale = age > max_age
    warning = (
        f"Ledger last verified {age} days ago. Updates released since "
        f"{verified.isoformat()} are missing; check {_STATUS_URL} before "
        "attributing recent traffic changes."
    ) if stale else None
    return {"age_days": age, "stale": stale, "warning": warning}


def load_google_updates() -> dict:
    with _DATA_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def query_google_updates(
    *,
    since: Optional[str] = None,
    kinds: Optional[Iterable[str]] = None,
    limit: int = 10,
    unverified: bool = False,
) -> dict:
    data = load_google_updates()
    fresh = freshness(data.get("last_verified"))
    if unverified:
        return {
            "last_verified": data.get("last_verified"),
            "source_of_truth": data.get("source_of_truth"),
            "freshness": fresh,
            "unverified": data.get("unverified", []),
        }

    out = list(data.get("updates", []))
    if since:
        if len(since) == 4:
            since_date = date(int(since), 1, 1)
        elif len(since) == 7:
            y, m = since.split("-")
            since_date = date(int(y), int(m), 1)
        else:
            since_date = date.fromisoformat(since)
        out = [u for u in out if date.fromisoformat(u["date"]) >= since_date]

    kind_set = set(kinds) if kinds else None
    if kind_set:
        wanted = set(kind_set)
        if wanted & {"core", "spam"}:
            wanted.add("core+spam")
        out = [u for u in out if u.get("kind") in wanted]

    out.sort(key=lambda u: u["date"], reverse=True)
    filtered = out[:limit] if limit else out

    return {
        "source_of_truth": data.get("source_of_truth"),
        "last_verified": data.get("last_verified"),
        "freshness": fresh,
        "count": len(filtered),
        "updates": filtered,
    }
