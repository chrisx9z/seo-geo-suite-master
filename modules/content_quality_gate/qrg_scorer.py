#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sept 2025 QRG Content Quality Scorer & Claim/Citation Gap Verifier
(Integrated from AgriciDaniel/claude-seo: content_quality.py + content_verify.py).

Evaluates content drafts against four QRG §4.6 heuristics:
  - filler_score         (0..100, lower is better)
  - ai_pattern_score     (0..100, lower is better)
  - information_density  (0..100, higher is better — numbers & capitalized entities per 100 words)
  - repetition_score     (0..100, lower is better — duplicate bigram excess)
  - overall_quality      (0..100, higher is better)

Also provides `verify_claims(text)` to surface statistical/quantitative/authority/temporal
claims and check whether each has a nearby citation marker within 200 characters.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List

_FILLER_PHRASES = (
    "in today's fast-paced",
    "in today's digital age",
    "in the realm of",
    "in this comprehensive guide",
    "in this article we will",
    "without further ado",
    "at the end of the day",
    "when it comes to",
    "it goes without saying",
    "needless to say",
    "first and foremost",
    "last but not least",
    "each and every",
    "as a matter of fact",
    "for all intents and purposes",
    "in order to",
    "due to the fact that",
    "at this point in time",
    "in the event that",
    "by the same token",
    # Vietnamese filler phrases
    "như chúng ta đã biết",
    "trong thời đại ngày nay",
    "không thể phủ nhận rằng",
    "tóm lại có thể nói rằng",
)

_AI_PATTERNS = (
    "delve into",
    "delving into",
    "tapestry of",
    "testament to",
    "underscores the importance",
    "navigating the complexities",
    "ever-evolving landscape",
    "it's important to note",
    "it is worth noting",
    "moreover,",
    "furthermore,",
    "in conclusion,",
    "to sum up,",
    "ultimately,",
    "unlock the power of",
    "unleash the potential",
    "game-changer",
    "game changing",
    "leverage the power",
    "seamless integration",
    "cutting-edge",
    "state-of-the-art",
    "holistic approach",
    "paradigm shift",
    "synergy",
    "pivotal role",
    "beacon of",
    "symphony of",
    "foster innovation",
    "empower",
)

_WORD_RE = re.compile(r"[A-Za-zÀ-ỹ0-9']+")
_NUMBER_RE = re.compile(
    r"\b\d+(?:\.\d+)?(?:\s*%|\s*(?:k|m|b|million|billion|trillion|ms|s|x|yr|years|ngày|tháng|năm|triệu|tỷ|nghìn|km|m2|usd|vnd|đ))?\b",
    re.IGNORECASE,
)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _strip_markup(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    return text


def _count_phrases(lowered: str, phrases: tuple[str, ...]) -> tuple[int, list[dict]]:
    hits: list[dict] = []
    total = 0
    for p in phrases:
        c = len(re.findall(r"\b" + re.escape(p).replace(r"\ ", r"\s+"), lowered))
        if c:
            hits.append({"phrase": p, "count": c})
            total += c
    hits.sort(key=lambda h: h["count"], reverse=True)
    return total, hits


def score_qrg_quality(raw_text: str) -> dict:
    """Compute QRG §4.6 content quality scores."""
    text = _strip_markup(raw_text or "")
    words = _WORD_RE.findall(text)
    word_count = len(words)
    if word_count == 0:
        return {
            "word_count": 0,
            "sentence_count": 0,
            "filler_score": 0,
            "ai_pattern_score": 0,
            "information_density": 0,
            "repetition_score": 0,
            "overall_quality": 0,
            "findings": ["Empty input."],
            "filler_hits": [],
            "ai_pattern_hits": [],
        }

    lowered = text.lower()
    sentences = [s for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    sentence_count = max(len(sentences), 1)

    filler_total, filler_hits = _count_phrases(lowered, _FILLER_PHRASES)
    filler_per_1k = (filler_total / word_count) * 1000
    filler_score = min(100, round(filler_per_1k * 8.3))

    ai_total, ai_hits = _count_phrases(lowered, _AI_PATTERNS)
    ai_per_1k = (ai_total / word_count) * 1000
    ai_pattern_score = min(100, round(ai_per_1k * 10.0))

    number_count = len(_NUMBER_RE.findall(text))
    cap_tokens = 0
    for sent in sentences:
        sent_words = _WORD_RE.findall(sent)
        for w in sent_words[1:]:
            if w[0].isupper() and len(w) > 1:
                cap_tokens += 1
    info_signals_per_100 = ((number_count + cap_tokens) / word_count) * 100
    information_density = min(100, round(info_signals_per_100 * 12.5))

    lower_words = [w.lower() for w in words]
    bigrams = list(zip(lower_words, lower_words[1:]))
    if bigrams:
        counts = Counter(bigrams)
        repeated = sum(c - 1 for c in counts.values() if c > 2)
        rep_ratio = repeated / len(bigrams)
        repetition_score = min(100, round(rep_ratio * 500))
    else:
        repetition_score = 0

    overall = (
        0.30 * (100 - ai_pattern_score)
        + 0.25 * (100 - filler_score)
        + 0.30 * information_density
        + 0.15 * (100 - repetition_score)
    )
    overall_quality = max(0, min(100, round(overall)))

    findings: list[str] = []
    if ai_pattern_score >= 40:
        findings.append(
            f"High AI-pattern density ({ai_total} hits across {word_count} words). "
            "QRG §4.6.6 flags paraphrased/AI-generated phrasing."
        )
    if filler_score >= 40:
        findings.append(
            f"Heavy filler phrasing ({filler_total} hits). "
            "QRG §4.6 penalizes low-effort filler that delays the main answer."
        )
    if information_density < 30:
        findings.append(
            "Low information density (few concrete numbers or named entities). "
            "Add specific figures, named sources, or verifiable examples."
        )
    if repetition_score >= 40:
        findings.append(
            "High bigram repetition. Vary phrasing and cut redundant restatements."
        )
    if word_count < 300:
        findings.append(
            f"Thin content ({word_count} words). Consider expanding or consolidating."
        )

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "filler_score": filler_score,
        "ai_pattern_score": ai_pattern_score,
        "information_density": information_density,
        "repetition_score": repetition_score,
        "overall_quality": overall_quality,
        "findings": findings,
        "filler_hits": filler_hits[:10],
        "ai_pattern_hits": ai_hits[:10],
    }


# --------------------------------------------------------------------------- #
# Claim Extractor & Citation-Gap Verifier (from content_verify.py)
# --------------------------------------------------------------------------- #
_CLAIM_PATTERNS: tuple[tuple[re.Pattern, str], ...] = (
    (re.compile(r"\b\d+(?:\.\d+)?\s*%\s+of\s+[a-zA-Z]+(?:\s+[a-zA-Z]+){0,4}", re.IGNORECASE), "statistic"),
    (re.compile(r"\b\d+(?:\.\d+)?\s*%\b"), "statistic"),
    (re.compile(r"\$\s?\d+(?:\.\d+)?\s*(?:million|billion|trillion|k|M|B)\b", re.IGNORECASE), "quantity"),
    (re.compile(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\s+\w+", re.IGNORECASE), "quantity"),
    (re.compile(r"\b\d+(?:\.\d+)?\s*(?:million|billion|trillion)\b", re.IGNORECASE), "quantity"),
    (re.compile(r"\baccording\s+to\s+(?:a\s+)?(?:[A-Z][a-z]+\s+){1,4}(?:study|report|survey|analysis|paper)\b"), "authority"),
    (re.compile(r"\b(?:Forrester|Gartner|McKinsey|Pew|Nielsen|Statista|Deloitte|Edelman|MIT|Stanford|Harvard|Wharton)\s+(?:said|reports?|found|noted)", re.IGNORECASE), "authority"),
    (re.compile(r"\bin\s+(?:19|20)\d{2}\b"), "temporal"),
    (re.compile(r"\bby\s+20\d{2}\b"), "temporal"),
    (re.compile(r"\b\d+(?:\.\d+)?\s*(?:x|times)\s+(?:more|less|faster|slower|higher|lower|better|worse)\b", re.IGNORECASE), "comparative"),
    (re.compile(r"\b(?:twice|thrice|half)\s+as\s+\w+", re.IGNORECASE), "comparative"),
)

_CITATION_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\[[^\]]+\]\(https?://[^)]+\)"),
    re.compile(r"<a\s+[^>]*href=[\"']https?://[^\"']+[\"']"),
    re.compile(r"\[\^?\d+\]"),
    re.compile(r"@type\s*:\s*[\"']Citation[\"']"),
    re.compile(
        r"\b(?:source\s*:|via\s*:|see\s+also\s*:|cited\s+(?:in|by)|according\s+to|per|theo\s+báo\s+cáo|nguồn\s*:)\s+[A-ZÀ-Ỹ]",
        re.IGNORECASE,
    ),
)


def _has_citation_near(text: str, position: int, window: int = 200) -> str | None:
    start = max(0, position - window)
    end = min(len(text), position + window)
    snippet = text[start:end]
    for pattern in _CITATION_PATTERNS:
        m = pattern.search(snippet)
        if m:
            return m.group(0)[:80]
    return None


def extract_claims(text: str) -> List[Dict]:
    found_spans: list[tuple[int, int, str]] = []
    for pattern, label in _CLAIM_PATTERNS:
        for m in pattern.finditer(text or ""):
            if any(s <= m.start() < e or s < m.end() <= e for s, e, _ in found_spans):
                continue
            found_spans.append((m.start(), m.end(), label))

    claims: list[dict] = []
    for start, end, label in sorted(found_spans):
        cite = _has_citation_near(text, start)
        claims.append({
            "text": text[start:end].strip(),
            "kind": label,
            "position": start,
            "has_citation": cite is not None,
            "nearby_citation": cite,
        })
    return claims


def verify_claims(text: str) -> dict:
    claims = extract_claims(text)
    uncited = [c for c in claims if not c["has_citation"]]
    return {
        "claims": claims,
        "claim_count": len(claims),
        "uncited_count": len(uncited),
        "uncited_ratio": round(len(uncited) / len(claims), 3) if claims else 0.0,
    }
