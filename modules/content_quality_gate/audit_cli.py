# -*- coding: utf-8 -*-
"""
Live-site junk audit & cleanup (uses the same rules as the pre-publish gate).

    python -m modules.content_quality_gate.audit_cli --site <site_id>          # report only
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
import time
from typing import Any, Dict, List

import requests
import urllib3

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE)
from modules.content_quality_gate.gate import check_post  # noqa: E402
from modules.content_quality_gate.spin import template_spin_ratios, SpinCorpus, SPIN_JUNK_RATIO  # noqa: E402
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


# Issues that mean "the body does not explain the title/keyword" -> post is junk (draft).
MISMATCH_ISSUES = ("off_topic_body", "boilerplate_template", "political_content", "thin_content",
                   "duplicate_sentences")
# Formatting issues on an otherwise on-topic post -> report as needs_fix, never draft.
STRUCTURAL_ISSUES = ("keyword_absent_from_headings", "no_headings", "top_list_unfulfilled", "placeholder_image")


def audit_site(site: Dict[str, Any], apply: bool, scope=frozenset({"junk", "repair", "slug"}), ids=None) -> Dict[str, Any]:
    url = site["url"].rstrip("/")
    s = _login(site)
    posts = _fetch_posts(s, url)
    spin = template_spin_ratios(posts)
    corpus = SpinCorpus(url)  # seed the pre-publish spin check with every post on the site
    corpus.seed(posts)
    corpus.save()
    report = {"site": url, "total": len(posts), "junk": [], "templated_spin": [], "needs_fix": [],
              "repaired": [], "slug_fixed": []}
    for p in posts:
        title = (p.get("title") or {}).get("raw", "")
        content = (p.get("content") or {}).get("raw", "")
        kw = (p.get("meta") or {}).get("rank_math_focus_keyword") or title
        res = check_post(title, content, keyword=kw, slug=p["slug"], destination=title)
        issues = list(res.issues)
        ratio = round(spin.get(p["id"], 0.0), 2)
        if ratio >= SPIN_JUNK_RATIO:
            issues.append(f"templated_spin:{ratio:.0%}")
        entry = {"id": p["id"], "title": title, "slug": p["slug"], "issues": issues, "spin": ratio}
        update: Dict[str, Any] = {}
        mismatch = [i for i in issues if i.split(":")[0] in MISMATCH_ISSUES]
        if mismatch:
            report["junk"].append(entry)
            update["status"] = "draft"
        elif ratio >= SPIN_JUNK_RATIO:
            report["templated_spin"].append(entry)
            if "spin" in scope:
                update["status"] = "draft"
        elif issues:
            report["needs_fix"].append(entry)
        if "status" not in update:
            if res.content != content:
                update["content"] = res.content
                report["repaired"].append({"id": p["id"], "title": title, "repairs": res.repairs})
            if res.slug and res.slug != p["slug"]:
                update["slug"] = res.slug
                report["slug_fixed"].append({"id": p["id"], "from": p["slug"], "to": res.slug})
        if apply and update:
            update = {k: v for k, v in update.items()
                      if (k == "status" and scope & {"junk", "spin"}) or (k == "content" and "repair" in scope)
                      or (k == "slug" and "slug" in scope)}
            if update and (ids is None or p["id"] in ids):
                r = s.post(f"{url}/wp-json/wp/v2/posts/{p['id']}", json=update, timeout=60)
                report.setdefault("applied", []).append({"id": p["id"], "fields": list(update), "http": r.status_code})
    applied = report.get("applied", [])
    print(f"[{url}] total={report['total']} junk={len(report['junk'])} templated_spin={len(report['templated_spin'])} "
          f"needs_fix={len(report['needs_fix'])} repaired={len(report['repaired'])} "
          f"slug_fixed={len(report['slug_fixed'])} apply={apply} "
          f"applied_ok={sum(1 for x in applied if x['http'] == 200)}/{len(applied)}")
    return report


def restore(site: Dict[str, Any], report_path: str) -> None:
    """Undo: republish every post that a previous --apply run moved to draft."""
    with open(report_path, encoding="utf-8") as f:
        rep = json.load(f)
    url = site["url"].rstrip("/")
    s = _login(site)
    ids = [a["id"] for a in rep.get("applied", []) if "status" in a.get("fields", [])]
    ok = sum(1 for pid in ids
             if s.post(f"{url}/wp-json/wp/v2/posts/{pid}", json={"status": "publish"}, timeout=60).status_code == 200)
    print(f"[{url}] restored {ok}/{len(ids)} posts to publish")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="all", help="site_id from sites config, or 'all'")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--scope", default="junk,repair,slug",
                    help="what --apply changes: junk (title/content mismatch -> draft), spin (templated "
                         "spin -> draft), repair (strip hallucinated/political paragraphs), slug")
    ap.add_argument("--ids", default=None, help="optional comma list of post IDs allowed to change (reviewed list)")
    ap.add_argument("--restore", default=None, help="path of a *_applied_*.json report to undo (republish drafts)")
    a = ap.parse_args()
    scope = {x.strip() for x in a.scope.split(",") if x.strip()}
    ids = {int(x) for x in a.ids.split(",") if x.strip()} if a.ids else None
    sites = [x for x in _load_sites() if a.site in ("all", x.get("site_id"))]
    if a.restore:
        for site in sites:
            restore(site, a.restore)
        return
    os.makedirs(os.path.join(BASE, "reports"), exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    for site in sites:
        try:
            rep = audit_site(site, a.apply, scope, ids)
        except Exception as e:  # keep going on other sites
            print(f"[{site.get('url')}] ERROR: {e}")
            continue
        suffix = f"_applied_{stamp}" if a.apply else ""
        out = os.path.join(BASE, "reports", f"quality_gate_{site.get('site_id')}{suffix}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(rep, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
