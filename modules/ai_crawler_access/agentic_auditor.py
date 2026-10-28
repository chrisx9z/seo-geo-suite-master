#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agentic Browsing & AI Resource Discovery Auditor + Fix Drafter
(Integrated from AgriciDaniel/claude-seo: agentic_check.py, agentic_fix.py, ucp_check.py).

Evaluates and drafts fixes for:
  1. RFC 9309 robots.txt groups for 13 AI crawlers & user-triggered agents,
     plus Content-Signal and Agentmap directives.
  2. /llms.txt conformance against Lighthouse 13.5 rules and llmstxt.org structure.
  3. Markdown delivery negotiation (Accept: text/markdown + Vary: Accept) and rel="alternate".
  4. Agentic Resource Discovery (ai-catalog.json) conformance.
  5. WebMCP form annotations & modelContext.registerTool scaffolds.
  6. Universal Commerce Protocol (/.well-known/ucp) profile validation.
"""

from __future__ import annotations

import json
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from modules.codebase_security.url_safety import (
    MAX_JSON_DEPTH,
    URLSafetyError,
    decode_body,
    json_depth_exceeds,
    safe_requests_get,
)

CHECKED_ON = "2026-10-29"
MAX_BODY = 2_000_000
SLUG_RE = re.compile(r"[^a-z0-9]+")

AI_AGENTS = [
    ("GPTBot", "OpenAI", "training", "honours"),
    ("OAI-SearchBot", "OpenAI", "search", "honours"),
    ("ChatGPT-User", "OpenAI", "user", "may not apply"),
    ("OAI-AdsBot", "OpenAI", "ads", "see vendor documentation"),
    ("ClaudeBot", "Anthropic", "training", "honours"),
    ("Claude-SearchBot", "Anthropic", "search", "honours"),
    ("Claude-User", "Anthropic", "user", "honours"),
    ("PerplexityBot", "Perplexity", "search", "honours"),
    ("Perplexity-User", "Perplexity", "user", "generally ignores"),
    ("Google-Extended", "Google", "control", "honours"),
    ("Google-Agent", "Google", "user", "generally ignores"),
    ("Applebot-Extended", "Apple", "control", "honours"),
    ("CCBot", "Common Crawl", "training", "honours"),
]

ROLE_MEANING = {
    "training": "model training",
    "search": "AI search indexing and citation",
    "user": "fetches and actions a person asked for",
    "control": "a robots.txt control token (no separate crawler)",
    "ads": "ad landing-page checks",
}

CONTENT_SIGNAL_KEYS = {"search", "ai-input", "ai-train"}
CONTENT_SIGNAL_EXPERIMENTAL = {"use": {"immediate", "reference", "full"}}
DEFAULT_SIGNAL = "search=yes, ai-input=yes, ai-train=no"

ARD_MEDIA_TYPES = {
    "application/ai-catalog+json",
    "application/agent-card+json",
    "application/a2a-agent-card+json",
    "application/mcp-server-card+json",
    "application/agent-skills+zip",
    "application/agent-skills+gzip",
    'text/markdown; profile="urn:air:agent-skills"',
    "application/ai-registry",
    "application/ai-registry+json",
}
ARD_URN = re.compile(r"^urn:air:([a-zA-Z0-9.-]+)(?::([a-zA-Z0-9._:-]+))?:([a-zA-Z0-9._-]+)$")

_LINE_BREAK = re.compile(r"\r\n|\n|\r")


def robots_lines(text: str) -> list[str]:
    """Split robots.txt on CR, LF or CRLF only (RFC 9309)."""
    lines = _LINE_BREAK.split((text or "").lstrip("\ufeff"))
    if lines and lines[-1] == "" and _LINE_BREAK.search(text[-2:] if text else ""):
        lines.pop()
    return lines


def parse_robots(text: str) -> dict:
    """Parse robots.txt into RFC 9309 groups plus global lines."""
    groups: list = []
    global_lines = {"sitemap": [], "agentmap": [], "orphan_content_signal": []}
    current = None
    last_was_ua = False
    for raw in robots_lines(text):
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, value = (part.strip() for part in line.split(":", 1))
        field = field.lower()
        if field == "user-agent":
            if current is None or not last_was_ua:
                current = {"agents": [], "rules": [], "content_signal": [], "other": []}
                groups.append(current)
            current["agents"].append(value)
            last_was_ua = True
            continue
        last_was_ua = False
        if field == "sitemap":
            global_lines["sitemap"].append(value)
        elif field == "agentmap":
            global_lines["agentmap"].append(value)
        elif current is None:
            if field == "content-signal":
                global_lines["orphan_content_signal"].append(value)
        elif field in ("allow", "disallow"):
            current["rules"].append((field, value))
        elif field == "content-signal":
            current["content_signal"].append(value)
        else:
            current["other"].append((field, value))
    return {"groups": groups, **global_lines}


def select_group(parsed: dict, token: str) -> dict:
    """RFC 9309: combine every group naming ``token``; else every ``*`` group."""
    token_l = token.lower()
    named = [g for g in parsed["groups"] if any(a.lower() == token_l for a in g["agents"])]
    chosen = named or [g for g in parsed["groups"] if "*" in g["agents"]]
    return {
        "matched": "named" if named else ("star" if chosen else "none"),
        "rules": [r for g in chosen for r in g["rules"]],
        "content_signal": [c for g in chosen for c in g["content_signal"]],
    }


def _pattern_matches(pattern: str, path: str) -> bool:
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    regex = "^" + ".*".join(re.escape(part) for part in body.split("*"))
    regex += "$" if anchored else ""
    return re.match(regex, path) is not None


def is_allowed(rules: list, path: str = "/") -> bool:
    """Longest-match evaluation; allow wins a tie; empty disallow allows all."""
    best_len, allowed = -1, True
    for field, value in rules:
        if field == "disallow" and value == "":
            continue
        if _pattern_matches(value, path):
            length = len(value)
            if length > best_len or (length == best_len and field == "allow"):
                best_len, allowed = length, field == "allow"
    return allowed


def parse_content_signal(value: str) -> dict:
    """Parse ``search=yes, ai-input=yes, ai-train=no`` into a dict plus issues."""
    signals, issues = {}, []
    for part in (value or "").split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            issues.append(f"malformed entry '{part}'")
            continue
        key, val = (s.strip().lower() for s in part.split("=", 1))
        signals[key] = val
        if key in CONTENT_SIGNAL_EXPERIMENTAL:
            if val not in CONTENT_SIGNAL_EXPERIMENTAL[key]:
                issues.append(f"value for '{key}' must be one of {sorted(CONTENT_SIGNAL_EXPERIMENTAL[key])}")
            continue
        if key not in CONTENT_SIGNAL_KEYS:
            issues.append(f"unknown key '{key}'")
        elif val not in ("yes", "no"):
            issues.append(f"value for '{key}' must be yes or no")
    return {"signals": signals, "issues": issues}


def add_content_signal(robots_text: str, signal: str = DEFAULT_SIGNAL) -> dict:
    """Insert ``Content-Signal: <signal>`` into each user-agent group that has none."""
    parsed = parse_content_signal(signal)
    if parsed["issues"]:
        raise ValueError("invalid signal: " + "; ".join(parsed["issues"]))
    robots_text = (robots_text or "").lstrip("\ufeff")
    newline = "\r\n" if "\r\n" in robots_text else "\n"
    lines = robots_lines(robots_text)

    def _field(line: str) -> str:
        body = line.lstrip("\ufeff").split("#", 1)[0]
        if ":" not in body:
            return ""
        return body.split(":", 1)[0].strip().lower() or "(unnamed)"

    groups, current, in_ua_block = [], None, False
    for idx, line in enumerate(lines):
        field = _field(line)
        if not field:
            continue
        if field == "user-agent":
            if current is None or not in_ua_block:
                current = {"last_ua": idx, "agents": [], "has_signal": False}
                groups.append(current)
            current["agents"].append(line.split(":", 1)[1].split("#", 1)[0].strip())
            current["last_ua"] = idx
            in_ua_block = True
            continue
        in_ua_block = False
        if current is not None and field == "content-signal":
            current["has_signal"] = True

    insert_after = {g["last_ua"] for g in groups if not g["has_signal"]}
    changed = [g["agents"] for g in groups if not g["has_signal"]]
    out = []
    for idx, line in enumerate(lines):
        out.append(line)
        if idx in insert_after:
            out.append(f"Content-Signal: {signal}")

    if not groups:
        tail = ["User-agent: *", f"Content-Signal: {signal}"]
        out = (out + [""] + tail) if any(ln.strip() for ln in out) else tail
        changed.append(["*"])
    text = newline.join(out)
    if robots_text.endswith(("\n", "\r")) or not robots_text:
        text += newline
    return {"robots_txt": text, "groups_changed": changed}


def evaluate_llms_txt(status: Optional[int], content: Optional[str]) -> dict:
    """Mirror Lighthouse 13.5.0 ``llms-txt`` and add llmstxt.org structure notes."""
    if status is None:
        return {"lighthouse": "fail", "errors": ["fetch failed"], "notes": []}
    if status >= 500:
        return {"lighthouse": "fail", "errors": [f"HTTP {status}"], "notes": []}
    if status >= 400:
        return {"lighthouse": "not-applicable", "errors": [], "notes": [f"HTTP {status}"]}
    content = (content or "").lstrip("\ufeff")
    errors = []
    if not re.search(r"^\s*#\s+.+", content, re.M):
        errors.append('missing an H1 header ("# Title")')
    if not re.search(r"\[.+\]\(.+\)", content):
        errors.append("contains no Markdown links")
    if len(content) < 50:
        errors.append("shorter than 50 characters")
    notes = []
    lines = [ln for ln in content.splitlines() if ln.strip()]
    if lines and not lines[0].lstrip().startswith("# "):
        notes.append("llmstxt.org expects the H1 to be the first line")
    if not re.search(r"^\s*>\s+\S", content, re.M):
        notes.append("no blockquote summary ('> ...') as llmstxt.org recommends")
    if not re.search(r"^\s*##\s+\S", content, re.M):
        notes.append("no H2 sections grouping the links")
    if re.search(r"^\s*<(!doctype|html)", content, re.I):
        notes.append("served HTML, not Markdown (likely a soft 404)")
    return {"lighthouse": "pass" if not errors else "fail", "errors": errors, "notes": notes}


def draft_llms_txt(url: str, html_str: str, max_links: int = 30) -> str:
    """Build an llms.txt draft from a page's HTML."""
    soup = BeautifulSoup(html_str or "", "html.parser")
    title = (soup.title.get_text(strip=True) if soup.title else "") or urlparse(url).netloc
    desc_tag = soup.find("meta", attrs={"name": "description"})
    summary = (desc_tag.get("content") or "").strip() if desc_tag else ""
    host = urlparse(url).netloc
    seen, links = set(), []
    containers = soup.find_all(["nav", "header", "footer"]) or [soup]
    for container in containers:
        for a in container.find_all("a", href=True):
            href = urljoin(url, a["href"]).split("#", 1)[0]
            text = " ".join(a.get_text(" ", strip=True).split())
            if urlparse(href).netloc != host or not text or href in seen:
                continue
            seen.add(href)
            links.append((text, href))
            if len(links) >= max_links:
                break
        if len(links) >= max_links:
            break
    lines = [f"# {title}", ""]
    lines += [f"> {summary}", ""] if summary else ["> Comprehensive resource and guide.", ""]
    lines += ["## Pages", ""]
    lines += [f"- [{text}]({href})" for text, href in links] or [f"- [Home]({url})"]
    return "\n".join(lines) + "\n"


def validate_ai_catalog(raw: str) -> dict:
    """Port of the ARD semantic checks Lighthouse 13.5.0 runs."""
    errors, warnings = [], []
    if json_depth_exceeds(raw):
        return {"errors": [f"malformed JSON: nested deeper than {MAX_JSON_DEPTH} levels"], "warnings": [], "entries": 0}
    try:
        data = json.loads(raw)
    except (ValueError, RecursionError) as exc:
        return {"errors": [f"malformed JSON: {type(exc).__name__}: {str(exc)[:200]}"], "warnings": [], "entries": 0}
    if not isinstance(data, dict):
        return {"errors": ["root must be a JSON object"], "warnings": [], "entries": 0}
    spec = data.get("specVersion")
    if not spec:
        errors.append("missing required 'specVersion'")
    elif spec != "1.0":
        warnings.append(f"unrecognised specVersion {spec!r}, expected '1.0'")
    entries = data.get("entries")
    if entries is None:
        errors.append("missing required 'entries' array")
        return {"errors": errors, "warnings": warnings, "entries": 0}
    if not isinstance(entries, list):
        errors.append("'entries' must be an array")
        return {"errors": errors, "warnings": warnings, "entries": 0}
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entry #{idx} is not an object")
            continue
        label = entry.get("displayName") or entry.get("identifier") or f"entry #{idx}"
        ident = entry.get("identifier")
        if not ident:
            errors.append(f"{label}: missing 'identifier'")
        elif not ARD_URN.match(str(ident)):
            errors.append(f"{label}: identifier must match 'urn:air:<publisher>[:<namespace>]:<name>'")
        if not entry.get("displayName"):
            errors.append(f"{label}: missing 'displayName'")
        media = entry.get("type")
        if not media:
            errors.append(f"{label}: missing 'type'")
        elif not isinstance(media, str):
            errors.append(f"{label}: 'type' must be a string")
        elif media not in ARD_MEDIA_TYPES:
            warnings.append(f"{label}: non-standard type {media!r}")
        has_url, has_data = "url" in entry, "data" in entry
        if has_url == has_data:
            errors.append(f"{label}: provide exactly one of 'url' or 'data'")
    return {"errors": errors, "warnings": warnings, "entries": len(entries)}


def parse_ucp_profile(payload: str) -> dict:
    """Parse a UCP (Universal Commerce Protocol) /.well-known/ucp profile."""
    ucp_version_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    ucp_transports = {"rest", "mcp", "a2a", "embedded"}
    report: dict = {
        "valid_json": False,
        "version": None,
        "services": [],
        "capabilities": [],
        "issues": [],
    }
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, RecursionError) as exc:
        report["issues"].append(f"invalid-json: {exc}")
        return report
    if not isinstance(data, dict):
        report["issues"].append("profile-not-object")
        return report
    report["valid_json"] = True
    ucp = data.get("ucp")
    if not isinstance(ucp, dict):
        report["issues"].append("missing-ucp-root")
        return report
    version = ucp.get("version")
    if not isinstance(version, str) or not ucp_version_re.match(version):
        report["issues"].append("version-missing-or-not-a-date")
    else:
        report["version"] = version
    services = ucp.get("services")
    if not isinstance(services, dict) or not services:
        report["issues"].append("missing-services")
    else:
        for name, variants in services.items():
            if isinstance(variants, list):
                for v in variants:
                    if isinstance(v, dict):
                        issues = []
                        if v.get("transport") not in ucp_transports:
                            issues.append("unknown-transport")
                        report["services"].append({"id": name, "transport": v.get("transport"), "issues": issues})
    caps = ucp.get("capabilities")
    if not isinstance(caps, dict) or not caps:
        report["issues"].append("missing-capabilities")
    else:
        for name, variants in caps.items():
            if isinstance(variants, list):
                for v in variants:
                    if isinstance(v, dict):
                        report["capabilities"].append({"id": name, "version": v.get("version")})
    return report


def evaluate_robots_ai_policy(robots_text: str) -> list[dict]:
    """Evaluate how a robots.txt treats all 13 documented AI crawlers and user-triggered agents."""
    parsed = parse_robots(robots_text or "")
    per_agent = []
    for token, vendor, role, behaviour in AI_AGENTS:
        sel = select_group(parsed, token)
        per_agent.append({
            "token": token,
            "vendor": vendor,
            "role": role,
            "governs": ROLE_MEANING[role],
            "robots_behaviour": behaviour,
            "group": sel["matched"],
            "root_allowed": is_allowed(sel["rules"], "/"),
            "content_signal": sel["content_signal"],
        })
    return per_agent
