# -*- coding: utf-8 -*-
"""
Master Network 10-Posts/Day Scheduler for Auto SEO GEO Suite
Orchestrates automated 10 posts/day scheduling across all network sites:
- vibemmo.net (300 posts: AI Agent, SaaS, Automation)
- mmdidau.com (300 posts: Vietnam Travel & Food)
- tobeigo.com (300 posts: Domestic & International Travel)
- triptip.cc  (300 posts: English Vietnam Travel Guides)
- zenshan.net (300 posts: Health, Nutrition & Mindfulness)
- nhatthegioi.com (300 posts: World Records & Top Lists)
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)

from cli.master_seo import load_config, get_site_session
from modules.travel_scheduler.travel_batch_scheduler import TravelBatchScheduler
from modules.travel_scheduler.vibe_batch_scheduler import VibeBatchScheduler
from modules.travel_scheduler.english_batch_scheduler import EnglishBatchScheduler
from modules.travel_scheduler.nhatthegioi_batch_scheduler import NhatTheGioiBatchScheduler

SITE_SCHEDULER_REGISTRY = {
    "vibemmo": {
        "scheduler_cls": VibeBatchScheduler,
        "plan_file": os.path.join(BASE_DIR, "config", "vibemmo_30day_content_plan.json"),
        "cache_file": os.path.join(BASE_DIR, "cache", "scheduled_vibemmo_net.json"),
        "theme": "AI Agent & SaaS Automation (10 posts/day)"
    },
    "mmdidau": {
        "scheduler_cls": TravelBatchScheduler,
        "plan_file": os.path.join(BASE_DIR, "docs", "MMDIDAU_30DAY_CONTENT_PLAN.json"),
        "cache_file": os.path.join(BASE_DIR, "cache", "scheduled_mmdidau_com.json"),
        "theme": "Du Lịch & Ẩm Thực Việt Nam (10 posts/day)"
    },
    "tobeigo": {
        "scheduler_cls": TravelBatchScheduler,
        "plan_file": os.path.join(BASE_DIR, "docs", "TOBEIGO_30DAY_CONTENT_PLAN.json"),
        "cache_file": os.path.join(BASE_DIR, "cache", "scheduled_tobeigo_com.json"),
        "theme": "Cẩm Nang Du Lịch Trong & Ngoài Nước (10 posts/day)"
    },
    "triptip": {
        "scheduler_cls": EnglishBatchScheduler,
        "plan_file": os.path.join(BASE_DIR, "config", "triptip_30day_content_plan.json"),
        "cache_file": os.path.join(BASE_DIR, "cache", "scheduled_triptip_cc.json"),
        "theme": "English Vietnam Travel Guides (10 posts/day)"
    },
    "zenshan": {
        "scheduler_cls": TravelBatchScheduler,
        "plan_file": os.path.join(BASE_DIR, "config", "zenshan_30day_content_plan.json"),
        "cache_file": os.path.join(BASE_DIR, "cache", "scheduled_zenshan_net.json"),
        "theme": "Sống Khỏe, Dinh Dưỡng & Thiền Định (10 posts/day)"
    },
    "nhatthegioi": {
        "scheduler_cls": NhatTheGioiBatchScheduler,
        "plan_file": os.path.join(BASE_DIR, "config", "nhatthegioi_30day_content_plan.json"),
        "cache_file": os.path.join(BASE_DIR, "cache", "scheduled_nhatthegioi_com.json"),
        "theme": "Top List Kỷ Lục Thú Vị Thế Giới (10 posts/day)"
    }
}

class NetworkSchedulerManager:
    def __init__(self):
        self.config = load_config()
        self.sites = self.config.get("sites", [])

    def get_site_conf(self, site_id: str) -> Optional[Dict[str, Any]]:
        for s in self.sites:
            if s.get("site_id") == site_id:
                return s
        return None

    def get_status_overview(self) -> List[Dict[str, Any]]:
        overview = []
        for site_id, meta in SITE_SCHEDULER_REGISTRY.items():
            site_conf = self.get_site_conf(site_id)
            plan_exists = os.path.exists(meta["plan_file"])
            plan_count = 0
            if plan_exists:
                try:
                    with open(meta["plan_file"], "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        plan_count = sum(len(d.get("posts", [])) for d in data)
                    elif isinstance(data, dict):
                        plan_count = sum(len(c.get("items", [])) for c in data.get("clusters", []))
                except Exception:
                    plan_count = 0

            scheduled_count = 0
            if os.path.exists(meta["cache_file"]):
                try:
                    with open(meta["cache_file"], "r", encoding="utf-8") as f:
                        cdata = json.load(f)
                    scheduled_count = len(cdata.get("scheduled_posts", []))
                except Exception:
                    scheduled_count = 0

            overview.append({
                "site_id": site_id,
                "url": site_conf.get("url") if site_conf else f"https://{site_id}.com",
                "configured": site_conf is not None,
                "plan_file": os.path.basename(meta["plan_file"]),
                "total_planned": plan_count,
                "scheduled_in_cache": scheduled_count,
                "theme": meta["theme"]
            })
        return overview

    def run_site(self, site_id: str, target_days: Optional[List[int]] = None, max_posts: Optional[int] = None):
        if site_id not in SITE_SCHEDULER_REGISTRY:
            print(f"[-] Unknown site_id: {site_id}")
            return False

        meta = SITE_SCHEDULER_REGISTRY[site_id]
        site_conf = self.get_site_conf(site_id)
        if not site_conf:
            print(f"[-] Site {site_id} is not configured in sites configuration.")
            return False

        admin_user = site_conf.get("admin_user", os.getenv("WP_ADMIN_USER", "admin"))
        admin_pass = site_conf.get("admin_pass") or site_conf.get("admin_password") or os.getenv("WP_ADMIN_PASSWORD", "")

        scheduler_cls = meta["scheduler_cls"]
        plan_file = meta["plan_file"]

        if not os.path.exists(plan_file):
            print(f"[-] Plan file not found: {plan_file}")
            return False

        print(f"\n========================================================")
        print(f" LAUNCHING SCHEDULER FOR: {site_id.upper()} ({site_conf['url']})")
        print(f" Theme: {meta['theme']}")
        print(f" Plan: {plan_file}")
        print(f"========================================================")

        try:
            scheduler = scheduler_cls(
                wp_url=site_conf["url"],
                admin_user=admin_user,
                admin_pass=admin_pass,
                plan_file=plan_file
            )
            scheduler.run_batch(target_days=target_days, max_posts=max_posts)
            return True
        except Exception as e:
            print(f"[-] Execution error on {site_id}: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Master Network 10-Posts/Day Scheduler")
    parser.add_argument("--site", choices=list(SITE_SCHEDULER_REGISTRY.keys()) + ["all"], default="all", help="Target site ID or 'all'")
    parser.add_argument("--days", help="Day number or range (e.g. 1, 1-3, all)")
    parser.add_argument("--max-posts", type=int, default=None, help="Max posts to schedule per site in this run")
    parser.add_argument("--status", action="store_true", help="Print status overview table and exit")
    args = parser.parse_args()

    mgr = NetworkSchedulerManager()

    if args.status or (args.site == "all" and not args.days and not args.max_posts):
        print(f"\n{'='*95}")
        print(f" 🚀 MASTER AUTO SEO GEO SUITE — 10 POSTS/DAY NETWORK STATUS OVERVIEW")
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
