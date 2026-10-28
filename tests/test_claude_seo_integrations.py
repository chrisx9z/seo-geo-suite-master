# -*- coding: utf-8 -*-
"""
Unit tests for all modules integrated from AgriciDaniel/claude-seo v2.5.0:
  - modules.codebase_security.url_safety
  - modules.content_quality_gate.humanizer
  - modules.content_quality_gate.qrg_scorer
  - modules.content_quality_gate.parasite_risk
  - modules.seo_drift.drift_monitor
  - modules.ai_crawler_access.agentic_auditor
  - modules.core_web_vitals.preload_and_lcp
  - modules.schema_geo.schema_v2
  - modules.search_console_sentinel.seo_updates
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from modules.ai_crawler_access import (
    add_content_signal,
    draft_llms_txt,
    evaluate_llms_txt,
    evaluate_robots_ai_policy,
    parse_ucp_profile,
    validate_ai_catalog,
)
from modules.codebase_security import (
    URLSafetyError,
    is_safe_ip,
    normalize_hostname,
    validate_url,
)
from modules.content_quality_gate import (
    audit_page_parasite_signals,
    check_post,
    classify_parasite_sections,
    humanize,
    score_qrg_quality,
    strip_invisible,
    verify_claims,
)
from modules.core_web_vitals import (
    analyse_preload_and_bfcache,
    decompose_lcp_subparts,
)
from modules.schema_geo import (
    generate_discussion_schema,
    generate_order_action_schema,
    generate_profile_page_schema,
    generate_reservation_schema,
    validate_ecommerce_schema,
)
from modules.search_console_sentinel import query_google_updates
from modules.seo_drift import (
    capture_baseline,
    generate_drift_html,
    get_history,
    run_comparison,
)


def test_url_safety_ssrf_and_ip_normalization():
    assert validate_url("https://example.com/page") is True
    assert validate_url("http://localhost:8080/admin") is False
    assert validate_url("http://127.0.0.1/secret") is False
    assert validate_url("http://169.254.169.254/latest/meta-data/") is False
    assert validate_url("http://2130706433/") is False  # decimal 127.0.0.1
    assert validate_url("http://0x7f000001/") is False  # hex 127.0.0.1
    assert validate_url("http://metadata.google.internal./") is False  # trailing dot FQDN
    assert validate_url("ftp://example.com/file") is False
    assert is_safe_ip("8.8.8.8") is True
    assert is_safe_ip("100.100.100.200") is False  # RFC 6598 shared space / Alibaba IMDS
    assert normalize_hostname("2130706433") == "127.0.0.1"


def test_humanizer_and_invisible_stripper():
    raw = "In today's fast-paced digital world, we will delve\u200b into a tapestry of tools 👍\u200d💻."
    cleaned, removed = strip_invisible(raw)
    assert removed == 1
    assert "\u200b" not in cleaned
    assert "\u200d" in cleaned  # Emoji ZWJ preserved

    res = humanize(raw)
    assert "delve into" not in res["cleaned"].lower()
    assert "explore" in res["cleaned"].lower()
    assert "range of" in res["cleaned"].lower()
    assert res["change_count"] >= 3


def test_gate_auto_strips_invisible_watermarks():
    paragraphs = [
        f"<p>Kinh nghiệm du lịch Đà Nẵng\u200b\u2060 tự túc chặng {i} khám phá bãi biển Mỹ Khê, bán đảo Sơn Trà, "
        f"cầu Rồng, ẩm thực miền Trung và lịch trình tham quan thực tế số {i}.</p>"
        for i in range(1, 35)
    ]
    body = "<h2>Cẩm nang du lịch Đà Nẵng tự túc</h2>" + "".join(paragraphs)
    res = check_post(
        title="Kinh nghiệm du lịch Đà Nẵng tự túc",
        content=body,
        keyword="du lịch Đà Nẵng",
        slug="du-lich-da-nang",
    )
    assert res.passed is True
    assert "\u200b" not in res.content
    assert any(r.startswith("stripped_invisible_chars:") for r in res.repairs)


def test_qrg_scorer_and_claim_verifier():
    good_text = (
        "According to Gartner, 68% of enterprise teams deployed AI agents in 2025 "
        "([Source](https://www.gartner.com/en/report)). In Hanoi and Da Nang, "
        "average response latency dropped by 140 ms across 12,500 requests."
    ) * 12
    qrg = score_qrg_quality(good_text)
    assert qrg["overall_quality"] >= 70
    assert qrg["information_density"] >= 40

    claims = verify_claims(good_text)
    assert claims["claim_count"] > 0
    assert claims["uncited_ratio"] == 0.0


def test_parasite_risk_classifier():
    rows = [
        audit_page_parasite_signals(
            "https://example.com/coupons/best-hosting",
            "Sponsored Content by Brand Studio. Buy Now with Promo Code and Coupon! "
            "<a href='https://aff.example/?aff_id=1'>1</a>"
            "<a href='https://aff.example/?tag=2'>2</a>"
            "<a href='https://aff.example/?partnerid=3'>3</a>",
        ),
        audit_page_parasite_signals(
            "https://example.com/blog/how-dns-works",
            "<p>DNS resolves domain names to IP addresses using authoritative name servers.</p>",
        ),
    ]
    report = classify_parasite_sections(rows)
    assert report["/coupons/"]["risk"] == "high"
    assert report["/blog/"]["risk"] == "low"


def test_seo_drift_baseline_and_comparison():
    html_v1 = """
    <html><head>
      <title>Best Da Nang Travel Guide</title>
      <meta name="description" content="Complete Da Nang itinerary.">
      <meta name="robots" content="index, follow">
      <link rel="canonical" href="https://example.com/da-nang">
      <meta property="og:title" content="Da Nang Guide">
      <script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","headline":"Da Nang"}</script>
    </head><body>
      <h1>Da Nang Travel Guide</h1>
      <h2>Where to Stay</h2>
    </body></html>
    """
    html_v2 = """
    <html><head>
      <title>Changed Title</title>
      <meta name="description" content="Complete Da Nang itinerary.">
      <meta name="robots" content="noindex, nofollow">
    </head><body>
      <h2>Where to Stay</h2>
    </body></html>
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "drift.db")
        url = "https://example.com/da-nang?utm_source=fb"
        base = capture_baseline(url, html_override=html_v1, db_path=db_path)
        assert base["status"] == "ok"
        assert base["url"] == "https://example.com/da-nang"

        comp = run_comparison(url, html_override=html_v2, db_path=db_path)
        assert comp["status"] == "ok"
        assert comp["summary"]["critical"] >= 3  # schema_removed, canonical_removed, noindex_added, h1_removed
        rules_triggered = {f["rule"] for f in comp["triggered_findings"]}
        assert {"schema_removed", "canonical_removed", "noindex_added", "h1_removed", "title_changed"} <= rules_triggered

        hist = get_history(url, db_path=db_path)
        assert len(hist["baselines"]) == 1
        assert len(hist["comparisons"]) == 1

        report_html = generate_drift_html(comp)
        assert "SEO Drift Report" in report_html
        assert "noindex_added" in report_html


def test_agentic_auditor_robots_llms_and_ucp():
    robots = "User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nDisallow: /\n"
    policy = evaluate_robots_ai_policy(robots)
    by_token = {p["token"]: p for p in policy}
    assert by_token["GPTBot"]["root_allowed"] is False
    assert by_token["OAI-SearchBot"]["root_allowed"] is True

    updated = add_content_signal(robots, "search=yes, ai-input=yes, ai-train=no")
    assert "Content-Signal: search=yes, ai-input=yes, ai-train=no" in updated["robots_txt"]

    llms_draft = draft_llms_txt(
        "https://example.com",
        "<html><head><title>Example</title><meta name='description' content='Site summary'></head>"
        "<body><nav><a href='/docs'>Documentation</a></nav></body></html>",
    )
    llms_eval = evaluate_llms_txt(200, llms_draft)
    assert llms_eval["lighthouse"] == "pass"

    catalog = json.dumps({
        "specVersion": "1.0",
        "entries": [{
            "identifier": "urn:air:example.com:docs-mcp",
            "displayName": "Docs MCP",
            "type": "application/mcp-server-card+json",
            "url": "https://example.com/mcp.json",
            "representativeQueries": ["How to authenticate?", "What endpoints exist?"],
        }],
    })
    cat_eval = validate_ai_catalog(catalog)
    assert cat_eval["errors"] == []
    assert cat_eval["entries"] == 1

    ucp_json = json.dumps({
        "ucp": {
            "version": "2026-08-25",
            "services": {"shopping": [{"version": "1.0", "transport": "rest", "endpoint": "https://example.com/ucp"}]},
            "capabilities": {"dev.ucp.shopping.catalog": [{"version": "1.0", "spec": "https://ucp.dev", "schema": "https://ucp.dev/s"}]},
        }
    })
    ucp_res = parse_ucp_profile(ucp_json)
    assert ucp_res["valid_json"] is True
    assert ucp_res["issues"] == []


def test_cwv_preload_and_lcp_subparts():
    html = """
    <html><head>
      <script type="speculationrules">{"prerender": [{"where": {"href_matches": "/*"}}]}</script>
      <link rel="preload" as="image" href="/hero.webp">
    </head><body>
      <img src="/hero.webp" fetchpriority="high" alt="Hero">
    </body></html>
    """
    res = analyse_preload_and_bfcache(html, {"Cache-Control": "public, max-age=3600"})
    assert res["score"] == 100
    assert res["speculation_rules"]["actions"] == ["prerender"]

    crux = {
        "record": {
            "metrics": {
                "largest_contentful_paint": {"percentiles": {"p75": 3200}},
                "largest_contentful_paint_image_time_to_first_byte": {"percentiles": {"p75": 1600}},
                "largest_contentful_paint_image_resource_load_delay": {"percentiles": {"p75": 400}},
                "largest_contentful_paint_image_resource_load_duration": {"percentiles": {"p75": 600}},
                "largest_contentful_paint_image_element_render_delay": {"percentiles": {"p75": 600}},
            }
        }
    }
    sub = decompose_lcp_subparts(crux, url="https://example.com")
    assert sub["p75_lcp_ms"] == 3200.0
    assert len(sub["dominant_subparts"]) == 1
    assert "TTFB dominates LCP" in sub["recommendations"][0]


def test_schema_v2_and_google_updates():
    prof = generate_profile_page_schema(
        "Chris Nguyen",
        url="https://example.com/author/chris",
        same_as=["https://github.com/chrisx9z"],
        knows_about=["SEO", "AI Automation"],
    )
    assert prof["@type"] == "ProfilePage"
    assert prof["mainEntity"]["knowsAbout"] == ["SEO", "AI Automation"]

    res_schema = generate_reservation_schema("Marea", "2026-06-04T19:30:00Z", party_size=4)
    assert res_schema["@type"] == "FoodEstablishmentReservation"

    ord_schema = generate_order_action_schema("Acme", order_url="https://acme.example/order")
    assert ord_schema["@type"] == "OrderAction"

    disc_schema = generate_discussion_schema(
        "How to optimize INP?", "Alex", url="https://forum.example/t/1", date_published="2026-05-01T00:00:00Z"
    )
    assert disc_schema["@type"] == "DiscussionForumPosting"

    bad_product = {"@context": "https://schema.org", "@type": "VehicleListing"}
    val = validate_ecommerce_schema(bad_product)
    assert val["ok"] is False
    assert val["summary"]["critical"] == 1

    updates = query_google_updates(since="2026-01", kinds=["core", "spam"], limit=5)
    assert updates["count"] > 0
    assert all(u["date"] >= "2026-01-01" for u in updates["updates"])


def test_health_monitor_canonical_hreflang_and_rich_snippets_v25():
    from modules.agentic_health_monitor.health_monitor import HealthMonitor
    from modules.schema_geo.rich_snippets_generator import RichSnippetsGenerator

    bad_html = """
    <html><head>
      <link rel="canonical" href="https://example.com/post/" />
      <link rel="canonical" href="https://example.com/post/" />
      <link rel="alternate" hreflang="en" href="https://example.com/post/?lang=en" />
    </head></html>
    """
    check_bad = HealthMonitor.verify_canonical_and_hreflang(bad_html)
    assert check_bad["passed"] is False
    assert "duplicate_canonical_tags:2" in check_bad["issues"]
    assert "hreflang_points_to_query_param:1" in check_bad["issues"]

    good_html = """
    <html><head>
      <link rel="canonical" href="https://example.com/post/" />
      <link rel="alternate" hreflang="vi" href="https://example.com/post/" />
      <link rel="alternate" hreflang="x-default" href="https://example.com/post/" />
    </head></html>
    """
    check_good = HealthMonitor.verify_canonical_and_hreflang(good_html)
    assert check_good["passed"] is True

    gen = RichSnippetsGenerator(
        site_name="Vietnam Travel Guide",
        site_url="https://example.com",
        publisher_name="Vietnam Travel Guide",
        logo_url="https://example.com/logo.png",
        niche="travel",
        lang="en",
    )
    schema_str = gen.generate_schema_graph({
        "title": "Best Da Nang Itinerary",
        "slug": "best-da-nang-itinerary",
        "content": "<div class='faq-section'><p><strong>When to visit?</strong> March to August.</p></div>",
    })
    assert "FAQPage" not in schema_str  # Retired by Google May 2026, off by default
    assert "Travel Itineraries" in schema_str

    # Code blocks and HTML attributes are protected during humanize()
    html_with_code = '<p><a href="https://example.com/delve-into-ai">Trong kỷ nguyên số hóa ngày nay,</a> we delve into <pre><code>def delve(): pass</code></pre></p>'
    hum = humanize(html_with_code)
    assert 'href="https://example.com/delve-into-ai"' in hum["cleaned"]
    assert "def delve(): pass" in hum["cleaned"]
    assert "explore" in hum["cleaned"]


def test_vietnamese_internal_linking_cannibalization_and_wikidata_geo():
    from modules.internal_linking.link_engine import InternalLinkEngine
    from modules.cannibalization_detector.detector import KeywordCannibalizationDetector
    from modules.geo_knowledge_graph.entity_linker import GeoEntityLinker

    # 1. Vietnamese InternalLinkEngine matches accented prose using unaccented/accented candidates
    engine = InternalLinkEngine(max_links_per_post=3)
    targets = [
        {
            "id": 101,
            "title": {"rendered": "Kinh nghiệm du lịch Đà Nẵng tự túc chi tiết"},
            "slug": "kinh-nghiem-du-lich-da-nang",
            "link": "https://example.com/kinh-nghiem-du-lich-da-nang/",
            "meta": {"rank_math_focus_keyword": "du lịch Đà Nẵng"},
        },
        {
            "id": 102,
            "title": {"rendered": "Hướng dẫn sửa lỗi máy tính Windows 11"},
            "slug": "sua-loi-may-tinh-windows-11",
            "link": "https://example.com/sua-loi-may-tinh-windows-11/",
        },
    ]
    body_html = (
        "<p>Trong chuyến hành trình khám phá miền Trung, du lịch Đà Nẵng luôn là lựa chọn hàng đầu của du khách.</p>"
        "<p>Nếu laptop gặp sự cố, bạn cần sửa lỗi máy tính Windows 11 ngay lập tức.</p>"
    )
    linked_html, count = engine.inject_links(body_html, targets, current_post_id=999)
    assert count == 2
    assert 'href="https://example.com/kinh-nghiem-du-lich-da-nang/"' in linked_html
    assert ">du lịch Đà Nẵng</a>" in linked_html

    # 2. KeywordCannibalizationDetector catches synonymous Vietnamese search intent (3N2Đ vs 3 ngày 2 đêm)
    det = KeywordCannibalizationDetector(risk_threshold=0.65)
    posts = [
        {"id": 1, "title": "Kinh nghiệm du lịch Phú Quốc 3 ngày 2 đêm tự túc", "slug": "du-lich-phu-quoc-3-ngay-2-dem", "link": "https://example.com/1"},
        {"id": 2, "title": "Cẩm nang phượt Phú Quốc 3N2Đ chi tiết", "slug": "phuot-phu-quoc-3n2d", "link": "https://example.com/2"},
        {"id": 3, "title": "Cách nấu phở bò Hà Nội chuẩn vị", "slug": "cach-nau-pho-bo-ha-noi", "link": "https://example.com/3"},
    ]
    conflicts = det.analyze_site_posts(posts)
    assert len(conflicts) == 1
    assert {conflicts[0]["post_a"]["id"], conflicts[0]["post_b"]["id"]} == {1, 2}
    assert "3n2d" in conflicts[0]["shared_intent_tokens"]

    # 3. GeoEntityLinker extracts Travel/UNESCO, World Record & AI Wikidata entities
    linker = GeoEntityLinker()
    ents = linker.extract_entities("Hành trình khám phá Vịnh Hạ Long, đảo Phú Quốc cùng trí tuệ nhân tạo OpenAI và đỉnh Everest.")
    uris = {e["sameAs"] for e in ents}
    assert "https://www.wikidata.org/wiki/Q189903" in uris  # Ha Long Bay
    assert "https://www.wikidata.org/wiki/Q146695" in uris  # Phu Quoc
    assert "https://www.wikidata.org/wiki/Q22670157" in uris  # OpenAI
    assert "https://www.wikidata.org/wiki/Q513" in uris     # Mount Everest


