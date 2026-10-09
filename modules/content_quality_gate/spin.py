# -*- coding: utf-8 -*-
"""
Cross-post template-spin detection (site-level).

A post whose sentences - after removing its own title/keyword tokens - appear verbatim in
many other posts of the same site is a Mad-Libs template: only the keyword was swapped, so
the body does not actually explain the title. A single-post check cannot see this.
"""
from __future__ import annotations

import collections
import re
from typing import Dict, Iterable, List, Set

from .gate import _strip_tags, keyword_tokens

MIN_SENTENCE_WORDS = 8
SHARED_IN_AT_LEAST = 4      # sentence present in >= N posts (incl. itself) = template sentence
SPIN_JUNK_RATIO = 0.6       # >= 60% template sentences -> templated_spin


def _sentences(title: str, keyword: str, content: str) -> Set[str]:
    drop = set(keyword_tokens(title) + keyword_tokens(keyword))
    out: Set[str] = set()
    for s in re.split(r"(?<=[.!?])\s+", _strip_tags(content).lower()):
        w = [x for x in re.findall(r"[\wÀ-ỹ]+", s) if x not in drop and not x.isdigit()]
        if len(w) >= MIN_SENTENCE_WORDS:
            out.add(" ".join(w))
    return out


def template_spin_ratios(posts: Iterable[Dict]) -> Dict[int, float]:
    """posts: WP REST items (context=edit). Returns {post_id: share of template sentences}."""
    sets: Dict[int, Set[str]] = {}
    for p in posts:
        title = (p.get("title") or {}).get("raw", "")
        kw = (p.get("meta") or {}).get("rank_math_focus_keyword") or ""
        sets[p["id"]] = _sentences(title, kw, (p.get("content") or {}).get("raw", ""))
    df = collections.Counter(s for ss in sets.values() for s in ss)
    return {pid: (sum(1 for s in ss if df[s] >= SHARED_IN_AT_LEAST) / len(ss)) if ss else 0.0
            for pid, ss in sets.items()}


class SpinCorpus:
    """Per-site sentence -> number-of-posts counter, persisted under cache/spin_corpus/<host>.json.

    Seeded by audit_cli from every post on the site and updated after each publish, so the
    pre-publish gate can tell when a new article re-uses sentences from earlier posts.
    """

    def __init__(self, site_url: str, base_dir: str = None):
        import os
        from urllib.parse import urlparse
        base_dir = base_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        host = (urlparse(site_url).hostname or site_url or "site").replace(".", "_")
        self.path = os.path.join(base_dir, "cache", "spin_corpus", f"{host}.json")
        self.counts: Dict[str, int] = {}
        if os.path.exists(self.path):
            import json
            with open(self.path, encoding="utf-8") as f:
                self.counts = json.load(f)

    def ratio(self, title: str, keyword: str, content: str) -> float:
        ss = _sentences(title, keyword, content)
        if not ss:
            return 0.0
        # the new post itself would be one more occurrence
        return sum(1 for s in ss if self.counts.get(s, 0) + 1 >= SHARED_IN_AT_LEAST) / len(ss)

    def add(self, title: str, keyword: str, content: str) -> None:
        for s in _sentences(title, keyword, content):
            self.counts[s] = self.counts.get(s, 0) + 1

    def seed(self, posts: Iterable[Dict]) -> None:
        self.counts = {}
        for p in posts:
            self.add((p.get("title") or {}).get("raw", ""),
                     (p.get("meta") or {}).get("rank_math_focus_keyword") or "",
                     (p.get("content") or {}).get("raw", ""))

    def save(self) -> None:
        import json
        import os
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.counts, f, ensure_ascii=False)
