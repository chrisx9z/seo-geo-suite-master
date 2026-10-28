#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO Drift Monitoring Engine (Integrated from AgriciDaniel/claude-seo).

Provides:
  - parse_html_seo_signals(html, base_url=None) -> dict
  - capture_baseline(url, db_path=None) -> dict
  - run_comparison(url, baseline_id=None, db_path=None) -> dict
  - get_history(url, limit=20, db_path=None) -> dict
  - generate_drift_html(comparison) -> str

Applies 17 comparison rules across CRITICAL, WARNING, and INFO severities,
backed by SQLite WAL snapshots and SSRF-safe fetching via `url_safety`.
"""

from __future__ import annotations

import hashlib
import html as html_lib
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

from modules.codebase_security.url_safety import (
    URLSafetyError,
    decode_response_text,
    safe_requests_get,
    validate_url,
)

try:
    import lxml  # noqa: F401
    _HTML_PARSER = "lxml"
except ImportError:
    _HTML_PARSER = "html.parser"

DEFAULT_DB_PATH = str(
    Path(__file__).resolve().parents[2] / "cache" / "seo_drift" / "baselines.db"
)

UTM_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"}

_PERFMATTERS_ATTRS = ("data-perfmatters-src", "data-perfmatters-srcset")
_EWWW_ATTRS = ("data-ewww-src", "data-eio")
_GENERIC_LAZY_ATTRS = ("data-src", "data-lazy-src", "data-original", "data-srcset")
_PERFMATTERS_CLASSES = {"perfmatters-lazy", "perfmatters-lazy-loaded"}
_EWWW_CLASSES = {"lazyload-eio", "lazyloaded-eio"}
_GENERIC_LAZY_CLASSES = {"lazyload", "lazyloaded", "lazy", "lazy-loaded"}


def _has_rel_token(tag, token: str) -> bool:
    rel = tag.get("rel", [])
    if isinstance(rel, str):
        rel = rel.split()
    return any(isinstance(value, str) and value.lower() == token for value in rel or [])


def _detect_lazy_method(img) -> str:
    if img.get("loading", "").lower() == "lazy":
        return "native"
    class_list = set(img.get("class", []) or [])
    if any(img.get(a) for a in _PERFMATTERS_ATTRS) or class_list & _PERFMATTERS_CLASSES:
        return "perfmatters"
    if any(img.get(a) for a in _EWWW_ATTRS) or class_list & _EWWW_CLASSES:
        return "ewww"
    if any(img.get(a) for a in _GENERIC_LAZY_ATTRS) or class_list & _GENERIC_LAZY_CLASSES:
        return "js-generic"
    return "none"


def parse_html_seo_signals(html_str: str, base_url: Optional[str] = None) -> dict:
    """Parse HTML and extract SEO-relevant elements (title, meta, canonical, headings, schema, OG, images, links)."""
    soup = BeautifulSoup(html_str or "", _HTML_PARSER)

    result: dict = {
        "title": None,
        "meta_description": None,
        "meta_robots": None,
        "canonical": None,
        "h1": [],
        "h2": [],
        "h3": [],
        "images": [],
        "links": {"internal": [], "external": []},
        "schema": [],
        "open_graph": {},
        "twitter_card": {},
        "word_count": 0,
        "hreflang": [],
    }

    title_tag = soup.find("title")
    if title_tag:
        result["title"] = title_tag.get_text(strip=True)

    for meta in soup.find_all("meta"):
        name = (meta.get("name") or "").lower()
        property_attr = (meta.get("property") or "").lower()
        content = meta.get("content", "")
        if name == "description":
            result["meta_description"] = content
        elif name == "robots":
            result["meta_robots"] = content
        if property_attr.startswith("og:"):
            result["open_graph"][property_attr] = content
        if name.startswith("twitter:"):
            result["twitter_card"][name] = content

    canonical = next(
        (link for link in soup.find_all("link") if _has_rel_token(link, "canonical")), None
    )
    if canonical:
        result["canonical"] = canonical.get("href")

    for link in soup.find_all("link"):
        if not _has_rel_token(link, "alternate"):
            continue
        hreflang = link.get("hreflang")
        if hreflang:
            result["hreflang"].append({
                "lang": hreflang,
                "href": link.get("href"),
            })

    for tag in ("h1", "h2", "h3"):
        for heading in soup.find_all(tag):
            text = heading.get_text(strip=True)
            if text:
                result[tag].append(text)

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if base_url and src:
            src = urljoin(base_url, src)
        result["images"].append({
            "src": src,
            "alt": img.get("alt"),
            "width": img.get("width"),
            "height": img.get("height"),
            "loading": img.get("loading"),
            "lazy_method": _detect_lazy_method(img),
        })

    if base_url:
        base_domain = urlparse(base_url).netloc
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            link_data = {
                "href": full_url,
                "text": a.get_text(strip=True)[:100],
                "rel": a.get("rel", []),
            }
            if parsed.netloc == base_domain:
                result["links"]["internal"].append(link_data)
            else:
                result["links"]["external"].append(link_data)

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            schema_data = json.loads(script.string or "")
            if isinstance(schema_data, dict) and "@graph" in schema_data:
                for item in schema_data["@graph"]:
                    if isinstance(item, dict):
                        result["schema"].append(item)
            elif isinstance(schema_data, list):
                for item in schema_data:
                    if isinstance(item, dict):
                        result["schema"].append(item)
            elif isinstance(schema_data, dict):
                result["schema"].append(schema_data)
        except (json.JSONDecodeError, TypeError):
            pass

    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    text = soup.get_text(separator=" ", strip=True)
    words = re.findall(r"\b\w+\b", text)
    result["word_count"] = len(words)

    return result


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()
    port = parsed.port
    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        port = None
    netloc = f"{hostname}:{port}" if port else hostname
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    filtered = {k: v for k, v in sorted(query_params.items()) if k not in UTM_PARAMS}
    query = urlencode(filtered, doseq=True)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((scheme, netloc, path, "", query, ""))


def url_hash(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode()).hexdigest()[:16]


def hash_content(content: str) -> str:
    return hashlib.sha256((content or "").encode("utf-8")).hexdigest()


def init_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    target = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(target), exist_ok=True)
    conn = sqlite3.connect(target)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS baselines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            url_hash TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            title TEXT,
            meta_description TEXT,
            canonical TEXT,
            robots TEXT,
            h1 TEXT,
            h2_json TEXT,
            h3_json TEXT,
            schema_json TEXT,
            og_json TEXT,
            cwv_json TEXT,
            html_hash TEXT,
            schema_hash TEXT,
            status_code INTEGER
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_url_hash ON baselines(url_hash)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            url_hash TEXT NOT NULL,
            baseline_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            results_json TEXT NOT NULL,
            critical_count INTEGER DEFAULT 0,
            warning_count INTEGER DEFAULT 0,
            info_count INTEGER DEFAULT 0,
            FOREIGN KEY (baseline_id) REFERENCES baselines(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_comp_url_hash ON comparisons(url_hash)")
    conn.commit()
    return conn


def fetch_page_data(url: str, timeout: int = 30) -> dict:
    result = {"status_code": None, "html": None, "parsed": None, "error": None}
    try:
        resp = safe_requests_get(url, timeout=timeout, allow_redirects=True)
        html_content = decode_response_text(resp)
        result["status_code"] = resp.status_code
        result["html"] = html_content
        result["parsed"] = parse_html_seo_signals(html_content, base_url=resp.url)
    except URLSafetyError as exc:
        result["error"] = f"url_safety: {exc}"
    except Exception as exc:
        result["error"] = f"Fetch failed: {exc}"
    return result


def capture_baseline(
    url: str,
    *,
    html_override: Optional[str] = None,
    status_code_override: int = 200,
    db_path: Optional[str] = None,
) -> dict:
    if html_override is None and not validate_url(url):
        return {"error": "URL rejected: only public http/https URLs are accepted (SSRF protection)"}

    if html_override is not None:
        html_content = html_override
        parsed = parse_html_seo_signals(html_content, base_url=url)
        status_code = status_code_override
    else:
        page_data = fetch_page_data(url)
        if page_data["error"]:
            return {"error": page_data["error"]}
        html_content = page_data["html"]
        parsed = page_data["parsed"]
        status_code = page_data["status_code"]

    html_content_hash = hash_content(html_content) if html_content else None
    schema_content = json.dumps(parsed.get("schema", []), sort_keys=True)
    schema_content_hash = hash_content(schema_content) if parsed.get("schema") else None

    now = datetime.now(timezone.utc).isoformat()
    norm_url = normalize_url(url)
    uhash = url_hash(url)
    h1_list = parsed.get("h1", [])
    h1_text = h1_list[0] if h1_list else None

    baseline = {
        "url": norm_url,
        "url_hash": uhash,
        "timestamp": now,
        "title": parsed.get("title"),
        "meta_description": parsed.get("meta_description"),
        "canonical": parsed.get("canonical"),
        "robots": parsed.get("meta_robots"),
        "h1": h1_text,
        "h2_json": json.dumps(parsed.get("h2", [])),
        "h3_json": json.dumps(parsed.get("h3", [])),
        "schema_json": json.dumps(parsed.get("schema", [])),
        "og_json": json.dumps(parsed.get("open_graph", {})),
        "cwv_json": None,
        "html_hash": html_content_hash,
        "schema_hash": schema_content_hash,
        "status_code": status_code,
    }

    conn = init_db(db_path)
    try:
        cursor = conn.execute(
            """
            INSERT INTO baselines (
                url, url_hash, timestamp, title, meta_description, canonical,
                robots, h1, h2_json, h3_json, schema_json, og_json, cwv_json,
                html_hash, schema_hash, status_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                baseline["url"], baseline["url_hash"], baseline["timestamp"],
                baseline["title"], baseline["meta_description"], baseline["canonical"],
                baseline["robots"], baseline["h1"], baseline["h2_json"],
                baseline["h3_json"], baseline["schema_json"], baseline["og_json"],
                baseline["cwv_json"], baseline["html_hash"], baseline["schema_hash"],
                baseline["status_code"],
            ),
        )
        conn.commit()
        baseline_id = cursor.lastrowid
    finally:
        conn.close()

    return {
        "status": "ok",
        "baseline_id": baseline_id,
        "url": norm_url,
        "timestamp": now,
        "summary": {
            "title": baseline["title"],
            "meta_description": baseline["meta_description"],
            "canonical": baseline["canonical"],
            "robots": baseline["robots"],
            "h1": baseline["h1"],
            "h2_count": len(parsed.get("h2", [])),
            "h3_count": len(parsed.get("h3", [])),
            "schema_count": len(parsed.get("schema", [])),
            "og_tag_count": len(parsed.get("open_graph", {})),
            "status_code": baseline["status_code"],
            "html_hash": html_content_hash[:12] + "..." if html_content_hash else None,
        },
    }


# --------------------------------------------------------------------------- #
# 17 Comparison Rules
# --------------------------------------------------------------------------- #
_RETIRED_OR_UNSUPPORTED_SCHEMA_TYPES = {"FAQPage", "HowTo", "Dataset"}


def _schema_types(schema_blocks: list) -> list[str]:
    types: set[str] = set()
    for block in schema_blocks:
        if not isinstance(block, dict):
            continue
        value = block.get("@type")
        values = value if isinstance(value, list) else [value]
        for item in values:
            if isinstance(item, str) and item:
                types.add(item.rsplit("/", 1)[-1].rsplit("#", 1)[-1])
    return sorted(types)


def _make_finding(rule: str, severity: str, triggered: bool, old_value, new_value, message: str) -> dict:
    return {
        "rule": rule,
        "severity": severity,
        "triggered": triggered,
        "old_value": old_value,
        "new_value": new_value,
        "message": message,
    }


def _evaluate_17_rules(baseline: dict, current: dict, current_status: Optional[int], current_html_hash: Optional[str]) -> list[dict]:
    old_schema = json.loads(baseline.get("schema_json") or "[]")
    new_schema = current.get("schema", [])
    schema_types = _schema_types(old_schema)
    retired_only = bool(schema_types) and all(t in _RETIRED_OR_UNSUPPORTED_SCHEMA_TYPES for t in schema_types)

    r1_trig = len(old_schema) > 0 and len(new_schema) == 0
    r1 = _make_finding(
        "schema_removed", "WARNING" if r1_trig and retired_only else "CRITICAL", r1_trig,
        f"{len(old_schema)} schema block(s)", "0 schema blocks",
        f"Structured data removed ({', '.join(schema_types) or 'all'})." if r1_trig else "Schema presence unchanged.",
    )

    old_can, new_can = baseline.get("canonical"), current.get("canonical")
    r2_trig = old_can is not None and new_can is not None and old_can != new_can
    r2 = _make_finding(
        "canonical_changed", "CRITICAL", r2_trig, old_can, new_can,
        f"Canonical URL changed from '{old_can}' to '{new_can}'." if r2_trig else "Canonical URL unchanged.",
    )

    r3_trig = old_can is not None and (new_can is None or new_can == "")
    r3 = _make_finding(
        "canonical_removed", "CRITICAL", r3_trig, old_can, None,
        "Canonical tag has been removed." if r3_trig else "Canonical tag presence unchanged.",
    )

    old_rob = (baseline.get("robots") or "").lower()
    new_rob = (current.get("meta_robots") or "").lower()
    r4_trig = "noindex" not in old_rob and "noindex" in new_rob
    r4 = _make_finding(
        "noindex_added", "CRITICAL", r4_trig, baseline.get("robots"), current.get("meta_robots"),
        "A 'noindex' directive has been added." if r4_trig else "Robots directives unchanged regarding noindex.",
    )

    old_h1 = baseline.get("h1")
    new_h1_list = current.get("h1", [])
    r5_trig = bool(old_h1) and len(new_h1_list) == 0
    r5 = _make_finding(
        "h1_removed", "CRITICAL", r5_trig, old_h1, None,
        "H1 heading has been removed." if r5_trig else "H1 presence unchanged.",
    )

    new_h1 = new_h1_list[0] if new_h1_list else ""
    if old_h1 and new_h1:
        ratio = SequenceMatcher(None, old_h1, new_h1).ratio()
        r6_trig = ratio < 0.5
        r6 = _make_finding(
            "h1_changed", "CRITICAL", r6_trig, old_h1, new_h1,
            f"H1 changed significantly (similarity: {ratio:.0%})." if r6_trig else f"H1 similar ({ratio:.0%}).",
        )
    else:
        r6 = _make_finding("h1_changed", "CRITICAL", False, old_h1, new_h1, "H1 comparison skipped.")

    old_title, new_title = baseline.get("title"), current.get("title")
    r7_trig = bool(old_title) and not new_title
    r7 = _make_finding(
        "title_removed", "CRITICAL", r7_trig, old_title, None,
        "Title tag has been removed." if r7_trig else "Title tag presence unchanged.",
    )

    old_st = baseline.get("status_code")
    r8_trig = (old_st is not None and 200 <= old_st < 400) and (current_status is not None and current_status >= 400)
    r8 = _make_finding(
        "status_code_error", "CRITICAL", r8_trig, old_st, current_status,
        f"Page now returns HTTP {current_status} (was {old_st})." if r8_trig else f"Status code: {old_st} -> {current_status}.",
    )

    old_t_s, new_t_s = (old_title or "").strip(), (new_title or "").strip()
    r9_trig = bool(old_t_s) and bool(new_t_s) and old_t_s != new_t_s
    r9 = _make_finding(
        "title_changed", "WARNING", r9_trig, old_t_s, new_t_s,
        "Title tag text has changed." if r9_trig else "Title text unchanged.",
    )

    old_md = (baseline.get("meta_description") or "").strip()
    new_md = (current.get("meta_description") or "").strip()
    r10_trig = bool(old_md) and bool(new_md) and old_md != new_md
    r10 = _make_finding(
        "meta_description_changed", "WARNING", r10_trig, old_md[:120], new_md[:120],
        "Meta description has changed." if r10_trig else "Meta description unchanged.",
    )

    r11 = _make_finding("cwv_regressed", "WARNING", False, None, None, "CWV comparison skipped.")
    r12 = _make_finding("perf_score_dropped", "WARNING", False, None, None, "Performance score comparison skipped.")

    old_og = json.loads(baseline.get("og_json") or "{}")
    new_og = current.get("open_graph", {})
    r13_trig = len(old_og) > 0 and len(new_og) == 0
    r13 = _make_finding(
        "og_tags_removed", "WARNING", r13_trig, list(old_og.keys()), [],
        "All Open Graph tags have been removed." if r13_trig else "OG tags presence unchanged.",
    )

    old_sh = baseline.get("schema_hash")
    new_sh = hash_content(json.dumps(new_schema, sort_keys=True)) if new_schema else None
    r14_trig = old_sh is not None and new_sh is not None and old_sh != new_sh
    r14 = _make_finding(
        "schema_modified", "WARNING", r14_trig,
        old_sh[:12] if old_sh else None, new_sh[:12] if new_sh else None,
        "Schema/JSON-LD content has been modified." if r14_trig else "Schema content hash unchanged.",
    )

    r15_trig = len(old_schema) == 0 and len(new_schema) > 0
    r15 = _make_finding(
        "schema_added", "INFO", r15_trig, "0 schema blocks", f"{len(new_schema)} schema block(s)",
        "New structured data added." if r15_trig else "No new schema added.",
    )

    old_h2 = json.loads(baseline.get("h2_json") or "[]")
    new_h2 = current.get("h2", [])
    r16_trig = old_h2 != new_h2
    r16 = _make_finding(
        "h2_structure_changed", "INFO", r16_trig, f"{len(old_h2)} H2s", f"{len(new_h2)} H2s",
        f"H2 heading structure changed ({len(old_h2)} -> {len(new_h2)})." if r16_trig else "H2 structure unchanged.",
    )

    old_hh = baseline.get("html_hash")
    r17_trig = old_hh is not None and current_html_hash is not None and old_hh != current_html_hash
    r17 = _make_finding(
        "content_hash_changed", "INFO", r17_trig,
        old_hh[:12] if old_hh else None, current_html_hash[:12] if current_html_hash else None,
        "Page content hash changed." if r17_trig else "Page content hash unchanged.",
    )

    return [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17]


def run_comparison(
    url: str,
    *,
    baseline_id: Optional[int] = None,
    html_override: Optional[str] = None,
    status_code_override: int = 200,
    db_path: Optional[str] = None,
) -> dict:
    if html_override is None and not validate_url(url):
        return {"error": "URL rejected: only public http/https URLs are accepted (SSRF protection)"}

    uhash = url_hash(url)
    norm_url = normalize_url(url)

    conn = init_db(db_path)
    try:
        if baseline_id is not None:
            row = conn.execute(
                "SELECT * FROM baselines WHERE id = ? AND url_hash = ?",
                (baseline_id, uhash),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM baselines WHERE url_hash = ? ORDER BY id DESC LIMIT 1",
                (uhash,),
            ).fetchone()

        if not row:
            conn.close()
            return {"error": f"No baseline found for {norm_url}. Run capture_baseline first."}

        columns = [desc[0] for desc in conn.execute("SELECT * FROM baselines LIMIT 0").description]
        baseline = dict(zip(columns, row))
    except sqlite3.Error as exc:
        conn.close()
        return {"error": f"Database error: {exc}"}

    if html_override is not None:
        html_content = html_override
        parsed = parse_html_seo_signals(html_content, base_url=url)
        status_code = status_code_override
    else:
        page_data = fetch_page_data(url)
        if page_data["error"]:
            conn.close()
            return {"error": page_data["error"]}
        html_content = page_data["html"]
        parsed = page_data["parsed"]
        status_code = page_data["status_code"]

    current_html_hash = hash_content(html_content) if html_content else None
    findings = _evaluate_17_rules(baseline, parsed, status_code, current_html_hash)

    triggered = [f for f in findings if f["triggered"]]
    untriggered = [f for f in findings if not f["triggered"]]

    critical_count = sum(1 for f in triggered if f["severity"] == "CRITICAL")
    warning_count = sum(1 for f in triggered if f["severity"] == "WARNING")
    info_count = sum(1 for f in triggered if f["severity"] == "INFO")
    now = datetime.now(timezone.utc).isoformat()

    result = {
        "status": "ok",
        "url": norm_url,
        "baseline_id": baseline["id"],
        "baseline_timestamp": baseline["timestamp"],
        "comparison_timestamp": now,
        "summary": {
            "total_rules": len(findings),
            "triggered": len(triggered),
            "critical": critical_count,
            "warning": warning_count,
            "info": info_count,
        },
        "triggered_findings": triggered,
        "untriggered_findings": untriggered,
        "current_status_code": status_code,
    }

    try:
        conn.execute(
            """
            INSERT INTO comparisons (
                url, url_hash, baseline_id, timestamp, results_json,
                critical_count, warning_count, info_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                norm_url, uhash, baseline["id"], now, json.dumps(result),
                critical_count, warning_count, info_count,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return result


def get_history(url: str, limit: int = 20, db_path: Optional[str] = None) -> dict:
    norm_url = normalize_url(url)
    uhash = url_hash(url)
    target = db_path or DEFAULT_DB_PATH
    if not os.path.exists(target):
        return {"url": norm_url, "baselines": [], "comparisons": []}

    conn = init_db(target)
    try:
        rows = conn.execute(
            """
            SELECT id, url, timestamp, title, canonical, robots, h1, status_code
            FROM baselines WHERE url_hash = ? ORDER BY id DESC LIMIT ?
            """,
            (uhash, limit),
        ).fetchall()
        baselines = [
            {
                "id": r[0], "url": r[1], "timestamp": r[2], "title": r[3],
                "canonical": r[4], "robots": r[5], "h1": r[6], "status_code": r[7],
            }
            for r in rows
        ]
        comp_rows = conn.execute(
            """
            SELECT id, baseline_id, timestamp, critical_count, warning_count, info_count
            FROM comparisons WHERE url_hash = ? ORDER BY id DESC LIMIT ?
            """,
            (uhash, limit),
        ).fetchall()
        comparisons = [
            {
                "id": r[0], "baseline_id": r[1], "timestamp": r[2],
                "critical": r[3], "warning": r[4], "info": r[5],
            }
            for r in comp_rows
        ]
    finally:
        conn.close()

    return {"url": norm_url, "baselines": baselines, "comparisons": comparisons}


def generate_drift_html(comparison: dict) -> str:
    """Generate a self-contained HTML report from comparison data."""
    url = html_lib.escape(str(comparison.get("url", "Unknown URL")))
    summary = comparison.get("summary", {})
    critical = summary.get("critical", 0)
    warning = summary.get("warning", 0)
    info = summary.get("info", 0)
    cards = []
    for f in comparison.get("triggered_findings", []):
        sev = html_lib.escape(str(f.get("severity", "INFO")))
        rule = html_lib.escape(str(f.get("rule", "")))
        msg = html_lib.escape(str(f.get("message", "")))
        old_v = html_lib.escape(str(f.get("old_value")))
        new_v = html_lib.escape(str(f.get("new_value")))
        cards.append(
            f"<div class='card {sev.lower()}'><strong>[{sev}] {rule}</strong>: {msg}"
            f"<div>Before: <code>{old_v}</code> | After: <code>{new_v}</code></div></div>"
        )
    body_cards = "\n".join(cards) or "<p>No SEO drift detected.</p>"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>SEO Drift Report - {url}</title></head>
<body><h1>SEO Drift Report: {url}</h1>
<p>Critical: {critical} | Warning: {warning} | Info: {info}</p>
{body_cards}
</body></html>"""
