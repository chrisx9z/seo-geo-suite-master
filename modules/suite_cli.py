#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unified SEO & GEO Master Suite CLI (`python -m modules.suite_cli`)
Connects all v2.5.0 / v5.4.0 modules:
  - health   : Full-stack site health, canonical/hreflang, CWV & Agentic readiness check
  - updates  : Query Google 2024–2026 algorithm updates
  - drift    : Capture SEO baseline or compare live URL for silent SEO regressions
  - qrg      : Score HTML/text file against Sept 2025 Google QRG §4.6 & humanize clichés
"""
from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from modules.site_registry import load_sites
from modules.agentic_health_monitor.health_monitor import HealthMonitor
from modules.search_console_sentinel import query_google_updates
from modules.seo_drift import capture_baseline, run_comparison
from modules.content_quality_gate import score_qrg_quality, humanize


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
    results = [monitor.check_site(s, deep=args.deep) for s in target_sites]
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


def cmd_updates(args: argparse.Namespace) -> int:
    kinds = [args.category] if args.category else None
    payload = query_google_updates(since=args.since, kinds=kinds, limit=args.limit)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_drift(args: argparse.Namespace) -> int:
    if args.action == "baseline":
        res = capture_baseline(args.url, db_path=args.db)
    else:
        res = run_comparison(args.url, db_path=args.db)
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

    sp_upd = sub.add_parser("updates", help="List Google algorithm updates")
    sp_upd.add_argument("--category", choices=["core", "spam", "reviews", "helpful-content", "documentation", "other"])
    sp_upd.add_argument("--since", help="ISO date YYYY-MM or YYYY-MM-DD")
    sp_upd.add_argument("--limit", type=int, default=10)
    sp_upd.set_defaults(func=cmd_updates)

    sp_drift = sub.add_parser("drift", help="Capture SEO baseline or compare URL for drift")
    sp_drift.add_argument("action", choices=["baseline", "compare"])
    sp_drift.add_argument("url", help="Target https:// URL")
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
