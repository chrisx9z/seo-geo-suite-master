# -*- coding: utf-8 -*-
"""
Travel Batch Scheduler Engine
Executes automated scheduling of authentic travel experience guides:
- Real travel photos fetched & converted to 16:9 WebP Zero-CLS
- Uploaded to WordPress Media Library
- Long-form (> 1,500 words) experience content generated
- Scheduled into WordPress (status: "future", date: "YYYY-MM-DDTHH:MM:SS")
- RankMath SEO meta tags injected
"""

import os
import re
import sys
import json
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from modules.travel_scheduler.real_image_fetcher import RealImageFetcher
from modules.travel_scheduler.travel_article_writer import TravelArticleWriter

class TravelBatchScheduler:
    def __init__(self, wp_url: str, admin_user: str, admin_pass: str, plan_file: str, log_file: Optional[str] = None):
        self.wp_url = wp_url.rstrip("/")
        self.admin_user = admin_user
        self.admin_pass = admin_pass
        self.plan_file = plan_file
        self.log_file = log_file or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "cache", f"scheduled_{self._get_host_slug()}.json"))
        
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TravelBatchScheduler/1.0"})
        self.nonce = ""
        self._authenticate()

        self.image_fetcher = RealImageFetcher()
        self.writer = TravelArticleWriter()
        self.scheduled_log = self._load_log()

    def _get_host_slug(self) -> str:
        h = self.wp_url.replace("https://", "").replace("http://", "").split("/")[0]
        return re.sub(r"[^a-zA-Z0-9]+", "_", h)

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
        print(f"Authenticating to {self.wp_url} as {self.admin_user}...")
        r_login = self.session.post(
            f"{self.wp_url}/wp-login.php",
            data={"log": self.admin_user, "pwd": self.admin_pass, "wp-submit": "Log In"},
            timeout=25
        )
        if "confirm_admin_email" in r_login.url or "confirm_admin_email" in r_login.text:
            try:
                soup = BeautifulSoup(r_login.text, "html.parser")
                links = [a.get("href") for a in soup.find_all("a", href=True)]
                remind_link = next((l for l in links if "remind_me_later" in l or "confirm_admin_email" in l), None)
                if remind_link:
                    self.session.get(remind_link, timeout=15)
            except Exception as e:
                print(f"Warning: confirm_admin_email bypass failed: {e}")

        r_admin = self.session.get(f"{self.wp_url}/wp-admin/edit.php", timeout=25)
        m = re.search(r'"nonce":"([a-f0-9]+)"', r_admin.text)
        self.nonce = m.group(1) if m else ""
        if not self.nonce:
            print(f"Warning: Nonce extraction failed for {self.wp_url}")
        else:
            print(f"Authenticated successfully. Nonce acquired.")

    def upload_image(self, file_path: str, alt_text: str, title: str) -> Optional[Dict[str, Any]]:
        """Uploads WebP photo to WordPress Media Library via REST API."""
        if not os.path.exists(file_path):
            return None

        filename = os.path.basename(file_path)
        upload_url = f"{self.wp_url}/wp-json/wp/v2/media"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/webp"
        }

        with open(file_path, "rb") as f_img:
            img_bytes = f_img.read()

        for attempt in range(1, 4):
            try:
                if self.nonce:
                    headers["X-WP-Nonce"] = self.nonce
                r = self.session.post(upload_url, headers=headers, data=img_bytes, timeout=40)
                if r.status_code in [200, 201]:
                    data = r.json()
                    mid = data.get("id")
                    source_url = data.get("source_url", "")
                    # Update alt text and title
                    try:
                        self.session.post(
                            f"{upload_url}/{mid}",
                            headers={"X-WP-Nonce": self.nonce} if self.nonce else {},
                            json={"alt_text": alt_text, "title": title},
                            timeout=15
                        )
                    except Exception:
                        pass
                    return {"id": mid, "url": source_url}
                elif r.status_code in [401, 403]:
                    print(f"Auth expired during upload of {filename}. Re-authenticating...")
                    self._authenticate()
                else:
                    print(f"Failed to upload media {filename}: HTTP {r.status_code}. Retrying...")
                    time.sleep(3)
            except Exception as e:
                print(f"Exception uploading {filename} on attempt {attempt}: {e}. Retrying in 4s...")
                time.sleep(4)
        return None

    def post_exists(self, slug: str) -> bool:
        """Checks if a post with this slug is already scheduled or published."""
        # Check in local log first
        for p in self.scheduled_log.get("scheduled_posts", []):
            if p.get("slug") == slug:
                return True
        # Check via WordPress REST
        try:
            r = self.session.get(f"{self.wp_url}/wp-json/wp/v2/posts?slug={slug}&status=any", headers={"X-WP-Nonce": self.nonce}, timeout=15)
            if r.status_code == 200 and len(r.json()) > 0:
                return True
        except Exception:
            pass
        return False

    def schedule_single_post(self, post_info: Dict[str, Any], topic_name: str, post_idx: int = 0) -> Optional[Dict[str, Any]]:
        keyword = post_info["keyword"]
        slug = post_info["slug"]
        schedule_date = post_info["schedule_date"]
        category_id = post_info.get("category_id", 76)
        lsi = post_info.get("lsi", "")

        if self.post_exists(slug):
            print(f"  [SKIP] Post '{slug}' already exists or scheduled.")
            return None

        print(f"\n---> Processing: {keyword}")
        print(f"     Slug: {slug} | Date: {schedule_date}")

        # Determine intent to estimate word count and required image count (Rule: >= 1 image per 500 words)
        intent = self.writer.detect_intent(keyword, topic_name)
        num_images_needed = 5 if intent in ["CAM_NANG", "LICH_TRINH"] else 3

        # 1. Fetch Real Photos (>= 1 image per 500 words)
        print(f"     [1/4] Fetching {num_images_needed} real photos from travel archives (Rule: 1 image/500w)...")
        photos = self.image_fetcher.get_real_photos_for_post(
            keyword, slug, destination=topic_name, seed_index=post_idx, count=num_images_needed
        )
        
        # 2. Upload All Photos to WordPress Media
        print(f"     [2/4] Uploading {len(photos)} authentic WebP photos to WordPress Media...")
        uploaded_image_urls = []
        featured_media_id = None
        featured_img_url = ""
        for i, photo in enumerate(photos):
            up = self.upload_image(photo["local_path"], photo["alt_text"], f"{keyword} ảnh {i+1}")
            if up:
                uploaded_image_urls.append(up["url"])
                if i == 0:
                    featured_media_id = up["id"]
                    featured_img_url = up["url"]
                    print(f"           Cover Media ID: {featured_media_id}")
                else:
                    print(f"           Content Media {i+1} ID: {up['id']}")

        # 3. Generate Long-Form Article with Distributed Images
        print(f"     [3/4] Writing long-form travel guide with {len(uploaded_image_urls)} distributed images...")
        article = self.writer.write_travel_guide(
            keyword=keyword,
            topic=topic_name,
            destination=topic_name,
            lsi=lsi,
            image_urls=uploaded_image_urls,
            intent=post_info.get("intent", "Cẩm nang")
        )
        print(f"           Generated {article['word_count']} words, {article.get('image_count', len(uploaded_image_urls))} images | Title: {article['title']}")

        # 4. Schedule Post via REST API
        print(f"     [4/4] Scheduling post to WordPress (status: future, date: {schedule_date})...")
        payload = {
            "title": article["title"],
            "content": article["content"],
            "slug": slug,
            "status": "future",
            "date": schedule_date,
            "categories": [category_id],
            "meta": {
                "rank_math_focus_keyword": keyword,
                "rank_math_title": article["title"],
                "rank_math_description": article["meta_description"]
            }
        }
        if featured_media_id:
            payload["featured_media"] = featured_media_id

        for attempt in range(1, 4):
            try:
                headers = {}
                if self.nonce:
                    headers["X-WP-Nonce"] = self.nonce
                r = self.session.post(
                    f"{self.wp_url}/wp-json/wp/v2/posts",
                    headers=headers,
                    json=payload,
                    timeout=35
                )
                if r.status_code in [200, 201]:
                    res_data = r.json()
                    post_id = res_data.get("id")
                    post_link = res_data.get("link", "")
                    print(f"     SUCCESS: Scheduled Post ID {post_id} -> {post_link}")

                    record = {
                        "id": post_id,
                        "title": article["title"],
                        "keyword": keyword,
                        "slug": slug,
                        "schedule_date": schedule_date,
                        "day": post_info.get("day"),
                        "link": post_link,
                        "word_count": article["word_count"],
                        "status": "future",
                        "featured_image": featured_img_url,
                        "intent": article.get("intent", intent),
                        "meta_description": article.get("meta_description", ""),
                        "image_count": article.get("image_count", len(uploaded_image_urls)),
                        "images": uploaded_image_urls
                    }
                    self.scheduled_log["scheduled_posts"].append(record)
                    self.scheduled_log["total_scheduled"] = len(self.scheduled_log["scheduled_posts"])
                    self._save_log()
                    return record
                elif r.status_code in [401, 403]:
                    print(f"     [*] Auth expired during post scheduling ({r.status_code}). Re-authenticating...")
                    self._authenticate()
                else:
                    print(f"     FAILED to schedule: HTTP {r.status_code} - {r.text[:300]}. Retrying...")
                    time.sleep(3)
            except Exception as e:
                print(f"     Exception scheduling post on attempt {attempt}: {e}. Retrying in 4s...")
                time.sleep(4)

        return None

    def run_batch(self, target_days: Optional[List[int]] = None, max_posts: Optional[int] = None):
        """Runs the scheduling batch for specified day numbers or entire plan."""
        with open(self.plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)

        count = 0
        print(f"\n====================================================================")
        print(f"STARTING TRAVEL BATCH SCHEDULER FOR: {self.wp_url}")
        print(f"Plan file: {self.plan_file}")
        print(f"====================================================================")

        for day_data in plan:
            day_num = day_data.get("day")
            if target_days and day_num not in target_days:
                continue

            topic = day_data.get("topic", "")
            posts = day_data.get("posts", [])
            print(f"\n>>> Day {day_num}: {topic} ({len(posts)} posts planned)")

            for p_idx, post in enumerate(posts):
                post["day"] = day_num
                res = self.schedule_single_post(post, topic, post_idx=p_idx)
                if res:
                    count += 1
                    time.sleep(2)  # courteous delay between posts

                if max_posts and count >= max_posts:
                    print(f"\nReached max_posts limit ({max_posts}). Stopping batch.")
                    return

        print(f"\nBatch completed. Total posts scheduled in this run: {count}")
        print(f"Lifetime scheduled: {self.scheduled_log['total_scheduled']} posts.")
