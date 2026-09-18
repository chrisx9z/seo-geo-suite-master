# -*- coding: utf-8 -*-
"""
VibeBatchScheduler - Automated Content Scheduler for VibeMMO.net
Enforces:
- 30-Day Content Plan across 5 Categories (AI, SaaS, MMO, Tools, Tech)
- 5 Articles per Day staggered at prime reading hours (08:00, 11:00, 14:00, 17:00, 20:00)
- Ultra-compressed WebP Featured Banner & Technical Diagram (< 50KB)
- RankMath 100/100 Standards (> 1,200 words, FAQ Schema, TOC, Outbound citations)
- Status: "future" for scheduled release
"""

import os
import sys
import json
import time
import re
from datetime import datetime, timedelta
import requests
from typing import Dict, Any, List, Optional

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from modules.wp_ai_autopilot.autopilot_orchestrator import WpAiAutopilot
from modules.content_crawler_pipeline.slug_optimizer import SlugOptimizer

HOURLY_STAGGERS = [
    "08:00:00", "11:00:00", "14:00:00", "17:00:00", "20:00:00"
]

class VibeBatchScheduler:
    def __init__(self, wp_url: str, admin_user: str, admin_pass: str, plan_file: Optional[str] = None, log_file: Optional[str] = None):
        self.wp_url = wp_url.rstrip("/")
        self.admin_user = admin_user
        self.admin_pass = admin_pass
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.plan_file = plan_file or os.path.join(base_dir, "config", "vibemmo_30day_content_plan.json")
        if not os.path.exists(self.plan_file):
            self.plan_file = os.path.join(base_dir, "docs", "VIBEMMO_30DAY_CONTENT_PLAN.json")

        self.log_file = log_file or os.path.join(base_dir, "cache", "scheduled_vibemmo_net.json")
        
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VibeBatchScheduler/1.0"})
        self.nonce = ""
        self._authenticate()

        self.autopilot = WpAiAutopilot(wp_url=self.wp_url, admin_user=self.admin_user, admin_pass=self.admin_pass)
        self.scheduled_log = self._load_log()

    def _load_log(self) -> Dict[str, Any]:
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"scheduled_posts": [], "total_scheduled": 0}

    def _save_log(self):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.scheduled_log, f, ensure_ascii=False, indent=2)

    def _authenticate(self):
        print(f"[*] Authenticating to {self.wp_url} as {self.admin_user}...")
        try:
            self.session.post(
                f"{self.wp_url}/wp-login.php",
                data={"log": self.admin_user, "pwd": self.admin_pass, "wp-submit": "Log In"},
                timeout=25
            )
            r_admin = self.session.get(f"{self.wp_url}/wp-admin/edit.php", timeout=25)
            m = re.search(r'"nonce":"([a-f0-9]+)"', r_admin.text)
            self.nonce = m.group(1) if m else ""
            if self.nonce:
                print(f"  [+] Authenticated successfully. Nonce: {self.nonce}")
            else:
                print(f"  [!] Warning: Nonce extraction failed for {self.wp_url}")
        except Exception as e:
            print(f"  [!] Auth exception: {e}")

    def post_exists(self, slug: str) -> bool:
        for p in self.scheduled_log.get("scheduled_posts", []):
            if p.get("slug") == slug:
                return True
        try:
            headers = {"X-WP-Nonce": self.nonce} if self.nonce else {}
            r = self.session.get(f"{self.wp_url}/wp-json/wp/v2/posts?slug={slug}&status=any", headers=headers, timeout=10)
            if r.status_code == 200 and len(r.json()) > 0:
                return True
        except Exception:
            pass
        return False

    def schedule_single_post(self, topic: str, slug: str, category_id: int, schedule_date: str, day_num: int, cluster_name: str) -> Optional[Dict[str, Any]]:
        if self.post_exists(slug):
            print(f"  [SKIP] Post '{slug}' already scheduled or exists.")
            return None

        print(f"\n---> [Day {day_num}] Processing: {topic}")
        print(f"     Slug: {slug} | Date: {schedule_date} | Category ID: {category_id}")

        res = self.autopilot.produce_and_publish(
            topic=topic,
            category_ids=[category_id],
            status="future",
            schedule_date=schedule_date
        )

        if res.get("status") == "success":
            record = {
                "id": res.get("post_id"),
                "title": res.get("title", topic),
                "slug": res.get("slug", slug),
                "keyword": res.get("focus_keyword", ""),
                "schedule_date": schedule_date,
                "day": day_num,
                "link": res.get("link", ""),
                "word_count": res.get("words", 0),
                "status": "future",
                "cluster": cluster_name,
                "category_id": category_id
            }
            self.scheduled_log["scheduled_posts"].append(record)
            self.scheduled_log["total_scheduled"] = len(self.scheduled_log["scheduled_posts"])
            self._save_log()
            print(f"     SUCCESS: Scheduled Post ID {record['id']} -> {record['link']}")
            return record
        else:
            print(f"     FAILED: {res.get('message', 'Unknown error')}")
            return None

    def run_batch(self, target_days: Optional[List[int]] = None, max_posts: Optional[int] = None):
        with open(self.plan_file, "r", encoding="utf-8") as f:
            plan_data = json.load(f)

        clusters = plan_data.get("clusters", [])
        base_date = datetime(2026, 9, 21)  # Starting from 2026-09-21

        total_processed = 0
        print(f"\n========================================================")
        print(f" STARTING VIBEMMO BATCH SCHEDULER FOR: {self.wp_url}")
        print(f" Plan File: {self.plan_file}")
        print(f" Total Clusters: {len(clusters)} days planned")
        print(f"========================================================")

        for c in clusters:
            day_num = c["day"]
            if target_days and day_num not in target_days:
                continue

            day_date = base_date + timedelta(days=day_num - 1)
            date_str = day_date.strftime("%Y-%m-%d")
            cluster_name = c["cluster_name"]
            pillar = c.get("pillar", "")
            cat_id = c.get("category_id", 4)

            print(f"\n========================================================")
            print(f" SCHEDULING VIBEMMO DAY {day_num:02d} ({date_str})")
            print(f" Pillar: {pillar} | Cluster: {cluster_name}")
            print(f" Category ID: {cat_id}")
            print(f"========================================================")

            for idx, item in enumerate(c["items"]):
                if max_posts and total_processed >= max_posts:
                    print(f"\n[*] Reached max_posts limit ({max_posts}). Stopping.")
                    return

                topic, slug, intent, lsi = item
                stagger_time = HOURLY_STAGGERS[idx % len(HOURLY_STAGGERS)]
                schedule_datetime_iso = f"{date_str}T{stagger_time}"

                res = self.schedule_single_post(
                    topic=topic,
                    slug=slug,
                    category_id=cat_id,
                    schedule_date=schedule_datetime_iso,
                    day_num=day_num,
                    cluster_name=cluster_name
                )
                if res:
                    total_processed += 1
                    time.sleep(2)

        print(f"\n========================================================")
        print(f" VIBEMMO BATCH COMPLETED! Total posts scheduled: {total_processed}")
        print(f" Lifetime scheduled: {self.scheduled_log['total_scheduled']} posts.")
        print(f" Log saved at: {self.log_file}")
        print(f"========================================================")
