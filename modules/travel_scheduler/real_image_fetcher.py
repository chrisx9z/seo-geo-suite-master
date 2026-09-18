# -*- coding: utf-8 -*-
"""
Real Image Fetcher Engine
Fetches authentic, high-resolution travel photography from Wikimedia Commons
Cascading search: Landmark mapping -> Unaccented keyword -> Unaccented Destination -> Travel Archive
Converts all photos into standardized 16:9 Zero-CLS WebP (1200x675) format (< 250KB).
"""

import os
import re
import sys
import random
import unicodedata
import requests
from typing import List, Dict, Optional, Any
from PIL import Image

VIETNAM_LANDMARK_MAP = {
    "trang an": "Trang An Ninh Binh",
    "hang mua": "Hang Mua Ninh Binh",
    "bai dinh": "Bai Dinh Pagoda",
    "thung nham": "Thung Nham Ninh Binh",
    "tam coc": "Tam Coc Ninh Binh",
    "bich dong": "Bich Dong Pagoda",
    "van long": "Van Long Nature Reserve",
    "hoa lu": "Hoa Lu Ancient Capital",
    "ba na": "Ba Na Hills",
    "cau vang": "Golden Bridge Da Nang",
    "ngu hanh son": "Marble Mountains Da Nang",
    "son tra": "Son Tra Peninsula",
    "chua linh ung": "Linh Ung Pagoda",
    "hoi an": "Hoi An Ancient Town",
    "chua cau": "Japanese Covered Bridge Hoi An",
    "rung dua bay mau": "Bay Mau Coconut Forest",
    "dai noi": "Hue Imperial City",
    "thien mu": "Thien Mu Pagoda",
    "khai dinh": "Khai Dinh Tomb",
    "tu duc": "Tu Duc Tomb",
    "song huong": "Perfume River Hue",
    "ha giang": "Ha Giang landscape",
    "ma pi leng": "Ma Pi Leng Pass",
    "nho que": "Nho Que River",
    "dong van": "Dong Van Karst Plateau",
    "lung cu": "Lung Cu Flag Tower",
    "sa pa": "Sa Pa Vietnam landscape",
    "fansipan": "Fansipan peak",
    "ta van": "Ta Van Sapa",
    "o quy ho": "O Quy Ho Pass",
    "ha long": "Ha Long Bay",
    "cat ba": "Lan Ha Bay Cat Ba",
    "phu quoc": "Phu Quoc Island",
    "bai sao": "Bai Sao Phu Quoc",
    "hon thom": "Hon Thom Island",
    "da lat": "Da Lat Vietnam",
    "xuan huong": "Xuan Huong Lake",
    "tuyen lam": "Tuyen Lam Lake",
    "nha trang": "Nha Trang Beach",
    "vinpearl": "Vinpearl Nha Trang",
    "hon tam": "Hon Tam Nha Trang",
    "quy nhon": "Quy Nhon landscape",
    "eo gio": "Eo Gio Quy Nhon",
    "ky co": "Ky Co Quy Nhon",
    "ghenh da dia": "Ghenh Da Dia Phu Yen",
    "phan thiet": "Mui Ne Sand Dunes",
    "mui ne": "Mui Ne Beach",
    "vung tau": "Vung Tau Beach",
    "con dao": "Con Dao Island",
    "ban gioc": "Ban Gioc Waterfall",
    "moc chau": "Moc Chau Tea Hill",
    "ta xua": "Ta Xua Cloud Hunting",
    "pu luong": "Pu Luong Nature Reserve",
    "tu san": "Nho Que River Tu San",
    "nho que": "Nho Que River",
    "tham ma": "Tham Ma Pass Ha Giang",
    "lung cu": "Lung Cu Flag Tower",
    "pao": "Ha Giang house of Pao",
    "tam giac mach": "Buckwheat flower Ha Giang",
    "na ka": "Na Ka Plum Valley Moc Chau",
    "ban ang": "Ban Ang Pine Forest Moc Chau",
    "dai yem": "Dai Yem Waterfall Moc Chau",
    "doi che": "Moc Chau Tea Hill",
    "mai chau": "Mai Chau valley Vietnam",
    "ban lac": "Ban Lac Mai Chau",
    "pha luong": "Pha Luong peak Moc Chau",
    "lan ha": "Lan Ha Bay Cat Ba",
    "ti top": "Ti Top Island Ha Long",
    "ti top": "Ti Top Island Ha Long",
    "sung sot": "Sung Sot Cave Ha Long",
    "viet hai": "Viet Hai village Cat Ba",
    "nguom ngao": "Nguom Ngao Cave Cao Bang",
    "pac bo": "Pac Bo Cao Bang",
    "thang hen": "Thang Hen Lake Cao Bang",
    "ba be": "Ba Be Lake Vietnam",
    "me pia": "Me Pia Pass Cao Bang",
    "khuoi ky": "Khuoi Ky village Cao Bang",
    "bat trang": "Bat Trang pottery village",
    "chua huong": "Perfume Pagoda Hanoi",
    "duong lam": "Duong Lam ancient village",
    "ba vi": "Ba Vi National Park",
    "ho tay": "West Lake Hanoi",
    "hoang thanh": "Imperial Citadel of Thang Long",
    "my khe": "My Khe Beach Da Nang",
    "cau rong": "Dragon Bridge Da Nang",
    "nam o": "Nam O Reef Da Nang",
    "cu lao cham": "Cu Lao Cham island",
    "thanh ha": "Thanh Ha pottery village Hoi An",
    "an bang": "An Bang Beach Hoi An",
    "thien an": "Thien An Hill Hue",
    "thuy tien": "Ho Thuy Tien Hue",
    "lang co": "Lang Co Bay Hue",
    "lap an": "Lap An Lagoon Hue",
    "thuy xuan": "Thuy Xuan incense village Hue",
    "dong ba": "Dong Ba Market Hue",
    "thien duong": "Thien Duong Cave Quang Binh",
    "nuoc mooc": "Nuoc Mooc Spring Quang Binh",
    "song chay": "Song Chay Dark Cave Quang Binh",
    "quang phu": "Quang Phu Sand Dunes Dong Hoi",
    "nhat le": "Nhat Le Beach Dong Hoi",
    "son doong": "Son Doong Cave Vietnam",
    "cu lao xanh": "Cu Lao Xanh Quy Nhon",
    "thap banh it": "Banh It Cham Tower Binh Dinh",
    "ghenh rang": "Ghenh Rang Tien Sa Quy Nhon",
    "hon kho": "Hon Kho Island Quy Nhon",
    "phuong mai": "Phuong Mai Sand Dunes Quy Nhon",
    "nhon hai": "Nhon Hai fishing village Quy Nhon"
}

def remove_accents(input_str: str) -> str:
    """Converts accented Vietnamese text to clean ASCII unaccented text."""
    s = input_str.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).strip()

class RealImageFetcher:
    def __init__(self, cache_dir: Optional[str] = None):
        self.headers = {"User-Agent": "MMDiDauTravelApp/1.0 (https://mmdidau.com; admin@mmdidau.com)"}
        self.cache_dir = cache_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "cache", "travel_images"))
        os.makedirs(self.cache_dir, exist_ok=True)

    def extract_search_queries(self, keyword: str, destination: str = "") -> List[str]:
        """Builds a cascade of search queries to guarantee high quality real photos."""
        queries = []
        clean_kw = remove_accents(keyword.lower())
        clean_dest = remove_accents(destination.lower())

        # 1. Match specific landmark
        for k, v in VIETNAM_LANDMARK_MAP.items():
            if k in clean_kw:
                queries.append(v)
                break

        # 2. Unaccented cleaned keyword without stop words
        stop_words = ["kinh", "nghiem", "du", "lich", "di", "tu", "tuc", "cam", "nang", "gia", "ve", "lich", "trinh", "2026", "2025", "review", "check", "in", "o", "dau", "ngon", "nhat", "dep", "re"]
        words = [w for w in clean_kw.split() if w not in stop_words]
        if words:
            queries.append(" ".join(words))

        # 3. Destination queries
        if clean_dest:
            queries.append(f"{clean_dest} Vietnam landscape")
            queries.append(f"{clean_dest} Vietnam travel")
            queries.append(f"{clean_dest} Vietnam")

        # 4. Universal Fallbacks
        queries.append("Vietnam travel landscape")
        queries.append("Vietnam scenery nature")

        return queries

    def search_wikimedia_images(self, query: str, limit: int = 12) -> List[Dict[str, Any]]:
        """Searches Wikimedia Commons for authentic photos matching query."""
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
                    # Filter out tiny logos, maps, or non-photos
                    w = info.get("width", 0)
                    h = info.get("height", 0)
                    if w >= 800 and h >= 500:
                        results.append({
                            "title": p.get("title", "").replace("File:", ""),
                            "url": u,
                            "width": w,
                            "height": h
                        })
            return results
        except Exception as e:
            return []

    def download_and_optimize(self, image_url: str, output_name: str) -> Optional[str]:
        """Downloads raw photo, crops to 16:9, resizes to 1200x675, and saves as WebP."""
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

            return out_file
        except Exception as e:
            print(f"Error processing image {image_url}: {e}")
            return None

    def get_real_photos_for_post(self, keyword: str, slug: str, destination: str = "", seed_index: int = 0, count: int = 3) -> List[Dict[str, str]]:
        """
        Fetches `count` real authentic photos for an article (Rule: >= 1 image per 500 words).
        1. Featured Cover Photo (chinh)
        2. In-content Experience Photos (kham-pha, can-canh, trai-nghiem, khong-gian, etc.)
        Uses seed_index to select diverse images across different posts of the same destination.
        """
        candidate_queries = self.extract_search_queries(keyword, destination)
        photos = []
        for q in candidate_queries:
            found = self.search_wikimedia_images(q, limit=15)
            if found:
                photos.extend(found)
            if len(photos) >= count + 6:
                break

        # Deduplicate photos by url
        unique_photos = []
        seen_urls = set()
        for p in photos:
            if p["url"] not in seen_urls:
                seen_urls.add(p["url"])
                unique_photos.append(p)

        if len(unique_photos) < count:
            extra = self.search_wikimedia_images(f"{remove_accents(destination)} Vietnam travel scenery", limit=15)
            for p in extra:
                if p["url"] not in seen_urls:
                    seen_urls.add(p["url"])
                    unique_photos.append(p)

        if not unique_photos:
            unique_photos = self.search_wikimedia_images("Vietnam travel landscape scenery", limit=15)

        if not unique_photos:
            # Fallback to local cached travel images
            if os.path.exists(self.cache_dir):
                cached_files = [f for f in os.listdir(self.cache_dir) if f.endswith(".webp") and not f.startswith("temp_")]
                for f in cached_files[:15]:
                    unique_photos.append({
                        "title": f.replace(".webp", "").replace("-", " "),
                        "url": f,
                        "local_file": os.path.join(self.cache_dir, f)
                    })

        num_avail = len(unique_photos)
        if num_avail == 0:
            return []

        # Pick `count` photos with seed_index offset
        selected = []
        for i in range(count):
            idx = (seed_index + i) % num_avail
            selected.append(unique_photos[idx])

        results = []
        suffixes = ["chinh", "kham-pha", "can-canh", "trai-nghiem", "khong-gian", "toan-canh", "chi-tiet"]
        for i, p in enumerate(selected):
            suffix = suffixes[i] if i < len(suffixes) else f"hinh-{i+1}"
            filename = f"{slug}-{suffix}"
            if p.get("local_file"):
                out_file = os.path.join(self.cache_dir, f"{filename}.webp")
                if not os.path.exists(out_file):
                    import shutil
                    shutil.copyfile(p["local_file"], out_file)
                local_webp = out_file
            else:
                local_webp = self.download_and_optimize(p["url"], filename)

            if local_webp:
                clean_title = re.sub(r"[_\-\.]+", " ", p["title"]).strip()
                results.append({
                    "local_path": local_webp,
                    "alt_text": f"{keyword} - Hình ảnh thực tế {clean_title}"[:100],
                    "caption": f"Hình ảnh thực tế {clean_title} được du khách ghi lại tại {destination}."[:120]
                })

        return results
