# -*- coding: utf-8 -*-
"""
Auto Internal Linking Engine (Topic Cluster & Silo Architecture — v2.5 Vietnamese & English Aware)
Supports:
- RankMath focus keyword extraction (`rank_math_focus_keyword` / `focus_keyword`)
- Vietnamese 2–3 character core words (does NOT strip 2-3 char words like "Đà", "Nẵng", "AI", "sửa", "lỗi")
- Accent-insensitive matching against accented Vietnamese prose while preserving original accented anchor text
"""
from __future__ import annotations

import html
import re
import unicodedata
from typing import Any, Dict, List, Tuple
from bs4 import BeautifulSoup

_LEADING_FILLER_RE = re.compile(
    r"^(?:top\s+\d+\s+|hướng\s+dẫn\s+|kinh\s+nghiệm\s+|cẩm\s+nang\s+|cách\s+|review\s+|khám\s+phá\s+|"
    r"bật\s+mí\s+|tổng\s+hợp\s+|complete\s+guide\s+to\s+|how\s+to\s+|best\s+)",
    re.IGNORECASE,
)


def _fold_ascii_preserve_len(text: str) -> str:
    """Folds Vietnamese characters to ASCII while preserving 1-to-1 character positions in `text`."""
    out: list[str] = []
    for ch in text:
        if ch in ("đ", "Đ"):
            out.append("d")
            continue
        decomposed = unicodedata.normalize("NFD", ch)
        base = "".join(c for c in decomposed if not unicodedata.combining(c))
        out.append((base[0] if base else ch).lower())
    return "".join(out)


class InternalLinkEngine:
    def __init__(self, max_links_per_post: int = 4):
        self.max_links = max_links_per_post

    @staticmethod
    def _extract_candidate_phrases(p: Dict[str, Any]) -> List[str]:
        candidates: List[str] = []
        meta = p.get("meta") if isinstance(p.get("meta"), dict) else {}
        focus_kw = (
            p.get("focus_keyword")
            or (meta or {}).get("rank_math_focus_keyword")
            or ""
        ).strip()
        if focus_kw:
            candidates.append(focus_kw.split(",")[0].strip())

        p_title = (
            p.get("title", {}).get("rendered", "")
            if isinstance(p.get("title"), dict)
            else str(p.get("title", ""))
        )
        p_title = html.unescape(re.sub(r"<[^>]+>", "", p_title)).strip()
        if p_title:
            # Split on colons/dashes/pipes to get core topic clauses
            clauses = [c.strip() for c in re.split(r"[:\|\–\—\-]", p_title) if len(c.strip()) >= 6]
            for clause in clauses[:2]:
                stripped = _LEADING_FILLER_RE.sub("", clause).strip()
                if len(stripped) >= 6:
                    candidates.append(stripped)
                words = [w for w in re.sub(r"[\(\)\[\]\{\}\?\!\,\.\"]", " ", stripped).split() if len(w) >= 2]
                if len(words) >= 3:
                    candidates.append(" ".join(words[:4]))
                    if len(words) >= 5:
                        candidates.append(" ".join(words[:5]))

        slug = (p.get("slug") or "").strip()
        if slug:
            slug_words = [w for w in slug.split("-") if w not in ("2024", "2025", "2026", "top", "nhung", "cac")]
            if 2 <= len(slug_words) <= 6:
                candidates.append(" ".join(slug_words))

        return candidates

    def inject_links(
        self,
        html_content: str,
        target_posts: List[Dict[str, Any]],
        current_post_id: int,
    ) -> Tuple[str, int]:
        if not html_content or not target_posts:
            return html_content, 0

        soup = BeautifulSoup(html_content, "html.parser")
        injected_count = 0
        used_target_ids = set()

        # Map folded ASCII phrase -> target metadata
        kw_map: Dict[str, Dict[str, Any]] = {}
        for p in target_posts:
            pid = p.get("id")
            if pid == current_post_id:
                continue
            p_link = p.get("link")
            if not p_link:
                continue
            p_title = (
                p.get("title", {}).get("rendered", "")
                if isinstance(p.get("title"), dict)
                else str(p.get("title", ""))
            )
            p_title = html.unescape(re.sub(r"<[^>]+>", "", p_title)).strip()

            for cand in self._extract_candidate_phrases(p):
                cand_folded = re.sub(r"\s+", " ", _fold_ascii_preserve_len(cand)).strip()
                if len(cand_folded) >= 6 and cand_folded not in kw_map:
                    kw_map[cand_folded] = {
                        "url": p_link,
                        "title": p_title,
                        "id": pid,
                    }

        if not kw_map:
            return html_content, 0

        sorted_kws = sorted(kw_map.keys(), key=len, reverse=True)[:80]
        regex_pattern = re.compile(
            r"(?<![a-z0-9])(" + "|".join(re.escape(k) for k in sorted_kws) + r")(?![a-z0-9])",
            re.IGNORECASE,
        )

        paragraphs = soup.find_all(["p", "li"])
        for p_tag in paragraphs:
            if injected_count >= self.max_links:
                break
            if p_tag.find_parent(["pre", "code", "table", "blockquote", "a", "h1", "h2", "h3", "h4"]):
                continue
            if len(p_tag.find_all("a")) >= 2:
                continue

            for child in list(p_tag.children):
                if injected_count >= self.max_links:
                    break
                if child.name is None:
                    text_str = str(child)
                    folded_str = _fold_ascii_preserve_len(text_str)
                    match = regex_pattern.search(folded_str)
                    if match:
                        matched_folded = re.sub(r"\s+", " ", match.group(0).lower()).strip()
                        meta = kw_map.get(matched_folded)
                        if not meta or meta["id"] in used_target_ids:
                            continue

                        start, end = match.span()
                        before = text_str[:start]
                        orig_text = text_str[start:end]
                        after = text_str[end:]

                        link_html = (
                            f'{html.escape(before)}'
                            f'<a href="{html.escape(meta["url"])}" title="{html.escape(meta["title"])}" '
                            f'class="autolink-cluster">{html.escape(orig_text)}</a>'
                            f'{html.escape(after)}'
                        )
                        frag = BeautifulSoup(link_html, "html.parser")
                        child.replace_with(*list(frag.contents))

                        used_target_ids.add(meta["id"])
                        injected_count += 1
                        break

        return str(soup), injected_count
