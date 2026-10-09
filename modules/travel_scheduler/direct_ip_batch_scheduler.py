# -*- coding: utf-8 -*-
"""
DirectIPBatchScheduler - content scheduler for sites whose public DNS points to a proxy/CDN
and must be reached on the origin server directly.

Enforces:
- Optional direct-origin routing: pass `direct_ip` (from private/sites.local.json) to pin the
  site's hostname to that IP for this process only
- Bypass WordPress admin email confirmation screen
- Top-list / record / curiosity content via WpAiAutopilot
- 5 articles per day staggered at prime reading hours (08:00, 11:30, 14:30, 17:30, 20:00)
- Status "future" for scheduled release
"""

import os
import sys
import json
import time
import re
import socket
from urllib.parse import urlparse
from datetime import datetime, timedelta
import requests
import urllib3
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

_orig_getaddrinfo = socket.getaddrinfo


def pin_host_to_ip(host: str, ip: str) -> None:
    """Resolve `host` (and www.`host`) to `ip` for this process (origin bypass of proxy DNS)."""
    hosts = {host, host[4:] if host.startswith("www.") else f"www.{host}"}

    def _patched(h, port, *args, **kwargs):
        return _orig_getaddrinfo(ip if h in hosts else h, port, *args, **kwargs)

    socket.getaddrinfo = _patched

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from modules.wp_rest_auth import get_rest_nonce  # noqa: E402
from modules.wp_ai_autopilot.autopilot_orchestrator import WpAiAutopilot
from modules.content_crawler_pipeline.slug_optimizer import generate_core_keyword_slug

HOURLY_STAGGERS = [
    "08:00:00", "11:30:00", "14:30:00", "17:30:00", "20:00:00"
]

class DirectIPBatchScheduler:
    def __init__(self, wp_url: str, admin_user: Optional[str] = None, admin_pass: Optional[str] = None, plan_file: Optional[str] = None, log_file: Optional[str] = None, direct_ip: Optional[str] = None):
        self.wp_url = wp_url.rstrip("/")
        self.direct_ip = direct_ip or os.environ.get("WP_DIRECT_IP", "")
        if self.direct_ip:
            pin_host_to_ip(urlparse(self.wp_url).hostname or "", self.direct_ip)
        self.admin_user = admin_user or os.environ.get("WP_ADMIN_USER", "")
        self.admin_pass = admin_pass or os.environ.get("WP_ADMIN_PASS", "")
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.plan_file = plan_file or os.path.join(base_dir, "private", "plans", f"{urlparse(self.wp_url).hostname}.json")
        self.log_file = log_file or os.path.join(base_dir, "cache", f"scheduled_{(urlparse(self.wp_url).hostname or 'site').replace('.', '_')}.json")
        
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DirectIPBatchScheduler/1.0"})
        self.nonce = ""
        self._authenticate()

        self.autopilot = WpAiAutopilot(wp_url=self.wp_url, admin_user=self.admin_user, admin_pass=self.admin_pass)
        self.autopilot.session = self.session
        self.autopilot.nonce = self.nonce
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
            r_login = self.session.post(
                f"{self.wp_url}/wp-login.php",
                data={"log": self.admin_user, "pwd": self.admin_pass, "wp-submit": "Log In"},
                timeout=30,
                verify=False
            )
            # Handle admin email confirmation if prompted
            if "confirm_admin_email" in r_login.url or "confirm_admin_email" in r_login.text:
                soup = BeautifulSoup(r_login.text, "html.parser")
                links = [a.get("href") for a in soup.find_all("a", href=True)]
                remind_link = next((l for l in links if "remind_me_later" in l or "confirm_admin_email" in l), None)
                if remind_link:
                    self.session.get(remind_link, verify=False, timeout=30)

            r_admin = self.session.get(f"{self.wp_url}/wp-admin/edit.php", timeout=30, verify=False)
            m = re.search(r'"nonce":"([a-f0-9]+)"', r_admin.text)
            self.nonce = m.group(1) if m else ""
            # verified wp_rest nonce (first-match regex can grab another plugin's nonce)
            self.nonce = get_rest_nonce(self.session, self.wp_url) or self.nonce
            if self.nonce:
                print(f"  [+] Authenticated successfully. Nonce: {self.nonce}")
                if hasattr(self, 'autopilot') and self.autopilot:
                    self.autopilot.session = self.session
                    self.autopilot.nonce = self.nonce
            else:
                print(f"  [!] Warning: Nonce extraction failed for {self.wp_url}")
        except Exception as e:
            print(f"  [!] Auth exception: {e}")

    def post_exists(self, slug: str, schedule_date: str = "", title: str = "") -> bool:
        for p in self.scheduled_log.get("scheduled_posts", []):
            if p.get("slug") == slug:
                return True
            if schedule_date and p.get("schedule_date") == schedule_date:
                return True
            if title and (p.get("title", "").strip().lower() == title.strip().lower() or title.strip().lower() in p.get("title", "").strip().lower()):
                return True
        try:
            headers = {"X-WP-Nonce": self.nonce} if self.nonce else {}
            r = self.session.get(f"{self.wp_url}/wp-json/wp/v2/posts?slug={slug}&status=any", headers=headers, timeout=15, verify=False)
            if r.status_code == 200 and len(r.json()) > 0:
                return True
        except Exception:
            pass
        return False

    def schedule_single_post(self, topic: str, slug: str, category_id: int, schedule_date: str, day_num: int, cluster_name: str) -> Optional[Dict[str, Any]]:
        if self.post_exists(slug, schedule_date=schedule_date, title=topic):
            print(f"  [SKIP] Post '{slug}' ({schedule_date}) already scheduled or exists.")
            return None

        print(f"\n---> [Day {day_num}] Processing: {topic}")
        print(f"     Slug: {slug} | Date: {schedule_date} | Category ID: {category_id}")

        for attempt in range(1, 4):
            try:
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
                        "category_id": category_id,
                        "category": cluster_name,
                        "url": res.get("link", f"{self.wp_url}/{slug}/")
                    }
                    self.scheduled_log["scheduled_posts"].append(record)
                    self.scheduled_log["total_scheduled"] = len(self.scheduled_log["scheduled_posts"])
                    self._save_log()
                    print(f"  [SUCCESS] Scheduled ID: {record['id']} | Link: {record['url']}")
                    return record
                else:
                    err_msg = res.get("message", "Unknown error")
                    print(f"  [!] Attempt {attempt}/3 failed: {err_msg}")
                    if "auth" in err_msg.lower() or "nonce" in err_msg.lower() or "401" in err_msg or "403" in err_msg:
                        print("  [*] Refreshing auth session and retrying...")
                        self._authenticate()
                        self.autopilot.nonce = self.nonce
                    time.sleep(3)
            except Exception as e:
                print(f"  [!] Attempt {attempt}/3 exception: {e}")
                time.sleep(3)

        return None

    def run_batch(self, target_days: Optional[List[int]] = None, max_posts: Optional[int] = None):
        print(f"\n{'='*75}")
        print(f"DIRECT-IP BATCH SCHEDULER ENGINE")
        print(f"Target URL: {self.wp_url} (Direct IP: {self.direct_ip or 'DNS'})")
        print(f"Plan File:  {self.plan_file}")
        print(f"Log File:   {self.log_file}")
        print(f"{'='*75}\n")

        if not os.path.exists(self.plan_file):
            print(f"[ERROR] Content plan not found at {self.plan_file}")
            return

        with open(self.plan_file, "r", encoding="utf-8") as f:
            days_data = json.load(f)

        processed = 0
        for day_item in days_data:
            day_num = day_item.get("day")
            if target_days and day_num not in target_days:
                continue

            day_posts = day_item.get("posts", [])
            print(f"\n>>> Processing Day {day_num} ({day_item.get('date')}) - Total: {len(day_posts)} posts")

            for post in day_posts:
                if max_posts and processed >= max_posts:
                    print(f"\n[INFO] Reached maximum requested posts ({max_posts}). Stopping.")
                    return

                topic = post.get("title", "")
                cat_id = post.get("category_id", 27)
                cat_name = post.get("category", "Uncategorized")
                schedule_date = post.get("schedule_date", "")

                slug = generate_core_keyword_slug(post.get("focus_keyword", topic))

                rec = self.schedule_single_post(
                    topic=topic,
                    slug=slug,
                    category_id=cat_id,
                    schedule_date=schedule_date,
                    day_num=day_num,
                    cluster_name=cat_name
                )
                if rec:
                    processed += 1
                    time.sleep(2)

        print(f"\n{'='*75}")
        print(f"BATCH SCHEDULING COMPLETE FOR {self.wp_url}")
        print(f"Total Newly Scheduled: {processed}")
        print(f"Lifetime Scheduled:    {self.scheduled_log.get('total_scheduled', 0)}")
        print(f"{'='*75}\n")
