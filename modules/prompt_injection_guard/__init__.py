# -*- coding: utf-8 -*-
"""
Module: AI Prompt Injection & Hidden Instruction Security Guard
Detects hidden text, CSS-hidden instructions, and prompt injection attempts targeting AI search crawlers.
"""
from .hidden_instructions import find_hidden_instructions, check_url, check_html

__all__ = ['find_hidden_instructions', 'check_url', 'check_html']
