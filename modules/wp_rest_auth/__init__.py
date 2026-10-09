# -*- coding: utf-8 -*-
"""
Reliable WordPress REST nonce for cookie-authenticated sessions.

Bug fixed: pipelines used `re.search(r'"nonce":"([a-f0-9]+)"', admin_html)`, which returns the
FIRST nonce on the page. On sites where another plugin prints its own nonce earlier
(tobeigo, zenshan) that is not the `wp_rest` nonce, and every REST call answers
403 `rest_cookie_invalid_nonce`.

Order: admin-ajax `rest-nonce` (core endpoint that returns exactly the wp_rest nonce),
then `wpApiSettings.nonce` on post-new.php, then the legacy first-match. The candidate is
verified against `/wp-json/wp/v2/users/me` before it is returned.
"""
from __future__ import annotations

import re
from typing import Optional

_WP_API_SETTINGS = re.compile(r"wpApiSettings\s*=\s*\{.*?\"nonce\"\s*:\s*\"([a-f0-9]+)\"", re.S)
_ANY_NONCE = re.compile(r"\"nonce\"\s*:\s*\"([a-f0-9]{10})\"")


def _verify(session, wp_url: str, nonce: str, timeout: int) -> bool:
    try:
        r = session.get(f"{wp_url}/wp-json/wp/v2/users/me", headers={"X-WP-Nonce": nonce},
                        params={"_fields": "id"}, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def get_rest_nonce(session, wp_url: str, timeout: int = 30) -> str:
    """Return a verified wp_rest nonce for a logged-in session, or "" if none works."""
    wp_url = wp_url.rstrip("/")
    candidates: list[str] = []
    try:
        r = session.get(f"{wp_url}/wp-admin/admin-ajax.php", params={"action": "rest-nonce"}, timeout=timeout)
        txt = (r.text or "").strip()
        if r.status_code == 200 and re.fullmatch(r"[a-f0-9]{10}", txt):
            candidates.append(txt)
    except Exception:
        pass
    for page in ("post-new.php", "edit.php"):
        try:
            html = session.get(f"{wp_url}/wp-admin/{page}", timeout=timeout).text
        except Exception:
            continue
        m = _WP_API_SETTINGS.search(html)
        if m:
            candidates.append(m.group(1))
        candidates.extend(_ANY_NONCE.findall(html))
    seen = set()
    for n in candidates:
        if n in seen:
            continue
        seen.add(n)
        if _verify(session, wp_url, n, timeout):
            return n
    return ""


def first_valid_nonce_or(session, wp_url: str, fallback: Optional[str] = "") -> str:
    return get_rest_nonce(session, wp_url) or (fallback or "")
