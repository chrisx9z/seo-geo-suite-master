# -*- coding: utf-8 -*-
"""
Module: AI Crawler Access & Bot Firewall Verifier
Audits whether AI search bots (GPTBot, ClaudeBot, PerplexityBot, etc.) are allowed by robots.txt
and whether edge WAFs/firewalls permit them to crawl live pages.
"""
from .ai_bot_access import check_access
from .robots_checker import check_robots_url
