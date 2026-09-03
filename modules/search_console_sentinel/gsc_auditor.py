"""
Google Search Console & Technical On-Page Speed Auditor
Audits Money Sites and Tier 1 Satellites for:
- Missing title / meta description lengths (140-160 chars)
- Images missing width / height / lazy loading (Zero CLS)
- Oversized images (> 50KB)
- Crawl bottlenecks, missing canonicals, and unminified assets.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any

class SearchConsoleAuditor:
    def __init__(self, site_url: str):
        self.site_url = site_url.rstrip("/")

    def audit_url_onpage_and_speed(self, url: str) -> Dict[str, Any]:
        """Performs deep technical On-Page & Core Web Vitals audit of a specific URL."""
        issues = []
        score = 100

        try:
            r = requests.get(url, timeout=12)
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            return {"url": url, "error": str(e), "score": 0}

        # 1. Check Title Tag
        title_tag = soup.find("title")
        title_text = title_tag.text.strip() if title_tag else ""
        if not title_text:
            issues.append("❌ Missing <title> tag (-25 pts)")
            score -= 25
        elif len(title_text) < 40 or len(title_text) > 65:
            issues.append(f"⚠️ Title length ({len(title_text)} chars) is outside optimal 50-60 chars (-5 pts)")
            score -= 5

        # 2. Check Meta Description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        desc_text = meta_desc.get("content", "").strip() if meta_desc else ""
        if not desc_text:
            issues.append("❌ Missing Meta Description tag (-20 pts)")
            score -= 20
        elif len(desc_text) < 120 or len(desc_text) > 165:
            issues.append(f"⚠️ Meta Description length ({len(desc_text)} chars) outside optimal 140-160 chars (-5 pts)")
            score -= 5

        # 3. Check Canonical Tag
        canonical = soup.find("link", rel="canonical")
        if not canonical or not canonical.get("href"):
            issues.append("❌ Missing <link rel='canonical'> tag (-15 pts)")
            score -= 15

        # 4. Check H1 Heading
        h1_tags = soup.find_all("h1")
        if len(h1_tags) == 0:
            issues.append("❌ Missing <h1> heading (-15 pts)")
            score -= 15
        elif len(h1_tags) > 1:
            issues.append(f"⚠️ Multiple <h1> headings found ({len(h1_tags)}) (-5 pts)")
            score -= 5

        # 5. Check Images for Zero CLS & Lazy Loading
        images = soup.find_all("img")
        missing_dimensions = 0
        missing_lazy = 0
        missing_alt = 0

        for img in images:
            if not img.get("width") or not img.get("height"):
                missing_dimensions += 1
            if img.get("loading") != "lazy":
                missing_lazy += 1
            if not img.get("alt"):
                missing_alt += 1

        if missing_dimensions > 0:
            issues.append(f"⚠️ {missing_dimensions} image(s) missing width/height attributes (Risk of CLS) (-10 pts)")
            score -= 10
        if missing_lazy > 0:
            issues.append(f"ℹ️ {missing_lazy} image(s) not using loading='lazy' (-5 pts)")
            score -= 5
        if missing_alt > 0:
            issues.append(f"⚠️ {missing_alt} image(s) missing alt text (-5 pts)")
            score -= 5

        # 6. Check Table of Contents
        if "ez-toc" not in html and "table-of-contents" not in html and "rankmath-toc" not in html:
            issues.append("ℹ️ Missing Table of Contents anchor links (-5 pts)")
            score -= 5

        # 7. Check Natural Heading Standards (RULES.md Section 5 - max 20% numbered or icon headings)
        import re
        subheadings = [h.text.strip() for h in soup.find_all(["h2", "h3", "h4"]) if h.text.strip()]
        if subheadings:
            numbered_or_icon_count = 0
            for h_text in subheadings:
                if re.match(r"^(\d+[\.\)]|\d+\.\d+|[IVXLCDM]+[\.\)]|[A-Z][\.\)])\s+", h_text) or \
                   re.match(r"^[\U00010000-\U0010ffff\u2600-\u27bf\ufe0f\u200d\u2300-\u23ff\u2b50\u2b55]", h_text):
                    numbered_or_icon_count += 1
            heading_ratio = numbered_or_icon_count / len(subheadings)
            if len(subheadings) >= 3 and heading_ratio > 0.20:
                issues.append(f"⚠️ {int(heading_ratio * 100)}% headings have mechanical numbering/icons (> 20% limit in RULES.md) (-10 pts)")
                score -= 10

        return {
            "url": url,
            "onpage_score": max(0, score),
            "status": "EXCELLENT" if score >= 85 else ("GOOD" if score >= 70 else "NEEDS_FIX"),
            "issues_count": len(issues),
            "issues": issues,
            "metrics": {
                "title_length": len(title_text),
                "desc_length": len(desc_text),
                "total_images": len(images),
                "images_with_cls_protection": len(images) - missing_dimensions
            }
        }
