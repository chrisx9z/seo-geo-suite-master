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

        combined_ctx = (topic + " " + category_name + " " + focus_keyword).lower()
        is_travel = any(w in combined_ctx for w in [
            "du lịch", "lịch trình", "khách sạn", "homestay", "resort", "địa điểm", "ăn gì", "chơi gì",
            "travel", "itinerary", "hotel", "beach", "island", "flight", "visa", "backpack", "phượt"
        ])
        is_world_record = any(w in combined_ctx for w in [
            "nhất thế giới", "kỷ lục", "hành tinh", "vũ trụ", "đại dương", "lớn nhất", "cao nhất", "sâu nhất", "dài nhất"
        ])
        is_troubleshooting_or_howto = any(w in combined_ctx for w in [
            "sửa lỗi", "khắc phục", "hướng dẫn", "cách làm", "cách dùng", "làm thế nào", "tại sao", "làm sao",
            "excel", "word", "powerpoint", "máy tính", "windows", "iphone", "android", "vneid", "bảo hiểm", "zalo", "facebook", "cccd", "mẹo vặt"
        ]) and not any(w in (topic + " " + focus_keyword).lower() for w in ["ai mmo", "chat gpt", "gemini", "claude", "midjourney", "suno", "kling"])

        if is_travel:
            prompt = f"""Bạn là Biên tập viên Du lịch & Lữ hành Thực địa Cao cấp (Senior Travel & Destination Editor).
Hãy viết một bài cẩm nang du lịch thực tế, chi tiết, giàu trải nghiệm thực địa 100% về chủ đề:
"{topic}"
Từ khóa chính: "{focus_keyword}" (BẮT BUỘC: Lồng ghép từ khóa chính này vào ít nhất một tiêu đề <h2> chính và trong 100 từ đầu tiên).
Chuyên mục: "{category_name or 'Cẩm Nang Du Lịch'}"

BỘ QUY TẮC BẮT BUỘC ĐỂ KHÔNG BỊ COI LÀ NỘI DUNG RÁC (ANTI-BOILERPLATE, ANTI-AI CLICHE):
1. CẤM TUYỆT ĐỐI CÂU MỞ BÀI SÁO RỖNG VÀ CẤM BỊA ĐẶT ĐỊA LÝ (không gắn núi đá vôi karst hay cố đô cho vùng biển/đô thị không có thật).
   Mở bài đi thẳng vào đặc trưng nổi bật nhất của điểm đến, thời điểm lý tưởng nhất để đi và tổng quan chi phí/lịch trình thực tế.
2. NỘI DUNG CHUYÊN SÂU (> 1,600 từ):
   - Hướng dẫn di chuyển thực tế (chặng bay/xe, thời gian di chuyển, mức giá tham khảo).
   - Lịch trình gợi ý hoặc danh sách tọa độ trải nghiệm/ẩm thực đặc sắc nhất kèm địa chỉ, khung giờ mở cửa và mẹo tránh đông đúc.
   - Bảng tổng hợp chi phí dự kiến hoặc so sánh các lựa chọn bằng thẻ <table>.
   - Kinh nghiệm đặt phòng, lưu ý an toàn và văn hóa bản địa.
   - FAQ giải đáp 3-4 câu hỏi thực tế của du khách.
3. ĐỊNH DẠNG:
   - Dùng HTML semantic: <h2>, <h3>, <p>, <ul>, <li>, <table>.
   - Có shortcode [ez-toc] ở đầu sau đoạn mở bài.

Đầu ra trả về trực tiếp mã HTML cho bài viết (không bao bọc trong ```html ... ```).
"""
        elif is_world_record:
            prompt = f"""Bạn là Biên tập viên Khoa học & Bách khoa Kỷ lục Thế giới (Senior Encyclopedia & Science Editor).
Hãy viết một bài phân tích chuyên sâu, chính xác về mặt số liệu khoa học/lịch sử/địa lý 100% bằng tiếng Việt về chủ đề:
"{topic}"
Từ khóa chính: "{focus_keyword}" (BẮT BUỘC: Lồng ghép từ khóa chính này vào ít nhất một tiêu đề <h2> chính và trong 100 từ đầu tiên).
Chuyên mục: "{category_name or 'Kỷ Lục & Khám Phá Thế Giới'}"

BỘ QUY TẮC BẮT BUỘC (ANTI-BOILERPLATE, ANTI-AI CLICHE):
1. CẤM TUYỆT ĐỐI các cụm từ khuôn mẫu giả tạo ("Chuẩn xác thực Guinness", "Vị trí Quán Quân / Á Quân" lắp ghép máy móc).
2. NỘI DUNG CHUYÊN SÂU (> 1,600 từ):
   - Giải thích rõ thông số đo đạc thực tế (kích thước, độ cao/sâu, niên đại, tọa độ địa lý, đơn vị nghiên cứu công bố).
   - Danh sách phân tích chi tiết từng kỷ lục/hạng mục kèm bối cảnh khoa học, lịch sử hình thành và điểm độc đáo.
   - Bảng đối chiếu thông số kỹ thuật/địa lý trực quan bằng thẻ <table>.
   - FAQ giải đáp 3-4 câu hỏi khoa học thú vị liên quan.
3. ĐỊNH DẠNG: Dùng HTML semantic <h2>, <h3>, <p>, <ul>, <li>, <table>; có [ez-toc] sau mở bài.

Đầu ra trả về trực tiếp mã HTML cho bài viết (không bao bọc trong ```html ... ```).
"""
        elif is_troubleshooting_or_howto:
            prompt = f"""Bạn là Chuyên gia Kỹ thuật Phần mềm & Thủ thuật Số Cao Cấp (Senior IT Specialist & Practical Tech Advisor).
Hãy viết một bài viết cẩm nang hướng dẫn thực hành và khắc phục sự cố cực kỳ chi tiết, dễ hiểu, thực tế và chuẩn xác 100% bằng tiếng Việt về chủ đề:
"{topic}"
Từ khóa chính: "{focus_keyword}" (BẮT BUỘC: Lồng ghép từ khóa chính này vào ít nhất một tiêu đề <h2> chính và trong 100 từ đầu tiên).
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
Từ khóa chính: "{focus_keyword}" (BẮT BUỘC: Lồng ghép từ khóa chính này vào ít nhất một tiêu đề <h2> chính và trong 100 từ đầu tiên).
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
        models_to_try = [
            "gemini-flash-lite-latest",
            "gemini-3.1-flash-lite",
            "gemini-flash-latest",
            "gemini-3.1-flash-lite-preview"
        ]
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

        # Generate authentic content with Gemini
        print(f"  [*] Generating authentic content via Gemini for: {topic}...")
        try:
            raw_body = self.generate_ai_content(topic, p_kw, category_name=cat_name)
        except Exception as e:
            print(f"  [-] Gemini generation failed: {e}. Raising error to prevent garbage boilerplate.")
            raise

        content = raw_body

        # Extract authentic meta description from the first substantive paragraph
        first_p_matches = re.findall(r"<p[^>]*>(.*?)</p>", content, flags=re.I | re.S)
        meta_desc = ""
        for p_html in first_p_matches:
            p_text = re.sub(r"<[^>]+>", " ", p_html)
            p_text = re.sub(r"\[/?ez-toc\]", "", p_text, flags=re.I)
            p_text = re.sub(r"\s+", " ", p_text).strip()
            if len(p_text) >= 60:
                meta_desc = p_text
                break
        if not meta_desc:
            meta_desc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|\[/?ez-toc\]", " ", content)).strip()
        if len(meta_desc) > 158:
            cut = meta_desc[:155].rsplit(" ", 1)[0]
            meta_desc = (cut if len(cut) >= 80 else meta_desc[:155]) + "..."

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
