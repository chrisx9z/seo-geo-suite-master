"""
GEO Knowledge Graph & Wikidata Entity Linker
Extracts recognized tech entities and attaches authoritative Wikidata / Wikipedia URIs
to Schema.org @graph (about, mentions) for maximum AI Search (Perplexity, SGE, ChatGPT) authority.
"""

import re
import json
from typing import List, Dict, Any

WIKIDATA_KNOWLEDGE_BASE = {
    "artificial intelligence": {"name": "Artificial intelligence", "sameAs": "https://www.wikidata.org/wiki/Q11660"},
    "tri tue nhan tao": {"name": "Trí tuệ nhân tạo", "sameAs": "https://vi.wikipedia.org/wiki/Tr%C3%AD_tu%E1%BB%87_nh%C3%A2n_t%E1%BA%A1o"},
    "deepseek": {"name": "DeepSeek", "sameAs": "https://www.wikidata.org/wiki/Q131317578"},
    "openai": {"name": "OpenAI", "sameAs": "https://www.wikidata.org/wiki/Q22670157"},
    "chatgpt": {"name": "ChatGPT", "sameAs": "https://www.wikidata.org/wiki/Q115564437"},
    "gemini": {"name": "Gemini (language model)", "sameAs": "https://www.wikidata.org/wiki/Q123689405"},
    "binance": {"name": "Binance", "sameAs": "https://www.wikidata.org/wiki/Q56278588"},
    "python": {"name": "Python (programming language)", "sameAs": "https://www.wikidata.org/wiki/Q28865"},
    "javascript": {"name": "JavaScript", "sameAs": "https://www.wikidata.org/wiki/Q2005"},
    "wordpress": {"name": "WordPress", "sameAs": "https://www.wikidata.org/wiki/Q13166"},
    "cloudflare": {"name": "Cloudflare", "sameAs": "https://www.wikidata.org/wiki/Q5136746"},
    "search engine optimization": {"name": "Search engine optimization", "sameAs": "https://www.wikidata.org/wiki/Q180711"},
    "seo": {"name": "Search engine optimization", "sameAs": "https://www.wikidata.org/wiki/Q180711"},
    "kinh dich": {"name": "I Ching", "sameAs": "https://www.wikidata.org/wiki/Q181036"},
    "i ching": {"name": "I Ching", "sameAs": "https://www.wikidata.org/wiki/Q181036"}
}

class GeoEntityLinker:
    def __init__(self):
        self.kb = WIKIDATA_KNOWLEDGE_BASE

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Finds matching entities from text content."""
        lower_text = text.lower()
        matched = []
        seen = set()

        for key, meta in self.kb.items():
            pattern = re.compile(rf"\b{re.escape(key)}\b", re.IGNORECASE)
            if pattern.search(lower_text) and meta["sameAs"] not in seen:
                matched.append({
                    "@type": "Thing",
                    "name": meta["name"],
                    "sameAs": meta["sameAs"]
                })
                seen.add(meta["sameAs"])
        return matched

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
