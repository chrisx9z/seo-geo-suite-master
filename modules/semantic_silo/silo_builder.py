"""
Semantic Silo & Topic Cluster Graph Builder
Constructs mathematical topic clusters from post titles and content,
identifies Pillar Posts vs Cluster Posts, and detects isolated Orphan Pages.
"""

import math
import re
from collections import Counter
from typing import List, Dict, Any, Tuple

class SemanticSiloBuilder:
    def __init__(self, cluster_threshold: float = 0.20):
        self.cluster_threshold = cluster_threshold

    def _tokenize(self, text: str) -> List[str]:
        text = re.sub(r"[\(\)\[\]\{\}\:\?\!\|\,\.\"\']", " ", text.lower())
        words = [w.strip() for w in text.split() if len(w.strip()) > 3]
        return words

    def _cosine_similarity(self, vec1: Counter, vec2: Counter) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
        sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        return float(numerator) / denominator

    def build_cluster_graph(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Groups posts into clusters based on TF-IDF cosine similarity.
        Determines the Pillar Post (highest degree centrality) and detects Orphan Pages.
        """
        post_vectors = {}
        for p in posts:
            title = p.get("title", {}).get("rendered", "") if isinstance(p.get("title"), dict) else str(p.get("title", ""))
            slug = p.get("slug", "").replace("-", " ")
            tokens = self._tokenize(title + " " + slug)
            post_vectors[p["id"]] = Counter(tokens)

        # Compute adjacency matrix
        connections = {p["id"]: [] for p in posts}
        post_lookup = {p["id"]: p for p in posts}

        post_ids = list(post_vectors.keys())
        for i in range(len(post_ids)):
            for j in range(i + 1, len(post_ids)):
                id1 = post_ids[i]
                id2 = post_ids[j]
                sim = self._cosine_similarity(post_vectors[id1], post_vectors[id2])
                if sim >= self.cluster_threshold:
                    connections[id1].append((id2, round(sim, 2)))
                    connections[id2].append((id1, round(sim, 2)))

        # Categorize into Clusters and find Pillars
        visited = set()
        clusters = []

        for pid in post_ids:
            if pid not in visited:
                component = []
                queue = [pid]
                visited.add(pid)
                while queue:
                    curr = queue.pop(0)
                    component.append(curr)
                    for neighbor, _ in connections[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                if len(component) >= 2:
                    # Find Pillar Post in this cluster (the one with the most internal connections)
                    pillar_id = max(component, key=lambda x: len(connections[x]))
                    pillar_post = post_lookup[pillar_id]
                    cluster_posts = [post_lookup[x] for x in component if x != pillar_id]
                    clusters.append({
                        "pillar_post": {
                            "id": pillar_id,
                            "title": pillar_post.get("title", {}).get("rendered", ""),
                            "slug": pillar_post.get("slug", ""),
                            "link": pillar_post.get("link", "")
                        },
                        "cluster_size": len(component),
                        "cluster_members": [
                            {"id": cp["id"], "title": cp.get("title", {}).get("rendered", ""), "slug": cp.get("slug", "")}
                            for cp in cluster_posts
                        ]
                    })

        # Detect Orphan Pages (Posts with 0 connections)
        orphans = [
            {"id": pid, "title": post_lookup[pid].get("title", {}).get("rendered", ""), "slug": post_lookup[pid].get("slug", "")}
            for pid in post_ids if len(connections[pid]) == 0
        ]

        return {
            "total_posts": len(posts),
            "total_clusters": len(clusters),
            "clusters": clusters,
            "orphan_posts_count": len(orphans),
            "orphan_posts": orphans
        }
