# -*- coding: utf-8 -*-
"""
Module: AI Crawler Access & Agentic Browsing Readiness Verifier
Audits whether AI search bots (GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot, etc.)
are allowed by robots.txt, evaluates Content-Signal & llms.txt & ai-catalog.json & UCP profiles,
and verifies whether edge WAFs/firewalls permit them to crawl live pages.
"""
from .ai_bot_access import check_access
from .robots_checker import check_robots_url
from .agentic_auditor import (
    AI_AGENTS,
    add_content_signal,
    draft_llms_txt,
    evaluate_llms_txt,
    evaluate_robots_ai_policy,
    is_allowed,
    parse_content_signal,
    parse_robots,
    parse_ucp_profile,
    select_group,
    validate_ai_catalog,
)

__all__ = [
    "check_access",
    "check_robots_url",
    "AI_AGENTS",
    "parse_robots",
    "select_group",
    "is_allowed",
    "parse_content_signal",
    "add_content_signal",
    "evaluate_robots_ai_policy",
    "evaluate_llms_txt",
    "draft_llms_txt",
    "validate_ai_catalog",
    "parse_ucp_profile",
]
