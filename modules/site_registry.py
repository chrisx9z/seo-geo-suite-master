# -*- coding: utf-8 -*-
"""
Site registry: all site-specific data lives in the gitignored `private/sites.local.json`.

The repo itself must never hard-code real domains, site ids, server IPs or content plans.
Per-site keys (all optional) read from each entry of `sites`:

    scheduler   "travel" (default) | "english" | "vibe" | "direct_ip"
    plan_file   path relative to repo root      (default private/plans/<site_id>.json)
    cache_file  path relative to repo root      (default cache/scheduled_<site_id>.json)
    direct_ip   origin IP to pin the site's host to (only for scheduler=direct_ip)
    theme       free-text label shown in status tables
"""
from __future__ import annotations

import importlib
import json
import os
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_CANDIDATES = ("private/sites.local.json", "config/sites.json")

SCHEDULERS = {
    "travel": ("modules.travel_scheduler.travel_batch_scheduler", "TravelBatchScheduler"),
    "english": ("modules.travel_scheduler.english_batch_scheduler", "EnglishBatchScheduler"),
    "vibe": ("modules.travel_scheduler.vibe_batch_scheduler", "VibeBatchScheduler"),
    "direct_ip": ("modules.travel_scheduler.direct_ip_batch_scheduler", "DirectIPBatchScheduler"),
}


def _abs(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(BASE_DIR, path)


def load_sites() -> List[Dict[str, Any]]:
    for rel in CONFIG_CANDIDATES:
        fp = _abs(rel)
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8") as f:
                return json.load(f).get("sites", [])
    return []


def find_site(key: str) -> Optional[Dict[str, Any]]:
    key = (key or "").lower()
    for s in load_sites():
        if key in (str(s.get("site_id", "")).lower(), str(s.get("url", "")).lower().rstrip("/")) \
                or key and key in str(s.get("url", "")).lower():
            return s
    return None


def plan_path(site: Dict[str, Any]) -> str:
    return _abs(site.get("plan_file") or os.path.join("private", "plans", f"{site.get('site_id')}.json"))


def cache_path(site: Dict[str, Any]) -> str:
    return _abs(site.get("cache_file") or os.path.join("cache", f"scheduled_{site.get('site_id')}.json"))


def scheduler_class(site: Dict[str, Any]):
    kind = site.get("scheduler", "travel")
    if kind not in SCHEDULERS:
        raise ValueError(f"Unknown scheduler '{kind}' for site {site.get('site_id')}; use one of {list(SCHEDULERS)}")
    mod, cls = SCHEDULERS[kind]
    return getattr(importlib.import_module(mod), cls)


def admin_credentials(site: Dict[str, Any]):
    user = site.get("admin_user") or os.getenv("WP_ADMIN_USER", "admin")
    pwd = site.get("admin_pass") or site.get("admin_password") \
        or os.getenv(site.get("admin_password_env") or "WP_ADMIN_PASSWORD", "")
    return user, pwd


def build_scheduler(site: Dict[str, Any], plan_file: Optional[str] = None):
    user, pwd = admin_credentials(site)
    kwargs = dict(wp_url=site["url"], admin_user=user, admin_pass=pwd,
                  plan_file=plan_file or plan_path(site), log_file=cache_path(site))
    if site.get("scheduler") == "direct_ip":
        kwargs["direct_ip"] = site.get("direct_ip")
    return scheduler_class(site)(**kwargs)
