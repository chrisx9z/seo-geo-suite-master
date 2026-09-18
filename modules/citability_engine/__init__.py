# -*- coding: utf-8 -*-
"""
Module: Citability & Structural Readability Engine
Measures passage shape, paragraph conciseness, heading hierarchy, and specificity for GEO.
"""
from .citability_checker import check_html, check_url, analyze

__all__ = ['check_html', 'check_url', 'analyze']
