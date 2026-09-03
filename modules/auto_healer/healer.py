"""
Auto 404 Healer & Fuzzy 301 Redirect Engine
Scans for 404 errors, computes string distance with existing posts,
and maps dead links to live URLs with 301 Permanent Redirects.
"""

import difflib
import re
from typing import List, Dict, Any, Optional, Tuple

class Auto404Healer:
    def __init__(self, min_similarity: float = 0.40):
        self.min_similarity = min_similarity

    def find_best_match(self, broken_path: str, existing_posts: List[Dict[str, Any]]) -> Optional[Tuple[Dict[str, Any], float]]:
        """
        Extracts slug from broken_path and finds the best matching post.
        """
        # Clean path into clean slug words
        clean_path = broken_path.strip("/").split("?")[0]
        slug_query = clean_path.split("/")[-1].lower().replace("-", " ")
        
        best_post = None
        highest_score = 0.0

        for post in existing_posts:
            post_slug = post.get("slug", "").replace("-", " ").lower()
            post_title = (post.get("title", {}).get("rendered", "") if isinstance(post.get("title"), dict) else str(post.get("title", ""))).lower()
            
            # Compute similarity ratio against slug and title
            score_slug = difflib.SequenceMatcher(None, slug_query, post_slug).ratio()
            score_title = difflib.SequenceMatcher(None, slug_query, post_title).ratio()
            score = max(score_slug, score_title)

            # Boost if main entity word matches
            query_words = set(slug_query.split())
            post_words = set(post_slug.split())
            common_words = query_words.intersection(post_words)
            if len(common_words) >= 2:
                score += 0.15

            if score > highest_score and score >= self.min_similarity:
                highest_score = score
                best_post = post

        if best_post:
            return best_post, min(highest_score, 1.0)
        return None
