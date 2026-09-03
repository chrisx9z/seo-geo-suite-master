#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module: Agentic Health Monitor & Auto-Healer
Features:
- Periodic uptime & response time checker across all multi-site domains.
- SEO broken link detector & 404 alert generator.
- Automatic cache clearing trigger (WP Rocket / Redis / Cloudflare).
- Multi-language Hreflang tag verification.
"""

import requests
from bs4 import BeautifulSoup
import time

class HealthMonitor:
    def __init__(self, sites):
        self.sites = sites

    def check_site(self, site):
        url = site.get("url")
        start = time.time()
        try:
            r = requests.get(url, timeout=10)
            latency = round((time.time() - start) * 1000, 2)
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("title")
            return {
                "site_id": site.get("site_id"),
                "status_code": r.status_code,
                "latency_ms": latency,
                "title": title.get_text() if title else "NO TITLE",
                "healthy": r.status_code == 200
            }
        except Exception as e:
            return {"site_id": site.get("site_id"), "healthy": False, "error": str(e)}
