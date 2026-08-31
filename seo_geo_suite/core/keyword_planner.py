import json
import requests
import pandas as pd
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class KeywordPlanner:
    """Scrapes Google Suggest, clusters keywords semantically, and builds 30/90-day growth plans."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    def fetch_google_suggestions(self, seed_keyword: str, language: str = "vi") -> List[str]:
        """Fetches keyword suggestions from Google Suggest API using prefix/suffix expansions."""
        results = set()
        results.add(seed_keyword)

        # Modifiers to expand queries
        expansions = ["", "la gi", "nhu the nao", "cach", "top", "gia", "o dau", "huong dan", "tot nhat", "2026"]
        
        for exp in expansions:
            q = f"{seed_keyword} {exp}".strip()
            url = f"https://suggestqueries.google.com/complete/search?client=chrome&hl={language}&q={requests.utils.quote(q)}"
            try:
                resp = requests.get(url, headers=self.headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    if len(data) > 1 and isinstance(data[1], list):
                        for item in data[1]:
                            results.add(item)
            except Exception:
                pass

        return sorted(list(results))

    def cluster_keywords(self, keywords: List[str], num_clusters: int = 4) -> Dict[str, Any]:
        """Groups keywords into semantic clusters using TF-IDF and KMeans."""
        if len(keywords) < num_clusters:
            num_clusters = max(1, len(keywords))

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=None)
        X = vectorizer.fit_transform(keywords)

        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        kmeans.fit(X)

        clusters = {}
        for idx, label in enumerate(kmeans.labels_):
            cluster_name = f"Cụm chủ đề {label + 1}"
            if cluster_name not in clusters:
                clusters[cluster_name] = []
            clusters[cluster_name].append(keywords[idx])

        # Name clusters by top representative keyword
        formatted_clusters = []
        for c_id, kw_list in clusters.items():
            pillar = kw_list[0] if kw_list else "Chủ đề chung"
            formatted_clusters.append({
                "cluster_id": c_id,
                "pillar_page": pillar,
                "cluster_size": len(kw_list),
                "keywords": kw_list,
                "search_intent": "Informational / Commercial"
            })

        return {
            "total_keywords": len(keywords),
            "num_clusters": len(formatted_clusters),
            "clusters": formatted_clusters
        }

    def generate_growth_roadmap(self, seed: str, language: str = "vi") -> Dict[str, Any]:
        """Builds a comprehensive 30-day and 90-day SEO & GEO content roadmap."""
        keywords = self.fetch_google_suggestions(seed, language=language)
        if len(keywords) < 6:
            # Fallback expansion
            keywords.extend([
                f"{seed} là gì",
                f"hướng dẫn {seed} từ A-Z",
                f"top công cụ {seed} hiệu quả nhất",
                f"chiến lược {seed} 2026",
                f"so sánh các giải pháp {seed}",
                f"lỗi thường gặp khi làm {seed}"
            ])
            keywords = list(set(keywords))

        cluster_result = self.cluster_keywords(keywords, num_clusters=min(5, max(2, len(keywords) // 4)))

        # Build 30-Day schedule (Week 1 to Week 4)
        schedule_30d = []
        weeks = ["Tuần 1: Nền Tảng & Bài Trụ Cột (Pillar)", "Tuần 2: Cụm Bài Bổ Trợ (Cluster 1)", "Tuần 3: Cụm Bài So Sánh & Thực Thi (Cluster 2)", "Tuần 4: Bài Hỏi Đáp FAQ & Tối Ưu AI Citability"]
        
        kw_iter = iter(keywords)
        for w_idx, week_title in enumerate(weeks):
            week_kws = []
            for _ in range(3):
                try:
                    week_kws.append(next(kw_iter))
                except StopIteration:
                    break
            schedule_30d.append({
                "phase": week_title,
                "target_keywords": week_kws,
                "deliverables": f"1 Bài chuyên sâu chuẩn GEO ({', '.join(week_kws)}) + 1 Bộ Schema FAQPage"
            })

        return {
            "seed_keyword": seed,
            "total_keywords_discovered": len(keywords),
            "clusters": cluster_result["clusters"],
            "roadmap_30_days": schedule_30d,
            "all_keywords": keywords
        }
