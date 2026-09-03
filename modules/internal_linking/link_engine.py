"""
Auto Internal Linking Engine (Topic Cluster & Silo Architecture) - Optimized Fast Match
"""

import re
import html
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Tuple

class InternalLinkEngine:
    def __init__(self, max_links_per_post: int = 4):
        self.max_links = max_links_per_post
        
    def inject_links(self, html_content: str, target_posts: List[Dict[str, Any]], current_post_id: int) -> Tuple[str, int]:
        soup = BeautifulSoup(html_content, "html.parser")
        injected_count = 0
        used_target_ids = set()
        
        kw_map = {}
        for p in target_posts:
            pid = p.get("id")
            if pid == current_post_id:
                continue
            
            p_link = p.get("link")
            p_title = p.get("title", {}).get("rendered", "") if isinstance(p.get("title"), dict) else str(p.get("title", ""))
            slug = p.get("slug", "")
            
            candidates = []
            if slug:
                candidates.append(slug.replace("-", " "))
            
            cleaned_title = re.sub(r"[\(\)\[\]\{\}\:\?\!\|\,\.]", " ", p_title)
            tokens = [w.strip() for w in cleaned_title.split() if len(w.strip()) > 3]
            if len(tokens) >= 3:
                candidates.append(" ".join(tokens[:3]))
                candidates.append(" ".join(tokens[1:4]))

            for cand in candidates:
                cand_clean = cand.strip()
                if len(cand_clean) >= 6 and cand_clean.lower() not in kw_map:
                    kw_map[cand_clean.lower()] = {
                        "text": cand_clean,
                        "url": p_link,
                        "title": p_title,
                        "id": pid
                    }

        if not kw_map:
            return html_content, 0

        sorted_kws = sorted(kw_map.keys(), key=lambda x: len(x), reverse=True)[:60]
        regex_pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted_kws) + r")\b", re.IGNORECASE)

        paragraphs = soup.find_all(["p", "li"])
        for p_tag in paragraphs:
            if injected_count >= self.max_links:
                break
            if p_tag.find_parent(["pre", "code", "table", "blockquote"]):
                continue
            if len(p_tag.find_all("a")) >= 2:
                continue

            for child in list(p_tag.children):
                if injected_count >= self.max_links:
                    break
                if child.name is None:
                    text_str = str(child)
                    match = regex_pattern.search(text_str)
                    if match:
                        matched_kw = match.group(0).lower()
                        meta = kw_map.get(matched_kw)
                        if not meta or meta["id"] in used_target_ids:
                            continue
                        
                        start, end = match.span()
                        before = text_str[:start]
                        after = text_str[end:]
                        orig_text = match.group(0)
                        
                        link_html = f'<a href="{meta["url"]}" title="{html.escape(meta["title"])}" class="autolink-cluster">{orig_text}</a>'
                        new_html = before + link_html + after
                        
                        new_soup = BeautifulSoup(new_html, "html.parser")
                        child.replace_with(new_soup)
                        
                        used_target_ids.add(meta["id"])
                        injected_count += 1
                        break

        return str(soup), injected_count
