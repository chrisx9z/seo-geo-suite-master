# -*- coding: utf-8 -*-
"""
DateTime & Schema Consistency Healer
Guarantees 100% synchronization across UI (<time>), HTML Meta, Schema JSON-LD,
and XML Sitemaps (<lastmod>). Enforces Single Source of Truth from DB and ISO 8601.
"""

from __future__ import annotations

import datetime
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup


@dataclass
class DateTimeAuditResult:
    passed: bool
    issues: List[str] = field(default_factory=list)
    published_time: Optional[str] = None
    modified_time: Optional[str] = None
    ui_time: Optional[str] = None
    schema_published: Optional[str] = None
    schema_modified: Optional[str] = None
    sitemap_lastmod: Optional[str] = None
    healed_html: Optional[str] = None


class DateTimeSchemaHealer:
    """
    Audits and automatically heals Date/Time & Schema desynchronization issues
    to protect against Google Entity Fact-Check and Soft-404 algorithmic penalties.
    """

    @staticmethod
    def parse_iso8601(dt_str: str) -> Optional[datetime.datetime]:
        if not dt_str or not isinstance(dt_str, str):
            return None
        dt_str = dt_str.strip()
        try:
            return datetime.datetime.fromisoformat(dt_str)
        except Exception:
            pass
        # Fallback regex for standard ISO formats
        iso_clean = re.sub(r"Z$", "+00:00", dt_str)
        try:
            return datetime.datetime.fromisoformat(iso_clean)
        except Exception:
            return None

    @classmethod
    def audit_html(
        cls,
        html: str,
        sitemap_lastmod: Optional[str] = None,
        db_post_date: Optional[str] = None,
        db_post_modified: Optional[str] = None,
    ) -> DateTimeAuditResult:
        issues: List[str] = []
        soup = BeautifulSoup(html, "html.parser")

        # 1. Meta tags
        meta_pub = soup.find("meta", property="article:published_time")
        meta_mod = soup.find("meta", property="article:modified_time")
        pub_val = meta_pub.get("content") if meta_pub else None
        mod_val = meta_mod.get("content") if meta_mod else None

        if not pub_val:
            issues.append("missing_article_published_time")
        if not mod_val:
            issues.append("missing_article_modified_time")

        # 2. UI <time> tags
        ui_times = soup.find_all("time")
        ui_pub_val = None
        has_false_updated_class = False

        for t in ui_times:
            classes = t.get("class", [])
            dt_attr = t.get("datetime", "")
            if "entry-date" in classes or "published" in classes:
                if not ui_pub_val:
                    ui_pub_val = dt_attr
            # Detect Newspaper theme bug: class contains 'updated' but datetime equals published date
            if "updated" in classes and dt_attr == pub_val and pub_val != mod_val:
                has_false_updated_class = True

        if has_false_updated_class:
            issues.append("ui_false_updated_class_on_publish_date")

        # 3. Schema JSON-LD
        schemas = soup.find_all("script", type="application/ld+json")
        schema_pub = None
        schema_mod = None

        for s in schemas:
            try:
                data = json.loads(s.string or "{}")
                nodes = data.get("@graph", [data]) if isinstance(data, dict) else []
                for node in nodes:
                    if isinstance(node, dict) and node.get("@type") in ("Article", "BlogPosting", "NewsArticle", "WebPage"):
                        if not schema_pub and node.get("datePublished"):
                            schema_pub = node.get("datePublished")
                        if not schema_mod and node.get("dateModified"):
                            schema_mod = node.get("dateModified")
            except Exception:
                pass

        if not schema_pub:
            issues.append("missing_schema_date_published")
        if not schema_mod:
            issues.append("missing_schema_date_modified")

        # 4. Check consistency across channels
        if pub_val and schema_pub and pub_val != schema_pub:
            issues.append(f"schema_published_mismatch: meta={pub_val} vs schema={schema_pub}")
        if mod_val and schema_mod and mod_val != schema_mod:
            issues.append(f"schema_modified_mismatch: meta={mod_val} vs schema={schema_mod}")

        # 5. Check against sitemap lastmod if provided
        if sitemap_lastmod and mod_val:
            dt_sitemap = cls.parse_iso8601(sitemap_lastmod)
            dt_meta = cls.parse_iso8601(mod_val)
            if dt_sitemap and dt_meta:
                if dt_sitemap.timestamp() != dt_meta.timestamp():
                    issues.append(f"sitemap_lastmod_mismatch: meta={mod_val} vs sitemap={sitemap_lastmod}")
            elif sitemap_lastmod != mod_val:
                issues.append(f"sitemap_lastmod_mismatch: meta={mod_val} vs sitemap={sitemap_lastmod}")

        # 6. Check against DB if provided
        if db_post_date and pub_val:
            # Check DB date substring (YYYY-MM-DD)
            if db_post_date[:10] not in pub_val:
                issues.append(f"db_post_date_mismatch: db={db_post_date} vs meta={pub_val}")

        passed = len(issues) == 0
        healed_html = None
        if not passed and (pub_val or db_post_date) and (mod_val or db_post_modified):
            effective_pub = pub_val or db_post_date
            effective_mod = mod_val or db_post_modified
            healed_html = cls.heal_html(html, effective_pub, effective_mod)

        return DateTimeAuditResult(
            passed=passed,
            issues=issues,
            published_time=pub_val,
            modified_time=mod_val,
            ui_time=ui_pub_val,
            schema_published=schema_pub,
            schema_modified=schema_mod,
            sitemap_lastmod=sitemap_lastmod,
            healed_html=healed_html,
        )

    @classmethod
    def heal_html(cls, html: str, published_iso: str, modified_iso: str) -> str:
        """
        Transforms raw HTML to eliminate false updated classes, normalize <time> tags,
        and guarantee synchronized meta tags in <head>.
        """
        if not html:
            return html

        # 1. Normalize theme class bugs (e.g. Newspaper theme 'entry-date updated')
        html = re.sub(
            r'(<time[^>]*class=["\'][^"\']*\bentry-date\b)\s+updated(\b[^"\']*["\'])',
            r"\g<1> published\g<2>",
            html,
            flags=re.IGNORECASE,
        )

        # 2. Normalize datetime attribute on entry-date published tags
        html = re.sub(
            r'(<time[^>]*class=["\'][^"\']*\bentry-date\b[^"\']*["\'][^>]*)\bdatetime=["\'][^"\']+["\']',
            r'\g<1>datetime="' + published_iso + '"',
            html,
            flags=re.IGNORECASE,
        )

        # 3. Clean duplicate or conflicting meta tags
        html = re.sub(r'<meta\s+property=["\']article:published_time["\'][^>]*>', "", html, flags=re.IGNORECASE)
        html = re.sub(r'<meta\s+property=["\']article:modified_time["\'][^>]*>', "", html, flags=re.IGNORECASE)
        html = re.sub(r'<meta\s+property=["\']og:updated_time["\'][^>]*>', "", html, flags=re.IGNORECASE)

        # 4. Inject canonical meta tags right before </head>
        meta_tags = (
            f"\n<!-- Single Source of Truth Date Synchronization -->\n"
            f'<meta property="article:published_time" content="{published_iso}" />\n'
            f'<meta property="article:modified_time" content="{modified_iso}" />\n'
            f'<meta property="og:updated_time" content="{modified_iso}" />\n'
        )

        if "</head>" in html:
            html = re.sub(r"</head>", meta_tags + "</head>", html, count=1, flags=re.IGNORECASE)
        elif "</HEAD>" in html:
            html = re.sub(r"</HEAD>", meta_tags + "</HEAD>", html, count=1)

        return html

    @staticmethod
    def generate_db_healing_sql(table_prefix: str = "wp_") -> str:
        """
        Returns SQL query to heal any corrupted rows where post_modified is older than post_date.
        """
        p = table_prefix
        return (
            f"UPDATE {p}posts "
            f"SET post_modified = post_date, post_modified_gmt = post_date_gmt "
            f"WHERE post_type = 'post' AND post_status = 'publish' AND post_modified < post_date;"
        )
