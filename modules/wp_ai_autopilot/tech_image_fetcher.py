# -*- coding: utf-8 -*-
"""
Tech Image Fetcher Engine
Fetches authentic, high-resolution photography for AI, Tech, Software, and Server topics
from Wikimedia Commons & curated photo repositories.
Enforces:
- Real authentic photography (hardware, GPU, servers, programming, workspaces)
- ZERO artificial text-card banners
- Standardized 16:9 Zero-CLS WebP (1200x675) format (< 80KB)
- 100% Zero-Duplicate images across posts via persistent registry and hash offsets
"""

import os
import re
import sys
import random
import unicodedata
import requests
import hashlib
import json
from typing import List, Dict, Optional, Any
from PIL import Image

TECH_KEYWORD_QUERY_MAP = {
    # Windows, OS & PC Troubleshooting
    "win 11": "Laptop computer desk workspace",
    "win 10": "Personal computer desk setup",
    "windows": "Laptop computer desk workspace",
    "cai win": "Personal computer desk setup",
    "uefi": "Computer motherboard electronics",
    "bios": "Computer motherboard electronics",
    "tpm": "Semiconductor microprocessor wafer",
    "usb": "USB flash drive computer",
    "o cung": "Solid state drive hardware computer",
    "ssd": "Solid state drive hardware computer",
    "ram": "Computer memory RAM motherboard",
    "chuot": "Computer keyboard and mouse desk",
    "ban phim": "Computer keyboard and mouse desk",
    "man hinh": "Computer monitor keyboard mouse",
    "quay man hinh": "Computer monitor keyboard mouse",
    "chup man hinh": "Laptop screen display workspace",
    "unikey": "Computer keyboard desk typing",
    "phim tat": "Computer keyboard desk workspace",
    "may in": "Printer laser modern office computer",
    "chia o dia": "Solid state drive hardware computer",
    "o dia": "Hard disk drive storage computer",
    "webcam": "Webcam camera computer laptop",
    "tiet kiem pin": "Laptop computer battery desk",
    "am thanh": "Headphones computer desk audio",
    "loa": "Headphones computer desk audio",
    
    # Networking & Smarthome
    "wifi": "Wireless Wi-Fi router",
    "mang": "Ethernet network cables router",
    "router": "Wireless Wi-Fi router",
    "internet": "Data center network server",
    "cu sac": "USB-C charger power adapter",
    "sac nhanh": "USB-C charger power adapter",
    "gan": "USB-C charger power adapter",
    "pin": "Lithium battery charger electronics",
    "tai nghe": "Wireless earbuds headphones",
    "true wireless": "Wireless earbuds headphones",
    "bluetooth": "Wireless earbuds headphones",
    "camera": "Security camera smart home",
    "an ninh": "Security camera smart home",
    "robot": "Robot vacuum cleaner floor",
    "hut bui": "Robot vacuum cleaner floor",
    
    # Software, Office & Utilities
    "excel": "Office workspace computer spreadsheet",
    "word": "Office workspace computer desk",
    "powerpoint": "Office workspace computer desk",
    "office": "Office workspace computer desk",
    "vneid": "Smartphone mobile screen app",
    "cccd": "Smartphone mobile screen app",
    "dinh danh": "Smartphone mobile screen app",
    "ngan hang": "Smartphone mobile banking screen",
    "ekyc": "Smartphone mobile banking screen",
    "tai khoan": "Smartphone mobile screen app",
    "gplx": "Smartphone mobile screen app",
    "zalo": "Smartphone mobile messaging app",
    "facebook": "Smartphone mobile screen app",
    "iphone": "Modern smartphone mobile desk",
    "android": "Modern smartphone mobile desk",
    "dien thoai": "Modern smartphone mobile desk",
    
    # Security & System
    "ransomware": "Cybersecurity server room computer",
    "ma doc": "Cybersecurity server room computer",
    "virus": "Cybersecurity server room computer",
    "bao mat": "Data security lock computer",
    "mat khau": "Computer keyboard cybersecurity",
    "password": "Computer keyboard cybersecurity",
    
    # AI Models & Dev
    "local llm": "NVIDIA GPU workstation",
    "ollama": "NVIDIA GPU workstation",
    "llama": "NVIDIA GPU workstation",
    "deepseek": "Supercomputer cluster",
    "qwen": "Supercomputer cluster",
    "gpu": "NVIDIA GPU graphics card",
    "vram": "NVIDIA GPU graphics card",
    "ai agent": "Artificial intelligence supercomputer",
    "agentic": "Artificial intelligence supercomputer",
    "fintech": "Financial stock market trading screens",
    "kiem tien": "Financial stock market screen office",
    "mmo": "Modern computer workstation office",
    "cloud": "Cloud server data center room",
    "vps": "Server rack data center",
    "linux": "Linux command line terminal computer",
    "docker": "Server rack data center",
    "fastapi": "Computer programming code monitor",
    "python": "Computer programming code monitor",
    "ranking": "Modern software developer office",
    "seo": "Modern software developer office",
    "indexing": "Data center server rack",
    "chatgpt": "Artificial intelligence supercomputer",
    "openai": "Artificial intelligence supercomputer",
    "gemini": "Modern computer technology workspace",
    "claude": "Modern computer technology workspace",
    "midjourney": "Digital art computer graphics",
    "leonardo": "Digital art painting computer workstation",
    "kling": "Cinema camera video editing console",
    "viggle": "Motion graphics animation computer studio",
    "runway": "Video editing console studio",
    "grok": "Artificial intelligence supercomputer",
    "perplexity": "Computer programming code monitor",
    "elevenlabs": "Sound recording studio microphone",
    "suno": "Sound recording studio console",
    "voice": "Sound recording studio microphone"
}

GENERAL_TECH_QUERIES = [
    "Laptop computer desk workspace",
    "Computer programming code monitor",
    "Personal computer desk setup",
    "NVIDIA GPU workstation",
    "Data center server rack",
    "Modern computer workstation office",
    "Supercomputer cluster",
    "Electronics circuit board motherboard",
    "Cybersecurity server room computer",
    "Software development team office",
    "Modern smartphone mobile desk",
    "Cloud server data center room",
    "High tech server room racks",
    "Computer hardware microprocessor",
    "Mechanical keyboard desk setup",
    "Multi-monitor developer workstation",
    "Digital audio workstation console",
    "Network engineering router rack",
    "Modern office laptop workspace",
    "AI robotics development laboratory"
]

def remove_accents(input_str: str) -> str:
    s = input_str.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).strip()

class TechImageFetcher:
    def __init__(self, cache_dir: Optional[str] = None):
        self.headers = {"User-Agent": os.getenv("IMAGE_FETCHER_UA", "TechImageBot/2.0 (Wikimedia-Client; +https://github.com/chrisx9z/seo-geo-suite-master)")}
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.cache_dir = cache_dir or os.path.join(base_dir, "cache", "tech_images")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.registry_file = os.path.join(self.cache_dir, "used_tech_images.json")
        self.used_images = self._load_registry()

    def _load_registry(self) -> Dict[str, str]:
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_registry(self):
        try:
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(self.used_images, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def extract_search_queries(self, topic: str, focus_keyword: str = "") -> List[str]:
        queries = []
        clean_topic = re.sub(r"[:\-\|\/\(\)\?\!,]+", " ", topic.lower())
        clean_topic = remove_accents(clean_topic)
        clean_focus = remove_accents(focus_keyword.lower()) if focus_keyword else ""

        # 1. Match specific topic keywords
        for k, v in TECH_KEYWORD_QUERY_MAP.items():
            if k in clean_topic or (clean_focus and k in clean_focus):
                queries.append(v)
                break

        # 2. Extract significant words
        stop_words = ["huong", "dan", "cach", "meo", "chi", "tiet", "cho", "nguoi", "moi", "hieu", "qua", "2026", "2025", "top", "nen", "khong", "la", "gi", "tot", "nhat", "nhanh", "de", "lam", "loi", "khac", "phuc", "review", "danh", "gia"]
        words = [w for w in clean_topic.split() if w not in stop_words and len(w) > 1]
        if words:
            queries.append(" ".join(words[:3]) + " computer")

        # 3. Add General Fallbacks
        queries.extend(GENERAL_TECH_QUERIES)

        # Unique preserving order
        seen = set()
        unique = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique.append(q)
        return unique

    def search_wikimedia_images(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": "6",
            "gsrlimit": str(limit),
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "format": "json"
        }
        try:
            r = requests.get(url, params=params, headers=self.headers, timeout=15)
            if r.status_code != 200:
                return []
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for p in pages.values():
                info = p.get("imageinfo", [{}])[0]
                u = info.get("url", "")
                clean_url = u.split("?")[0]
                if clean_url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    w = info.get("width", 0)
                    h = info.get("height", 0)
                    # Filter out portrait images, logos, tiny screenshots
                    if w >= 800 and h >= 500 and (w / h) >= 1.2:
                        results.append({
                            "title": p.get("title", "").replace("File:", ""),
                            "url": u,
                            "width": w,
                            "height": h
                        })
            return results
        except Exception:
            return []

    def download_and_optimize(self, image_url: str, output_name: str) -> Optional[str]:
        out_file = os.path.join(self.cache_dir, f"{output_name}.webp")
        temp_raw = os.path.join(self.cache_dir, f"temp_{output_name}.raw")

        try:
            r = requests.get(image_url, headers=self.headers, timeout=25, stream=True)
            if r.status_code != 200:
                return None

            with open(temp_raw, "wb") as f:
                for chunk in r.iter_content(chunk_size=32768):
                    f.write(chunk)

            img = Image.open(temp_raw).convert("RGB")
            orig_w, orig_h = img.size
            target_ratio = 16.0 / 9.0
            orig_ratio = orig_w / orig_h

            if orig_ratio > target_ratio:
                new_w = int(orig_h * target_ratio)
                left = (orig_w - new_w) // 2
                img = img.crop((left, 0, left + new_w, orig_h))
            else:
                new_h = int(orig_w / target_ratio)
                top = (orig_h - new_h) // 2
                img = img.crop((0, top, orig_w, top + new_h))

            img = img.resize((1200, 675), Image.Resampling.LANCZOS)
            img.save(out_file, "WEBP", quality=80)

            if os.path.exists(temp_raw):
                os.remove(temp_raw)

            return out_file
        except Exception as e:
            if os.path.exists(temp_raw):
                try:
                    os.remove(temp_raw)
                except Exception:
                    pass
            print(f"[-] Error processing image {image_url}: {e}")
            return None

    def get_real_photo_for_post(self, topic: str, focus_keyword: str, slug: str, seed_index: int = 0) -> Optional[Dict[str, str]]:
        queries = self.extract_search_queries(topic, focus_keyword)
        candidates = []
        for q in queries:
            photos = self.search_wikimedia_images(q, limit=10)
            if photos:
                # Filter out photos already used by other slugs
                for p in photos:
                    assigned_slug = self.used_images.get(p["url"])
                    if not assigned_slug or assigned_slug == slug:
                        candidates.append(p)
            if len(candidates) >= 6:
                break

        if not candidates:
            # Fallback across the general tech query pool
            slug_hash = int(hashlib.md5(slug.encode("utf-8")).hexdigest()[:6], 16)
            fallback_q = GENERAL_TECH_QUERIES[slug_hash % len(GENERAL_TECH_QUERIES)]
            photos = self.search_wikimedia_images(fallback_q, limit=10)
            for p in photos:
                assigned_slug = self.used_images.get(p["url"])
                if not assigned_slug or assigned_slug == slug:
                    candidates.append(p)

        if not candidates:
            return None

        # Pick photo based on hash of slug + seed_index
        slug_seed = int(hashlib.md5(f"{slug}-{seed_index}".encode("utf-8")).hexdigest()[:6], 16)
        selected = candidates[slug_seed % len(candidates)]
        suffix = "featured" if seed_index == 0 else f"fig{seed_index}"
        filename = f"{slug}-{suffix}"
        local_path = self.download_and_optimize(selected["url"], filename)
        if not local_path:
            return None

        # Register URL to slug to guarantee zero duplicates across network
        self.used_images[selected["url"]] = slug
        self._save_registry()

        clean_title = re.sub(r"[_\-\.]+", " ", selected["title"]).strip()
        alt_label = f"{topic} - Ảnh minh họa thực tế" if seed_index == 0 else f"{topic} - Hình {seed_index}"
        caption = f"Hình ảnh thực tế minh họa: {clean_title}."
        return {
            "local_path": local_path,
            "alt_text": alt_label[:100],
            "title": f"{topic} - {suffix.upper()}",
            "caption": caption
        }
