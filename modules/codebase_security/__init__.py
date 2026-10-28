# -*- coding: utf-8 -*-
"""
Codebase Security Module
Integrated with Cloudflare's security-audit-skill standards and claude-seo SSRF / DNS-pinning guard.
"""

from .auditor import CodebaseSecurityAuditor
from .url_safety import (
    URLSafetyError,
    decode_body,
    decode_response_text,
    is_safe_ip,
    json_depth_exceeds,
    make_safe_playwright_route_handler,
    new_guarded_context,
    normalize_hostname,
    read_bounded,
    safe_requests_get,
    safe_requests_head,
    safe_requests_session,
    validate_url,
    validate_url_strict,
)

__all__ = [
    "CodebaseSecurityAuditor",
    "URLSafetyError",
    "is_safe_ip",
    "normalize_hostname",
    "validate_url",
    "validate_url_strict",
    "safe_requests_get",
    "safe_requests_head",
    "safe_requests_session",
    "decode_response_text",
    "decode_body",
    "read_bounded",
    "json_depth_exceeds",
    "make_safe_playwright_route_handler",
    "new_guarded_context",
]
