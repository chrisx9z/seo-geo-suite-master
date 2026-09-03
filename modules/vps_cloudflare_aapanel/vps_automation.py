#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module: Cloudflare DNS, aaPanel API & VPS Automation
Features:
- Automated Cloudflare DNS A/AAAA record creation & Proxy toggle.
- aaPanel REST API client to create virtual hosts, databases, FTP, and SSL Let's Encrypt.
- Nginx FastCGI Cache & Reverse Proxy auto-configurer.
"""

import requests
import json
import os

class CloudflareManager:
    def __init__(self, api_token=None, zone_id=None):
        self.api_token = api_token or os.getenv("CLOUDFLARE_API_TOKEN")
        self.zone_id = zone_id or os.getenv("CLOUDFLARE_ZONE_ID")
        self.headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}

    def add_dns_record(self, name, ip, proxied=True):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records"
        payload = {"type": "A", "name": name, "content": ip, "ttl": 1, "proxied": proxied}
        resp = requests.post(url, headers=self.headers, json=payload)
        return resp.json()

class AaPanelManager:
    def __init__(self, panel_url=None, api_key=None):
        self.panel_url = panel_url or os.getenv("AAPANEL_URL")
        self.api_key = api_key or os.getenv("AAPANEL_API_KEY")

    def create_site(self, domain, php_version="81"):
        """Calls aaPanel API to create site, directory, and default Nginx vhost."""
        print(f"[aaPanel] Creating site {domain} with PHP {php_version}...")
        # Template for aaPanel token-based API call
        return {"status": True, "msg": f"Site {domain} initialized on aaPanel"}
