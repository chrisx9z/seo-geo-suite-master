#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
wp-ai-post CLI Tool
Autonomous AI Content Production & Satellite Site Nurturing.

Usage:
    python wp_ai_post.py yourdomain.com --topic "Hướng Dẫn Kiếm Tiền MMO Tự Động Với AI Agent 2026"
    python wp_ai_post.py yourdomain.com --topic "DeepSeek V4 & V5" --status future --date "2026-09-04T08:00:00"
"""

import os
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.wp_ai_autopilot.autopilot_orchestrator import WpAiAutopilot

def main():
    parser = argparse.ArgumentParser(description="WP AI Autopilot - Automated SEO Content Generator")
    parser.add_argument("domain", help="Target domain (e.g. yourdomain.com or https://yourdomain.com)")
    parser.add_argument("--topic", required=True, help="Topic for the article")
    parser.add_argument("--status", default="publish", choices=["publish", "future", "draft"], help="Post status")
    parser.add_argument("--date", default=None, help="Schedule date ISO string (e.g. 2026-09-04T08:00:00) when status=future")
    parser.add_argument("--category", type=int, default=4, help="Category ID (default 4: Cong Nghe & SaaS)")
    parser.add_argument("--dry-run", action="store_true", help="Generate content and assets locally without publishing to WordPress")

    args = parser.parse_args()

    domain = args.domain.strip()
    if not domain.startswith("http"):
        wp_url = f"https://{domain}"
    else:
        wp_url = domain

    import json
    import shutil

    # Auto-initialize environment defaults on freshly cloned device
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_file = os.path.join(base_dir, ".env")
    env_example = os.path.join(base_dir, ".env.example")
    if not os.path.exists(env_file) and os.path.exists(env_example):
        shutil.copyfile(env_example, env_file)

    priv_dir = os.path.join(base_dir, "private")
    os.makedirs(priv_dir, exist_ok=True)

    admin_user = os.getenv("WP_ADMIN_USER", "admin")
    admin_pass = os.getenv("WP_ADMIN_PASSWORD", "")

    # Look up private local config if exists, then public config
    for c_rel in [os.path.join("private", "sites.local.json"), "config.json", os.path.join("config", "sites.json")]:
        c_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", c_rel))
        if os.path.exists(c_path):
            try:
                with open(c_path, "r", encoding="utf-8") as f:
                    conf = json.load(f)
                    for s in conf.get("sites", []):
                        if domain == s.get("site_id") or domain in s.get("url", "") or domain in s.get("name", "").lower():
                            wp_url = s.get("url", wp_url)
                            admin_user = s.get("admin_user", admin_user)
                            admin_pass = s.get("admin_pass") or s.get("admin_password") or admin_pass
                            break
            except Exception:
                pass
        if admin_pass:
            break

    autopilot = WpAiAutopilot(wp_url=wp_url, admin_user=admin_user, admin_pass=admin_pass)
    res = autopilot.produce_and_publish(
        topic=args.topic,
        category_ids=[args.category],
        status=args.status,
        schedule_date=args.date,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()
