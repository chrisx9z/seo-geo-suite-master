# -*- coding: utf-8 -*-
"""
Live-site junk audit & cleanup (uses the same rules as the pre-publish gate).

    python -m modules.content_quality_gate.audit_cli --site mmdidau            # report only
    python -m modules.content_quality_gate.audit_cli --site all --apply        # fix

--apply:
  * junk posts      -> moved to `draft` (reversible; never hard-deleted automatically)
  * stripped geo hallucination paragraphs -> content updated
  * bad slugs       -> renamed to short keyword slug (WordPress stores _wp_old_slug => 301)
Report is written to reports/quality_gate_<site>.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List

import requests
import urllib3

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE)
from modules.content_quality_gate.gate import check_post  # noqa: E402
from modules.wp_rest_auth import get_rest_nonce  # noqa: E402

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _load_sites() -> List[Dict[str, Any]]:
    for p in ("private/sites.local.json", "config/sites.json"):
        fp = os.path.join(BASE, p)
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8") as f:
                return json.load(f).get("sites", [])
    raise SystemExit("No sites config found (private/sites.local.json)")


def _login(site: Dict[str, Any]) -> requests.Session:
    s = requests.Session()
    s.verify = False
    s.headers.update({"User-Agent": "Mozilla/5.0 QualityGateAudit/1.0"})
    url = site["url"].rstrip("/")
    s.post(f"{url}/wp-login.php", data={"log": site.get("admin_user"),
           "pwd": site.get("admin_pass") or site.get("admin_password"), "wp-submit": "Log In"}, timeout=30)
    if not any(c.name.startswith("wordpress_logged_in") for c in s.cookies):
        raise RuntimeError(f"WP login failed for {url} (check admin_user/admin_pass in sites config)")
    r = s.get(f"{url}/wp-admin/post-new.php", timeout=30)
    m = re.search(r'"nonce":"([a-f0-9]+)"', r.text)
    nonce = get_rest_nonce(s, url) or (m.group(1) if m else "")
    if not nonce:
        raise RuntimeError(f"Login/nonce failed for {url}")
    s.headers["X-WP-Nonce"] = nonce
    return s


def _fetch_posts(s: requests.Session, url: str) -> List[Dict[str, Any]]:
    posts, page = [], 1
    while True:
        r = s.get(f"{url}/wp-json/wp/v2/posts", params={"context": "edit", "per_page": 100, "page": page,
                  "status": "publish,future", "_fields": "id,slug,status,title,content,meta"}, timeout=60)
        if r.status_code != 200 or not r.json():
            break
        posts.extend(r.json())
        if page >= int(r.headers.get("X-WP-TotalPages", 1)):
            break
        page += 1
    return posts


def audit_site(site: Dict[str, Any], apply: bool) -> Dict[str, Any]:
    url = site["url"].rstrip("/")
    s = _login(site)
    posts = _fetch_posts(s, url)
    report = {"site": url, "total": len(posts), "junk": [], "repaired": [], "slug_fixed": []}
    for p in posts:
        title = (p.get("title") or {}).get("raw", "")
        content = (p.get("content") or {}).get("raw", "")
        kw = (p.get("meta") or {}).get("rank_math_focus_keyword") or title
        res = check_post(title, content, keyword=kw, slug=p["slug"], destination=title)
        update: Dict[str, Any] = {}
        if not res.passed:
            report["junk"].append({"id": p["id"], "title": title, "slug": p["slug"], "issues": res.issues})
            update["status"] = "draft"
        else:
            if res.content != content:
                update["content"] = res.content
                report["repaired"].append({"id": p["id"], "title": title, "repairs": res.repairs})
            if res.slug and res.slug != p["slug"]:
                update["slug"] = res.slug
                report["slug_fixed"].append({"id": p["id"], "from": p["slug"], "to": res.slug})
        if apply and update:
            s.post(f"{url}/wp-json/wp/v2/posts/{p['id']}", json=update, timeout=60)
    print(f"[{url}] total={report['total']} junk={len(report['junk'])} "
          f"repaired={len(report['repaired'])} slug_fixed={len(report['slug_fixed'])} apply={apply}")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="all", help="site_id from sites config, or 'all'")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    sites = [x for x in _load_sites() if a.site in ("all", x.get("site_id"))]
    os.makedirs(os.path.join(BASE, "reports"), exist_ok=True)
    for site in sites:
        try:
            rep = audit_site(site, a.apply)
        except Exception as e:  # keep going on other sites
            print(f"[{site.get('url')}] ERROR: {e}")
            continue
        out = os.path.join(BASE, "reports", f"quality_gate_{site.get('site_id')}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(rep, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
