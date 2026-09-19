"""
Content Auditor Module for Master Auto SEO GEO Suite
Audits WordPress content against repo rules:
- Image density (1 image per 500 words)
- Featured image presence
- Word count & Thin content (min 1000 words)
- Natural headings (max 20% numbered or icon headings)
- Rule 1: No marketing voice (buzzwords, hype)
- Rule 2 & 4: Specificity & concrete details
- Rule 3: Sentence rhythm variation
- Rule 5: Conversational tone
- Rule 6: Anti-AI fingerprints (cliché leads, filler transitions, redundant conclusions)
"""

from .auditor import ContentAuditor

__all__ = ["ContentAuditor"]
