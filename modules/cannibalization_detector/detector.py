# -*- coding: utf-8 -*-
"""
Keyword Cannibalization & Search-Intent Overlap Detector (v2.5)
Combines:
1. Exact/Normalized RankMath Focus Keyword collision check (`rank_math_focus_keyword`).
2. Vietnamese/English Search-Intent Token Normalization (e.g., `3n2d` <-> `3 ngay 2 dem`, stripping generic filler).
3. Weighted Hybrid Score (Token Jaccard + Cosine Similarity + SequenceMatcher).
"""
from __future__ import annotations

import difflib
import html
import math
import re
import unicodedata
from collections import Counter
from typing import Any, Dict, List

_INTENT_STOPWORDS = {
    "va", "cua", "cho", "cac", "nhung", "mot", "la", "co", "tai", "voi", "trong", "khi",
    "nao", "gi", "moi", "nhat", "2024", "2025", "2026", "top", "hay", "dep", "cach",
    "kinh", "nghiem", "huong", "dan", "cam", "nang", "review", "chi", "tiet", "tu", "den",
    "toan", "dien", "tong", "hop", " the", "and", "for", "with", "guide", "best", "complete",
    "ultimate", "how", "what", "from", "into",
}

_SYNONYM_PATTERNS = [
    (re.compile(r"\b(\d+)\s*ngay\s*(\d+)\s*dem\b"), r"\1n\2d"),
    (re.compile(r"\btp\s*hcm\b|\bsai\s*gon\b|\bho\s*chi\s*minh\b"), "tphcm"),
    (re.compile(r"\blam\s*the\s*nao\b|\blam\s*sao\b"), "cach"),
    (re.compile(r"\bkhac\s*phuc\b|\bsua\s*loi\b|\bxu\s*ly\b"), "sualoi"),
    (re.compile(r"\blu\s*hanh\b|\bdu\s*lich\b|\bphuot\b"), "dulich"),
]


def _normalize_intent_text(text: str) -> str:
    s = html.unescape(re.sub(r"<[^>]+>", " ", str(text or "")))
    s = s.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", s)
    ascii_s = "".join(c for c in nfkd if not unicodedata.combining(c)).lower()
    ascii_s = re.sub(r"[^a-z0-9\s]", " ", ascii_s)
    ascii_s = re.sub(r"\s+", " ", ascii_s).strip()
    for rx, rep in _SYNONYM_PATTERNS:
        ascii_s = rx.sub(rep, ascii_s)
    return ascii_s


def _intent_tokens(text: str) -> List[str]:
    norm = _normalize_intent_text(text)
    return [t for t in norm.split() if len(t) >= 2 and t not in _INTENT_STOPWORDS]


def _cosine(c1: Counter, c2: Counter) -> float:
    if not c1 or not c2:
        return 0.0
    inter = set(c1.keys()) & set(c2.keys())
    num = sum(c1[k] * c2[k] for k in inter)
    den = math.sqrt(sum(v * v for v in c1.values())) * math.sqrt(sum(v * v for v in c2.values()))
    return (num / den) if den else 0.0


class KeywordCannibalizationDetector:
    def __init__(self, risk_threshold: float = 0.65):
        self.risk_threshold = risk_threshold

    @staticmethod
    def _extract_focus_kw(p: Dict[str, Any]) -> str:
        meta = p.get("meta") if isinstance(p.get("meta"), dict) else {}
        kw = p.get("focus_keyword") or (meta or {}).get("rank_math_focus_keyword") or ""
        return _normalize_intent_text(str(kw).split(",")[0])

    def analyze_site_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes pairwise search-intent, focus keyword, title, and slug overlap across all posts.
        Returns a list of high-risk cannibalization conflicts with actionable SEO/GEO remedies.
        """
        conflicts: List[Dict[str, Any]] = []
        n = len(posts)

        prepared = []
        for p in posts:
            title = (
                p.get("title", {}).get("rendered", "")
                if isinstance(p.get("title"), dict)
                else str(p.get("title", ""))
            )
            slug = str(p.get("slug", ""))
            fkw = self._extract_focus_kw(p)
            toks = _intent_tokens(f"{title} {slug.replace('-', ' ')} {fkw}")
            prepared.append({
                "raw": p,
                "title": title,
                "slug": slug,
                "fkw": fkw,
                "tokens": set(toks),
                "counter": Counter(toks),
            })

        for i in range(n):
            for j in range(i + 1, n):
                a = prepared[i]
                b = prepared[j]
                p1, p2 = a["raw"], b["raw"]

                # 1. Exact Focus Keyword Collision
                fkw_collision = bool(a["fkw"] and b["fkw"] and a["fkw"] == b["fkw"])

                # 2. SequenceMatcher on title & slug
                title_ratio = difflib.SequenceMatcher(None, a["title"].lower(), b["title"].lower()).ratio()
                slug_ratio = difflib.SequenceMatcher(None, a["slug"].lower(), b["slug"].lower()).ratio()

                # 3. Search-Intent Token Jaccard & Cosine Similarity
                union_len = len(a["tokens"] | b["tokens"])
                jaccard = (len(a["tokens"] & b["tokens"]) / union_len) if union_len else 0.0
                cosine_sim = _cosine(a["counter"], b["counter"])
                intent_score = (0.55 * cosine_sim) + (0.45 * jaccard)

                combined_score = 1.0 if fkw_collision else max(title_ratio, slug_ratio, intent_score)

                if combined_score >= self.risk_threshold:
                    shared_tokens = sorted(a["tokens"] & b["tokens"])
                    conflicts.append({
                        "post_a": {"id": p1.get("id"), "title": a["title"], "slug": a["slug"], "link": p1.get("link")},
                        "post_b": {"id": p2.get("id"), "title": b["title"], "slug": b["slug"], "link": p2.get("link")},
                        "conflict_score": round(combined_score, 3),
                        "focus_keyword_collision": fkw_collision,
                        "shared_intent_tokens": shared_tokens,
                        "risk_level": "CRITICAL" if combined_score >= 0.8 else "HIGH",
                        "recommendation": (
                            "Gộp bài viết (301 Redirect + Content Merge) thành 1 Pillar Post toàn diện, "
                            f"hoặc phân tách rõ Search Intent và đặt thẻ rel='canonical' từ bài {p2.get('id')} trỏ về bài chính {p1.get('id')}."
                        ),
                    })

        conflicts.sort(key=lambda x: x["conflict_score"], reverse=True)
        return conflicts
