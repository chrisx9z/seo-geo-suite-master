"""
Keyword Cannibalization Detector & Resolver Engine
Scans all website posts and calculates pairwise semantic overlap
to identify cannibalization risks where two pages compete for identical intent.
"""

import difflib
from typing import List, Dict, Any

class KeywordCannibalizationDetector:
    def __init__(self, risk_threshold: float = 0.65):
        self.risk_threshold = risk_threshold

    def analyze_site_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes pairwise title and slug similarity across all posts.
        Returns a list of high-risk cannibalization conflicts with actionable remedies.
        """
        conflicts = []
        n = len(posts)

        for i in range(n):
            for j in range(i + 1, n):
                p1 = posts[i]
                p2 = posts[j]

                title1 = p1.get("title", {}).get("rendered", "") if isinstance(p1.get("title"), dict) else str(p1.get("title", ""))
                title2 = p2.get("title", {}).get("rendered", "") if isinstance(p2.get("title"), dict) else str(p2.get("title", ""))
                slug1 = p1.get("slug", "")
                slug2 = p2.get("slug", "")

                # Similarity
                title_ratio = difflib.SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
                slug_ratio = difflib.SequenceMatcher(None, slug1.lower(), slug2.lower()).ratio()
                combined_score = max(title_ratio, slug_ratio)

                if combined_score >= self.risk_threshold:
                    conflicts.append({
                        "post_a": {"id": p1.get("id"), "title": title1, "slug": slug1, "link": p1.get("link")},
                        "post_b": {"id": p2.get("id"), "title": title2, "slug": slug2, "link": p2.get("link")},
                        "conflict_score": round(combined_score, 3),
                        "risk_level": "CRITICAL" if combined_score >= 0.8 else "HIGH",
                        "recommendation": (
                            "Gộp bài viết (Content Consolidation) thành 1 Pillar Post toàn diện, "
                            f"hoặc đặt thẻ rel='canonical' từ bài {p2.get('id')} trỏ về bài chính {p1.get('id')}."
                        )
                    })

        # Sort conflicts descending by score
        conflicts.sort(key=lambda x: x["conflict_score"], reverse=True)
        return conflicts
