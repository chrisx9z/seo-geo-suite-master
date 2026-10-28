#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic AI-Pattern Humanizer & Invisible Watermark Stripper
(Integrated from AgriciDaniel/claude-seo and extended with Vietnamese AI clichés).

Removes two classes of synthetic-writing signals:
  1. Invisible Unicode watermarks / zero-width format characters / Unicode tag chars
     (U+E0000..U+E007F) while preserving legitimate emoji sequences (ZWJ + VS16).
  2. Deterministic English and Vietnamese AI-writing clichés (e.g., "delve into",
     "in the ever-evolving landscape of", "trong bối cảnh hiện nay", "bức tranh toàn cảnh").
"""

from __future__ import annotations

import re
from typing import Tuple

_INVISIBLE_DELETE = {
    0x200B,  # ZERO WIDTH SPACE
    0x200C,  # ZERO WIDTH NON-JOINER
    0xFEFF,  # ZERO WIDTH NO-BREAK SPACE (BOM)
    0x00AD,  # SOFT HYPHEN
    0x2060,  # WORD JOINER
    0x202A,  # LEFT-TO-RIGHT EMBEDDING
    0x202B,  # RIGHT-TO-LEFT EMBEDDING
    0x202C,  # POP DIRECTIONAL FORMATTING
    0x202D,  # LEFT-TO-RIGHT OVERRIDE
    0x202E,  # RIGHT-TO-LEFT OVERRIDE
    0x2066,  # LEFT-TO-RIGHT ISOLATE
    0x2067,  # RIGHT-TO-LEFT ISOLATE
    0x2068,  # FIRST STRONG ISOLATE
    0x2069,  # POP DIRECTIONAL ISOLATE
}
_INVISIBLE_SPACE = {
    0x00A0,  # NO-BREAK SPACE
    0x202F,  # NARROW NO-BREAK SPACE
    0x205F,  # MEDIUM MATHEMATICAL SPACE
    0x3000,  # IDEOGRAPHIC SPACE
}
_EMOJI_GLUE = {
    0x200D,  # ZERO WIDTH JOINER
    0xFE0F,  # VARIATION SELECTOR-16
}


def _is_emoji_base(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x1F000 <= cp <= 0x1FAFF
        or 0x2600 <= cp <= 0x27BF
        or 0x2300 <= cp <= 0x23FF
        or cp in (0x200D, 0xFE0F, 0x20E3)
    )


def strip_invisible(text: str) -> Tuple[str, int]:
    """Remove zero-width / directional-override / tag characters while keeping emoji glue."""
    if not text:
        return "", 0
    out: list[str] = []
    removed = 0
    n = len(text)
    for i, ch in enumerate(text):
        cp = ord(ch)
        if cp in _INVISIBLE_DELETE or 0xE0000 <= cp <= 0xE007F:
            removed += 1
        elif cp in _INVISIBLE_SPACE:
            out.append(" ")
            removed += 1
        elif cp in _EMOJI_GLUE:
            prev_ch = text[i - 1] if i > 0 else ""
            next_ch = text[i + 1] if i + 1 < n else ""
            if _is_emoji_base(prev_ch) or _is_emoji_base(next_ch):
                out.append(ch)
            else:
                removed += 1
        else:
            out.append(ch)
    return "".join(out), removed


# Deterministic phrase replacements (English + Vietnamese AI clichés)
_REPLACEMENTS: tuple[tuple[re.Pattern, str, str], ...] = (
    # English AI Clichés
    (re.compile(r"\bin today's fast-paced digital world,?\s*", re.IGNORECASE), "", "cliché opening"),
    (re.compile(r"\bin today's digital age,?\s*", re.IGNORECASE), "", "cliché opening"),
    (re.compile(r"\bin an era where\b", re.IGNORECASE), "when", "cliché opening"),
    (re.compile(r"\bin the realm of\b", re.IGNORECASE), "in", "filler preposition"),
    (re.compile(r"\bin the ever-evolving landscape of\b", re.IGNORECASE), "in", "AI cliché"),
    (re.compile(r"\bnavigating the complexities of\b", re.IGNORECASE), "handling", "AI cliché"),
    (re.compile(r"\bit's important to note that\s*", re.IGNORECASE), "", "throat-clearing"),
    (re.compile(r"\bit is worth noting that\s*", re.IGNORECASE), "", "throat-clearing"),
    (re.compile(r"\bit should be noted that\s*", re.IGNORECASE), "", "throat-clearing"),
    (re.compile(r"\bneedless to say,?\s*", re.IGNORECASE), "", "throat-clearing"),
    (re.compile(r"\bat the end of the day,?\s*", re.IGNORECASE), "ultimately, ", "cliché"),
    (re.compile(r"\ba testament to\b", re.IGNORECASE), "evidence of", "AI cliché"),
    (re.compile(r"\bunderscores the importance of\b", re.IGNORECASE), "shows why", "AI cliché"),
    (re.compile(r"\bdelve into\b", re.IGNORECASE), "explore", "AI-favorite verb"),
    (re.compile(r"\bdelving into\b", re.IGNORECASE), "exploring", "AI-favorite verb"),
    (re.compile(r"\bdelves into\b", re.IGNORECASE), "explores", "AI-favorite verb"),
    (re.compile(r"\bleverage\b", re.IGNORECASE), "use", "jargon"),
    (re.compile(r"\bleveraging\b", re.IGNORECASE), "using", "jargon"),
    (re.compile(r"\butilize\b", re.IGNORECASE), "use", "filler"),
    (re.compile(r"\butilizing\b", re.IGNORECASE), "using", "filler"),
    (re.compile(r"\bunlock the full potential of\b", re.IGNORECASE), "get the most from", "AI cliché"),
    (re.compile(r"\bunlock the power of\b", re.IGNORECASE), "use", "AI cliché"),
    (re.compile(r"\bunleash the power of\b", re.IGNORECASE), "use", "AI cliché"),
    (re.compile(r"\bpave the way for\b", re.IGNORECASE), "enable", "cliché"),
    (re.compile(r"\bgame-changer\b", re.IGNORECASE), "major shift", "hype"),
    (re.compile(r"\bgame changing\b", re.IGNORECASE), "significant", "hype"),
    (re.compile(r"\btapestry of\b", re.IGNORECASE), "range of", "AI cliché"),
    (re.compile(r"\bbeacon of\b", re.IGNORECASE), "example of", "AI cliché"),
    (re.compile(r"\bsymphony of\b", re.IGNORECASE), "combination of", "AI cliché"),
    (re.compile(r"\bin conclusion,?\s*", re.IGNORECASE), "", "essay sign-off"),
    (re.compile(r"\bto sum up,?\s*", re.IGNORECASE), "", "essay sign-off"),
    (re.compile(r"\bin summary,?\s*", re.IGNORECASE), "", "essay sign-off"),
    (re.compile(r"\bin order to\b", re.IGNORECASE), "to", "wordy"),
    (re.compile(r"\bdue to the fact that\b", re.IGNORECASE), "because", "wordy"),
    (re.compile(r"\bfor the purpose of\b", re.IGNORECASE), "for", "wordy"),
    (re.compile(r"\bin the event that\b", re.IGNORECASE), "if", "wordy"),
    (re.compile(r"\bat this point in time\b", re.IGNORECASE), "now", "wordy"),
    # Vietnamese AI Clichés
    (re.compile(r"\btrong kỷ nguyên số hóa ngày nay,?\s*", re.IGNORECASE), "", "cliché opening VI"),
    (re.compile(r"\btrong thời đại công nghệ số phát triển vượt bậc,?\s*", re.IGNORECASE), "", "cliché opening VI"),
    (re.compile(r"\bđiều quan trọng cần lưu ý là\s*", re.IGNORECASE), "", "throat-clearing VI"),
    (re.compile(r"\bkhông thể phủ nhận rằng\s*", re.IGNORECASE), "", "throat-clearing VI"),
    (re.compile(r"\bnhư chúng ta đã biết,?\s*", re.IGNORECASE), "", "throat-clearing VI"),
    (re.compile(r"\btóm lại,?\s*có thể nói rằng\s*", re.IGNORECASE), "", "essay sign-off VI"),
)


def _match_case(source: str, replacement: str) -> str:
    if not replacement:
        return ""
    if source.isupper():
        return replacement.upper()
    if source[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement


_PROTECTED_HTML_RE = re.compile(
    r"(<(?:pre|code|script|style)\b[^>]*>.*?</(?:pre|code|script|style)>|<[^>]+>)",
    re.IGNORECASE | re.DOTALL,
)


def humanize(text: str) -> dict:
    """Return a dict with ``cleaned``, ``changes``, and ``change_count``.
    Preserves HTML tags and <pre>/<code>/<script>/<style> blocks intact.
    """
    cleaned, invis_count = strip_invisible(text or "")
    changes: list[dict] = []
    if invis_count:
        changes.append({
            "kind": "invisible_chars",
            "count": invis_count,
            "note": "Removed zero-width / directional-override / tag characters",
        })

    # Stash protected HTML blocks and tags so replacements never alter attributes/code
    stash: list[str] = []

    def _stash_match(m: re.Match) -> str:
        idx = len(stash)
        stash.append(m.group(0))
        return f"\x00HTML_STASH_{idx}\x00"

    prose = _PROTECTED_HTML_RE.sub(_stash_match, cleaned)

    for pattern, replacement, reason in _REPLACEMENTS:
        matches = list(pattern.finditer(prose))
        if not matches:
            continue
        for m in reversed(matches):
            rep = _match_case(m.group(0), replacement)
            prose = prose[: m.start()] + rep + prose[m.end():]
        changes.append({
            "kind": "phrase",
            "pattern": pattern.pattern,
            "replacement": replacement,
            "count": len(matches),
            "reason": reason,
        })

    def _unstash_match(m: re.Match) -> str:
        return stash[int(m.group(1))]

    cleaned = re.sub(r"\x00HTML_STASH_(\d+)\x00", _unstash_match, prose)

    return {
        "cleaned": cleaned,
        "changes": changes,
        "change_count": sum(c.get("count", 1) for c in changes),
    }
