# -*- coding: utf-8 -*-
"""
Master Network 10-Posts/Day Scheduler for Auto SEO GEO Suite.

Orchestrates scheduled publishing across every site listed in the gitignored
`private/sites.local.json`. Per-site scheduler type, plan file and cache file are read
from that config (see modules/site_registry.py) - no site is hard-coded in the repo.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)

from modules.site_registry import load_sites, plan_path, cache_path, build_scheduler  # noqa: E402

# site_id -> site config (from private config only)
SITE_SCHEDULER_REGISTRY: Dict[str, Dict[str, Any]] = {
    s["site_id"]: s for s in load_sites() if s.get("site_id")
}


def _count_plan(path: str) -> int:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0
    if isinstance(data, list):
        return sum(len(d.get("posts", [])) for d in data)
    if isinstance(data, dict):
        return sum(len(c.get("items", [])) for c in data.get("clusters", []))
    return 0


class NetworkSchedulerManager:
    def __init__(self):
        self.sites = list(SITE_SCHEDULER_REGISTRY.values())

    def get_site_conf(self, site_id: str) -> Optional[Dict[str, Any]]:
        return SITE_SCHEDULER_REGISTRY.get(site_id)

    def get_status_overview(self) -> List[Dict[str, Any]]:
        overview = []
        for site_id, site in SITE_SCHEDULER_REGISTRY.items():
            plan, cache = plan_path(site), cache_path(site)
            scheduled = 0
            if os.path.exists(cache):
                try:
                    with open(cache, "r", encoding="utf-8") as f:
                        scheduled = len(json.load(f).get("scheduled_posts", []))
                except Exception:
                    scheduled = 0
            overview.append({
                "site_id": site_id,
                "url": site.get("url", ""),
                "configured": True,
                "plan_file": os.path.basename(plan),
                "total_planned": _count_plan(plan),
                "scheduled_in_cache": scheduled,
                "theme": site.get("theme", ""),
            })
        return overview

    def run_site(self, site_id: str, target_days: Optional[List[int]] = None, max_posts: Optional[int] = None):
        site = self.get_site_conf(site_id)
        if not site:
            print(f"[-] Site {site_id} is not configured in private/sites.local.json.")
            return False
        plan = plan_path(site)
        if not os.path.exists(plan):
            print(f"[-] Plan file not found: {plan}")
            return False

        print("\n========================================================")
        print(f" LAUNCHING SCHEDULER FOR: {site_id.upper()} ({site['url']})")
        print(f" Scheduler: {site.get('scheduler', 'travel')}  Theme: {site.get('theme', '')}")
        print(f" Plan: {plan}")
        print("========================================================")
        try:
            build_scheduler(site, plan_file=plan).run_batch(target_days=target_days, max_posts=max_posts)
            return True
        except Exception as e:
            print(f"[-] Execution error on {site_id}: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Master Network 10-Posts/Day Scheduler")
    parser.add_argument("--site", choices=list(SITE_SCHEDULER_REGISTRY.keys()) + ["all"], default="all",
                        help="Target site ID or 'all'")
    parser.add_argument("--days", help="Day number or range (e.g. 1, 1-3, all)")
    parser.add_argument("--max-posts", type=int, default=None, help="Max posts to schedule per site in this run")
    parser.add_argument("--status", action="store_true", help="Print status overview table and exit")
    args = parser.parse_args()

    mgr = NetworkSchedulerManager()

    if args.status or (args.site == "all" and not args.days and not args.max_posts):
        print(f"\n{'='*95}")
        print(" MASTER AUTO SEO GEO SUITE - 10 POSTS/DAY NETWORK STATUS OVERVIEW")
        print(f"{'='*95}")
        print(f"{'Site ID':12} | {'URL':24} | {'Plan File':32} | {'Planned':7} | {'Scheduled':9}")
        print(f"{'-'*12}-+-{'-'*24}-+-{'-'*32}-+-{'-'*7}-+-{'-'*9}")
        for s in mgr.get_status_overview():
            print(f"{s['site_id']:12} | {s['url']:24} | {s['plan_file']:32} | {s['total_planned']:7} | {s['scheduled_in_cache']:9}")
        print(f"{'='*95}\n")
        if args.status:
            return

    target_days = None
    if args.days and args.days.lower() != "all":
        if "-" in str(args.days):
            start, end = str(args.days).split("-")
            target_days = list(range(int(start), int(end) + 1))
        elif "," in str(args.days):
            target_days = [int(x.strip()) for x in str(args.days).split(",")]
        else:
            target_days = [int(args.days)]

    sites_to_run = list(SITE_SCHEDULER_REGISTRY.keys()) if args.site == "all" else [args.site]
    for sid in sites_to_run:
        mgr.run_site(sid, target_days=target_days, max_posts=args.max_posts)


if __name__ == "__main__":
    main()
