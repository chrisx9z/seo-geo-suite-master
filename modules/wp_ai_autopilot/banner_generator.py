"""
Lightweight WebP Banner & Technical Illustration Generator (< 50KB)
Creates high-definition 16:9 WebP images (Featured Image + In-Content Technical Diagram).
"""

import os
from PIL import Image, ImageDraw
from typing import Optional

class WebPBannerGenerator:
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), "..", "..", "assets", "banners")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_banner(self, title: str, category: str = "TECH & AI", slug: str = "banner") -> str:
        """Featured Banner (1200x675, Dark Cyberpunk, < 50KB)."""
        width, height = 1200, 675
        img = Image.new("RGB", (width, height), color=(11, 13, 19))
        draw = ImageDraw.Draw(img)

        # Cyber Grid
        for x in range(0, width, 45):
            draw.line([(x, 0), (x, height)], fill=(22, 27, 38), width=1)
        for y in range(0, height, 45):
            draw.line([(0, y), (width, y)], fill=(22, 27, 38), width=1)

        cyan_accent = (0, 229, 255)
        violet_accent = (168, 85, 247)
        draw.rectangle([(0, height - 6), (width, height)], fill=cyan_accent)
        draw.line([(60, 50), (220, 50)], fill=cyan_accent, width=4)

        for r in [120, 180, 240]:
            draw.arc([(width - 200 - r, 80 - r), (width - 200 + r, 80 + r)], start=0, end=360, fill=(28, 35, 51), width=1)

        draw.rectangle([(60, 80), (240, 115)], fill=(18, 24, 38), outline=cyan_accent, width=1)
        draw.text((75, 90), f"// {category.upper()}", fill=cyan_accent)
        draw.rectangle([(60, 140), (width - 60, height - 80)], fill=(15, 18, 26, 180), outline=(32, 40, 58), width=1)
        draw.text((100, 190), "MASTER SEO GEO SPECIAL REPORT", fill=(140, 155, 180))

        words = title.split()
        lines, cur_line = [], []
        for w in words:
            if len(" ".join(cur_line + [w])) <= 45:
                cur_line.append(w)
            else:
                lines.append(" ".join(cur_line))
                cur_line = [w]
        if cur_line:
            lines.append(" ".join(cur_line))

        y_offset = 260
        for idx, line in enumerate(lines[:3]):
            color = (255, 255, 255) if idx == 0 else (220, 230, 245)
            draw.text((100, y_offset), line, fill=color)
            y_offset += 65

        draw.text((100, height - 125), "🌐 AUTO SEO GEO MASTER SUITE  |  HIGH INFORMATION GAIN  |  RANKMATH 100/100", fill=(90, 105, 130))

        out_path = os.path.join(self.output_dir, f"{slug}-featured.webp")
        img.save(out_path, "WEBP", quality=82, method=6)
        # Also generate ultra-compressed AVIF
        avif_path = out_path.replace(".webp", ".avif")
        try:
            img.save(avif_path, "AVIF", quality=75)
            print(f"  🖼️ Generated Ultra-compressed AVIF: {os.path.basename(avif_path)} ({os.path.getsize(avif_path)/1024:.1f} KB)")
        except Exception:
            pass
        print(f"  🎨 Generated Featured Banner: {os.path.basename(out_path)} ({os.path.getsize(out_path)/1024:.1f} KB)")
        return out_path

    def generate_in_content_illustration(self, focus_keyword: str, slug: str) -> str:
        """In-Content Technical Flowchart / Infographic Image (1200x675, < 50KB)."""
        width, height = 1200, 675
        img = Image.new("RGB", (width, height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)

        # Draw Blueprint Grid
        for x in range(0, width, 40):
            draw.line([(x, 0), (x, height)], fill=(26, 38, 66), width=1)
        for y in range(0, height, 40):
            draw.line([(0, y), (width, y)], fill=(26, 38, 66), width=1)

        # Header Title
        draw.text((80, 50), f"KIẾN TRÚC KỸ THUẬT & LUỒNG XỬ LÝ DỮ LIỆU: {focus_keyword.upper()}", fill=(56, 189, 248))
        draw.line([(80, 85), (width - 80, 85)], fill=(56, 189, 248), width=2)

        # Draw 3 Architectural Blocks
        box_width = 300
        box_height = 360
        y_pos = 140

        boxes = [
            ("1. Ingestion Layer", ["Thu Thập Dữ Liệu", "Khử Trùng & Lọc Rác", "Data Normalization"], (30, 41, 59), (56, 189, 248)),
            ("2. AI Reasoning Core", ["Phân Tích Ngữ Nghĩa", "Mô Hình Hóa Logic", "Tối Ưu Quyết Định"], (30, 41, 59), (74, 222, 128)),
            ("3. Execution Gateway", ["Bắn Tín Hiệu API", "Tự Động Hóa Thực Thi", "Báo Cáo & Giám Sát"], (30, 41, 59), (168, 85, 247))
        ]

        for idx, (b_title, b_items, bg, border_col) in enumerate(boxes):
            x_pos = 80 + idx * 370
            draw.rectangle([(x_pos, y_pos), (x_pos + box_width, y_pos + box_height)], fill=bg, outline=border_col, width=2)
            draw.text((x_pos + 20, y_pos + 25), b_title, fill=border_col)
            draw.line([(x_pos + 20, y_pos + 60), (x_pos + box_width - 20, y_pos + 60)], fill=(51, 65, 85), width=1)

            item_y = y_pos + 80
            for it in b_items:
                draw.text((x_pos + 20, item_y), f"• {it}", fill=(203, 213, 225))
                item_y += 50

            # Arrow to next box
            if idx < 2:
                arrow_x = x_pos + box_width + 15
                draw.line([(arrow_x, y_pos + 180), (arrow_x + 35, y_pos + 180)], fill=(148, 163, 184), width=3)
                draw.polygon([(arrow_x + 35, y_pos + 175), (arrow_x + 45, y_pos + 180), (arrow_x + 35, y_pos + 185)], fill=(148, 163, 184))

        draw.text((80, height - 70), f"Biểu đồ minh họa chuyên sâu: {focus_keyword}  |  Nguồn: Master SEO Architecture Framework", fill=(100, 116, 139))

        out_path = os.path.join(self.output_dir, f"{slug}-diagram.webp")
        img.save(out_path, "WEBP", quality=82, method=6)
        # Also generate ultra-compressed AVIF
        avif_path = out_path.replace(".webp", ".avif")
        try:
            img.save(avif_path, "AVIF", quality=75)
            print(f"  🖼️ Generated Ultra-compressed AVIF: {os.path.basename(avif_path)} ({os.path.getsize(avif_path)/1024:.1f} KB)")
        except Exception:
            pass
        print(f"  🎨 Generated In-Content Diagram: {os.path.basename(out_path)} ({os.path.getsize(out_path)/1024:.1f} KB)")
        return out_path
