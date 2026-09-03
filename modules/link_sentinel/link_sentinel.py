"""
Automated Internal Link Sentinel & 404 Auto-Healer (Concurrent ThreadPool Edition)
"""

import re
import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from typing import Dict, List, Any

class InternalLinkSentinel:
    def __init__(self, site_url: str):
        self.site_url = site_url.rstrip("/")
        self.domain = self.site_url.replace("https://", "").replace("http://", "").split("/")[0]

    def _resolve_url(self, session: requests.Session, url: str) -> tuple:
        try:
            r = session.head(url, timeout=3, allow_redirects=False)
            return (url, r.status_code, r.headers.get("Location"))
        except Exception:
            return (url, 200, None)

    def audit_and_heal_posts(self, posts: List[Dict[str, Any]], session: requests.Session) -> Dict[str, Any]:
        report = {
            "total_posts_scanned": len(posts),
            "total_links_checked": 0,
            "broken_links_found": 0,
            "stale_redirects_found": 0,
            "healed_posts": []
        }

        slug_to_link = {}
        for p in posts:
            slug = p.get("slug")
            link = p.get("link")
            if slug and link:
                slug_to_link[slug] = link

        # 1. Collect all unique internal links across posts
        links_to_test = set()
        post_soups = []

        for p in posts:
            content = p.get("content", {}).get("rendered", "") if isinstance(p.get("content"), dict) else str(p.get("content", ""))
            soup = BeautifulSoup(content, "html.parser")
            post_soups.append((p, soup))
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                if self.domain in href or (href.startswith("/") and not href.startswith("//")):
                    full_url = href if href.startswith("http") else f"{self.site_url}/{href.lstrip('/')}"
                    links_to_test.add(full_url)

        report["total_links_checked"] = len(links_to_test)

        # 2. Concurrently resolve all unique links with 10 threads
        url_status = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._resolve_url, session, u) for u in links_to_test]
            for f in futures:
                u, sc, loc = f.result()
                url_status[u] = (sc, loc)

        # 3. Heal posts
        for p, soup in post_soups:
            post_id = p.get("id")
            post_modified = False
            for a in soup.find_all("a", href=True):
                href = a.get("href", "").strip()
                full_url = href if href.startswith("http") else f"{self.site_url}/{href.lstrip('/')}"
                if full_url in url_status:
                    sc, loc = url_status[full_url]
                    clean_slug = href.strip("/").split("/")[-1].split("?")[0]

                    if sc == 404:
                        report["broken_links_found"] += 1
                        if clean_slug in slug_to_link:
                            a["href"] = slug_to_link[clean_slug]
                            post_modified = True
                        else:
                            a.replace_with(a.text)
                            post_modified = True
                    elif sc in [301, 302] and loc and loc != full_url:
                        report["stale_redirects_found"] += 1
                        a["href"] = loc
                        post_modified = True

            if post_modified:
                report["healed_posts"].append({
                    "id": post_id,
                    "title": p.get("title", {}).get("rendered", ""),
                    "new_content": str(soup)
                })

        return report
