# -*- coding: utf-8 -*-
"""
Semantic Silo, Topic Cluster & True Orphan Page Graph Builder (v2.5 Vietnamese & English Aware)
Constructs mathematical topic clusters from post titles, focus keywords, categories, and slugs;
identifies Pillar Posts vs Cluster Posts; and parses actual `<a href="...">` internal links
across post bodies to compute real In-Degree / Out-Degree and detect true Orphan Pages (`in_degree == 0`).
"""
from __future__ import annotations

import html
import math
import re
import unicodedata
from collections import Counter
from typing import Any, Dict, List, Set, Tuple

_STOP_PHRASES = (
    "kinh nghiem", "huong dan", "cam nang", "chi tiet", "toan dien", "tong hop",
    "complete guide", "ultimate guide", "how to",
)

_STOPWORDS = {
    "va", "cua", "cho", "cac", "nhung", "mot", "la", "co", "tai", "voi", "trong", "khi",
    "nao", "gi", "moi", "nhat", "2024", "2025", "2026", "top", "hay", "dep", "cach",
    "review", "tu", "den", "the", "and", "for", "with", "guide", "best", "complete",
    "ultimate", "how", "what", "from", "into", "ve", "nay", "do", "nhu", "nen",
}


def _fold_ascii(text: str) -> str:
    s = html.unescape(re.sub(r"<[^>]+>", " ", str(text or "")))
    s = s.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", s)
    folded = "".join(c for c in nfkd if not unicodedata.combining(c)).lower()
    folded = re.sub(r"[^a-z0-9\s]", " ", folded)
    folded = re.sub(r"\s+", " ", folded).strip()
    for phrase in _STOP_PHRASES:
        folded = re.sub(rf"\b{re.escape(phrase)}\b", " ", folded)
    return re.sub(r"\s+", " ", folded).strip()


class SemanticSiloBuilder:
    def __init__(self, cluster_threshold: float = 0.22):
        self.cluster_threshold = cluster_threshold

    def _tokenize(self, text: str) -> List[str]:
        folded = _fold_ascii(text)
        folded = re.sub(r"[^a-z0-9\s]", " ", folded)
        # Keep 2+ character words so Vietnamese core tokens ("da", "nang", "ai", "loi", "hue") are preserved
        return [w for w in folded.split() if len(w) >= 2 and w not in _STOPWORDS]

    @staticmethod
    def _cosine_similarity(vec1: Counter, vec2: Counter) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        if not intersection:
            return 0.0
        numerator = sum(vec1[x] * vec2[x] for x in intersection)
        sum1 = sum(v * v for v in vec1.values())
        sum2 = sum(v * v for v in vec2.values())
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        return (float(numerator) / denominator) if denominator else 0.0

    @staticmethod
    def _extract_title(p: Dict[str, Any]) -> str:
        t = p.get("title", {}).get("rendered", "") if isinstance(p.get("title"), dict) else str(p.get("title", ""))
        return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()

    @staticmethod
    def _extract_body(p: Dict[str, Any]) -> str:
        c = p.get("content", {}).get("rendered", "") if isinstance(p.get("content"), dict) else str(p.get("content", ""))
        return c or ""

    def compute_internal_link_graph(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parses `<a href="...">` inside every post's HTML content to compute exact
        `in_degree`, `out_degree`, and true Orphan Pages (`in_degree == 0`).
        """
        slug_to_id: Dict[str, Any] = {}
        id_to_post: Dict[Any, Dict[str, Any]] = {}
        in_links: Dict[Any, Set[Any]] = {}
        out_links: Dict[Any, Set[Any]] = {}

        for p in posts:
            pid = p.get("id")
            if pid is None:
                continue
            id_to_post[pid] = p
            in_links[pid] = set()
            out_links[pid] = set()
            slug = str(p.get("slug") or "").strip("/").lower()
            if slug:
                slug_to_id[slug] = pid
            link = str(p.get("link") or "").rstrip("/")
            if link:
                tail = link.split("/")[-1].lower()
                if tail:
                    slug_to_id[tail] = pid

        href_re = re.compile(r'<a[^>]+href=["\']([^"\'#\?]+)', re.IGNORECASE)
        for p in posts:
            src_id = p.get("id")
            if src_id is None:
                continue
            body = self._extract_body(p)
            for m in href_re.finditer(body):
                href = m.group(1).strip().rstrip("/")
                if not href:
                    continue
                tail_slug = href.split("/")[-1].lower()
                dst_id = slug_to_id.get(tail_slug)
                if dst_id is not None and dst_id != src_id:
                    out_links[src_id].add(dst_id)
                    in_links[dst_id].add(src_id)

        true_orphans = [
            {
                "id": pid,
                "title": self._extract_title(id_to_post[pid]),
                "slug": id_to_post[pid].get("slug", ""),
                "link": id_to_post[pid].get("link", ""),
                "out_degree": len(out_links[pid]),
            }
            for pid in id_to_post
            if len(in_links[pid]) == 0
        ]

        return {
            "in_degree": {pid: len(s) for pid, s in in_links.items()},
            "out_degree": {pid: len(s) for pid, s in out_links.items()},
            "true_orphan_count": len(true_orphans),
            "true_orphan_posts": true_orphans,
        }

    def build_cluster_graph(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Groups posts into semantic clusters based on Vietnamese/English token cosine similarity,
        determines Pillar Posts, and computes both semantic orphans and link-graph orphans.
        """
        post_vectors = {}
        post_lookup = {}
        for p in posts:
            pid = p["id"]
            post_lookup[pid] = p
            title = self._extract_title(p)
            slug = str(p.get("slug", "")).replace("-", " ")
            meta = p.get("meta") if isinstance(p.get("meta"), dict) else {}
            fkw = p.get("focus_keyword") or (meta or {}).get("rank_math_focus_keyword") or ""
            tokens = self._tokenize(f"{title} {slug} {fkw}")
            post_vectors[pid] = Counter(tokens)

        connections: Dict[Any, List[Tuple[Any, float]]] = {p["id"]: [] for p in posts}
        post_ids = list(post_vectors.keys())

        for i in range(len(post_ids)):
            for j in range(i + 1, len(post_ids)):
                id1, id2 = post_ids[i], post_ids[j]
                sim = self._cosine_similarity(post_vectors[id1], post_vectors[id2])
                if sim >= self.cluster_threshold:
                    connections[id1].append((id2, round(sim, 2)))
                    connections[id2].append((id1, round(sim, 2)))

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
                    pillar_id = max(component, key=lambda x: len(connections[x]))
                    pillar_post = post_lookup[pillar_id]
                    cluster_posts = [post_lookup[x] for x in component if x != pillar_id]
                    clusters.append({
                        "pillar_post": {
                            "id": pillar_id,
                            "title": self._extract_title(pillar_post),
                            "slug": pillar_post.get("slug", ""),
                            "link": pillar_post.get("link", ""),
                        },
                        "cluster_size": len(component),
                        "cluster_members": [
                            {
                                "id": cp["id"],
                                "title": self._extract_title(cp),
                                "slug": cp.get("slug", ""),
                                "link": cp.get("link", ""),
                            }
                            for cp in cluster_posts
                        ],
                    })

        orphans = [
            {
                "id": pid,
                "title": self._extract_title(post_lookup[pid]),
                "slug": post_lookup[pid].get("slug", ""),
                "link": post_lookup[pid].get("link", ""),
            }
            for pid in post_ids
            if len(connections[pid]) == 0
        ]

        link_graph = self.compute_internal_link_graph(posts)

        return {
            "total_posts": len(posts),
            "total_clusters": len(clusters),
            "clusters": clusters,
            "orphan_posts_count": len(orphans),
            "orphan_posts": orphans,
            "link_graph": link_graph,
        }

    @staticmethod
    def build_related_cluster_box_html(related_posts: List[Dict[str, Any]], lang: str = "vi") -> str:
        """Generates a clean semantic HTML related-reading cluster box to rescue Orphan Pages."""
        valid = [p for p in related_posts if p.get("link") and p.get("title")]
        if not valid:
            return ""
        heading = "Related In-Depth Guides" if lang.startswith("en") else "Bài Viết Chuyên Sâu Cùng Chủ Đề"
        items_html = []
        for p in valid[:4]:
            t = html.escape(str(p["title"]).strip())
            u = html.escape(str(p["link"]).strip())
            items_html.append(f'  <li style="margin:6px 0;"><a href="{u}" class="autolink-cluster">{t}</a></li>')
        return (
            '<div class="asg-topic-cluster-box" style="background:#f8fafc;border-left:4px solid #0284c7;'
            'padding:14px 18px;margin:22px 0;border-radius:6px;">\n'
            f'  <p style="margin:0 0 8px 0;font-weight:700;color:#0f172a;">📚 {heading}:</p>\n'
            '  <ul style="margin:0;padding-left:20px;">\n'
            + "\n".join(items_html)
            + "\n  </ul>\n</div>"
        )
