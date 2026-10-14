# -*- coding: utf-8 -*-
"""
Unit tests for DateTime & Schema Synchronization and Auto-Healing Engine.
Verifies Single Source of Truth consistency, ISO 8601 compliance,
theme class repair, and auto-healing SQL generation.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.auto_healer import DateTimeSchemaHealer, DateTimeAuditResult


SAMPLE_HTML_CLEAN = """<!DOCTYPE html>
<html>
<head>
    <title>Sample SEO Article</title>
    <meta property="article:published_time" content="2026-09-15T08:20:00+07:00" />
    <meta property="article:modified_time" content="2026-10-10T22:28:29+07:00" />
    <meta property="og:updated_time" content="2026-10-10T22:28:29+07:00" />
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": "Sample SEO Article",
        "datePublished": "2026-09-15T08:20:00+07:00",
        "dateModified": "2026-10-10T22:28:29+07:00"
    }
    </script>
</head>
<body>
    <span class="td-post-date">
        <time class="entry-date published td-module-date" datetime="2026-09-15T08:20:00+07:00">15 Tháng 9, 2026</time>
    </span>
</body>
</html>"""


SAMPLE_HTML_BUGGY_NEWSPAPER = """<!DOCTYPE html>
<html>
<head>
    <title>Buggy Article</title>
    <meta property="article:published_time" content="2026-09-15T08:20:00+07:00" />
    <meta property="article:modified_time" content="2026-10-10T22:28:29+07:00" />
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": "Buggy Article",
        "datePublished": "2026-09-15T08:20:00+07:00",
        "dateModified": "2026-10-10T22:28:29+07:00"
    }
    </script>
</head>
<body>
    <span class="td-post-date">
        <time class="entry-date updated td-module-date" datetime="2026-09-15T08:20:00+07:00">15 Tháng 9, 2026</time>
    </span>
</body>
</html>"""


SAMPLE_HTML_DESYNC_SCHEMA = """<!DOCTYPE html>
<html>
<head>
    <title>Desync Article</title>
    <meta property="article:published_time" content="2026-09-15T08:20:00+07:00" />
    <meta property="article:modified_time" content="2026-10-10T22:28:29+07:00" />
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": "Desync Article",
        "datePublished": "2026-01-01T00:00:00+07:00",
        "dateModified": "2026-05-01T00:00:00+07:00"
    }
    </script>
</head>
<body>
    <time class="entry-date published" datetime="2026-09-15T08:20:00+07:00">15/09/2026</time>
</body>
</html>"""


def test_clean_html_passes_audit():
    res = DateTimeSchemaHealer.audit_html(
        html=SAMPLE_HTML_CLEAN,
        sitemap_lastmod="2026-10-10T22:28:29+07:00",
        db_post_date="2026-09-15 08:20:00",
        db_post_modified="2026-10-10 22:28:29",
    )
    assert res.passed
    assert len(res.issues) == 0
    assert res.published_time == "2026-09-15T08:20:00+07:00"
    assert res.modified_time == "2026-10-10T22:28:29+07:00"


def test_clean_html_with_utc_sitemap_passes():
    # 2026-10-10 15:28:29 UTC == 2026-10-10 22:28:29 +07:00
    res = DateTimeSchemaHealer.audit_html(
        html=SAMPLE_HTML_CLEAN,
        sitemap_lastmod="2026-10-10T15:28:29+00:00",
    )
    assert res.passed


def test_newspaper_theme_false_updated_detected():
    res = DateTimeSchemaHealer.audit_html(html=SAMPLE_HTML_BUGGY_NEWSPAPER)
    assert not res.passed
    assert "ui_false_updated_class_on_publish_date" in res.issues


def test_newspaper_theme_auto_healed():
    pub = "2026-09-15T08:20:00+07:00"
    mod = "2026-10-10T22:28:29+07:00"
    healed = DateTimeSchemaHealer.heal_html(SAMPLE_HTML_BUGGY_NEWSPAPER, pub, mod)

    assert 'class="entry-date published td-module-date"' in healed
    assert 'class="entry-date updated td-module-date"' not in healed

    # Re-auditing healed html must pass
    res_healed = DateTimeSchemaHealer.audit_html(healed, sitemap_lastmod=mod)
    assert res_healed.passed


def test_schema_desync_detected():
    res = DateTimeSchemaHealer.audit_html(html=SAMPLE_HTML_DESYNC_SCHEMA)
    assert not res.passed
    assert any("schema_published_mismatch" in i for i in res.issues)
    assert any("schema_modified_mismatch" in i for i in res.issues)


def test_sitemap_lastmod_mismatch_detected():
    res = DateTimeSchemaHealer.audit_html(
        html=SAMPLE_HTML_CLEAN,
        sitemap_lastmod="2025-01-01T00:00:00+07:00",
    )
    assert not res.passed
    assert any("sitemap_lastmod_mismatch" in i for i in res.issues)


def test_db_healing_sql_generation():
    sql = DateTimeSchemaHealer.generate_db_healing_sql(table_prefix="wp_test_")
    assert "UPDATE wp_test_posts" in sql
    assert "SET post_modified = post_date, post_modified_gmt = post_date_gmt" in sql
    assert "WHERE post_type = 'post' AND post_status = 'publish' AND post_modified < post_date;" in sql


def test_iso8601_parsing_helpers():
    dt1 = DateTimeSchemaHealer.parse_iso8601("2026-10-10T22:28:29+07:00")
    dt2 = DateTimeSchemaHealer.parse_iso8601("2026-10-10T15:28:29Z")
    assert dt1 is not None and dt2 is not None
    assert dt1.timestamp() == dt2.timestamp()

    invalid = DateTimeSchemaHealer.parse_iso8601("not-a-date")
    assert invalid is None
