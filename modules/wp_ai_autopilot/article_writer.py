"""
Article Writer Engine - Enterprise RankMath SEO & Quality Standards (Upgraded 2026)
Uses Google Gemini (3.5-Flash / 3.7-Flash / 3.8-Flash) to generate deep, 100% authentic,
actionable technical guides without generic boilerplate or text-card filler.
"""

import os
import json
import re
import time
import random
from datetime import datetime
from typing import Dict, Any, Optional, List

AUTHORITY_SOURCES_WHITELIST = [
    {"name": "Wikipedia Official Archive", "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"},
    {"name": "GitHub Open Source Specifications", "url": "https://github.com"},
    {"name": "W3C Web Standards", "url": "https://www.w3.org/standards/"},
    {"name": "ArXiv Scientific Papers", "url": "https://arxiv.org/abs/2303.08774"},
    {"name": "IETF Engineering Standards", "url": "https://www.ietf.org/standards/"}
]

class ArticleWriter:
    def __init__(self, provider: str = "auto", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not self.api_key:
            env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
            if os.path.exists(env_file):
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            self.api_key = line.split("=", 1)[1].strip()
                            break

    def _calculate_rankmath_density(self, content: str, keyword: str) -> float:
        clean_text = re.sub(r"<[^>]+>", " ", content.lower())
        words = [w for w in clean_text.split() if len(w) > 0]
        total_words = len(words)
        if total_words == 0:
            return 0.0
        kw_clean = keyword.lower().strip()
        matches = len(re.findall(r'\b' + re.escape(kw_clean) + r'\b', clean_text))
        return (matches / total_words) * 100

    def generate_ai_content(self, topic: str, focus_keyword: str, category_name: str = "") -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing. Authentic generation requires active API key.")

        from google import genai
        client = genai.Client(api_key=self.api_key)

        is_troubleshooting_or_howto = any(w in (topic + " " + category_name + " " + focus_keyword).lower() for w in [
            "sửa lỗi", "khắc phục", "hướng dẫn", "cách làm", "cách dùng", "làm thế nào", "tại sao", "làm sao",
            "excel", "word", "powerpoint", "máy tính", "windows", "iphone", "android", "vneid", "bảo hiểm", "zalo", "facebook", "cccd", "mẹo vặt"
        ]) and not any(w in (topic + " " + focus_keyword).lower() for w in ["ai mmo", "chat gpt", "gemini", "claude", "midjourney", "suno", "kling"])

        if is_troubleshooting_or_howto:
            prompt = f"""Bạn là Chuyên gia Kỹ thuật Phần mềm & Thủ thuật Số Cao Cấp (Senior IT Specialist & Practical Tech Advisor).
Hãy viết một bài viết cẩm nang hướng dẫn thực hành và khắc phục sự cố cực kỳ chi tiết, dễ hiểu, thực tế và chuẩn xác 100% bằng tiếng Việt về chủ đề:
"{topic}"
Từ khóa chính: "{focus_keyword}"
Chuyên mục: "{category_name or 'Thủ Thuật & Xử Lý Sự Cố'}"

BỘ QUY TẮC BẮT BUỘC ĐỂ KHÔNG BỊ COI LÀ NỘI DUNG RÁC (ANTI-BOILERPLATE, ANTI-AI CLICHE):
1. CẤM TUYỆT ĐỐI CÂU MỞ BÀI SÁO RỖNG ("Trong thời đại số...", "Hiện nay nhiều người dùng gặp...", "Máy tính/điện thoại là vật dụng quan trọng...").
   Mở bài đi thẳng vào vấn đề cốt lõi: nêu rõ biểu hiện lỗi hoặc nhu cầu của người dùng, nguyên nhân gốc rễ (Root Cause) và lộ trình giải quyết dứt điểm vấn đề ngay tại bài viết này.
2. NỘI DUNG CHUYÊN SÂU (> 1,800 từ):
   - Phân tích nguyên nhân kỹ thuật chi tiết (tại sao xảy ra hiện tượng này, xung đột phần mềm/hệ điều hành, phân quyền, cache, cấu hình sai).
   - Hướng dẫn các giải pháp thực tế theo thứ tự từ đơn giản nhất (Quick Fix) đến triệt để chuyên sâu (Deep Troubleshooting).
   - Mỗi bước hướng dẫn phải cực kỳ rõ ràng: từng cú click chuột, phím tắt (Shortcut), đường dẫn menu cài đặt cụ thể (Settings/Registry/Terminal/CLI nếu có) hoặc công thức chuẩn xác (nếu là Excel/Word/Phần mềm).
   - Bảng tổng hợp đối soát các trường hợp lỗi, nguyên nhân và cách xử lý tương ứng bằng thẻ <table>.
   - Các lưu ý an toàn dữ liệu (Backup, bảo mật thông tin cá nhân, tránh thao tác sai hỏng hệ thống).
   - FAQ: Giải đáp chi tiết 3-4 câu hỏi/thắc mắc thực tế hay gặp nhất của người dùng khi áp dụng.
3. ĐỊNH DẠNG:
   - Dùng HTML semantic: <h2>, <h3>, <p>, <ul>, <li>, <code>, <pre>.
   - Có shortcode [ez-toc] ở đầu sau đoạn mở bài.
   - Bảng so sánh / tổng hợp bằng thẻ <table> có CSS rõ ràng.
   - Khối lệnh/phím tắt/code dùng <pre><code> hoặc <code>.

Đầu ra trả về trực tiếp mã HTML cho bài viết (không bao bọc trong ```html ... ```).
"""
        else:
            prompt = f"""Bạn là Kỹ sư Trưởng AI & Chuyên gia Kỹ thuật Phần mềm thực chiến (Enterprise Tech Lead).
Hãy viết một bài viết cẩm nang kỹ thuật cực kỳ chi tiết, thực tế, sâu sắc và thực chiến 100% bằng tiếng Việt về chủ đề:
"{topic}"
Từ khóa chính: "{focus_keyword}"
Chuyên mục: "{category_name or 'Trí Tuệ Nhân Tạo & AI'}"

BỘ QUY TẮC BẮT BUỘC ĐỂ KHÔNG BỊ COI LÀ NỘI DUNG RÁC (ANTI-BOILERPLATE, ANTI-AI CLICHE):
1. CẤM TUYỆT ĐỐI CÂU MỞ BÀI SÁO RỖNG ("Trong kỷ nguyên số...", "Trí tuệ nhân tạo ngày nay...", "Nhiều người nghĩ tự động hóa là...").
   Mở bài đi thẳng vào vấn đề cốt lõi, nêu rõ giải pháp kỹ thuật, lợi ích định lượng và lý do lập trình viên/doanh nghiệp cần triển khai giải pháp này ngay trong năm 2026.
2. NỘI DUNG CHUYÊN SÂU (> 1,800 từ):
   - Kiến trúc kỹ thuật và luồng dữ liệu (Data Pipeline / System Flow) chi tiết.
   - Hướng dẫn cài đặt, cấu hình từng bước kèm mã nguồn / lệnh CLI thực tế.
   - Bảng đối soát benchmark hiệu năng thực tế (thời gian, RAM/VRAM tiêu thụ, chi phí, throughput).
   - Tích hợp thực chiến vào hệ thống sản phẩm / MMO tự động hóa.
   - FAQ giải quyết 3-4 lỗi thực tế hay gặp nhất.
3. ĐỊNH DẠNG:
   - Dùng HTML semantic: <h2>, <h3>, <p>, <ul>, <li>, <code>, <pre>.
   - Có shortcode [ez-toc] ở đầu sau đoạn mở bài.
   - Bảng so sánh bằng thẻ <table> có CSS rõ ràng.
   - Khối code dùng <pre><code class="language-bash"> hoặc <pre><code class="language-python">.

Đầu ra trả về trực tiếp mã HTML cho bài viết (không bao bọc trong ```html ... ```).
"""
        models_to_try = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.7-flash"]
        for attempt in range(1, 4):
            for m in models_to_try:
                try:
                    resp = client.models.generate_content(model=m, contents=prompt)
                    if resp and resp.text:
                        raw = resp.text.strip()
                        if raw.startswith("```html"):
                            raw = raw[7:]
                        if raw.startswith("```"):
                            raw = raw[3:]
                        if raw.endswith("```"):
                            raw = raw[:-3]
                        return raw.strip()
                except Exception as e:
                    print(f"[-] Model {m} error (attempt {attempt}/3): {e}")
                    time.sleep(2)
            if attempt < 3:
                backoff = 5 * attempt
                print(f"[!] All models busy on attempt {attempt}. Backing off for {backoff}s before retry...")
                time.sleep(backoff)

        raise RuntimeError("All Gemini models failed after 3 backoff cycles.")

    def write_article(self, topic: str, outline_data: Dict[str, Any], content_img_url: str = "", force_outbound: Optional[bool] = None, category_name: str = "") -> Dict[str, Any]:
        p_kw = outline_data.get("primary_keyword", topic).strip()
        cat_name = category_name or outline_data.get("category_name", "")

        # Preserve full topic as title if it is descriptive
        # Clean topic: remove trailing punctuation and conjunctions
        cleaned_topic = re.sub(r'[\s\&\,\:\;\-\/]+$', '', topic).strip()
        seo_title = cleaned_topic

        meta_desc = f"Khám phá toàn tập {cleaned_topic}: Thông tin chi tiết, phân tích chuyên sâu và cẩm nang hữu ích cập nhật mới nhất 2026."
        if len(meta_desc) > 160:
            meta_desc = meta_desc[:157] + "..."

        # Generate authentic content with Gemini
        print(f"  [*] Generating authentic content via Gemini for: {topic}...")
        try:
            raw_body = self.generate_ai_content(topic, p_kw, category_name=cat_name)
        except Exception as e:
            print(f"  [-] Gemini generation failed: {e}. Raising error to prevent garbage boilerplate.")
            raise

        content = raw_body

        clean_words = re.sub(r"<[^>]+>", " ", content).split()
        word_count = len(clean_words)

        density = self._calculate_rankmath_density(content, p_kw)

        return {
            "title": seo_title,
            "meta_description": meta_desc,
            "content": content,
            "word_count": word_count,
            "focus_keyword": p_kw,
            "keyword_density": round(density, 2),
            "has_outbound_link": False
        }

WpAiArticleWriter = ArticleWriter
