"""
Automated Internal Link Sentinel & 404 Auto-Healer (Concurrent ThreadPool Edition)

Safety rules (ported from ultimate-seo-geo 1.19–1.21): a link is only "broken" when a GET
confirms 404/410. HEAD answers of 403/404/405/501 are retried with GET, refusals (401/429)
and network errors are "unverified" and never touched, and non-page hrefs (mailto:, tel:,
Cloudflare /cdn-cgi/l/email-protection) are skipped.
"""

import re
import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from typing import Dict, List, Any

try:
    from modules.ai_crawler_access.url_safety import is_crawlable_href, is_refusal
except ImportError:  # pragma: no cover
    from ..ai_crawler_access.url_safety import is_crawlable_href, is_refusal

HEAD_UNRELIABLE = (403, 404, 405, 501)
BROKEN_STATUSES = (404, 410)


class InternalLinkSentinel:
    def __init__(self, site_url: str):
        self.site_url = site_url.rstrip("/")
        self.domain = self.site_url.replace("https://", "").replace("http://", "").split("/")[0]

    def _resolve_url(self, session: requests.Session, url: str) -> tuple:
        """(url, status or None when unverified, Location)."""
        try:
            r = session.head(url, timeout=5, allow_redirects=False)
            if r.status_code in HEAD_UNRELIABLE:
                r = session.get(url, timeout=8, allow_redirects=False, stream=True)
                r.close()
            if is_refusal(r.status_code, internal=True):
                return (url, None, None)
            return (url, r.status_code, r.headers.get("Location"))
        except Exception:
            return (url, None, None)

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
                if not is_crawlable_href(href):
                    continue
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
                    if sc is None:  # refused / network error: unverified, never touch
                        report["unverified_links"] = report.get("unverified_links", 0) + 1
                        continue
                    clean_slug = href.strip("/").split("/")[-1].split("?")[0]

                    if sc in BROKEN_STATUSES:
                        report["broken_links_found"] += 1
                        if clean_slug in slug_to_link:
                            a["href"] = slug_to_link[clean_slug]
                            post_modified = True
                        else:
                            a.replace_with(a.text)
                            post_modified = True
                    elif sc in (301, 302, 307, 308) and loc and loc != full_url:
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
