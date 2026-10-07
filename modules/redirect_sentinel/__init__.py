# -*- coding: utf-8 -*-
"""
Module: Redirect Sentinel & Chain Auditor
Detects multi-hop redirect chains, redirect loops, HTTP-to-HTTPS downgrade,
and links pointing to redirects in site templates (nav, header, footer).
"""
from .redirect_checker import check_redirects, check_url, audit_site_redirects

__all__ = ['check_redirects', 'check_url', 'audit_site_redirects']
