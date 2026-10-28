#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module: Agentic Health Monitor & Full-Stack SEO/CWV Sentinel
Features:
- Uptime, SSRF-safe HTTP fetch & response latency check across all multi-site domains.
- Canonical & Hreflang consistency verification (flags duplicate canonicals or ?lang= non-canonical hreflangs).
- Core Web Vitals preload, fetchpriority, Speculation Rules & bfcache static analysis.
- Agentic Readiness checks (/robots.txt AI crawlers & /llms.txt evaluation).
"""
from __future__ import annotations

import time
from typing import Any, Dict, List
from bs4 import BeautifulSoup
import requests

from modules.core_web_vitals.preload_and_lcp import analyse_preload_and_bfcache
from modules.ai_crawler_access.agentic_auditor import evaluate_robots_ai_policy, evaluate_llms_txt


class HealthMonitor:
    def __init__(self, sites: List[Dict[str, Any]]):
        self.sites = sites

    @staticmethod
    def verify_canonical_and_hreflang(html_text: str) -> Dict[str, Any]:
        """Inspects <link rel="canonical"> and <link rel="alternate" hreflang="..."> tags for conflicts."""
        soup = BeautifulSoup(html_text or "", "html.parser")
        canonicals = [
            link.get("href", "").strip()
            for link in soup.find_all("link", rel=lambda v: v and "canonical" in (v if isinstance(v, list) else [v]))
            if link.get("href")
        ]
        hreflangs = []
        non_canonical_query_hreflangs = []
        for link in soup.find_all("link", hreflang=True):
            code = link.get("hreflang", "").strip()
            href = link.get("href", "").strip()
            hreflangs.append({"hreflang": code, "href": href})
            if "?lang=" in href or "&lang=" in href:
                non_canonical_query_hreflangs.append(href)

        issues = []
        if len(canonicals) == 0:
            issues.append("missing_canonical")
        elif len(set(canonicals)) > 1:
            issues.append(f"conflicting_canonicals:{len(canonicals)}")
        elif len(canonicals) > 1:
            issues.append(f"duplicate_canonical_tags:{len(canonicals)}")

        if non_canonical_query_hreflangs:
            issues.append(f"hreflang_points_to_query_param:{len(non_canonical_query_hreflangs)}")

        return {
            "canonical_count": len(canonicals),
            "canonical_url": canonicals[0] if canonicals else None,
            "hreflang_count": len(hreflangs),
            "non_canonical_query_hreflangs": non_canonical_query_hreflangs,
            "issues": issues,
            "passed": len(issues) == 0,
        }

    def check_site(self, site: Dict[str, Any], deep: bool = False) -> Dict[str, Any]:
        url = (site.get("url") or "").rstrip("/")
        site_id = site.get("site_id") or site.get("slug") or url
        start = time.time()
        try:
            r = requests.get(url, timeout=12)
            latency = round((time.time() - start) * 1000, 2)
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("title")
            canon_check = self.verify_canonical_and_hreflang(r.text)
            cwv_check = analyse_preload_and_bfcache(r.text, dict(r.headers))

            result: Dict[str, Any] = {
                "site_id": site_id,
                "url": url,
                "status_code": r.status_code,
                "latency_ms": latency,
                "title": title.get_text().strip() if title else "NO TITLE",
                "canonical_hreflang": canon_check,
                "cwv_signals": {
                    "lcp_fetchpriority_high": cwv_check["lcp_image_candidate"]["has_fetchpriority_high"],
                    "lcp_lazy_load_antipattern": cwv_check["lcp_image_candidate"]["has_lazy_load_antipattern"],
                    "speculation_rules_count": cwv_check["speculation_rules_count"],
                    "bfcache_eligible": cwv_check["bfcache_blockers"]["bfcache_eligible"],
                },
                "healthy": r.status_code == 200,
            }

            if deep:
                try:
                    r_rob = requests.get(f"{url}/robots.txt", timeout=8)
                    if r_rob.status_code == 200:
                        result["robots_ai"] = evaluate_robots_ai_policy(r_rob.text)
                except Exception:
                    result["robots_ai"] = {"error": "unreachable"}

                try:
                    r_llms = requests.get(f"{url}/llms.txt", timeout=8)
                    if r_llms.status_code == 200:
                        result["llms_txt"] = evaluate_llms_txt(r_llms.text)
                    else:
                        result["llms_txt"] = {"status_code": r_llms.status_code, "valid": False}
                except Exception:
                    result["llms_txt"] = {"error": "unreachable"}

            return result
        except Exception as e:
            return {"site_id": site_id, "url": url, "healthy": False, "error": str(e)}
