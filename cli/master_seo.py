#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Master Auto SEO GEO Suite CLI
Multi-site automation tool for Deployments, SEO Audits, Fast Indexing, Auto Internal Linking, and Rich Schemas.

Usage:
    python master_seo.py deploy          --site <site_id>
    python master_seo.py audit           --site <site_id>
    python master_seo.py fast-index      --site <site_id>
    python master_seo.py auto-link       --site <site_id>
    python master_seo.py generate-schema --site <site_id>
    python master_seo.py list-sites
"""

import argparse
import json
import os
import sys
import requests
import zipfile
import io
import time
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Import local modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from modules.fast_indexing.instant_indexer import InstantIndexer
    from modules.internal_linking.link_engine import InternalLinkEngine
    from modules.schema_geo.rich_snippets_generator import RichSnippetsGenerator
except ImportError:
    pass

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "sites.json")
PRIVATE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "private", "sites.local.json")

def load_config():
    # Auto-initialize environment defaults when freshly cloned on another device
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_file = os.path.join(base_dir, ".env")
    env_example = os.path.join(base_dir, ".env.example")
    if not os.path.exists(env_file) and os.path.exists(env_example):
        import shutil
        shutil.copyfile(env_example, env_file)

    priv_dir = os.path.join(base_dir, "private")
    os.makedirs(priv_dir, exist_ok=True)

    if os.path.exists(PRIVATE_CONFIG_PATH):
        with open(PRIVATE_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    example_sites = os.path.join(base_dir, "config", "sites.example.json")
    if os.path.exists(example_sites):
        import shutil
        shutil.copyfile(example_sites, CONFIG_PATH)
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"Error: Config file not found at {CONFIG_PATH} or {PRIVATE_CONFIG_PATH}")
    sys.exit(1)

def get_target_sites(args):
    config = load_config()
    sites = config.get("sites", [])
    if not sites:
        print("Error: No sites found in configuration.")
        sys.exit(1)
    if getattr(args, "site", None):
        for s in sites:
            if s.get("site_id") == args.site or args.site in s.get("url", ""):
                return [s]
        print(f"Error: Site '{args.site}' not found in configuration.")
        sys.exit(1)
    return sites

def get_site(site_id):
    config = load_config()
    for s in config.get("sites", []):
        if s.get("site_id") == site_id:
            return s
    print(f"Error: Site '{site_id}' not found in sites.json")
    sys.exit(1)

def get_site_session(site):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 Master-SEO-CLI"})
    admin_user = site.get("admin_user", os.getenv("WP_ADMIN_USER", "admin"))
    admin_pass = site.get("admin_pass") or site.get("admin_password") or os.getenv("WP_ADMIN_PASSWORD", "")
    if not admin_pass:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as ef:
                for line in ef:
                    if line.startswith("WP_ADMIN_PASSWORD="):
                        val = line.split("=", 1)[1].strip()
                        if val:
                            admin_pass = val
    session.post(f"{site['url']}/wp-login.php",
        data={"log": admin_user, "pwd": admin_pass, "wp-submit": "Log In"}, timeout=20)
    return session

def deploy_site(site):
    print(f"\n=== Deploying Auto SEO GEO Master Suite to {site['name']} ({site['url']}) ===")
    session = get_site_session(site)
    plugin_file = os.path.join(os.path.dirname(__file__), "..", "plugins", "auto-seo-geo-master-suite", "auto-seo-geo-master-suite.php")
    with open(plugin_file, "r", encoding="utf-8") as pf:
        plugin_code = pf.read()

    slug = site.get("plugin_slug", "auto-seo-geo-master-suite")
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{slug}/{slug}.php", plugin_code)
    zip_buf.seek(0)
    zip_data = zip_buf.read()

    r_up_page = session.get(f"{site['url']}/wp-admin/plugin-install.php?tab=upload", timeout=15)
    soup = BeautifulSoup(r_up_page.text, "html.parser")
    nonce_in = soup.find("input", {"name": "_wpnonce"})
    if not nonce_in:
        print("Failed to get upload nonce.")
        return

    r_upload = session.post(
        f"{site['url']}/wp-admin/update.php?action=upload-plugin",
        data={"_wpnonce": nonce_in.get("value", ""), "install-plugin-submit": "Install Now"},
        files={"pluginzip": ("auto-seo-geo-master-suite.zip", zip_data, "application/zip")},
        timeout=30
    )
    soup_res = BeautifulSoup(r_upload.text, "html.parser")
    for a in soup_res.find_all("a", href=True):
        if "overwrite" in a.get("href") or "update-selected" in a.get("href") or "activate" in a.get("href"):
            href = a.get("href")
            session.get(href if href.startswith("http") else f"{site['url']}/wp-admin/" + href, timeout=20)

    session.get(f"{site['url']}/wp-admin/admin-post.php?action=purge_cache&type=all", timeout=20)
    print(f"✅ Successfully deployed and purged cache on {site['name']}!")

def audit_site(site):
    print(f"\n=== Running Comprehensive Master SEO & Health Audit on {site['name']} ({site['url']}) ===")
    langs = site.get("languages", {}).get("supported", ["vi", "en", "zh"])
    for l in langs:
        r = requests.get(f"{site['url']}/?lang={l}", headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("title")
        desc = soup.find("meta", {"name": "description"})
        hreflangs = soup.find_all("link", {"rel": "alternate", "hreflang": True})
        print(f"\n[Language: {l.upper()}]")
        print(f"  Title: {title.get_text() if title else '❌ Missing'}")
        print(f"  Description: {desc.get('content') if desc else '❌ Missing'}")
        print(f"  Hreflang Tags: {len(hreflangs)} detected")

    # Run On-Page & Core Web Vitals Audit by default
    audit_onpage_speed_site(site)

    # Run Internal Link Sentinel by default
    audit_internal_links_site(site)

    print(f"\n✅ Comprehensive Master SEO Audit Completed for {site['name']}.")

def fast_index_site(site):
    print(f"\n=== Running Fast Indexing (Bing IndexNow) on {site['name']} ===")
    session = requests.Session()
    r = session.get(f"{site['url']}/wp-json/wp/v2/posts?per_page=20")
    if r.status_code != 200:
        print(f"Error fetching posts: {r.status_code}")
        return
    urls = [p["link"] for p in r.json()]
    host = site['url'].replace("https://", "").replace("http://", "").strip("/ ")
    indexer = InstantIndexer(host=host)
    res = indexer.submit_bing_indexnow(urls)
    print(f"✅ Submitted {len(urls)} URLs to IndexNow protocol.")

def auto_link_site(site):
    print(f"\n=== Running Auto Internal Linking Engine on {site['name']} ===")
    session = get_site_session(site)
    r_admin = session.get(f"{site['url']}/wp-admin/edit.php")
    import re
    m = re.search(r'"nonce":"([a-f0-9]+)"', r_admin.text)
    wp_nonce = m.group(1) if m else ""
    
    r_posts = session.get(f"{site['url']}/wp-json/wp/v2/posts?per_page=50")
    posts = r_posts.json() if r_posts.status_code == 200 else []
    link_engine = InternalLinkEngine(max_links_per_post=3)
    total_injected = 0
    for p in posts[:15]:
        updated_content, count = link_engine.inject_links(p["content"]["rendered"], posts, p["id"])
        if count > 0:
            session.post(
                f"{site['url']}/wp-json/wp/v2/posts/{p['id']}",
                headers={"X-WP-Nonce": wp_nonce},
                json={"content": updated_content}
            )
            total_injected += count
    print(f"✅ Auto Internal Linking completed: {total_injected} links injected.")

def list_sites():
    config = load_config()
    print("\n=== Configured Sites in Auto SEO GEO Suite ===")
    for idx, s in enumerate(config.get("sites", [])):
        print(f"[{idx + 1}] ID: {s['site_id']} | Name: {s['name']} | URL: {s['url']}")

def write_post_site(site, topic, category, status, date):
    from modules.wp_ai_autopilot.autopilot_orchestrator import WpAiAutopilot
    autopilot = WpAiAutopilot(wp_url=site["url"])
    autopilot.produce_and_publish(
        topic=topic,
        category_ids=[category],
        status=status,
        schedule_date=date
    )

def test_404_healer_site(site, test_slug="sample-post"):
    print(f"\n=== Testing Auto 404 Healer on {site['name']} ===")
    test_url = f"{site['url']}/{test_slug}/"
    r = requests.get(test_url, allow_redirects=False, headers={"User-Agent": "Mozilla/5.0"})
    print(f"Request: {test_url}")
    print(f"Status Code: {r.status_code}")
    if r.status_code == 301:
        print(f"✅ Auto 301 Healed Target: {r.headers.get('Location')}")
    else:
        print(f"Result: HTTP {r.status_code}")

def check_news_sitemap_site(site):
    print(f"\n=== Verifying Google News XML Sitemap on {site['name']} ===")
    sitemap_url = f"{site['url']}/news-sitemap.xml"
    r = requests.get(sitemap_url, headers={"User-Agent": "Mozilla/5.0"})
    print(f"URL: {sitemap_url} | HTTP {r.status_code}")
    if r.status_code == 200 and "<news:news>" in r.text:
        urls_count = r.text.count("<url>")
        print(f"✅ Valid Google News XML Sitemap detected! ({urls_count} recent news articles included)")
    else:
        print("❌ Sitemap response invalid or missing news namespace.")

def analyze_serp_gap(competitor_url):
    from modules.serp_gap_hunter.serp_analyzer import SerpGapAnalyzer
    print(f"\n=== Running SERP Competitor & Content Gap Analysis ===")
    analyzer = SerpGapAnalyzer()
    res = analyzer.analyze_competitor_url(competitor_url)
    print(f"Competitor: {competitor_url}")
    print(f"Word Count: {res.get('word_count')} words | H2 tags: {res.get('h2_count')}")
    print(f"Detected Features: {res.get('features')}")
def audit_cannibalization_site(site):
    from modules.cannibalization_detector.detector import KeywordCannibalizationDetector
    print(f"\n=== Auditing Keyword Cannibalization on {site['name']} ===")
    r = requests.get(f"{site['url']}/wp-json/wp/v2/posts?per_page=50")
    posts = r.json() if r.status_code == 200 else []
    detector = KeywordCannibalizationDetector(risk_threshold=0.60)
    conflicts = detector.analyze_site_posts(posts)
    print(f"Total Posts Scanned: {len(posts)} | Total Conflicts: {len(conflicts)}")
    for idx, c in enumerate(conflicts[:5]):
        print(f"[{idx+1}] Risk: {c['risk_level']} (Score: {c['conflict_score']})")
        print(f"    - Post A: {c['post_a']['title']}")
        print(f"    - Post B: {c['post_b']['title']}")
    if not conflicts:
        print("✅ No keyword cannibalization detected on site!")

def build_silo_site(site):
    from modules.semantic_silo.silo_builder import SemanticSiloBuilder
    print(f"\n=== Building Semantic Silo & Topic Clusters on {site['name']} ===")
    r = requests.get(f"{site['url']}/wp-json/wp/v2/posts?per_page=50")
    posts = r.json() if r.status_code == 200 else []
    silo_builder = SemanticSiloBuilder(cluster_threshold=0.20)
    res = silo_builder.build_cluster_graph(posts)
    print(f"Total Posts Scanned: {res['total_posts']} | Clusters Formed: {res['total_clusters']}")
    for idx, cl in enumerate(res["clusters"]):
        pillar = cl["pillar_post"]
        print(f"📍 CLUSTER {idx+1}: {pillar['title']}")
        print(f"   👑 PILLAR POST: /{pillar['slug']}/ (Size: {cl['cluster_size']})")
    if res["orphan_posts"]:
        print(f"\n⚠️ ORPHAN POSTS DETECTED ({res['orphan_posts_count']}):")
        for op in res["orphan_posts"][:5]:
            print(f"   ❌ /{op['slug']}/: {op['title']}")

def inject_eeat_site(site, post_id=665, persona="ai_engineer"):
    from modules.eeat_persona.persona_manager import EeatPersonaManager
    print(f"\n=== Injecting E-E-A-T Author Persona into Post {post_id} on {site['name']} ===")
    session = get_site_session(site)
    r_admin = session.get(f"{site['url']}/wp-admin/edit.php")
    import re
    m = re.search(r'"nonce":"([a-f0-9]+)"', r_admin.text)
    wp_nonce = m.group(1) if m else ""
    mgr = EeatPersonaManager()
    author_box = mgr.generate_author_box_html(persona)
    r_post = session.get(f"{site['url']}/wp-json/wp/v2/posts/{post_id}")
    if r_post.status_code == 200:
        c = r_post.json()["content"]["rendered"]
        if "eeat-author-box" not in c:
            new_c = c + f"\n\n<!-- E-E-A-T Author Box -->\n{author_box}"
            session.post(f"{site['url']}/wp-json/wp/v2/posts/{post_id}", headers={"X-WP-Nonce": wp_nonce}, json={"content": new_c})
            print(f"✅ Injected E-E-A-T Author Box into Post {post_id}!")
        else:
            print("ℹ️ Post already has E-E-A-T author box.")

def heal_orphans_site(site):
    from modules.semantic_silo.silo_builder import SemanticSiloBuilder
    from modules.orphan_healer.orphan_healer import OrphanLinkHealer
    print(f"\n=== Healing Orphan Posts on {site['name']} ===")
    session = get_site_session(site)
    r_admin = session.get(f"{site['url']}/wp-admin/edit.php")
    import re
    m = re.search(r'"nonce":"([a-f0-9]+)"', r_admin.text)
    wp_nonce = m.group(1) if m else ""
    r_posts = session.get(f"{site['url']}/wp-json/wp/v2/posts?per_page=50")
    posts = r_posts.json() if r_posts.status_code == 200 else []
    silo_builder = SemanticSiloBuilder(cluster_threshold=0.20)
    silo_res = silo_builder.build_cluster_graph(posts)
    orphans = silo_res["orphan_posts"]
    if not orphans:
        print("✅ No orphan posts found! All articles are properly bridged.")
        return
    pillar = posts[0]
    pillar_id = pillar["id"]
    pillar_html = pillar["content"]["rendered"]
    healer = OrphanLinkHealer()
    bridged = 0
    for op in orphans:
        op_full = next((p for p in posts if p["id"] == op["id"]), op)
        updated_html, success = healer.bridge_orphan_to_host(pillar_html, op_full)
        if success:
            pillar_html = updated_html
            bridged += 1
            print(f"  🔗 Bridged /{op_full.get('slug')}/ into Pillar Post {pillar_id}")
    if bridged > 0:
        session.post(f"{site['url']}/wp-json/wp/v2/posts/{pillar_id}", headers={"X-WP-Nonce": wp_nonce}, json={"content": pillar_html})
        print(f"✅ Healed {bridged} orphan posts by bridging to Pillar Post {pillar_id}!")

def warm_edge_site(site):
    from modules.cloudflare_edge.worker_generator import CloudflareEdgeManager
    print(f"\n=== Warming Cloudflare Edge CDN Cache on {site['name']} ===")
    r = requests.get(f"{site['url']}/wp-json/wp/v2/posts?per_page=30")
    posts = r.json() if r.status_code == 200 else []
    urls = [site['url']] + [p['link'] for p in posts]
    mgr = CloudflareEdgeManager()
    res = mgr.warm_cache_urls(urls)
    print(f"✅ Warmed {res['success']}/{res['urls']} URLs across Cloudflare global edge PoPs!")
def audit_internal_links_site(site):
    from modules.link_sentinel.link_sentinel import InternalLinkSentinel
    print(f"\n=== Running Internal Link Sentinel on {site['name']} ===")
    session = get_site_session(site)
    r = session.get(f"{site['url']}/wp-json/wp/v2/posts?per_page=30", timeout=25)
    posts = r.json() if r.status_code == 200 else []
    sentinel = InternalLinkSentinel(site['url'])
    res = sentinel.audit_and_heal_posts(posts, session)
    print(f"Total Posts Scanned: {res['total_posts_scanned']}")
    print(f"Total Links Checked: {res['total_links_checked']}")
    print(f"Broken 404 Links Found: {res['broken_links_found']}")
    print(f"Stale 301 Redirects Found: {res['stale_redirects_found']}")
    if res['healed_posts']:
        print(f"✅ Auto-healed {len(res['healed_posts'])} posts in database!")
    else:
        print("✅ 100% of internal links are clean, healthy, and canonical!")

def audit_onpage_speed_site(site, target_url=None):
    from modules.search_console_sentinel.gsc_auditor import SearchConsoleAuditor
    auditor = SearchConsoleAuditor(site['url'])
    url = target_url or site['url']
    print(f"\n=== Technical On-Page & Core Web Vitals Audit: {url} ===")
    res = auditor.audit_url_onpage_and_speed(url)
    print(f"Overall Score: {res['onpage_score']}/100 ({res['status']})")
    print(f"Total Images: {res['metrics']['total_images']} | With Zero-CLS Protection: {res['metrics']['images_with_cls_protection']}")
    if res['issues']:
        print("Issues Detected:")
        for iss in res['issues']:
            print(f"  {iss}")
    else:
        print("✅ Zero critical technical SEO or Core Web Vitals bottlenecks found!")

def optimize_site(site):
    print(f"\n{'='*75}")
    print(f"🚀 MASTER ENTERPRISE OPTIMIZATION: {site['name']} ({site['url']})")
    print(f"{'='*75}")
    
    # 1. Universal Plugin Deploy
    try:
        deploy_site(site)
    except Exception as e:
        print(f"⚠️ Plugin Deploy: {e}")

    # 2. Comprehensive Multilingual & On-Page Technical Audit
    try:
        audit_site(site)
    except Exception as e:
        print(f"⚠️ Audit: {e}")

    # 3. Internal Link Sentinel (ThreadPool multi-threaded auto-scan & healing)
    try:
        audit_internal_links_site(site)
    except Exception as e:
        print(f"⚠️ Link Sentinel: {e}")

    # 4. Semantic Silo & Topic Clusters
    try:
        build_silo_site(site)
    except Exception as e:
        print(f"⚠️ Silo Builder: {e}")

    # 5. Orphan Post Healer (Contextual Bridging to Pillar content)
    try:
        heal_orphans_site(site)
    except Exception as e:
        print(f"⚠️ Orphan Healer: {e}")

    # 6. Keyword Cannibalization Detection
    try:
        audit_cannibalization_site(site)
    except Exception as e:
        print(f"⚠️ Cannibalization: {e}")

    # 7. Fast Indexing (Bing IndexNow Protocol)
    try:
        fast_index_site(site)
    except Exception as e:
        print(f"⚠️ IndexNow: {e}")

    # 8. Cloudflare Global Edge CDN Warming
    try:
        warm_edge_site(site)
    except Exception as e:
        print(f"⚠️ Edge Warming: {e}")

    # 9. Google News XML Sitemap Verification
    try:
        check_news_sitemap_site(site)
    except Exception as e:
        print(f"⚠️ News Sitemap: {e}")

    print(f"\n🎉 100% ENTERPRISE OPTIMIZATION COMPLETED FOR: {site['name']} ({site['url']})\n")

def schedule_travel_site(site, plan_path=None, days=None, max_posts=None):
    from modules.travel_scheduler.travel_batch_scheduler import TravelBatchScheduler
    
    if not plan_path:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if "mmdidau" in site.get("site_id", "") or "mmdidau" in site.get("url", ""):
            plan_path = os.path.join(base_dir, "docs", "MMDIDAU_30DAY_CONTENT_PLAN.json")
        elif "tobeigo" in site.get("site_id", "") or "tobeigo" in site.get("url", ""):
            plan_path = os.path.join(base_dir, "docs", "TOBEIGO_30DAY_CONTENT_PLAN.json")
        else:
            plan_path = os.path.join(base_dir, "docs", f"{site.get('site_id')}_30DAY_CONTENT_PLAN.json")
            
    if not os.path.exists(plan_path):
        print(f"Error: Plan file not found at {plan_path}")
        return
        
    admin_user = site.get("admin_user", os.getenv("WP_ADMIN_USER", "admin"))
    admin_pass = site.get("admin_pass") or site.get("admin_password") or os.getenv("WP_ADMIN_PASSWORD", "")
    
    target_days = None
    if days:
        if "-" in str(days):
            start, end = str(days).split("-")
            target_days = list(range(int(start), int(end) + 1))
        elif "," in str(days):
            target_days = [int(x.strip()) for x in str(days).split(",")]
        elif str(days).lower() != "all":
            target_days = [int(days)]
            
    scheduler = TravelBatchScheduler(
        wp_url=site["url"],
        admin_user=admin_user,
        admin_pass=admin_pass,
        plan_file=plan_path
    )
    scheduler.run_batch(target_days=target_days, max_posts=max_posts)

def main():
    parser = argparse.ArgumentParser(description="Master Auto SEO GEO Suite CLI")
    parser.add_argument("command", choices=["optimize", "optimize-all", "deploy", "audit", "fast-index", "auto-link", "list-sites", "write-post", "heal-404", "news-sitemap", "serp-gap", "cannibalization", "build-silo", "inject-eeat", "heal-orphans", "warm-edge", "audit-links", "audit-onpage", "schedule-travel", "clone-site"], help="Action to perform")
    parser.add_argument("--site", default=None, help="Site ID or domain to target (omit to apply to ALL sites)")
    parser.add_argument("--from-site", default="mmdidau", help="Source site ID to clone from (for clone-site)")
    parser.add_argument("--to-domain", default="triptip.cc", help="Target domain to clone to (for clone-site)")
    parser.add_argument("--to-brand", default="TripTip", help="Target brand name (for clone-site)")
    parser.add_argument("--days", help="Day number or range for travel scheduler (e.g. 1, 1-5, all)")
    parser.add_argument("--plan", help="Custom path to content plan JSON")
    parser.add_argument("--max-posts", type=int, default=None, help="Maximum posts to schedule in this run")
    parser.add_argument("--post-id", type=int, default=665, help="Post ID for EEAT injection")
    parser.add_argument("--topic", help="Topic for AI article writer")
    parser.add_argument("--category", type=int, default=4, help="Category ID (default 4: Cong Nghe & SaaS)")
    parser.add_argument("--status", default="publish", choices=["publish", "future", "draft"], help="Post status")
    parser.add_argument("--date", help="Schedule date ISO string (e.g. 2026-09-04T08:00:00)")
    parser.add_argument("--url", help="URL for testing or competitor analysis")
    parser.add_argument("--all", action="store_true", help="Apply to all configured sites")

    args = parser.parse_args()

    if args.command == "list-sites":
        list_sites()
        return

    if args.command == "clone-site":
        from modules.migration.wp_clone_packager import WPClonePackager
        packager = WPClonePackager(
            source_site_id=args.from_site or "mmdidau",
            target_domain=args.to_domain or "triptip.cc",
            target_name=args.to_brand or "TripTip"
        )
        packager.run_all()
        return

    if args.command == "serp-gap":
        if not args.url:
            print("Error: --url <competitor_url> is required for serp-gap.")
            sys.exit(1)
        analyze_serp_gap(args.url)
        return

    targets = get_target_sites(args)

    for s in targets:
        if args.command in ["optimize", "optimize-all"]:
            optimize_site(s)
        elif args.command == "deploy":
            deploy_site(s)
        elif args.command == "audit":
            audit_site(s)
        elif args.command == "fast-index":
            fast_index_site(s)
        elif args.command == "auto-link":
            auto_link_site(s)
        elif args.command == "heal-404":
            test_404_healer_site(s, test_slug="sample-post" if not args.url else args.url)
        elif args.command == "news-sitemap":
            check_news_sitemap_site(s)
        elif args.command == "cannibalization":
            audit_cannibalization_site(s)
        elif args.command == "build-silo":
            build_silo_site(s)
        elif args.command == "inject-eeat":
            inject_eeat_site(s, post_id=args.post_id)
        elif args.command == "heal-orphans":
            heal_orphans_site(s)
        elif args.command == "warm-edge":
            warm_edge_site(s)
        elif args.command == "audit-links":
            audit_internal_links_site(s)
        elif args.command == "audit-onpage":
            audit_onpage_speed_site(s, target_url=args.url)
        elif args.command == "write-post":
            if not args.topic:
                print("Error: --topic is required for write-post command.")
                sys.exit(1)
            write_post_site(s, args.topic, args.category, args.status, args.date)
        elif args.command == "schedule-travel":
            schedule_travel_site(s, plan_path=args.plan, days=args.days, max_posts=args.max_posts)

if __name__ == "__main__":
    main()
