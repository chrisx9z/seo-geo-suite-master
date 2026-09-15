# -*- coding: utf-8 -*-
"""
English Travel Batch Scheduler Engine for TripTip.cc
Automated high-quality scheduler for Vietnam Travel (English Edition):
- Reads config/triptip_30day_content_plan.json
- Staggers 10 articles per day across natural publication hours
- Fetches real photos & converts to 16:9 WebP (< 250KB)
- Uploads to WordPress Media Library
- Injects 4-5 images into long-form article content (>= 1 image/500w)
- Posts to WordPress with status: "future" and RankMath SEO tags
"""

import os
import re
import sys
import json
import time
from datetime import datetime, timedelta
import requests
from typing import Dict, Any, List, Optional

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from modules.travel_scheduler.real_image_fetcher import RealImageFetcher
from modules.travel_scheduler.english_travel_writer import EnglishTravelWriter

HOURLY_STAGGERS = [
    "07:15:00", "08:45:00", "10:15:00", "11:45:00", "13:15:00",
    "14:45:00", "16:15:00", "17:45:00", "19:15:00", "20:45:00"
]

CATEGORY_SLUG_TO_ID = {
    "travel-guides": 76,
    "itineraries": 6,
    "transportation": 11,
    "destinations": 7,
    "food-and-drink": 8,
    "culture": 2,
    "where-to-stay": 91,
    "restaurants-cafes": 573,
    "hotels-resorts": 26,
    "homestays": 92
}

class EnglishBatchScheduler:
    def __init__(self, wp_url: str, admin_user: str, admin_pass: str, plan_file: str, log_file: Optional[str] = None):
        self.wp_url = wp_url.rstrip("/")
        self.admin_user = admin_user
        self.admin_pass = admin_pass
        self.plan_file = plan_file
        self.log_file = log_file or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "cache", "scheduled_triptip_cc.json")
        )
        
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EnglishBatchScheduler/1.0"})
        self.nonce = ""
        self._authenticate()

        self.image_fetcher = RealImageFetcher()
        self.writer = EnglishTravelWriter()
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
        for attempt in range(1, 6):
            try:
                print(f"[*] Authenticating to {self.wp_url} as {self.admin_user} (Attempt {attempt}/5)...")
                r_login = self.session.post(
                    f"{self.wp_url}/wp-login.php",
                    data={"log": self.admin_user, "pwd": self.admin_pass, "wp-submit": "Log In"},
                    timeout=60
                )
                r_admin = self.session.get(f"{self.wp_url}/wp-admin/edit.php", timeout=60)
                m = re.search(r'"nonce":"([a-f0-9]+)"', r_admin.text)
                self.nonce = m.group(1) if m else ""
                if not self.nonce:
                    r_post_new = self.session.get(f"{self.wp_url}/wp-admin/post-new.php", timeout=60)
                    m2 = re.search(r'wpApiSettings\s*=\s*\{.*?"nonce":"([a-f0-9]+)"', r_post_new.text, re.DOTALL)
                    if m2:
                        self.nonce = m2.group(1)
                print(f"  [+] Authenticated. Nonce: {self.nonce or 'None (using session cookie)'}")
                return
            except Exception as e:
                print(f"  [-] Auth attempt {attempt} failed: {e}. Retrying in 5s...")
                time.sleep(5)
        raise RuntimeError("Failed to authenticate to WordPress after 5 attempts.")

    def upload_image(self, local_path: str, alt_text: str, title: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(local_path):
            return None

        filename = os.path.basename(local_path)
        mime_type = "image/webp" if filename.endswith(".webp") else "image/jpeg"

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": mime_type
        }
        if self.nonce:
            headers["X-WP-Nonce"] = self.nonce

        with open(local_path, "rb") as img_f:
            img_bytes = img_f.read()

        for attempt in range(1, 4):
            try:
                r = self.session.post(
                    f"{self.wp_url}/wp-json/wp/v2/media",
                    headers=headers,
                    data=img_bytes,
                    timeout=60
                )
                if r.status_code in [200, 201]:
                    media_data = r.json()
                    media_id = media_data.get("id")
                    source_url = media_data.get("source_url")
                    up_headers = {}
                    if self.nonce:
                        up_headers["X-WP-Nonce"] = self.nonce
                    self.session.post(
                        f"{self.wp_url}/wp-json/wp/v2/media/{media_id}",
                        headers=up_headers,
                        json={"alt_text": alt_text, "caption": alt_text, "title": title},
                        timeout=30
                    )
                    return {"id": media_id, "url": source_url}
                elif r.status_code in [401, 403]:
                    print(f"  [*] Auth expired during media upload ({r.status_code}). Re-authenticating...")
                    self._authenticate()
                    if self.nonce:
                        headers["X-WP-Nonce"] = self.nonce
                else:
                    print(f"  [-] Media upload error ({r.status_code}): {r.text[:200]}")
            except Exception as e:
                print(f"  [-] Media upload exception on attempt {attempt}: {e}. Retrying in 4s...")
                time.sleep(4)
        return None

    def post_exists(self, slug: str) -> bool:
        for p in self.scheduled_log.get("scheduled_posts", []):
            if p.get("slug") == slug:
                return True
        return False

    def schedule_single_post(self, post_info: Dict[str, Any], cluster_name: str, pillar: str, cat_slug: str, post_idx: int = 0) -> Optional[Dict[str, Any]]:
        keyword = post_info["keyword"]
        slug = post_info["slug"]
        title = post_info["title"]
        schedule_date = post_info["schedule_date"]
        lsi = post_info.get("lsi", "")
        cat_id = CATEGORY_SLUG_TO_ID.get(cat_slug, 76)

        if self.post_exists(slug):
            print(f"  [SKIP] Post '{slug}' already exists in scheduled log.")
            return None

        print(f"\n---> [{post_info.get('day_num')}/30 - #{post_idx+1}] Processing: {title}")
        print(f"     Slug: {slug} | Date: {schedule_date} | Cat: {cat_slug} (ID: {cat_id})")

        # 1. Fetch 4 authentic travel photos (rule: >= 1 image per 500 words for ~2,000w article)
        num_images_needed = 4
        print(f"     [1/4] Fetching {num_images_needed} authentic photos from Wikimedia Commons...")
        photos = self.image_fetcher.get_real_photos_for_post(
            keyword=keyword,
            slug=slug,
            destination=cluster_name,
            seed_index=post_idx,
            count=num_images_needed
        )

        # 2. Upload Photos to WordPress Media Library
        print(f"     [2/4] Uploading {len(photos)} WebP photos to WordPress Media Library...")
        uploaded_image_urls = []
        featured_media_id = None
        featured_img_url = ""

        for i, photo in enumerate(photos):
            photo_alt = f"{title} - Authentic travel photo {i+1}"
            up = self.upload_image(photo["local_path"], photo_alt, f"{title} photo {i+1}")
            if up:
                uploaded_image_urls.append(up["url"])
                if i == 0:
                    featured_media_id = up["id"]
                    featured_img_url = up["url"]
                    print(f"           Cover Media ID: {featured_media_id}")
                else:
                    print(f"           Content Media {i+1} ID: {up['id']}")

        # 3. Generate Long-Form English Travel Article
        print(f"     [3/4] Writing long-form English travel guide with {len(uploaded_image_urls)} distributed images...")
        post_data = {
            "title": title,
            "keyword": keyword,
            "slug": slug,
            "cluster_name": cluster_name,
            "pillar": pillar,
            "lsi": lsi
        }
        article = self.writer.write_article(post_data, uploaded_image_urls)
        print(f"           Generated {article['word_count']} words, {article['image_count']} images | Intent: {article['intent']}")

        # 4. Schedule Post via REST API
        print(f"     [4/4] Scheduling post to WordPress (status: future, date: {schedule_date})...")
        payload = {
            "title": article["title"],
            "content": article["content"],
            "slug": slug,
            "status": "future",
            "date": schedule_date,
            "categories": [cat_id],
            "meta": {
                "rank_math_focus_keyword": keyword,
                "rank_math_title": article["title"],
                "rank_math_description": article["meta_description"]
            }
        }
        if featured_media_id:
            payload["featured_media"] = featured_media_id

        headers = {}
        if self.nonce:
            headers["X-WP-Nonce"] = self.nonce

        for attempt in range(1, 4):
            try:
                r = self.session.post(
                    f"{self.wp_url}/wp-json/wp/v2/posts",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                if r.status_code in [200, 201]:
                    res_data = r.json()
                    post_id = res_data.get("id")
                    post_link = res_data.get("link", "")
                    print(f"     [+] SUCCESS: Scheduled Post ID {post_id} -> {post_link}")

                    record = {
                        "id": post_id,
                        "title": article["title"],
                        "keyword": keyword,
                        "slug": slug,
                        "schedule_date": schedule_date,
                        "day": post_info.get("day_num"),
                        "link": post_link,
                        "word_count": article["word_count"],
                        "status": "future",
                        "featured_image": featured_img_url,
                        "intent": article.get("intent"),
                        "meta_description": article.get("meta_description"),
                        "image_count": len(uploaded_image_urls),
                        "images": uploaded_image_urls
                    }
                    self.scheduled_log["scheduled_posts"].append(record)
                    self.scheduled_log["total_scheduled"] = len(self.scheduled_log["scheduled_posts"])
                    self._save_log()
                    return record
                elif r.status_code in [401, 403]:
                    print(f"     [*] Auth expired during post scheduling ({r.status_code}). Re-authenticating...")
                    self._authenticate()
                    if self.nonce:
                        headers["X-WP-Nonce"] = self.nonce
                else:
                    print(f"     [-] Failed to schedule post: HTTP {r.status_code}: {r.text[:300]}")
            except Exception as e:
                print(f"     [-] Exception during schedule post attempt {attempt}: {e}. Retrying in 4s...")
                time.sleep(4)
        return None

    def run_batch(self, target_days: Optional[List[int]] = None, max_posts: Optional[int] = None):
        with open(self.plan_file, "r", encoding="utf-8") as f:
            plan_data = json.load(f)

        clusters = plan_data.get("clusters", [])
        base_date = datetime(2026, 9, 11)  # Starting tomorrow 2026-09-11

        total_processed = 0

        for c in clusters:
            day_num = c["day"]
            if target_days and day_num not in target_days:
                continue

            day_date = base_date + timedelta(days=day_num - 1)
            date_str = day_date.strftime("%Y-%m-%d")
            cluster_name = c["cluster_name"]
            pillar = c.get("pillar", "")
            cat_slug = c.get("cat_slug", "destinations")

            print(f"\n========================================================")
            print(f" SCHEDULING DAY {day_num:02d} ({date_str})")
            print(f" Pillar: {pillar} | Cluster: {cluster_name}")
            print(f" Category: {cat_slug}")
            print(f"========================================================")

            for idx, item in enumerate(c["items"]):
                if max_posts and total_processed >= max_posts:
                    print(f"\n[*] Reached max_posts limit ({max_posts}). Stopping.")
                    return

                title, slug, vol, intent, lsi = item
                stagger_time = HOURLY_STAGGERS[idx % len(HOURLY_STAGGERS)]
                schedule_datetime_iso = f"{date_str}T{stagger_time}"

                post_info = {
                    "day_num": day_num,
                    "title": title,
                    "slug": slug,
                    "keyword": title.split(":")[0].strip() if ":" in title else title,
                    "lsi": lsi,
                    "intent": intent,
                    "schedule_date": schedule_datetime_iso
                }

                res = self.schedule_single_post(
                    post_info=post_info,
                    cluster_name=cluster_name,
                    pillar=pillar,
                    cat_slug=cat_slug,
                    post_idx=idx
                )
                if res:
                    total_processed += 1
                    time.sleep(1)

        print(f"\n========================================================")
        print(f" BATCH COMPLETED! Total posts scheduled: {total_processed}")
        print(f" Log saved at: {self.log_file}")
        print(f"========================================================")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TripTip.cc English Travel Batch Scheduler")
    parser.add_argument("--days", default="1-10", help="Day range to schedule (e.g. 1-10, 1,2,3, or all)")
    parser.add_argument("--max-posts", type=int, default=None, help="Maximum posts to process")
    args = parser.parse_args()

    plan_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config", "triptip_30day_content_plan.json"))
    
    # Load credentials
    conf_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "private", "sites.local.json"))
    with open(conf_file, "r", encoding="utf-8") as f:
        site = next(s for s in json.load(f)["sites"] if s["site_id"] == "triptip")

    target_days = None
    if args.days:
        if "-" in str(args.days):
            start, end = str(args.days).split("-")
            target_days = list(range(int(start), int(end) + 1))
        elif "," in str(args.days):
            target_days = [int(x.strip()) for x in str(args.days).split(",")]
        elif str(args.days).lower() != "all":
            target_days = [int(args.days)]

    scheduler = EnglishBatchScheduler(
        wp_url=site["url"],
        admin_user=site["admin_user"],
        admin_pass=site["admin_pass"],
        plan_file=plan_path
    )
    scheduler.run_batch(target_days=target_days, max_posts=args.max_posts)
