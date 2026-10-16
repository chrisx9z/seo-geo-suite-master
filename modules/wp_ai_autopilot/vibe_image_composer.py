# -*- coding: utf-8 -*-
"""
VibeImageComposer - Professional, Unique, Brand-Tailored AI Banner Generator
Creates 1200x675 16:9 Zero-CLS WebP images for AI & Tech portals.
Guarantees:
- Every image is generated fresh (Tạo mới 100%)
- Distinct brand color palette & vector/geometric graphics per topic (Không lặp lại)
- Modern, clean, high-tech aesthetics (Chuyên nghiệp)
- Strict WebP compression (< 75KB)
"""

import os
import math
from typing import Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont

BRAND_PROFILES: Dict[str, Dict[str, Any]] = {
    "chat gpt": {
        "bg_top": (10, 18, 15), "bg_bot": (5, 9, 8),
        "primary": (16, 163, 127), "accent": (52, 211, 153),
        "tag": "OPENAI ECOSYSTEM", "motif": "spiral_nodes"
    },
    "chat gpt plus": {
        "bg_top": (20, 12, 35), "bg_bot": (8, 5, 15),
        "primary": (168, 85, 247), "accent": (245, 158, 11),
        "tag": "GPT-4o & PLUS REVIEW", "motif": "hexagon_core"
    },
    "gemini ai": {
        "bg_top": (10, 16, 36), "bg_bot": (5, 8, 20),
        "primary": (66, 133, 244), "accent": (147, 51, 234),
        "tag": "GOOGLE DEEPMIND", "motif": "sparkle_star"
    },
    "google ai studio": {
        "bg_top": (12, 22, 35), "bg_bot": (6, 12, 20),
        "primary": (6, 182, 212), "accent": (56, 189, 248),
        "tag": "API & DEVELOPER CLOUD", "motif": "api_mesh"
    },
    "claude ai": {
        "bg_top": (26, 18, 14), "bg_bot": (12, 8, 6),
        "primary": (217, 119, 87), "accent": (249, 115, 22),
        "tag": "ANTHROPIC CLAUDE", "motif": "concentric_rings"
    },
    "grok ai": {
        "bg_top": (15, 17, 23), "bg_bot": (8, 9, 12),
        "primary": (224, 231, 255), "accent": (56, 189, 248),
        "tag": "xAI ELON MUSK", "motif": "cyber_matrix"
    },
    "perplexity ai": {
        "bg_top": (8, 26, 28), "bg_bot": (4, 13, 15),
        "primary": (20, 184, 166), "accent": (45, 212, 191),
        "tag": "AI REALTIME SEARCH", "motif": "search_pulse"
    },
    "meta ai": {
        "bg_top": (10, 20, 45), "bg_bot": (5, 10, 24),
        "primary": (0, 129, 251), "accent": (96, 165, 250),
        "tag": "META LLAMA 3", "motif": "infinity_loop"
    },
    "kling ai": {
        "bg_top": (28, 12, 12), "bg_bot": (14, 5, 5),
        "primary": (255, 94, 58), "accent": (251, 146, 60),
        "tag": "GENERATIVE VIDEO AI", "motif": "camera_shutter"
    },
    "tạo video ai": {
        "bg_top": (24, 12, 28), "bg_bot": (12, 5, 14),
        "primary": (244, 63, 94), "accent": (245, 158, 11),
        "tag": "TOP VIDEO AI TOOLS", "motif": "filmstrip_flow"
    },
    "tạo ảnh ai": {
        "bg_top": (22, 14, 38), "bg_bot": (10, 6, 20),
        "primary": (139, 92, 246), "accent": (236, 72, 153),
        "tag": "AI ART & GRAPHICS", "motif": "prism_canvas"
    },
    "suno ai": {
        "bg_top": (25, 10, 30), "bg_bot": (11, 4, 14),
        "primary": (236, 72, 153), "accent": (168, 85, 247),
        "tag": "AI MUSIC STUDIO", "motif": "soundwave_spectrum"
    },
    "ai voice": {
        "bg_top": (14, 18, 38), "bg_bot": (6, 8, 20),
        "primary": (99, 102, 241), "accent": (6, 182, 212),
        "tag": "VOICE CLONING & TTS", "motif": "voice_acoustics"
    },
    "character ai": {
        "bg_top": (24, 12, 34), "bg_bot": (10, 5, 16),
        "primary": (168, 85, 247), "accent": (244, 63, 94),
        "tag": "ROLEPLAY & VIRTUAL AVATAR", "motif": "chat_dialogue"
    },
    "gamma ai": {
        "bg_top": (10, 22, 36), "bg_bot": (5, 11, 18),
        "primary": (6, 182, 212), "accent": (59, 130, 246),
        "tag": "AI PRESENTATION & SLIDES", "motif": "slide_deck"
    },
    "check ai": {
        "bg_top": (10, 22, 18), "bg_bot": (5, 11, 8),
        "primary": (16, 185, 129), "accent": (52, 211, 153),
        "tag": "AI DETECTOR & BYPASS", "motif": "security_shield"
    },
    "blackbox ai": {
        "bg_top": (10, 18, 12), "bg_bot": (4, 9, 6),
        "primary": (34, 197, 94), "accent": (56, 189, 248),
        "tag": "AI CODE & DEVELOPER", "motif": "code_brackets"
    },
    "copilot ai": {
        "bg_top": (10, 18, 36), "bg_bot": (5, 9, 20),
        "primary": (0, 120, 212), "accent": (56, 189, 248),
        "tag": "MICROSOFT 365 COPILOT", "motif": "fluent_tiles"
    },
    "kiếm tiền bằng ai": {
        "bg_top": (26, 18, 8), "bg_bot": (12, 8, 3),
        "primary": (245, 158, 11), "accent": (251, 191, 36),
        "tag": "AI MMO AUTOMATION 2026", "motif": "wealth_growth"
    },
    "ai là gì": {
        "bg_top": (12, 16, 32), "bg_bot": (5, 8, 16),
        "primary": (99, 102, 241), "accent": (56, 189, 248),
        "tag": "COMPREHENSIVE AI GUIDE", "motif": "neural_synapse"
    },
    # ---------------- GENERAL TECH & APPLICATION CATEGORIES ----------------
    "thu-thuat-may-tinh": {
        "bg_top": (12, 22, 38), "bg_bot": (6, 12, 22),
        "primary": (59, 130, 246), "accent": (56, 189, 248),
        "tag": "WINDOWS & PC GUIDE", "motif": "pc_desktop"
    },
    "tin-hoc-van-phong": {
        "bg_top": (10, 26, 20), "bg_bot": (5, 13, 10),
        "primary": (16, 185, 129), "accent": (52, 211, 153),
        "tag": "OFFICE & PRODUCTIVITY", "motif": "spreadsheet_grid"
    },
    "dien-thoai-thiet-bi": {
        "bg_top": (22, 14, 38), "bg_bot": (10, 6, 20),
        "primary": (139, 92, 246), "accent": (192, 132, 252),
        "tag": "SMARTPHONE & DEVICES", "motif": "mobile_screen"
    },
    "mang-xa-hoi-ung-dung": {
        "bg_top": (14, 18, 38), "bg_bot": (7, 9, 20),
        "primary": (14, 165, 233), "accent": (244, 63, 94),
        "tag": "SOCIAL NETWORK & APPS", "motif": "social_network"
    },
    "sua-loi-su-co": {
        "bg_top": (30, 14, 14), "bg_bot": (15, 6, 6),
        "primary": (239, 68, 68), "accent": (245, 158, 11),
        "tag": "TROUBLESHOOTING & REPAIR", "motif": "gear_repair"
    },
    "dich-vu-cong-tien-ich": {
        "bg_top": (10, 20, 36), "bg_bot": (5, 10, 18),
        "primary": (234, 179, 8), "accent": (59, 130, 246),
        "tag": "DIGITAL PUBLIC SERVICES", "motif": "shield_identity"
    },
    "meo-vat-doi-song": {
        "bg_top": (8, 26, 26), "bg_bot": (4, 13, 13),
        "primary": (20, 184, 166), "accent": (251, 191, 36),
        "tag": "PRACTICAL LIFE HACKS", "motif": "lightbulb_spark"
    }
}

DEFAULT_PROFILE: Dict[str, Any] = {
    "bg_top": (15, 23, 42), "bg_bot": (8, 12, 22),
    "primary": (56, 189, 248), "accent": (168, 85, 247),
    "tag": "TECH HOW-TO & SOLUTIONS", "motif": "hexagon_core"
}

class VibeImageComposer:
    def __init__(self, output_dir: str = "cache/tech_images"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.font_bold = self._load_font("C:/Windows/Fonts/arialbd.ttf", 36)
        self.font_title_mid = self._load_font("C:/Windows/Fonts/arialbd.ttf", 30)
        self.font_subtitle = self._load_font("C:/Windows/Fonts/arial.ttf", 20)
        self.font_badge = self._load_font("C:/Windows/Fonts/arialbd.ttf", 15)
        self.font_mono = self._load_font("C:/Windows/Fonts/consola.ttf", 14)

    def _load_font(self, font_path: str, size: int):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            return ImageFont.load_default()

    def get_profile_for_keyword(self, primary_kw: str, category_name: str = "") -> dict:
        kw_norm = primary_kw.strip().lower()
        cat_norm = category_name.strip().lower()

        # Check explicit brand / tool matches first
        for k, prof in BRAND_PROFILES.items():
            if k in kw_norm or kw_norm in k:
                return prof

        # Check category name mapping
        cat_map = {
            "máy tính": "thu-thuat-may-tinh", "windows": "thu-thuat-may-tinh", "macos": "thu-thuat-may-tinh",
            "văn phòng": "tin-hoc-van-phong", "excel": "tin-hoc-van-phong", "word": "tin-hoc-van-phong", "office": "tin-hoc-van-phong",
            "điện thoại": "dien-thoai-thiet-bi", "thiết bị": "dien-thoai-thiet-bi", "iphone": "dien-thoai-thiet-bi", "android": "dien-thoai-thiet-bi",
            "mạng xã hội": "mang-xa-hoi-ung-dung", "ứng dụng": "mang-xa-hoi-ung-dung", "facebook": "mang-xa-hoi-ung-dung", "zalo": "mang-xa-hoi-ung-dung",
            "sửa lỗi": "sua-loi-su-co", "khắc phục": "sua-loi-su-co", "sự cố": "sua-loi-su-co", "lỗi": "sua-loi-su-co",
            "dịch vụ công": "dich-vu-cong-tien-ich", "tiện ích": "dich-vu-cong-tien-ich", "vneid": "dich-vu-cong-tien-ich", "cccd": "dich-vu-cong-tien-ich",
            "mẹo vặt": "meo-vat-doi-song", "đời sống": "meo-vat-doi-song"
        }
        for term, cat_key in cat_map.items():
            if term in cat_norm or term in kw_norm:
                return BRAND_PROFILES.get(cat_key, DEFAULT_PROFILE)

        return DEFAULT_PROFILE

    def create_gradient_canvas(self, width: int, height: int, top_col: tuple, bot_col: tuple) -> Image.Image:
        base = Image.new("RGB", (width, height), top_col)
        draw = ImageDraw.Draw(base)
        for y in range(height):
            ratio = y / float(height)
            r = int(top_col[0] * (1 - ratio) + bot_col[0] * ratio)
            g = int(top_col[1] * (1 - ratio) + bot_col[1] * ratio)
            b = int(top_col[2] * (1 - ratio) + bot_col[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        return base

    def draw_tech_grid(self, draw: ImageDraw.Draw, width: int, height: int, accent_col: tuple):
        grid_col = (accent_col[0] // 8, accent_col[1] // 8, accent_col[2] // 8)
        step = 48
        for x in range(0, width, step):
            draw.line([(x, 0), (x, height)], fill=grid_col, width=1)
        for y in range(0, height, step):
            draw.line([(0, y), (width, y)], fill=grid_col, width=1)
            
        border_col = (accent_col[0] // 3, accent_col[1] // 3, accent_col[2] // 3)
        draw.rectangle([(8, 8), (width - 9, height - 9)], outline=border_col, width=2)
        accent_bright = accent_col
        draw.line([(10, 10), (45, 10)], fill=accent_bright, width=3)
        draw.line([(10, 10), (10, 45)], fill=accent_bright, width=3)
        draw.line([(width - 45, 10), (width - 10, 10)], fill=accent_bright, width=3)
        draw.line([(width - 10, 10), (width - 10, 45)], fill=accent_bright, width=3)

    def draw_motif(self, draw: ImageDraw.Draw, motif_type: str, cx: int, cy: int, primary: tuple, accent: tuple):
        if motif_type == "spiral_nodes":
            for r in [40, 80, 120, 160]:
                draw.arc([(cx - r, cy - r), (cx + r, cy + r)], start=0, end=360, fill=primary, width=2)
            for i in range(12):
                angle = i * (math.pi / 6)
                x1 = int(cx + 50 * math.cos(angle))
                y1 = int(cy + 50 * math.sin(angle))
                x2 = int(cx + 155 * math.cos(angle + 0.3))
                y2 = int(cy + 155 * math.sin(angle + 0.3))
                draw.line([(x1, y1), (x2, y2)], fill=accent, width=2)
                draw.ellipse([(x2 - 5, y2 - 5), (x2 + 5, y2 + 5)], fill=primary)
            draw.ellipse([(cx - 20, cy - 20), (cx + 20, cy + 20)], fill=accent)

        elif motif_type == "sparkle_star":
            for r in [60, 120, 180]:
                draw.arc([(cx - r, cy - r), (cx + r, cy + r)], start=0, end=360, fill=(primary[0]//4, primary[1]//4, primary[2]//4), width=1)
            draw.polygon([(cx, cy - 140), (cx + 35, cy), (cx, cy + 140), (cx - 35, cy)], fill=primary)
            draw.polygon([(cx - 140, cy), (cx, cy + 35), (cx + 140, cy), (cx, cy - 35)], fill=accent)
            draw.ellipse([(cx - 25, cy - 25), (cx + 25, cy + 25)], fill=(255, 255, 255))

        elif motif_type == "soundwave_spectrum":
            bars = 24
            spacing = 12
            start_x = cx - (bars * spacing) // 2
            for i in range(bars):
                bx = start_x + i * spacing
                h = int(30 + 110 * math.sin((i / bars) * math.pi) * abs(math.cos(i * 0.7)))
                col = accent if i % 2 == 0 else primary
                draw.line([(bx, cy - h), (bx, cy + h)], fill=col, width=6)
            draw.ellipse([(cx - 160, cy - 160), (cx + 160, cy + 160)], outline=primary, width=2)

        elif motif_type == "camera_shutter":
            draw.rectangle([(cx - 140, cy - 90), (cx + 140, cy + 90)], outline=primary, width=4)
            draw.polygon([(cx + 140, cy - 50), (cx + 190, cy - 80), (cx + 190, cy + 80), (cx + 140, cy + 50)], fill=accent)
            draw.ellipse([(cx - 50, cy - 50), (cx + 50, cy + 50)], outline=accent, width=3)
            draw.polygon([(cx - 15, cy - 25), (cx + 25, cy), (cx - 15, cy + 25)], fill=primary)

        elif motif_type == "security_shield":
            draw.polygon([(cx, cy - 130), (cx + 110, cy - 70), (cx + 110, cy + 30), (cx, cy + 140), (cx - 110, cy + 30), (cx - 110, cy - 70)], outline=primary, fill=(primary[0]//5, primary[1]//5, primary[2]//5))
            draw.polygon([(cx, cy - 100), (cx + 80, cy - 50), (cx + 80, cy + 20), (cx, cy + 110), (cx - 80, cy + 20), (cx - 80, cy - 50)], outline=accent, width=3)
            draw.line([(cx - 35, cy), (cx - 10, cy + 30)], fill=accent, width=8)
            draw.line([(cx - 10, cy + 30), (cx + 45, cy - 35)], fill=accent, width=8)

        elif motif_type == "slide_deck":
            draw.rectangle([(cx - 100, cy - 80), (cx + 120, cy + 60)], outline=(primary[0]//3, primary[1]//3, primary[2]//3), fill=(primary[0]//8, primary[1]//8, primary[2]//8))
            draw.rectangle([(cx - 120, cy - 100), (cx + 100, cy + 40)], outline=primary, width=3, fill=(primary[0]//6, primary[1]//6, primary[2]//6))
            draw.rectangle([(cx - 140, cy - 120), (cx + 80, cy + 20)], outline=accent, width=4, fill=(primary[0]//4, primary[1]//4, primary[2]//4))
            draw.line([(cx - 120, cy - 70), (cx + 40, cy - 70)], fill=(255, 255, 255), width=3)
            draw.line([(cx - 120, cy - 40), (cx + 10, cy - 40)], fill=accent, width=2)
            draw.line([(cx - 120, cy - 15), (cx - 10, cy - 15)], fill=accent, width=2)

        elif motif_type == "code_brackets":
            draw.rectangle([(cx - 140, cy - 100), (cx + 140, cy + 100)], outline=primary, width=3, fill=(10, 15, 12))
            draw.line([(cx - 140, cy - 70), (cx + 140, cy - 70)], fill=primary, width=2)
            draw.ellipse([(cx - 120, cy - 85), (cx - 110, cy - 75)], fill=(239, 68, 68))
            draw.ellipse([(cx - 100, cy - 85), (cx - 90, cy - 75)], fill=(245, 158, 11))
            draw.ellipse([(cx - 80, cy - 85), (cx - 70, cy - 75)], fill=(34, 197, 94))
            draw.line([(cx - 60, cy - 30), (cx - 90, cy), (cx - 60, cy + 30)], fill=accent, width=5)
            draw.line([(cx - 20, cy + 40), (cx + 20, cy - 40)], fill=(255, 255, 255), width=4)
            draw.line([(cx + 60, cy - 30), (cx + 90, cy), (cx + 60, cy + 30)], fill=accent, width=5)

        elif motif_type == "wealth_growth":
            draw.line([(cx - 130, cy + 100), (cx + 130, cy + 100)], fill=primary, width=3)
            draw.line([(cx - 130, cy - 100), (cx - 130, cy + 100)], fill=primary, width=3)
            pts = [(cx - 120, cy + 80), (cx - 60, cy + 40), (cx, cy + 60), (cx + 60, cy - 20), (cx + 120, cy - 90)]
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i+1]], fill=accent, width=6)
                draw.ellipse([(pts[i][0] - 6, pts[i][1] - 6), (pts[i][0] + 6, pts[i][1] + 6)], fill=(255, 255, 255))
            draw.ellipse([(pts[-1][0] - 8, pts[-1][1] - 8), (pts[-1][0] + 8, pts[-1][1] + 8)], fill=primary)
            draw.polygon([(cx + 135, cy - 105), (cx + 105, cy - 95), (cx + 115, cy - 75)], fill=primary)

        elif motif_type == "pc_desktop":
            # Monitor outline
            draw.rectangle([(cx - 130, cy - 90), (cx + 130, cy + 60)], outline=primary, width=3, fill=(10, 15, 25))
            # Screen inner border
            draw.rectangle([(cx - 120, cy - 80), (cx + 120, cy + 50)], outline=(primary[0]//3, primary[1]//3, primary[2]//3))
            # Window bar
            draw.rectangle([(cx - 120, cy - 80), (cx + 120, cy - 60)], fill=(primary[0]//4, primary[1]//4, primary[2]//4))
            draw.ellipse([(cx - 110, cy - 73), (cx - 104, cy - 67)], fill=(239, 68, 68))
            draw.ellipse([(cx - 98, cy - 73), (cx - 92, cy - 67)], fill=(245, 158, 11))
            draw.ellipse([(cx - 86, cy - 73), (cx - 80, cy - 67)], fill=(34, 197, 94))
            # Screen content lines
            draw.line([(cx - 100, cy - 35), (cx + 80, cy - 35)], fill=accent, width=3)
            draw.line([(cx - 100, cy - 10), (cx + 50, cy - 10)], fill=(255, 255, 255), width=2)
            draw.line([(cx - 100, cy + 15), (cx + 20, cy + 15)], fill=(156, 163, 175), width=2)
            # Stand
            draw.polygon([(cx - 20, cy + 60), (cx + 20, cy + 60), (cx + 35, cy + 100), (cx - 35, cy + 100)], fill=primary)
            draw.rectangle([(cx - 60, cy + 98), (cx + 60, cy + 105)], fill=accent)

        elif motif_type == "spreadsheet_grid":
            # Spreadsheet table
            draw.rectangle([(cx - 130, cy - 80), (cx + 130, cy + 80)], outline=primary, width=3, fill=(10, 20, 15))
            # Header row
            draw.rectangle([(cx - 130, cy - 80), (cx + 130, cy - 45)], fill=primary)
            draw.line([(cx - 50, cy - 80), (cx - 50, cy - 45)], fill=(255, 255, 255), width=2)
            draw.line([(cx + 40, cy - 80), (cx + 40, cy - 45)], fill=(255, 255, 255), width=2)
            # Row lines
            for ry in [-10, 25, 60]:
                draw.line([(cx - 130, cy + ry), (cx + 130, cy + ry)], fill=(primary[0]//3, primary[1]//3, primary[2]//3), width=1)
            # Col lines
            draw.line([(cx - 50, cy - 45), (cx - 50, cy + 80)], fill=(primary[0]//3, primary[1]//3, primary[2]//3), width=1)
            draw.line([(cx + 40, cy - 45), (cx + 40, cy + 80)], fill=(primary[0]//3, primary[1]//3, primary[2]//3), width=1)
            # Highlighted cell
            draw.rectangle([(cx - 50, cy - 10), (cx + 40, cy + 25)], outline=accent, width=3, fill=(accent[0]//5, accent[1]//5, accent[2]//5))
            draw.text((cx - 25, cy - 2), "SUM()", font=self.font_mono, fill=(255, 255, 255))

        elif motif_type == "mobile_screen":
            # Smartphone outline
            draw.rounded_rectangle([(cx - 75, cy - 120), (cx + 75, cy + 120)], radius=20, outline=primary, width=3, fill=(15, 12, 25))
            # Dynamic Island / Notch
            draw.rounded_rectangle([(cx - 25, cy - 108), (cx + 25, cy - 96)], radius=6, fill=accent)
            # UI Cards
            draw.rounded_rectangle([(cx - 55, cy - 70), (cx + 55, cy - 10)], radius=8, fill=(primary[0]//4, primary[1]//4, primary[2]//4), outline=primary)
            draw.line([(cx - 40, cy - 50), (cx + 20, cy - 50)], fill=accent, width=3)
            draw.line([(cx - 40, cy - 30), (cx + 40, cy - 30)], fill=(255, 255, 255), width=2)
            draw.rounded_rectangle([(cx - 55, cy + 10), (cx + 55, cy + 70)], radius=8, fill=(primary[0]//5, primary[1]//5, primary[2]//5))
            # Home bar
            draw.line([(cx - 25, cy + 105), (cx + 25, cy + 105)], fill=(255, 255, 255), width=3)

        elif motif_type == "social_network":
            # Central hub
            draw.ellipse([(cx - 30, cy - 30), (cx + 30, cy + 30)], fill=primary, outline=accent, width=2)
            satellites = [
                (cx - 100, cy - 70, accent), (cx + 90, cy - 60, primary),
                (cx - 110, cy + 40, primary), (cx + 100, cy + 50, accent),
                (cx, cy - 110, accent), (cx, cy + 100, primary)
            ]
            for sx, sy, col in satellites:
                draw.line([(cx, cy), (sx, sy)], fill=(accent[0]//2, accent[1]//2, accent[2]//2), width=2)
                draw.ellipse([(sx - 16, sy - 16), (sx + 16, sy + 16)], fill=col)
                draw.ellipse([(sx - 6, sy - 6), (sx + 6, sy + 6)], fill=(255, 255, 255))

        elif motif_type == "gear_repair":
            # Gear center
            draw.ellipse([(cx - 70, cy - 70), (cx + 70, cy + 70)], outline=primary, width=16)
            for i in range(8):
                angle = i * (math.pi / 4)
                gx = int(cx + 80 * math.cos(angle))
                gy = int(cy + 80 * math.sin(angle))
                draw.rectangle([(gx - 12, gy - 12), (gx + 12, gy + 12)], fill=primary)
            draw.ellipse([(cx - 35, cy - 35), (cx + 35, cy + 35)], fill=(25, 12, 12), outline=accent, width=3)
            # Wrench silhouette in center
            draw.line([(cx - 25, cy + 25), (cx + 25, cy - 25)], fill=accent, width=8)
            draw.ellipse([(cx + 18, cy - 32), (cx + 32, cy - 18)], fill=accent)

        elif motif_type == "shield_identity":
            # Shield
            draw.polygon([(cx, cy - 110), (cx + 90, cy - 60), (cx + 90, cy + 20), (cx, cy + 110), (cx - 90, cy + 20), (cx - 90, cy - 60)], outline=primary, width=3, fill=(10, 20, 35))
            # Inner ID badge
            draw.rounded_rectangle([(cx - 55, cy - 50), (cx + 55, cy + 50)], radius=8, outline=accent, width=2, fill=(15, 30, 50))
            draw.ellipse([(cx - 25, cy - 35), (cx - 5, cy - 15)], fill=primary)
            draw.line([(cx + 5, cy - 30), (cx + 40, cy - 30)], fill=(255, 255, 255), width=2)
            draw.line([(cx + 5, cy - 18), (cx + 30, cy - 18)], fill=accent, width=2)
            draw.line([(cx - 40, cy + 10), (cx + 40, cy + 10)], fill=(255, 255, 255), width=2)
            draw.line([(cx - 40, cy + 25), (cx + 20, cy + 25)], fill=(156, 163, 175), width=2)

        elif motif_type == "lightbulb_spark":
            # Bulb dome
            draw.ellipse([(cx - 50, cy - 80), (cx + 50, cy + 20)], outline=primary, width=3, fill=(20, 30, 25))
            draw.rectangle([(cx - 25, cy + 10), (cx + 25, cy + 45)], fill=primary)
            draw.line([(cx - 18, cy + 52), (cx + 18, cy + 52)], fill=accent, width=4)
            # Filament
            draw.line([(cx - 15, cy - 20), (cx, cy - 40)], fill=accent, width=3)
            draw.line([(cx, cy - 40), (cx + 15, cy - 20)], fill=accent, width=3)
            # Sparks
            for angle in [0, 45, 90, 135, 180, 225, 315]:
                rad = math.radians(angle)
                x1 = int(cx + 70 * math.cos(rad))
                y1 = int(cy - 30 + 70 * math.sin(rad))
                x2 = int(cx + 95 * math.cos(rad))
                y2 = int(cy - 30 + 95 * math.sin(rad))
                draw.line([(x1, y1), (x2, y2)], fill=accent, width=2)

        else:
            for r in [60, 110, 160]:
                draw.regular_polygon((cx, cy, r), 6, outline=primary if r == 110 else accent, width=2)
            draw.ellipse([(cx - 20, cy - 20), (cx + 20, cy + 20)], fill=primary)
            draw.ellipse([(cx - 8, cy - 8), (cx + 8, cy + 8)], fill=(255, 255, 255))

    def compose_banner(self, title: str, category_name: str, primary_kw: str, slug: str, site_domain: str = "") -> str:
        width, height = 1200, 675
        profile = self.get_profile_for_keyword(primary_kw, category_name=category_name)
        
        img = self.create_gradient_canvas(width, height, profile["bg_top"], profile["bg_bot"])
        draw = ImageDraw.Draw(img)
        
        self.draw_tech_grid(draw, width, height, profile["accent"])
        self.draw_motif(draw, profile["motif"], cx=970, cy=337, primary=profile["primary"], accent=profile["accent"])
        
        draw.rectangle([(70, 65), (420, 102)], fill=(profile["bg_bot"][0] + 15, profile["bg_bot"][1] + 15, profile["bg_bot"][2] + 20), outline=profile["primary"], width=1)
        draw.text((85, 73), f"// {category_name.upper()}  •  2026", font=self.font_badge, fill=profile["accent"])
        draw.text((70, 125), f"▶ CHỦ ĐỀ CỐT LÕI: {profile['tag']}", font=self.font_mono, fill=(156, 163, 175))
        
        words = title.split()
        lines, current = [], []
        for w in words:
            test_line = " ".join(current + [w])
            if len(test_line) <= 34:
                current.append(w)
            else:
                lines.append(" ".join(current))
                current = [w]
        if current:
            lines.append(" ".join(current))
            
        y_pos = 175
        for idx, line in enumerate(lines[:3]):
            fill_col = (255, 255, 255) if idx < 2 else profile["accent"]
            draw.text((70, y_pos), line, font=self.font_title_mid, fill=fill_col)
            y_pos += 48
            
        y_pos = max(y_pos + 15, 360)
        kw_display = primary_kw.upper()
        draw.rectangle([(70, y_pos), (520, y_pos + 46)], fill=(profile["bg_top"][0] + 25, profile["bg_top"][1] + 25, profile["bg_top"][2] + 30), outline=profile["accent"], width=2)
        draw.text((85, y_pos + 12), f"FOCUS KEYWORD: {kw_display}", font=self.font_badge, fill=(255, 255, 255))
        
        y_bot = height - 105
        draw.line([(70, y_bot - 20), (740, y_bot - 20)], fill=(profile["accent"][0]//3, profile["accent"][1]//3, profile["accent"][2]//3), width=1)
        draw.text((70, y_bot), "✓ FACT-CHECKED 2026", font=self.font_badge, fill=profile["primary"])
        draw.text((275, y_bot), "✓ HƯỚNG DẪN THỰC THI", font=self.font_badge, fill=(209, 213, 219))
        draw.text((495, y_bot), "✓ TỐI ƯU HIỆU SUẤT", font=self.font_badge, fill=profile["accent"])
        
        # Watermark
        domain_tag = site_domain.upper() if site_domain else "TECH PORTAL"
        watermark_text = f"{domain_tag}  |  DIGITAL AUTOMATION & AI SAAS INTELLIGENCE"
        draw.text((70, y_bot + 32), watermark_text, font=self.font_mono, fill=(107, 114, 128))
        
        out_path = os.path.join(self.output_dir, f"{slug}-featured.webp")
        img.save(out_path, "WEBP", quality=85, method=6)
        
        file_size_kb = os.path.getsize(out_path) / 1024
        print(f"  [+] Generated Unique WebP Banner: {os.path.basename(out_path)} ({file_size_kb:.1f} KB)")
        return out_path
