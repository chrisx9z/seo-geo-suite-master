"""
Automated Orphan Link Healer Module
Identifies isolated orphan posts with 0 internal cluster connections,
locates contextually optimal host articles (such as Pillar Posts),
and injects natural bridging backlinks to restore 100% topical link flow.
"""

import re
import html
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Tuple

class OrphanLinkHealer:
    def __init__(self):
        pass

    def bridge_orphan_to_host(self, host_html: str, orphan_post: Dict[str, Any]) -> Tuple[str, bool]:
        """
        Injects a natural contextual bridge link pointing to the orphan_post inside host_html.
        """
        orphan_title = orphan_post.get("title", {}).get("rendered", "") if isinstance(orphan_post.get("title"), dict) else str(orphan_post.get("title", ""))
        orphan_slug = orphan_post.get("slug", "")
        orphan_url = orphan_post.get("link", "")
        if not orphan_url:
            return host_html, False

        # Clean title for anchor text
        clean_anchor = re.sub(r"[\(\)\[\]\{\}\:\?\!\|\,\.]", " ", orphan_title)
        tokens = [w.strip() for w in clean_anchor.split() if len(w.strip()) > 3]
        anchor_phrase = " ".join(tokens[:4]) if len(tokens) >= 4 else orphan_slug.replace("-", " ")

        bridge_html = (
            f'<p class="cluster-bridge-callout" style="background:#131d31; border-left:4px solid #38bdf8; padding:14px 18px; margin:24px 0; border-radius:6px;">'
            f'📌 <em>Xem bài phân tích chuyên sâu liên quan:</em> '
            f'<a href="{orphan_url}" title="{html.escape(orphan_title)}" style="color:#38bdf8; font-weight:600; text-decoration:underline;">{orphan_title}</a>.'
            f'</p>'
        )

        soup = BeautifulSoup(host_html, "html.parser")
        
        # Check if already linked
        if orphan_url in host_html or orphan_slug in host_html:
            return host_html, False

        # Find a suitable insertion point (e.g. before the last H2 or FAQ)
        faq_section = soup.find("div", class_="faq-section")
        if faq_section:
            bridge_soup = BeautifulSoup(bridge_html, "html.parser")
            faq_section.insert_before(bridge_soup)
            return str(soup), True

        # Fallback: append at the end
        paragraphs = soup.find_all("p")
        if paragraphs and len(paragraphs) >= 3:
            target_p = paragraphs[-2]
            bridge_soup = BeautifulSoup(bridge_html, "html.parser")
            target_p.insert_after(bridge_soup)
            return str(soup), True

        return host_html + "\n\n" + bridge_html, True
