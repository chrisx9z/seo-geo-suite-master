# -*- coding: utf-8 -*-
"""
Tech Image Fetcher Engine
Fetches authentic, high-resolution photography for AI, Tech, Software, and Server topics
from Wikimedia Commons & curated photo repositories.
Enforces:
- Real authentic photography (hardware, GPU, servers, programming, workspaces)
- ZERO artificial text-card banners
- Standardized 16:9 Zero-CLS WebP (1200x675) format (< 80KB)
"""

import os
import re
import sys
import random
import unicodedata
import requests
from typing import List, Dict, Optional, Any
from PIL import Image

TECH_KEYWORD_QUERY_MAP = {
    "local llm": "NVIDIA GPU workstation",
    "ollama": "NVIDIA GPU workstation",
    "llama": "NVIDIA GPU workstation",
    "deepseek": "Supercomputer cluster",
    "qwen": "Supercomputer cluster",
    "gpu": "NVIDIA GPU graphics card",
    "vram": "NVIDIA GPU graphics card",
    "ai agent": "Modern computer workstation office",
    "tro ly ai": "Modern computer workstation office",
    "computer use": "Computer programming code screen",
    "n8n": "Data center server rack",
    "dify": "Modern computer workstation office",
    "automation": "Data center server rack",
    "saas": "Modern computer workstation office",
    "micro saas": "Modern computer workstation office",
    "shorts": "Video camera studio digital",
    "video": "Video editing console screen",
    "kiem tien": "Financial stock market screen office",
    "mmo": "Modern computer workstation office",
    "cloud": "Cloud server data center room",
    "vps": "Server rack data center",
    "linux": "Linux command line terminal computer",
    "docker": "Server rack data center",
    "fastapi": "Computer programming code monitor",
    "python": "Computer programming code monitor",
    "ranking": "Modern computer workstation office",
    "seo": "Modern computer workstation office",
    "indexing": "Data center server rack"
}

GENERAL_TECH_QUERIES = [
    "NVIDIA GPU workstation",
    "Computer programming code monitor",
    "Data center server rack",
    "Modern computer workstation office",
    "Supercomputer cluster",
    "Semiconductor microprocessor wafer",
    "Electronics circuit board motherboard"
]

def remove_accents(input_str: str) -> str:
    s = input_str.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).strip()

class TechImageFetcher:
    def __init__(self, cache_dir: Optional[str] = None):
        self.headers = {"User-Agent": "VibeMMOBot/2.0 (contact@vibemmo.net; enterprise seo)"}
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.cache_dir = cache_dir or os.path.join(base_dir, "cache", "tech_images")
        os.makedirs(self.cache_dir, exist_ok=True)

    def extract_search_queries(self, topic: str, focus_keyword: str = "") -> List[str]:
        queries = []
        combined = f"{focus_keyword} {topic}".lower()
        clean_text = remove_accents(combined)

        for trigger, q in TECH_KEYWORD_QUERY_MAP.items():
            if trigger in combined or trigger in clean_text:
                if q not in queries:
                    queries.append(q)

        # Fallback queries
        for gq in GENERAL_TECH_QUERIES:
            if gq not in queries:
                queries.append(gq)

        return queries

    def search_wikimedia_images(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        search_url = "https://commons.wikimedia.org/w/api.php"
        s_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srnamespace": "6",
            "srlimit": str(limit)
        }
        try:
            r = requests.get(search_url, params=s_params, headers=self.headers, timeout=12)
            if r.status_code != 200:
                return []
            data = r.json()
            items = data.get("query", {}).get("search", [])
            valid_titles = [x["title"] for x in items if any(x["title"].lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"])]
            if not valid_titles:
                return []

            info_params = {
                "action": "query",
                "titles": "|".join(valid_titles[:6]),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "format": "json"
            }
            r_info = requests.get(search_url, params=info_params, headers=self.headers, timeout=12)
            if r_info.status_code != 200:
                return []

            results = []
            for p in r_info.json().get("query", {}).get("pages", {}).values():
                inf = p.get("imageinfo", [{}])[0]
                w = inf.get("width", 0)
                h = inf.get("height", 0)
                u = inf.get("url", "")
                if w >= 800 and h >= 500 and u:
                    results.append({
                        "title": p.get("title", "").replace("File:", ""),
                        "url": u,
                        "width": w,
                        "height": h
                    })
            return results
        except Exception as e:
            print(f"[-] Wikimedia search error for '{query}': {e}")
            return []

    def download_and_optimize(self, image_url: str, output_name: str) -> Optional[str]:
        try:
            out_file = os.path.join(self.cache_dir, f"{output_name}.webp")
            if os.path.exists(out_file) and os.path.getsize(out_file) > 10000:
                return out_file

            temp_raw = os.path.join(self.cache_dir, f"temp_{output_name}.raw")
            r = requests.get(image_url, headers=self.headers, timeout=25)
            if r.status_code != 200 or len(r.content) < 5000:
                return None

            with open(temp_raw, "wb") as f:
                f.write(r.content)

            img = Image.open(temp_raw)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            w, h = img.size
            target_ratio = 16 / 9
            current_ratio = w / h

            if current_ratio > target_ratio:
                new_w = int(h * target_ratio)
                left = (w - new_w) // 2
                img = img.crop((left, 0, left + new_w, h))
            else:
                new_h = int(w / target_ratio)
                top = (h - new_h) // 2
                img = img.crop((0, top, w, top + new_h))

            img = img.resize((1200, 675), Image.Resampling.LANCZOS)
            img.save(out_file, "WEBP", quality=82)

            if os.path.exists(temp_raw):
                os.remove(temp_raw)

            print(f"  [+] Optimized real photo: {os.path.basename(out_file)} ({os.path.getsize(out_file)/1024:.1f} KB)")
            return out_file
        except Exception as e:
            print(f"[-] Error processing image {image_url}: {e}")
            return None

    def get_real_photo_for_post(self, topic: str, focus_keyword: str, slug: str, seed_index: int = 0) -> Optional[Dict[str, str]]:
        queries = self.extract_search_queries(topic, focus_keyword)
        candidates = []
        for q in queries:
            photos = self.search_wikimedia_images(q, limit=8)
            if photos:
                candidates.extend(photos)
            if len(candidates) >= 5:
                break

        if not candidates:
            candidates = self.search_wikimedia_images("Modern computer workstation office", limit=6)

        if not candidates:
            return None

        # Pick photo based on seed_index
        selected = candidates[seed_index % len(candidates)]
        filename = f"{slug}-featured"
        local_path = self.download_and_optimize(selected["url"], filename)
        if not local_path:
            return None

        clean_title = re.sub(r"[_\-\.]+", " ", selected["title"]).strip()
        return {
            "local_path": local_path,
            "alt_text": f"{topic} - Ảnh minh họa thực tế {clean_title}"[:100],
            "title": f"{topic} Featured Image"
        }
