#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parasite-SEO (Site Reputation Abuse) Risk Scanner
(Integrated from AgriciDaniel/claude-seo: parasite_risk.py).

Per Google's site-reputation abuse policy (clarified Nov 2024 & Aug 2026),
evaluates URLs by subfolder section across three signals:
  1. Third-party authorship density ("Partner Content", "Sponsored", "Brand Studio")
  2. Commercial-intent skew ("Buy Now", "Promo Code", "Coupon", "Best X Deals")
  3. Outbound affiliate-link density ("tag=", "aff_id=", "utm_source=", etc.)
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Iterable
from urllib.parse import urlparse

from modules.codebase_security.url_safety import (
    URLSafetyError,
    decode_response_text,
    safe_requests_get,
)

_THIRD_PARTY_BYLINE_PATTERNS = (
    r"\bPartner\s+Content\b",
    r"\bSponsored\s+Content\b",
    r"\bSponsored\s+by\b",
    r"\bBrand\s+Studio\b",
    r"\bIn\s+Partnership\s+With\b",
    r"\bAdvertisement\b",
    r"\bAdvertorial\b",
    r"\bPaid\s+Post\b",
    r"\bPromoted\b",
    r"\bPaid\s+Content\b",
    r"\bBài\s+PR\b",
    r"\bTài\s+trợ\s+bởi\b",
)
_THIRD_PARTY_RE = re.compile("|".join(_THIRD_PARTY_BYLINE_PATTERNS), re.IGNORECASE)

_COMMERCE_PATTERNS = (
    r"\bBuy\s+Now\b",
    r"\bShop\s+Now\b",
    r"\bAdd\s+to\s+Cart\b",
    r"\bCompare\s+Prices\b",
    r"\bBest\s+\w+\s+Deals?\b",
    r"\bPromo\s+Code\b",
    r"\bCoupon\b",
    r"\bDiscount\s+Code\b",
    r"\bAffiliate\s+Disclosure\b",
    r"\bMã\s+giảm\s+giá\b",
    r"\bMua\s+ngay\b",
)
_COMMERCE_RE = re.compile("|".join(_COMMERCE_PATTERNS), re.IGNORECASE)

_AFFILIATE_LINK_RE = re.compile(
    r"\b(?:tag=|aff_id=|affid=|partnerid=|ref_=|utm_source=|utm_campaign=)",
    re.IGNORECASE,
)


def _subfolder(url: str) -> str:
    path = urlparse(url).path or "/"
    parts = [p for p in path.split("/") if p]
    return f"/{parts[0]}/" if parts else "/"


def audit_page_parasite_signals(url: str, html: str) -> dict:
    return {
        "url": url,
        "third_party_hits": len(_THIRD_PARTY_RE.findall(html or "")),
        "commerce_hits": len(_COMMERCE_RE.findall(html or "")),
        "affiliate_link_hits": len(_AFFILIATE_LINK_RE.findall(html or "")),
    }


def classify_parasite_sections(rows: list[dict]) -> dict:
    by_section: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_section[_subfolder(row["url"])].append(row)

    report: dict[str, dict] = {}
    for section, pages in by_section.items():
        n = len(pages)
        third_party_rate = sum(p["third_party_hits"] for p in pages) / n
        commerce_rate = sum(p["commerce_hits"] for p in pages) / n
        affiliate_rate = sum(p["affiliate_link_hits"] for p in pages) / n

        flags: list[str] = []
        risk = "low"

        if third_party_rate >= 1.0:
            flags.append("third-party-authorship-density")
        if commerce_rate >= 2.0:
            flags.append("commercial-intent-skew")
        if affiliate_rate >= 3.0:
            flags.append("affiliate-density")

        if "third-party-authorship-density" in flags:
            risk = "high"
        elif "commercial-intent-skew" in flags and "affiliate-density" in flags:
            risk = "high"
        elif flags:
            risk = "medium"

        report[section] = {
            "page_count": n,
            "third_party_hits_per_page": round(third_party_rate, 2),
            "commerce_hits_per_page": round(commerce_rate, 2),
            "affiliate_link_hits_per_page": round(affiliate_rate, 2),
            "flags": flags,
            "risk": risk,
            "sample_urls": [p["url"] for p in pages[:3]],
        }

    rates = [v["commerce_hits_per_page"] for v in report.values() if v["page_count"] > 0]
    if rates:
        mean_rate = sum(rates) / len(rates)
        for _section, row in report.items():
            if mean_rate > 0 and row["commerce_hits_per_page"] > 2 * mean_rate:
                if "commercial-intent-drift" not in row["flags"]:
                    row["flags"].append("commercial-intent-drift")
                if row["risk"] == "low":
                    row["risk"] = "medium"

    return report


def scan_parasite_risk(urls: Iterable[str], *, timeout: int = 20) -> dict:
    rows: list[dict] = []
    errors: list[dict] = []
    for url in urls:
        try:
            resp = safe_requests_get(url, timeout=timeout, allow_redirects=True)
            rows.append(audit_page_parasite_signals(resp.url, decode_response_text(resp)))
        except URLSafetyError as exc:
            errors.append({"url": url, "error": f"url_safety: {exc}"})
        except Exception as exc:
            errors.append({"url": url, "error": str(exc)})

    sections = classify_parasite_sections(rows)
    severities = Counter(v["risk"] for v in sections.values())
    overall_risk = "high" if severities.get("high", 0) > 0 else (
        "medium" if severities.get("medium", 0) > 0 else "low"
    )

    return {
        "pages_audited": len(rows),
        "errors": errors,
        "by_section": sections,
        "summary": dict(severities),
        "overall_risk": overall_risk,
    }
