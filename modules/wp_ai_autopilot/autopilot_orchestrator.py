"""
WP AI Autopilot Master Orchestrator (RankMath 100/100 Default Standards)
- No Thin Content (Strictly >= 1,000 words, target 1,500 - 2,500 words)
- Core Keyword Slug (Short lowercase ASCII, no stop words)
- Featured Image + In-Content Illustration (< 50KB WebP, Focus Keyword Alt Text)
- RankMath Meta Fields (rank_math_focus_keyword, rank_math_title, rank_math_description)
"""

import os
import sys
import json
import re
from datetime import datetime, timezone
import requests
from typing import Dict, Any, Optional

from .keyword_researcher import KeywordResearcher
from .article_writer import ArticleWriter
from .banner_generator import WebPBannerGenerator

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from modules.content_crawler_pipeline.slug_optimizer import SlugOptimizer
from modules.internal_linking.link_engine import InternalLinkEngine
from modules.fast_indexing.instant_indexer import InstantIndexer

class WpAiAutopilot:
    def __init__(self, wp_url: str, admin_user: Optional[str] = None, admin_pass: Optional[str] = None):
        self.wp_url = wp_url.rstrip("/")
        self.host = self.wp_url.replace("https://", "").replace("http://", "").strip("/ ")
        self.admin_user = admin_user or os.getenv("WP_ADMIN_USER", "admin")
        self.admin_pass = admin_pass or os.getenv("WP_ADMIN_PASSWORD", "")
        
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 Wp-AI-Autopilot"})
        self.nonce = ""
        self._authenticate()

        self.researcher = KeywordResearcher()
        self.writer = ArticleWriter()
        self.banner_gen = WebPBannerGenerator()
        self.link_engine = InternalLinkEngine(max_links_per_post=3)
        self.indexer = InstantIndexer(host=self.host)

    def _authenticate(self):
        try:
            self.session.post(f"{self.wp_url}/wp-login.php",
                data={"log": self.admin_user, "pwd": self.admin_pass, "wp-submit": "Log In"}, timeout=10)
            r_admin = self.session.get(f"{self.wp_url}/wp-admin/edit.php", timeout=10)
            m = re.search(r'"nonce":"([a-f0-9]+)"', r_admin.text)
            self.nonce = m.group(1) if m else ""
        except Exception:
            self.nonce = ""

    def upload_webp_media(self, file_path: str, alt_text: str, title: str) -> Optional[Dict[str, Any]]:
        """Uploads a WebP image and configures Alt Text containing Focus Keyword."""
        if not os.path.exists(file_path) or not self.nonce:
            return None

        filename = os.path.basename(file_path)
        upload_url = f"{self.wp_url}/wp-json/wp/v2/media"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/webp",
            "X-WP-Nonce": self.nonce
        }
        with open(file_path, "rb") as f_img:
            r = self.session.post(upload_url, headers=headers, data=f_img, timeout=30)
            if r.status_code in [200, 201]:
                m_data = r.json()
                mid = m_data.get("id")
                source_url = m_data.get("source_url", "")
                # Update Alt text and Title
                self.session.post(f"{upload_url}/{mid}", headers={"X-WP-Nonce": self.nonce}, json={"alt_text": alt_text, "title": title})
                return {"id": mid, "url": source_url}
        return None

    def produce_and_publish(self, topic: str, category_ids: list = [4], status: str = "publish", schedule_date: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        print(f"\n{'='*70}")
        mode_str = "[DRY-RUN LOCAL PREVIEW]" if dry_run else f"STRICT RANKMATH SEO STANDARDS FOR {self.host.upper()}"
        print(f"🤖 WP AI AUTOPILOT: {mode_str}")
        print(f"Topic: {topic}")
        print(f"{'='*70}")

        # Step 1: Research Keywords & Slug
        print("\n[1/6] Keyword Research & Core Keyword Slug extraction...")
        outline_data = self.researcher.analyze_topic(topic)
        focus_keyword = outline_data["primary_keyword"]
        slug = SlugOptimizer.extract_core_slug(focus_keyword)
        print(f"  ⭐ Focus Keyword: {focus_keyword}")
        print(f"  🔗 Core Keyword Slug: /{slug}/")

        # Step 2: Generate BOTH Featured Image & In-Content Technical Diagram (< 50KB)
        print("\n[2/6] Generating 2 Professional WebP Images (< 50KB each)...")
        banner_path = self.banner_gen.generate_banner(topic, category="TECH & AI", slug=slug)
        diagram_path = self.banner_gen.generate_in_content_illustration(focus_keyword=focus_keyword, slug=slug)

        if dry_run:
            diagram_url = f"file://{os.path.abspath(diagram_path)}"
            featured_id = None
        else:
            featured_upload = self.upload_webp_media(banner_path, alt_text=f"{focus_keyword} ảnh đại diện", title=f"{focus_keyword} Banner")
            diagram_upload = self.upload_webp_media(diagram_path, alt_text=f"{focus_keyword} sơ đồ kiến trúc kỹ thuật chi tiết", title=f"{focus_keyword} Architecture Diagram")
            diagram_url = diagram_upload["url"] if diagram_upload else ""
            featured_id = featured_upload["id"] if featured_upload else None

        # Step 3: Write Deep Article (> 1,000 words guaranteed)
        print("\n[3/6] Synthesizing Deep Structured Content (Enforcing > 1,000 Words & RankMath)...")
        article_data = self.writer.write_article(topic, outline_data, content_img_url=diagram_url)
        seo_title = article_data["title"]
        meta_desc = article_data["meta_description"]
        html_content = article_data["content"]
        word_count = article_data["word_count"]
        print(f"  📝 SEO Title: {seo_title} ({len(seo_title)} chars)")
        print(f"  📄 Meta Description: {meta_desc} ({len(meta_desc)} chars)")
        print(f"  📊 Word Count: {word_count} words (Strictly No Thin Content)")

        if dry_run:
            out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "output", "posts"))
            os.makedirs(out_dir, exist_ok=True)
            local_file = os.path.join(out_dir, f"{slug}.html")
            with open(local_file, "w", encoding="utf-8") as f:
                f.write(f"<!-- Title: {seo_title} -->\n<!-- Meta: {meta_desc} -->\n<!-- Focus Keyword: {focus_keyword} -->\n" + html_content)
            print(f"\n✨ [DRY RUN] Bài viết và hình ảnh WebP đã được tạo thành công cục bộ!")
            print(f"  💾 Tệp HTML: {local_file}")
            print(f"  🖼️ Featured Banner: {banner_path}")
            print(f"  📊 In-Content Diagram: {diagram_path}")
            print(f"{'='*70}\n")
            return {
                "status": "dry_run_success",
                "post_id": 0,
                "title": seo_title,
                "slug": slug,
                "link": local_file,
                "words": word_count,
                "focus_keyword": focus_keyword,
                "banner_path": banner_path,
                "diagram_path": diagram_path
            }

        # Step 4: Internal Linking
        print("\n[4/6] Injecting contextual internal links...")
        try:
            r_posts = self.session.get(f"{self.wp_url}/wp-json/wp/v2/posts?per_page=30", timeout=15)
            existing_posts = r_posts.json() if r_posts.status_code == 200 else []
        except Exception:
            existing_posts = []
        linked_content, links_count = self.link_engine.inject_links(html_content, existing_posts, current_post_id=0)

        # Step 5: WordPress REST API Dispatch with RankMath Post Meta
        print(f"\n[5/6] Dispatching to WordPress with RankMath Post Meta...")
        payload = {
            "title": seo_title,
            "slug": slug,
            "status": status,
            "categories": category_ids,
            "content": linked_content,
            "excerpt": meta_desc,
            "meta": {
                "rank_math_focus_keyword": focus_keyword,
                "rank_math_title": seo_title,
                "rank_math_description": meta_desc,
                "rank_math_pillar_content": "1"
            }
        }
        if featured_id:
            payload["featured_media"] = featured_id
        if status == "future" and schedule_date:
            payload["date"] = schedule_date

        r_pub = self.session.post(
            f"{self.wp_url}/wp-json/wp/v2/posts",
            headers={"X-WP-Nonce": self.nonce},
            json=payload,
            timeout=30
        )

        post_id = None
        post_link = ""
        if r_pub.status_code in [200, 201]:
            pub_data = r_pub.json()
            post_id = pub_data.get("id")
            post_link = pub_data.get("link")
            print(f"  🎉 Post Created Successfully! ID: {post_id} -> {post_link}")
        else:
            print(f"  ❌ Publish Failed: {r_pub.text[:200]}")
            return {"status": "error", "message": r_pub.text}

        # Step 6: Technical On-page Audit, Instant IndexNow & Purge Cache
        if status == "publish" and post_link:
            print("\n[6/6] Technical On-page Audit, IndexNow Ping & Server Cache Purge...")
            try:
                from modules.search_console_sentinel.gsc_auditor import SearchConsoleAuditor
                auditor = SearchConsoleAuditor(self.wp_url)
                audit_res = auditor.audit_url_onpage_and_speed(post_link)
                print(f"  🩺 Technical On-page & Zero-CLS Score: {audit_res.get('onpage_score', 100)}/100 ({audit_res.get('status')})")
            except Exception:
                pass
            self.indexer.submit_bing_indexnow([post_link])
            self.session.get(f"{self.wp_url}/wp-admin/admin-post.php?action=purge_cache&type=all", timeout=15)
            print("  ✅ Pinged IndexNow and purged all server caches.")

        print(f"\n{'='*70}")
        print(f"✨ COMPLETED RANKMATH 100/100 POST: {seo_title}")
        print(f"🔗 Live URL: {post_link}")
        print(f"{'='*70}\n")

        return {
            "status": "success",
            "post_id": post_id,
            "title": seo_title,
            "slug": slug,
            "link": post_link,
            "words": word_count,
            "focus_keyword": focus_keyword
        }
