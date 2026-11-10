# -*- coding: utf-8 -*-
"""
Keyword Cannibalization & Cross-Site Copying Guard.

Prevents:
1. Same-Site Keyword Cannibalization:
   - Never allow two posts on the same site to share the same normalized focus keyword
     or core entity slug (prevents WordPress -2/-3 duplicate slugs and SERP competition).
2. Cross-Site Keyword Copying:
   - Never allow two different sites in the network to schedule/publish the exact same
     normalized focus keyword or core entity slug.
"""
from __future__ import annotations

import glob
import json
import os
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from .gate import normalize_slug

GENERIC_KW_STOPWORDS = {
    "kinh", "nghiệm", "nghiem", "du", "lịch", "lich", "tự", "tu", "túc", "tuc",
    "cẩm", "cam", "nang", "khám", "kham", "phá", "pha", "chi", "tiết", "tiet",
    "hướng", "huong", "dẫn", "dan", "toàn", "toan", "tập", "tap", "từ", "đến",
    "den", "a", "z", "mới", "moi", "nhất", "nhat", "review", "check", "in",
    "cách", "cach", "là", "la", "gì", "gi", "và", "va", "của", "cua", "cho",
    "người", "nguoi", "2024", "2025", "2026", "2027", "guide", "complete",
    "ultimate", "best", "how", "to", "in", "for", "the", "of", "and"
}


def normalize_keyword_key(keyword: str) -> str:
    """Normalizes a focus keyword for exact comparison (strips years & punctuation)."""
    s = (keyword or "").lower().strip()
    s = re.sub(r"\b202[0-9]\b", "", s)
    s = re.sub(r"[^\w\sà-ỹ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def core_entity_key(keyword: str, slug: str = "") -> str:
    """Extracts the core entity slug stripped of generic travel/tutorial modifiers."""
    s = normalize_slug(slug, keyword)
    s = re.sub(r"-[2-9]$", "", s)
    prefixes = [
        "kinh-nghiem-du-lich-", "kinh-nghiem-di-", "kinh-nghiem-",
        "cam-nang-du-lich-", "cam-nang-", "du-lich-", "kham-pha-",
        "lich-trinh-du-lich-", "lich-trinh-", "huong-dan-", "cach-sua-loi-",
        "cach-khac-phuc-", "cach-"
    ]
    for p in prefixes:
        if s.startswith(p) and len(s) > len(p) + 3:
            s = s[len(p):]
            break
    suffixes = [
        "-tu-tuc", "-chi-tiet", "-moi-nhat", "-toan-tap", "-cho-nguoi-moi"
    ]
    for suf in suffixes:
        if s.endswith(suf) and len(s) > len(suf) + 3:
            s = s[:-len(suf)]
            break
    return s


def check_keyword_cannibalization(
    site_url: str,
    keyword: str,
    slug: str = "",
    title: str = "",
    base_dir: Optional[str] = None,
    allow_existing_post_id: Optional[int] = None,
) -> Tuple[bool, List[str]]:
    """
    Checks `cache/scheduled_*.json` across all sites to ensure:
      1. `site_url` does not already have a post with the same normalized keyword or slug
         (Same-Site Keyword Cannibalization).
      2. No other site in the network has a scheduled/published post with the exact same
         normalized keyword or slug (Cross-Site Keyword Copying).

    Returns `(passed, issues)`.
    """
    if not site_url:
        return True, []

    base_dir = base_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    cache_dir = os.path.join(base_dir, "cache")
    if not os.path.isdir(cache_dir):
        return True, []

    target_host = (urlparse(site_url).hostname or site_url).replace(".", "_").lower()
    target_norm_kw = normalize_keyword_key(keyword or title)
    target_slug = re.sub(r"-[2-9]$", "", (slug or "").lower().strip())
    target_core = core_entity_key(keyword or title, target_slug)

    issues: List[str] = []

    for path in glob.glob(os.path.join(cache_dir, "scheduled_*.json")):
        fname = os.path.basename(path).lower()
        file_host = fname.replace("scheduled_", "").replace(".json", "")
        is_same_site = (file_host == target_host)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        for p in data.get("scheduled_posts", []):
            pid = p.get("id")
            if allow_existing_post_id and pid == allow_existing_post_id:
                continue
            p_kw = p.get("keyword") or p.get("title") or ""
            p_slug = re.sub(r"-[2-9]$", "", (p.get("slug") or "").lower().strip())
            p_norm_kw = normalize_keyword_key(p_kw)
            p_core = core_entity_key(p_kw, p_slug)

            if is_same_site:
                if target_slug and p_slug and target_slug == p_slug:
                    issues.append(f"same_site_slug_cannibalization:{target_slug}(id={pid})")
                    break
                if target_norm_kw and p_norm_kw and target_norm_kw == p_norm_kw:
                    issues.append(f"same_site_keyword_cannibalization:{target_norm_kw}(id={pid})")
                    break
            else:
                # Cross-site check: block exact keyword copy or exact slug copy across sites
                if target_slug and p_slug and len(target_slug) >= 8 and target_slug == p_slug:
                    issues.append(f"cross_site_slug_copy:{target_slug}@{file_host}(id={pid})")
                    break
                if target_norm_kw and p_norm_kw and len(target_norm_kw) >= 10 and target_norm_kw == p_norm_kw:
                    issues.append(f"cross_site_keyword_copy:{target_norm_kw}@{file_host}(id={pid})")
                    break
                if target_core and p_core and len(target_core) >= 12 and target_core == p_core:
                    issues.append(f"cross_site_entity_copy:{target_core}@{file_host}(id={pid})")
                    break

    return (len(issues) == 0), issues
