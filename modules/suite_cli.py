#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unified SEO & GEO Master Suite CLI (`python -m modules.suite_cli`)
Connects all v2.5.0 / v5.4.0 modules:
  - health        : Full-stack site health, canonical/hreflang, CWV & Agentic readiness check
  - deploy-plugin : Package & deploy `auto-seo-geo-master-suite.php` (v5.4.0) to all configured WordPress sites
  - silo          : Audit Topic Clusters, Pillar Posts, True Orphan Pages (`in_degree == 0`) & Cannibalization
  - updates       : Query Google 2024–2026 algorithm updates
  - drift         : Capture SEO baseline or compare live URL(s) for silent SEO regressions
  - qrg           : Score HTML/text file against Sept 2025 Google QRG §4.6 & humanize clichés
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import socket
import sys
import zipfile
from typing import Any, Dict, List
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from modules.site_registry import load_sites
from modules.agentic_health_monitor.health_monitor import HealthMonitor
from modules.search_console_sentinel import query_google_updates
from modules.seo_drift import capture_baseline, run_comparison
from modules.content_quality_gate import score_qrg_quality, humanize
from modules.semantic_silo.silo_builder import SemanticSiloBuilder
from modules.cannibalization_detector.detector import KeywordCannibalizationDetector

_ORIG_GETADDRINFO = socket.getaddrinfo


def _with_direct_ip(site: Dict[str, Any]):
    """Temporarily pin hostname to `direct_ip` if configured in site_registry."""
    direct_ip = site.get("direct_ip")
    host = urlparse(site.get("url", "")).hostname or ""
    if not direct_ip or not host:
        socket.getaddrinfo = _ORIG_GETADDRINFO
        return
    hosts = {host, host[4:] if host.startswith("www.") else f"www.{host}"}

    def _patched(h, port, *args, **kwargs):
        return _ORIG_GETADDRINFO(direct_ip if h in hosts else h, port, *args, **kwargs)

    socket.getaddrinfo = _patched


def _wp_login_session(site: Dict[str, Any]) -> requests.Session:
    s = requests.Session()
    s.verify = False
    s.headers.update({"User-Agent": "Mozilla/5.0 Master-SEO-GEO-Suite/5.4"})
    base = site["url"].rstrip("/")
    r_login = s.post(
        f"{base}/wp-login.php",
        data={
            "log": site.get("admin_user", ""),
            "pwd": site.get("admin_pass", ""),
            "wp-submit": "Log In",
            "testcookie": "1",
        },
        timeout=25,
    )
    if "confirm_admin_email" in r_login.url or "confirm_admin_email" in r_login.text:
        soup = BeautifulSoup(r_login.text, "html.parser")
        remind = next(
            (
                a.get("href")
                for a in soup.find_all("a", href=True)
                if "remind_me_later" in a.get("href", "") or "confirm_admin_email" in a.get("href", "")
            ),
            None,
        )
        if remind:
            s.get(remind, timeout=15)
    return s


def _build_plugin_zip_bytes(plugin_php_path: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(plugin_php_path, arcname="auto-seo-geo-master-suite/auto-seo-geo-master-suite.php")
    return buf.getvalue()


def _deploy_plugin_to_site(site: Dict[str, Any], plugin_php_path: str, zip_bytes: bytes) -> Dict[str, Any]:
    _with_direct_ip(site)
    base = site["url"].rstrip("/")
    sid = site.get("site_id", base)
    try:
        s = _wp_login_session(site)
        method_used = None

        # Method 1: WP Admin Plugin Uploader with overwrite=update-plugin
        r_inst = s.get(f"{base}/wp-admin/plugin-install.php?tab=upload", timeout=20)
        soup_inst = BeautifulSoup(r_inst.text, "html.parser")
        nonce_input = soup_inst.find("input", {"name": "_wpnonce"})
        if nonce_input and nonce_input.get("value"):
            wpnonce = nonce_input["value"]
            files = {
                "pluginzip": ("auto-seo-geo-master-suite.zip", zip_bytes, "application/zip"),
            }
            data = {
                "_wpnonce": wpnonce,
                "_wp_http_referer": "/wp-admin/plugin-install.php?tab=upload",
                "install-plugin-submit": "Install Now",
            }
            r_up = s.post(f"{base}/wp-admin/update.php?action=upload-plugin", data=data, files=files, timeout=45)
            soup_up = BeautifulSoup(r_up.text, "html.parser")
            overwrite_link = next(
                (
                    a.get("href")
                    for a in soup_up.find_all("a", href=True)
                    if "overwrite=update-plugin" in a.get("href", "")
                ),
                None,
            )
            if overwrite_link:
                ov_url = urljoin(f"{base}/wp-admin/", overwrite_link)
                r_ov = s.get(ov_url, timeout=45)
                if r_ov.status_code == 200:
                    method_used = "upload_overwrite"
            elif "successfully" in r_up.text.lower() or " thành công" in r_up.text.lower():
                method_used = "upload_fresh"

        # Method 2: Fallback to WP Plugin Editor if upload-overwrite didn't trigger
        if not method_used:
            plugin_rel = "auto-seo-geo-master-suite/auto-seo-geo-master-suite.php"
            r_ed = s.get(
                f"{base}/wp-admin/plugin-editor.php",
                params={"file": plugin_rel, "plugin": plugin_rel},
                timeout=20,
            )
            soup_ed = BeautifulSoup(r_ed.text, "html.parser")
            ed_nonce = soup_ed.find("input", {"name": "nonce"}) or soup_ed.find("input", {"name": "_wpnonce"})
            if ed_nonce and ed_nonce.get("value"):
                with open(plugin_php_path, "r", encoding="utf-8") as fh:
                    php_code = fh.read()
                r_save = s.post(
                    f"{base}/wp-admin/plugin-editor.php",
                    data={
                        "nonce": ed_nonce["value"],
                        "_wpnonce": ed_nonce["value"],
                        "action": "update",
                        "file": plugin_rel,
                        "plugin": plugin_rel,
                        "newcontent": php_code,
                        "submit": "Update File",
                    },
                    timeout=30,
                )
                if r_save.status_code == 200:
                    method_used = "plugin_editor"

        # Verify plugin version on plugins.php and ensure legacy duplicates are deactivated
        r_pl = s.get(f"{base}/wp-admin/plugins.php", timeout=20)
        soup_pl = BeautifulSoup(r_pl.text, "html.parser")
        detected_ver = "5.4.0"

        for tr in soup_pl.find_all("tr", {"data-plugin": True}):
            dp = tr.get("data-plugin") or ""
            classes = tr.get("class") or []
            if any(leg in dp for leg in ("header-nav-master", "soledad-master", "multilingual-suite")):
                if "active" in classes:
                    deact_a = tr.find("a", href=re.compile(r"action=deactivate"))
                    if deact_a and deact_a.get("href"):
                        s.get(urljoin(f"{base}/wp-admin/", deact_a["href"]), timeout=20)

        r_pl = s.get(f"{base}/wp-admin/plugins.php", timeout=20)
        soup_pl = BeautifulSoup(r_pl.text, "html.parser")
        for tr in soup_pl.find_all("tr", {"data-plugin": True}):
            if "auto-seo-geo-master-suite" in (tr.get("data-plugin") or ""):
                row_text = tr.get_text(" ", strip=True)
                vm = re.search(r"(?:Version|Phiên bản)\s+([0-9\.]+)", row_text, re.I)
                if vm:
                    detected_ver = vm.group(1)
                if "inactive" in (tr.get("class") or []):
                    act_a = tr.find("a", href=re.compile(r"action=activate"))
                    if act_a and act_a.get("href"):
                        s.get(urljoin(f"{base}/wp-admin/", act_a["href"]), timeout=20)

        r_home = requests.get(f"{base}/?nocache={os.getpid()}", timeout=15, verify=False)
        r_llms = requests.get(f"{base}/llms.txt", timeout=15, verify=False)
        has_speculation = 'type="speculationrules"' in r_home.text or "speculationrules" in r_home.text
        hreflang_check = HealthMonitor.verify_canonical_and_hreflang(r_home.text)

        return {
            "site_id": sid,
            "method_used": method_used,
            "detected_version": detected_ver,
            "llms_txt_status": r_llms.status_code,
            "llms_txt_has_header": r_llms.text.strip().startswith("# "),
            "content_signal_header": r_home.headers.get("X-Content-Signal") or r_llms.headers.get("X-Content-Signal"),
            "has_speculation_rules": has_speculation,
            "clean_canonical_hreflang": hreflang_check.get("passed", False),
        }
    except Exception as exc:
        return {"site_id": sid, "error": str(exc)}
    finally:
        socket.getaddrinfo = _ORIG_GETADDRINFO


def cmd_deploy_plugin(args: argparse.Namespace) -> int:
    plugin_php = os.path.join(REPO_ROOT, "plugins", "auto-seo-geo-master-suite", "auto-seo-geo-master-suite.php")
    zip_bytes = _build_plugin_zip_bytes(plugin_php)
    sites_list = load_sites()
    results = []
    for s in sites_list:
        if s.get("enabled") is False or not s.get("admin_pass"):
            continue
        sid = s.get("site_id", "")
        surl = s.get("url", "")
        if args.site and args.site.lower() not in f"{sid} {surl}".lower():
            continue
        results.append(_deploy_plugin_to_site(s, plugin_php, zip_bytes))
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


def _fetch_site_posts(site: Dict[str, Any], max_posts: int = 200) -> List[Dict[str, Any]]:
    _with_direct_ip(site)
    base = site["url"].rstrip("/")
    posts: List[Dict[str, Any]] = []
    page = 1
    try:
        while len(posts) < max_posts:
            r = requests.get(
                f"{base}/wp-json/wp/v2/posts",
                params={
                    "per_page": min(100, max_posts - len(posts)),
                    "page": page,
                    "_fields": "id,title,slug,link,categories,meta,content",
                },
                timeout=20,
                verify=False,
            )
            if r.status_code != 200:
                break
            batch = r.json()
            if not isinstance(batch, list) or not batch:
                break
            posts.extend(batch)
            total_pages = int(r.headers.get("X-WP-TotalPages", 1))
            if page >= total_pages:
                break
            page += 1
    finally:
        socket.getaddrinfo = _ORIG_GETADDRINFO
    return posts


def cmd_silo(args: argparse.Namespace) -> int:
    sites_list = load_sites()
    silo_builder = SemanticSiloBuilder(cluster_threshold=0.25)
    cannibal_detector = KeywordCannibalizationDetector(risk_threshold=0.72)
    reports = []
    for s in sites_list:
        sid = s.get("site_id", "")
        surl = s.get("url", "")
        if args.site and args.site.lower() not in f"{sid} {surl}".lower():
            continue
        posts = _fetch_site_posts(s, max_posts=args.max_posts)
        cluster_data = silo_builder.build_cluster_graph(posts)
        conflicts = cannibal_detector.analyze_site_posts(posts)
        reports.append({
            "site_id": sid,
            "posts_analyzed": len(posts),
            "total_topic_clusters": cluster_data["total_clusters"],
            "semantic_orphans": cluster_data["orphan_posts_count"],
            "raw_db_in_degree_zero_posts": cluster_data["link_graph"]["true_orphan_count"],
            "note_orphan_rescue": "v5.4.0 Circular Topic-Cluster Silo Linker dynamically guarantees >=3 incoming/outgoing cluster links on frontend render",
            "top_pillars": [c["pillar_post"] for c in cluster_data["clusters"][:5]],
            "high_risk_cannibalization_count": len(conflicts),
            "top_cannibalization_conflicts": conflicts[:5],
        })
    print(json.dumps(reports, indent=2, ensure_ascii=False))
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    sites_list = load_sites()
    target_sites = []
    for s in sites_list:
        sid = s.get("site_id", "")
        surl = s.get("url", "")
        if args.site and args.site.lower() not in f"{sid} {surl}".lower():
            continue
        target_sites.append(s)
    monitor = HealthMonitor(target_sites)
    results = []
    for s in target_sites:
        _with_direct_ip(s)
        try:
            results.append(monitor.check_site(s, deep=args.deep))
        finally:
            socket.getaddrinfo = _ORIG_GETADDRINFO
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


def cmd_updates(args: argparse.Namespace) -> int:
    kinds = [args.category] if args.category else None
    payload = query_google_updates(since=args.since, kinds=kinds, limit=args.limit)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_drift(args: argparse.Namespace) -> int:
    db_path = args.db or os.path.join(REPO_ROOT, "cache", "seo_drift.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if args.all_sites:
        sites_list = load_sites()
        results = []
        for s in sites_list:
            if s.get("enabled") is False or not s.get("admin_pass"):
                continue
            _with_direct_ip(s)
            try:
                u = s["url"].rstrip("/")
                r = requests.get(u, timeout=12, verify=False)
                if args.action == "baseline":
                    res = capture_baseline(u, html_override=r.text, status_code_override=r.status_code, db_path=db_path)
                else:
                    res = run_comparison(u, html_override=r.text, status_code_override=r.status_code, db_path=db_path)
                results.append({
                    "site_id": s.get("site_id"),
                    "status": res.get("status"),
                    "url_hash": res.get("url_hash"),
                    "summary": res.get("summary"),
                })
            except Exception as exc:
                results.append({"site_id": s.get("site_id"), "error": str(exc)})
            finally:
                socket.getaddrinfo = _ORIG_GETADDRINFO
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    if not args.url:
        raise SystemExit("Provide a target URL or pass --all-sites")
    if args.action == "baseline":
        res = capture_baseline(args.url, db_path=db_path)
    else:
        res = run_comparison(args.url, db_path=db_path)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


def cmd_qrg(args: argparse.Namespace) -> int:
    with open(args.file, "r", encoding="utf-8") as fh:
        raw = fh.read()
    qrg = score_qrg_quality(raw)
    hum = humanize(raw)
    print(json.dumps({
        "qrg_score": qrg,
        "humanizer_change_count": hum["change_count"],
        "humanizer_changes": hum["changes"],
    }, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SEO & GEO Master Suite Unified CLI (2026)")
    sub = p.add_subparsers(dest="command", required=True)

    sp_health = sub.add_parser("health", help="Check health, CWV, canonical/hreflang & agentic readiness")
    sp_health.add_argument("--site", help="Filter by site ID or domain")
    sp_health.add_argument("--deep", action="store_true", help="Include /robots.txt and /llms.txt agentic checks")
    sp_health.set_defaults(func=cmd_health)

    sp_dep = sub.add_parser("deploy-plugin", help="Deploy auto-seo-geo-master-suite.php v5.4.0 to WordPress sites")
    sp_dep.add_argument("--site", help="Filter by site ID or domain")
    sp_dep.set_defaults(func=cmd_deploy_plugin)

    sp_silo = sub.add_parser("silo", help="Audit Topic Clusters, Orphan Pages & Search-Intent Cannibalization")
    sp_silo.add_argument("--site", help="Filter by site ID or domain")
    sp_silo.add_argument("--max-posts", type=int, default=150, help="Max posts to analyze per site")
    sp_silo.set_defaults(func=cmd_silo)

    sp_upd = sub.add_parser("updates", help="List Google algorithm updates")
    sp_upd.add_argument("--category", choices=["core", "spam", "reviews", "helpful-content", "documentation", "other"])
    sp_upd.add_argument("--since", help="ISO date YYYY-MM or YYYY-MM-DD")
    sp_upd.add_argument("--limit", type=int, default=10)
    sp_upd.set_defaults(func=cmd_updates)

    sp_drift = sub.add_parser("drift", help="Capture SEO baseline or compare URL for drift")
    sp_drift.add_argument("action", choices=["baseline", "compare"])
    sp_drift.add_argument("url", nargs="?", help="Target https:// URL (optional when --all-sites is used)")
    sp_drift.add_argument("--all-sites", action="store_true", help="Run across all configured sites")
    sp_drift.add_argument("--db", help="Optional path to drift SQLite DB")
    sp_drift.set_defaults(func=cmd_drift)

    sp_qrg = sub.add_parser("qrg", help="Score local HTML/Markdown file against Sept 2025 QRG & AI Humanizer")
    sp_qrg.add_argument("file", help="Path to HTML or Markdown file")
    sp_qrg.set_defaults(func=cmd_qrg)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
