# -*- coding: utf-8 -*-
"""
Real Image Fetcher Engine
Fetches authentic, high-resolution travel photography from Wikimedia Commons
Cascading search: Landmark mapping -> Topic mapping -> Unaccented keyword -> Unaccented Destination -> Travel Archive
Converts all photos into Cinema Ultra HD 16:9 Zero-CLS WebP (1920x1080) format (Quality 92) with rich color grading.
Guarantees 100% Zero-Duplicate images across posts via persistent registry and hash offsets.
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
from PIL import Image, ImageEnhance

VIETNAM_LANDMARK_MAP = {
    "trang an": "Trang An Ninh Binh",
    "hang mua": "Hang Mua Ninh Binh",
    "bai dinh": "Bai Dinh Pagoda",
    "thung nham": "Thung Nham Ninh Binh",
    "tam coc": "Tam Coc Ninh Binh",
    "bich dong": "Bich Dong Pagoda",
    "van long": "Van Long Nature Reserve",
    "hoa lu": "Hoa Lu Ancient Capital",
    "dong van": "Dong Van Karst Plateau Geopark",
    "ma pi leng": "Ma Pi Leng Pass",
    "nho que": "Nho Que River Tu San Canyon",
    "lung cu": "Lung Cu Flag Tower",
    "du gia": "Du Gia Waterfall Ha Giang",
    "dinh vua meo": "Hmong Kings Palace Dinh Vua Meo",
    "lo lo chai": "Lo Lo Chai Village Dong Van",
    "tham ma": "Tham Ma Slope Ha Giang",
    "ban gioc": "Ban Gioc Waterfall",
    "nguom ngao": "Nguom Ngao Cave Cao Bang",
    "mat than": "Mat Than Mountain Cao Bang",
    "phia oac": "Phia Oac National Park Cao Bang",
    "khau coc cha": "Khau Coc Cha Pass Cao Bang",
    "ba be": "Ba Be Lake Bac Kan",
    "fansipan": "Fansipan Mountain Sapa",
    "o quy ho": "O Quy Ho Pass",
    "muong hoa": "Muong Hoa Valley Sapa",
    "cat cat": "Cat Cat Village Sapa",
    "ta van": "Ta Van Village Sapa",
    "y ty": "Y Ty Lao Cai terraced fields",
    "halong": "Ha Long Bay limestone karsts",
    "ha long": "Ha Long Bay limestone karsts",
    "bai tu long": "Bai Tu Long Bay",
    "lan ha": "Lan Ha Bay Cat Ba",
    "cat ba": "Cat Ba National Park",
    "ho guom": "Hoan Kiem Lake Hanoi",
    "pho co": "Hanoi Old Quarter streets",
    "van mieu": "Temple of Literature Hanoi",
    "hoang thanh": "Thang Long Imperial Citadel",
    "hoa lo": "Hoa Lo Prison Memorial",
    "chua mot cot": "One Pillar Pagoda Hanoi",
    "chua tran quoc": "Tran Quoc Pagoda Hanoi",
    "tay ho": "West Lake Tay Ho Hanoi",
    "hoi an": "Hoi An Ancient Town lantern",
    "chua cau": "Japanese Covered Bridge Hoi An",
    "ba na": "Ba Na Hills Golden Bridge",
    "ngu hanh son": "Marble Mountains Da Nang",
    "ban dao son tra": "Son Tra Peninsula Da Nang",
    "my khe": "My Khe Beach Da Nang",
    "cau rong": "Dragon Bridge Da Nang",
    "hai van": "Hai Van Pass coastal railway",
    "dai noi": "Hue Imperial City Citadel",
    "chua thien mu": "Thien Mu Pagoda Hue",
    "lang khai dinh": "Khai Dinh Tomb Hue",
    "lang tu duc": "Tu Duc Tomb Hue",
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
    "nhon hai": "Nhon Hai fishing village Quy Nhon",
    "ba den": "Nui Ba Den Tay Ninh",
    "nui ba den": "Nui Ba Den Tay Ninh",
    "tay bo da son": "Tay Bo Da Son Buddha Ba Den",
    "toa thanh": "Cao Dai Temple Tay Ninh",
    "cao dai": "Cao Dai Temple Tay Ninh",
    "dau tieng": "Dau Tieng Lake",
    "ma thien lanh": "Ma Thien Lanh Tay Ninh",
    "ben tre": "Ben Tre Mekong Delta",
    "tien giang": "My Tho Tien Giang",
    "thoi son": "Thoi Son Island Tien Giang",
    "cai be": "Cai Be floating market",
    "chua vinh trang": "Vinh Trang Pagoda My Tho",
    "cai rang": "Cai Rang floating market Can Tho",
    "tra su": "Tra Su cajuput forest",
    "ba chua xu": "Ba Chua Xu Temple Chau Doc",
    "that son": "That Son An Giang",
    "can gio": "Can Gio mangrove forest",
    "tram chim": "Tram Chim National Park Dong Thap",
    "sa dec": "Sa Dec flower village",
    "mui ca mau": "Cape Ca Mau Vietnam",
    "do son": "Do Son Beach Hai Phong",
    "con phung": "Con Phung Ben Tre Mekong",
    "dao dua": "Dao Dua Ben Tre",
    "con quy": "Ben Tre Mekong Delta river",
    "dong tam": "Dong Tam Snake Farm Tien Giang",
    "hu tieu": "Hu Tieu My Tho noodle",
    "cai mon": "Cho Lach Ben Tre fruit garden",
    "cua lo": "Cua Lo Beach Nghe An",
    "lan ha": "Lan Ha Bay Cat Ba",
    "cat ba": "Cat Ba Island Hai Phong",
    "ha long": "Ha Long Bay Vietnam",
    "quang ninh": "Ha Long Bay Quang Ninh",
    # Thailand Landmarks
    "bangkok": "Bangkok Thailand cityscape",
    "grand palace": "Grand Palace Bangkok",
    "wat phra kaew": "Wat Phra Kaew Bangkok",
    "wat arun": "Wat Arun Bangkok",
    "wat pho": "Wat Pho Bangkok",
    "chao phraya": "Chao Phraya River Bangkok",
    "chatuchak": "Chatuchak Weekend Market Bangkok",
    "jodd fairs": "Bangkok night market street food",
    "suon cay": "Bangkok night market street food",
    "iconsiam": "ICONSIAM Bangkok Thailand",
    "pattaya": "Pattaya Thailand beach",
    "chiang mai": "Chiang Mai Thailand",
    "wat doi suthep": "Wat Phra That Doi Suthep Chiang Mai",
    "phuket": "Phuket Thailand beach",
    "phi phi": "Phi Phi Islands Thailand",
    "ayutthaya": "Ayutthaya Historical Park",
    # Singapore & Malaysia Food & Specialties
    "com ga": "Hainanese chicken rice Singapore",
    "chao ech": "Frog porridge Singapore",
    "roti canai": "Roti canai Malaysia",
    "teh tarik": "Teh tarik tea Malaysia",
    "satay": "Satay skewers Singapore Malaysia",
    "laksa": "Laksa noodle soup Singapore",
    "nasi lemak": "Nasi lemak Malaysia",
    # Singapore Landmarks
    "universal studios": "Universal Studios Singapore",
    "gardens by the bay": "Gardens by the Bay Singapore",
    "marina bay sands": "Marina Bay Sands Singapore",
    "marina bay": "Marina Bay Sands Singapore",
    "sentosa": "Sentosa Island Singapore",
    "merlion": "Merlion Park Singapore",
    "changi": "Jewel Changi Airport Singapore",
    "singapore": "Singapore city skyline",
    # Malaysia Landmarks
    "kuala lumpur": "Petronas Twin Towers Kuala Lumpur",
    "petronas": "Petronas Twin Towers Kuala Lumpur",
    "batu": "Batu Caves Selangor Malaysia",
    "penang": "George Town Penang street art",
    "malacca": "Malacca Malaysia",
    "genting": "Genting Highlands Malaysia",
    "langkawi": "Langkawi Malaysia beach",
    # Bali & Indonesia Landmarks
    "bali": "Bali Indonesia landscape temple",
    "ubud": "Ubud Bali rice terrace monkey forest",
    "tegallalang": "Tegallalang Rice Terrace Bali",
    "tanah lot": "Tanah Lot Temple Bali",
    "uluwatu": "Uluwatu Temple Bali cliff",
    "nusa penida": "Kelingking Beach Nusa Penida Bali",
    "kuta": "Kuta Beach Bali sunset",
    "seminyak": "Seminyak Bali beach",
    "canggu": "Canggu Bali beach"
}

VIETNAM_TOPIC_MAP = {
    "private car": ["Toyota Innova Vietnam", "Car Vietnam road highway", "Vietnam expressway travel", "Vietnam passenger van"],
    "car hire": ["Toyota Innova Vietnam", "Car Vietnam road highway", "Vietnam passenger van"],
    "driver": ["Toyota Innova Vietnam", "Vietnam road highway", "Hanoi traffic street"],
    "train": ["Vietnam Railways train", "Reunification Express train", "Train in Vietnam"],
    "sleeper bus": ["Vietnam bus highway", "Transinco bus Vietnam", "Vietnam sleeper bus"],
    "bus": ["Vietnam bus highway", "Transinco bus Vietnam", "Vietnam coach travel"],
    "scooter": ["Hanoi traffic street", "Vietnam motorbike road", "Saigon motorcycle street"],
    "motorbike": ["Hanoi traffic street", "Vietnam motorbike road", "Saigon motorcycle street"],
    "flight": ["Vietnam Airlines aircraft", "Noi Bai airport Hanoi", "Tan Son Nhat airport"],
    "airport": ["Vietnam Airlines aircraft", "Noi Bai airport Hanoi", "Tan Son Nhat airport"],
    "boat": ["Halong Bay boat cruise", "Mekong Delta river boat", "Tam Coc rowboat"],
    "cruise": ["Halong Bay boat cruise", "Lan Ha Bay cruise", "Mekong river cruise"],
    "street food": ["Vietnamese pho noodle soup", "Vietnamese banh mi street food", "Vietnamese street food market"],
    "food": ["Vietnamese pho noodle soup", "Vietnamese banh mi street food", "Vietnamese food dish"],
    "coffee": ["Vietnamese iced coffee", "Hanoi egg coffee cafe", "Vietnam coffee beans"],
    "market": ["Ben Thanh Market Saigon", "Dong Ba Market Hue", "Hanoi Old Quarter market"],
    "waterfall": ["Ban Gioc waterfall Vietnam", "Datanla waterfall Da Lat", "Silver waterfall Sapa"],
    "cave": ["Phong Nha cave Vietnam", "Paradise cave Vietnam", "Nguom Ngao cave Cao Bang"],
    "trekking": ["Sapa terraced rice fields", "Muong Hoa valley trekking", "Fansipan mountain trail"],
    "beach": ["My Khe beach Da Nang", "An Bang beach Hoi An", "Phu Quoc island beach"]
}

VIETNAMESE_STOP_WORDS = set([
    "kinh", "nghiem", "du", "lich", "di", "tu", "tuc", "cam", "nang", "gia", "ve",
    "lich", "trinh", "2026", "2025", "review", "check", "in", "o", "dau", "ngon",
    "nhat", "dep", "re", "huong", "dan", "chi", "tiet"
])

ENGLISH_STOP_WORDS = set([
    "with", "in", "rates", "booking", "tips", "best", "day", "trips", "guide", "honest",
    "cost", "costs", "how", "to", "for", "and", "the", "a", "an", "of", "on", "by",
    "from", "at", "what", "where", "when", "why", "who", "which", "review", "ultimate",
    "complete", "essential", "everything", "need", "know", "2025", "2026", "scenic",
    "overview", "top", "things", "do", "see", "itinerary", "route", "routes", "vs"
])

def remove_accents(input_str: str) -> str:
    """Converts accented Vietnamese text to clean ASCII unaccented text."""
    s = input_str.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).strip()

class RealImageFetcher:
    def __init__(self, cache_dir: Optional[str] = None):
        self.headers = {"User-Agent": os.getenv("IMAGE_FETCHER_UA", "SeoGeoSuiteImageFetcher/2.0 (+https://github.com/chrisx9z/seo-geo-suite-master)")}
        self.cache_dir = cache_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "cache", "travel_images"))
        os.makedirs(self.cache_dir, exist_ok=True)
        self.registry_file = os.path.join(self.cache_dir, "used_images_registry.json")
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
            current = self._load_registry()
            current.update(self.used_images)
            self.used_images = current
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(self.used_images, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def extract_search_queries(self, keyword: str, destination: str = "") -> List[str]:
        """Builds a cascade of search queries to guarantee high quality real photos."""
        queries = []
        # Strip punctuation into clean spaces
        clean_kw = re.sub(r"[:\-\|\/\(\)\?\!,]+", " ", keyword.lower())
        clean_kw = remove_accents(clean_kw).strip()
        clean_dest = remove_accents(destination.lower()).strip()

        # Smart country detection
        target_country = "Vietnam"
        if any(w in clean_kw or w in clean_dest for w in ["thai lan", "thailand", "bangkok", "chiang mai", "pattaya", "phuket", "wat ", "siam"]):
            target_country = "Thailand"
        elif any(w in clean_kw or w in clean_dest for w in ["singapore", "marina bay", "sentosa", "merlion", "changi"]):
            target_country = "Singapore"
        elif any(w in clean_kw or w in clean_dest for w in ["malaysia", "kuala lumpur", "penang", "malacca", "genting"]):
            target_country = "Malaysia"
        elif any(w in clean_kw or w in clean_dest for w in ["bali", "indonesia", "ubud", "uluwatu", "tanah lot"]):
            target_country = "Bali Indonesia" 

        # 1. Match specific landmarks (sorted by longest key first, add up to 3)
        matched_landmarks = 0
        for k, v in sorted(VIETNAM_LANDMARK_MAP.items(), key=lambda x: len(x[0]), reverse=True):
            if k in clean_kw:
                queries.append(v)
                matched_landmarks += 1
                if matched_landmarks >= 3:
                    break

        # 2. Match topic keywords (transport, food, trekking, etc.)
        for topic, topic_queries in VIETNAM_TOPIC_MAP.items():
            if topic in clean_kw:
                queries.extend(topic_queries)
                break

        # 3. Clean words by stripping stop words
        words = [w for w in clean_kw.split() if w not in VIETNAMESE_STOP_WORDS and w not in ENGLISH_STOP_WORDS]
        if words and len(words) <= 5:
            queries.append(" ".join(words) + f" {target_country}")
        elif words:
            queries.append(" ".join(words[:4]))

        # 4. Destination queries
        if clean_dest:
            queries.append(f"{clean_dest} {target_country} landscape")
            queries.append(f"{clean_dest} {target_country} travel")
            queries.append(f"{clean_dest} {target_country}")

        # 5. Universal Fallbacks
        queries.append(f"{target_country} travel landscape")
        queries.append(f"{target_country} scenery nature")

        # Unique preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)

        return unique_queries

    def search_wikimedia_images(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
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
            "iiurlwidth": "2560",
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
                u = info.get("thumburl") or info.get("url", "")
                orig_url = info.get("url", "")
                clean_url = orig_url.split("?")[0]
                if clean_url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    w = info.get("width", 0)
                    h = info.get("height", 0)
                    # Filter for high-res travel photography (w >= 1000)
                    if w >= 1000 and h >= 550:
                        results.append({
                            "title": p.get("title", "").replace("File:", ""),
                            "url": u,
                            "orig_url": orig_url,
                            "width": w,
                            "height": h
                        })
            # Prioritize highest resolution original photography
            results.sort(key=lambda x: x["width"] * x["height"], reverse=True)
            return results
        except Exception:
            return []

    def download_and_optimize(self, image_url: str, output_name: str) -> Optional[str]:
        """Downloads raw photo, crops to 16:9, resizes to 1200x675, and saves as WebP."""
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

            # 1920x1080 Ultra HD Cinema Standard
            img = img.resize((1920, 1080), Image.Resampling.LANCZOS)

            # High-End Travel Grading: rich natural vibrance, deeper contrast, razor-sharp detail
            img = ImageEnhance.Color(img).enhance(1.06)
            img = ImageEnhance.Contrast(img).enhance(1.04)
            img = ImageEnhance.Sharpness(img).enhance(1.12)

            # High quality WebP (Q=92) preserves pristine gradients, textures & landscapes
            img.save(out_file, "WEBP", quality=92, method=4)

            if os.path.exists(temp_raw):
                os.remove(temp_raw)

            return out_file
        except Exception as e:
            if os.path.exists(temp_raw):
                try:
                    os.remove(temp_raw)
                except Exception:
                    pass
            print(f"Error processing image {image_url}: {e}")
            return None

    def get_real_photos_for_post(self, keyword: str, slug: str, destination: str = "", seed_index: int = 0, count: int = 3) -> List[Dict[str, str]]:
        """
        Fetches `count` real authentic photos for an article (Rule: >= 1 image per 500 words).
        Guarantees zero duplicate images across different post slugs.
        """
        candidate_queries = self.extract_search_queries(keyword, destination)
        photos = []
        for q in candidate_queries:
            found = self.search_wikimedia_images(q, limit=15)
            if found:
                photos.extend(found)
            if len(photos) >= count * 3:
                break

        # Filter out photos already used by other slugs
        unique_photos = []
        seen_urls = set()
        for p in photos:
            raw_id = p.get("orig_url") or p["url"]
            if raw_id not in seen_urls:
                seen_urls.add(raw_id)
                assigned_slug = self.used_images.get(raw_id)
                if not assigned_slug or assigned_slug == slug:
                    unique_photos.append(p)

        # Fallback queries if needed
        if len(unique_photos) < count:
            # Detect country for fallback
            target_country = "Vietnam"
            clean_kw_low = remove_accents(keyword.lower())
            clean_dest_low = remove_accents(destination.lower())
            if any(w in clean_kw_low or w in clean_dest_low for w in ["thai lan", "thailand", "bangkok", "chiang mai", "pattaya", "phuket", "wat ", "siam"]):
                target_country = "Thailand"
            elif any(w in clean_kw_low or w in clean_dest_low for w in ["singapore", "marina bay", "sentosa"]):
                target_country = "Singapore"
            elif any(w in clean_kw_low or w in clean_dest_low for w in ["malaysia", "kuala lumpur", "penang", "malacca", "genting"]):
                target_country = "Malaysia"
            elif any(w in clean_kw_low or w in clean_dest_low for w in ["bali", "indonesia", "ubud"]):
                target_country = "Bali Indonesia"
            fallback_queries = [
                f"{target_country} landmark",
                f"{target_country} tourism",
                f"{target_country} city",
                f"{target_country} travel",
                target_country
            ]
            for fq in fallback_queries:
                extra = self.search_wikimedia_images(fq, limit=15)
                for p in extra:
                    u = p.get("orig_url") or p["url"]
                    if u not in seen_urls:
                        seen_urls.add(u)
                        assigned_slug = self.used_images.get(u)
                        if not assigned_slug or assigned_slug == slug:
                            unique_photos.append(p)
                if len(unique_photos) >= count:
                    break

        if not unique_photos:
            return []

        # Deterministic slug seed offset to avoid clumping
        slug_hash_seed = int(hashlib.md5(slug.encode("utf-8")).hexdigest()[:6], 16)
        num_avail = len(unique_photos)

        selected = []
        for i in range(min(count, num_avail)):
            idx = (slug_hash_seed + seed_index + i) % num_avail
            selected.append(unique_photos[idx])

        results = []
        suffixes = ["chinh", "kham-pha", "can-canh", "trai-nghiem", "khong-gian", "toan-canh", "chi-tiet"]
        for i, p in enumerate(selected):
            suffix = suffixes[i] if i < len(suffixes) else f"hinh-{i+1}"
            filename = f"{slug}-{suffix}"
            local_webp = self.download_and_optimize(p["url"], filename)

            if local_webp:
                # Register URL to slug to guarantee zero duplicates across network
                raw_id = p.get("orig_url") or p["url"]
                self.used_images[raw_id] = slug
                clean_title = re.sub(r"[_\-\.]+", " ", p["title"]).strip()
                results.append({
                    "local_path": local_webp,
                    "alt_text": f"{keyword} - Hình ảnh thực tế {clean_title}"[:100],
                    "caption": f"Hình ảnh thực tế {clean_title} được du khách ghi lại tại {destination}."[:120]
                })

        self._save_registry()
        return results
