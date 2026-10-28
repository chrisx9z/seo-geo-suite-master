# -*- coding: utf-8 -*-
"""
GEO Knowledge Graph & Wikidata Entity Linker (v2.5 Multi-Vertical Edition)
Extracts recognized entities across Tech/AI, Travel/UNESCO Destinations, and World Records/Science,
and attaches authoritative Wikidata / Wikipedia URIs to Schema.org @graph (`about`, `mentions`)
for maximum AI Search (Google AI Overviews, Perplexity, ChatGPT Search, Claude) citation authority.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List


def _fold_ascii(text: str) -> str:
    s = (text or "").replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


WIKIDATA_KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    # --- Tech, AI & Software Engineering ---
    "artificial intelligence": {"name": "Artificial intelligence", "sameAs": "https://www.wikidata.org/wiki/Q11660"},
    "tri tue nhan tao": {"name": "Trí tuệ nhân tạo", "sameAs": "https://www.wikidata.org/wiki/Q11660"},
    "deepseek": {"name": "DeepSeek", "sameAs": "https://www.wikidata.org/wiki/Q131317578"},
    "openai": {"name": "OpenAI", "sameAs": "https://www.wikidata.org/wiki/Q22670157"},
    "chatgpt": {"name": "ChatGPT", "sameAs": "https://www.wikidata.org/wiki/Q115564437"},
    "gemini": {"name": "Gemini (language model)", "sameAs": "https://www.wikidata.org/wiki/Q123689405"},
    "claude": {"name": "Claude (language model)", "sameAs": "https://www.wikidata.org/wiki/Q117246169"},
    "python": {"name": "Python (programming language)", "sameAs": "https://www.wikidata.org/wiki/Q28865"},
    "javascript": {"name": "JavaScript", "sameAs": "https://www.wikidata.org/wiki/Q2005"},
    "wordpress": {"name": "WordPress", "sameAs": "https://www.wikidata.org/wiki/Q13166"},
    "cloudflare": {"name": "Cloudflare", "sameAs": "https://www.wikidata.org/wiki/Q5136746"},
    "docker": {"name": "Docker (software)", "sameAs": "https://www.wikidata.org/wiki/Q15206305"},
    "kubernetes": {"name": "Kubernetes", "sameAs": "https://www.wikidata.org/wiki/Q22661306"},
    "microsoft excel": {"name": "Microsoft Excel", "sameAs": "https://www.wikidata.org/wiki/Q11272"},
    "windows 11": {"name": "Windows 11", "sameAs": "https://www.wikidata.org/wiki/Q107263055"},
    "search engine optimization": {"name": "Search engine optimization", "sameAs": "https://www.wikidata.org/wiki/Q180711"},
    "seo": {"name": "Search engine optimization", "sameAs": "https://www.wikidata.org/wiki/Q180711"},
    "core web vitals": {"name": "Core Web Vitals", "sameAs": "https://www.wikidata.org/wiki/Q107392246"},
    "schema.org": {"name": "Schema.org", "sameAs": "https://www.wikidata.org/wiki/Q3475322"},
    # --- Travel, UNESCO Heritage & Destinations ---
    "ha long": {"name": "Hạ Long Bay", "sameAs": "https://www.wikidata.org/wiki/Q189903"},
    "halong bay": {"name": "Hạ Long Bay", "sameAs": "https://www.wikidata.org/wiki/Q189903"},
    "phong nha": {"name": "Phong Nha – Kẻ Bàng National Park", "sameAs": "https://www.wikidata.org/wiki/Q23513"},
    "trang an": {"name": "Tràng An Scenic Landscape Complex", "sameAs": "https://www.wikidata.org/wiki/Q7833409"},
    "ninh binh": {"name": "Ninh Bình", "sameAs": "https://www.wikidata.org/wiki/Q36662"},
    "hoi an": {"name": "Hội An", "sameAs": "https://www.wikidata.org/wiki/Q36094"},
    "da nang": {"name": "Da Nang", "sameAs": "https://www.wikidata.org/wiki/Q25282"},
    "phu quoc": {"name": "Phú Quốc", "sameAs": "https://www.wikidata.org/wiki/Q146695"},
    "da lat": {"name": "Da Lat", "sameAs": "https://www.wikidata.org/wiki/Q25281"},
    "sa pa": {"name": "Sa Pa", "sameAs": "https://www.wikidata.org/wiki/Q303200"},
    "sapa": {"name": "Sa Pa", "sameAs": "https://www.wikidata.org/wiki/Q303200"},
    "ha giang": {"name": "Hà Giang", "sameAs": "https://www.wikidata.org/wiki/Q36669"},
    "nha trang": {"name": "Nha Trang", "sameAs": "https://www.wikidata.org/wiki/Q25279"},
    "ha noi": {"name": "Hanoi", "sameAs": "https://www.wikidata.org/wiki/Q1858"},
    "hanoi": {"name": "Hanoi", "sameAs": "https://www.wikidata.org/wiki/Q1858"},
    "con dao": {"name": "Côn Đảo", "sameAs": "https://www.wikidata.org/wiki/Q1094879"},
    "cat ba": {"name": "Cát Bà Island", "sameAs": "https://www.wikidata.org/wiki/Q1050188"},
    "quy nhon": {"name": "Quy Nhơn", "sameAs": "https://www.wikidata.org/wiki/Q36073"},
    "mui ne": {"name": "Mũi Né", "sameAs": "https://www.wikidata.org/wiki/Q1012161"},
    "bangkok": {"name": "Bangkok", "sameAs": "https://www.wikidata.org/wiki/Q1861"},
    "tokyo": {"name": "Tokyo", "sameAs": "https://www.wikidata.org/wiki/Q1490"},
    "singapore": {"name": "Singapore", "sameAs": "https://www.wikidata.org/wiki/Q334"},
    # --- World Records, Geography & Science ---
    "everest": {"name": "Mount Everest", "sameAs": "https://www.wikidata.org/wiki/Q513"},
    "mariana": {"name": "Mariana Trench", "sameAs": "https://www.wikidata.org/wiki/Q179744"},
    "amazon": {"name": "Amazon River", "sameAs": "https://www.wikidata.org/wiki/Q3783"},
    "sahara": {"name": "Sahara", "sameAs": "https://www.wikidata.org/wiki/Q6583"},
    "thai binh duong": {"name": "Pacific Ocean", "sameAs": "https://www.wikidata.org/wiki/Q98"},
    "pacific ocean": {"name": "Pacific Ocean", "sameAs": "https://www.wikidata.org/wiki/Q98"},
    "he mat troi": {"name": "Solar System", "sameAs": "https://www.wikidata.org/wiki/Q544"},
    "solar system": {"name": "Solar System", "sameAs": "https://www.wikidata.org/wiki/Q544"},
    "nasa": {"name": "NASA", "sameAs": "https://www.wikidata.org/wiki/Q23548"},
    "unesco": {"name": "UNESCO", "sameAs": "https://www.wikidata.org/wiki/Q7809"},
}


class GeoEntityLinker:
    def __init__(self, custom_kb: Dict[str, Dict[str, str]] | None = None):
        self.kb = dict(WIKIDATA_KNOWLEDGE_BASE)
        if custom_kb:
            self.kb.update(custom_kb)

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Finds matching Wikidata-backed entities from accented or unaccented text content."""
        clean_text = re.sub(r"<[^>]+>", " ", text or "")
        folded_text = _fold_ascii(clean_text)
        matched: List[Dict[str, str]] = []
        seen: set[str] = set()

        for key, meta in self.kb.items():
            folded_key = _fold_ascii(key)
            pattern = re.compile(rf"\b{re.escape(folded_key)}\b", re.IGNORECASE)
            if pattern.search(folded_text) and meta["sameAs"] not in seen:
                matched.append({
                    "@type": "Thing",
                    "name": meta["name"],
                    "sameAs": meta["sameAs"],
                })
                seen.add(meta["sameAs"])
        return matched

    @staticmethod
    def extract_authoritative_citations(html_content: str) -> List[str]:
        """Extracts authoritative external reference URLs from HTML for Schema.org `citation`."""
        if not html_content:
            return []
        auth_domains = (
            "wikipedia.org", "wikidata.org", "w3.org", "ietf.org", "arxiv.org",
            "developers.google.com", "schema.org", "unesco.org", "nasa.gov",
            "github.com", "mozilla.org", ".gov", ".edu",
        )
        urls = re.findall(r'<a[^>]+href=["\'](https?://[^"\'>\s]+)["\']', html_content, flags=re.I)
        citations: List[str] = []
        seen: set[str] = set()
        for u in urls:
            u_low = u.lower()
            if any(d in u_low for d in auth_domains) and u not in seen:
                citations.append(u)
                seen.add(u)
        return citations[:10]

    def inject_geo_quotable_block(self, html_content: str, entity_name: str, core_definition: str) -> str:
        """
        Injects a journalism-standard quotable summary block optimized for AI search engines.
        """
        block = (
            f'<div class="geo-quotable-summary" style="background:#0f172a; border-left:4px solid #00e5ff; '
            f'padding:16px 20px; border-radius:6px; margin:24px 0; color:#e2e8f0;">\n'
            f'  <strong style="color:#00e5ff; font-size:1.05em;">💡 Tóm Tắt Thực Thể (GEO Quick Answer):</strong>\n'
            f'  <p style="margin:8px 0 0 0; line-height:1.6; font-size:0.98em;">'
            f'  <strong>{entity_name}</strong>: {core_definition}</p>\n'
            f'</div>\n'
        )
        return block + html_content
