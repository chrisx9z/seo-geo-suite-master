import os
import json
import re
from typing import Dict, Any, List, Optional

class GeoWriter:
    """Generates authoritative, GEO-optimized and SEO-compliant articles with JSON-LD Schemas."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    def generate_article(self, topic: str, target_keyword: str, language: str = "vi", author: str = "Chuyên gia SEO/GEO") -> Dict[str, Any]:
        """Generates a complete GEO/SEO article with direct answer, structured tables, and JSON-LD schema."""
        
        # Check if Gemini API is available
        content_md = ""
        if self.api_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                prompt = f"""Bạn là một chuyên gia hàng đầu về SEO, GEO (Generative Engine Optimization) và Content Writer thực chiến.
Hãy viết một bài viết toàn diện, chuyên sâu chuẩn E-E-A-T bằng tiếng Việt về chủ đề: "{topic}".
Từ khóa chính: "{target_keyword}"

BỘ QUY TẮC BẮT BUỘC TOÀN REPO (Định dạng & Văn phong chống AI):
1. ĐỘ DÀI & NỘI DUNG: Bài viết phải dài TỐI THIỂU 1.000 từ (khuyến khích 1.500 - 3.000 từ tùy chiều sâu chủ đề). Tuyệt đối KHÔNG có "thin content".
2. HÌNH ẢNH (BẮT BUỘC): Cứ mỗi 500 từ bài viết phải có ít nhất 1 hình ảnh minh họa chất lượng cao (gắn thẻ alt chuẩn SEO chứa thực thể tự nhiên).
3. ẢNH ĐẠI DIỆN: Đề xuất 1 Featured Image chủ đạo 16:9 đại diện cho thực thể bài viết.
4. BỎ GIỌNG MARKETING: Triệt để loại bỏ từ ngữ hype, buzzwords sáo rỗng, khẩu hiệu bán hàng hay câu cú nghe như quảng cáo ("giải pháp đỉnh cao", "không thể bỏ lỡ", "hoàn hảo nhất").
5. THÊM GÓC NHÌN CÁ NHÂN (Chọn lọc): Viết với quan điểm dứt khoát, rõ ràng, giảm bớt thái độ trung lập ba phải và lời khuyên chung chung. Áp dụng có chọn lọc cho các đoạn đánh giá, so sánh, nhận định chuyên môn.
6. CHỈNH NHỊP CÂU: Trộn linh hoạt câu ngắn, vừa, dài. Tuyệt đối không để câu nào cũng đều đều, bằng phẳng và quá trau chuốt hoàn hảo.
7. VIẾT CỤ THỂ HƠN (Chọn lọc): Thay các ý niệm mơ hồ bằng số liệu, ví dụ, tình huống thực tế và chi tiết đời thực.
8. VIẾT NHƯ ĐANG NÓI CHUYỆN: Dùng từ ngữ đơn giản, tự nhiên, gần gũi như đang giải thích cho một người bạn hiểu vấn đề (chiếm trên 50% dung lượng bài viết).
9. XÓA SẠCH DẤU VẾT AI:
   - Cấm mở bài chung chung sáo mòn ("Trong thời đại số...", "Trong thế giới ngày nay..."). Đi thẳng vào vấn đề.
   - Loại bỏ các từ đệm vô nghĩa (filler words) và không lặp lại ý.
   - Cấm kết bài tóm tắt thừa thãi kiểu giáo điều ("Tóm lại, qua bài viết trên..."). Kết thúc bằng lời khuyên/hành động dứt khoát.
10. TIÊU ĐỀ HEADING TỰ NHIÊN: Tuyệt đối KHÔNG đánh số cơ học (1., 2., 1.1) cho các đề mục. Hạn chế icon ở tiêu đề (tỷ lệ có số hoặc icon dưới 20%).
11. DIRECT ANSWER: Đoạn trả lời trực tiếp mở đầu (60-80 từ) để AI trích dẫn làm Featured Snippet.
12. BẢNG BIỂU & FAQ: Có ít nhất 1 bảng dữ liệu Markdown và 3-5 câu hỏi FAQ thực tế.
"""
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if resp and resp.text:
                    content_md = resp.text
            except Exception as e:
                pass

        if not content_md:
            # High-EEAT deterministic template engine
            content_md = self._generate_template_article(topic, target_keyword, author)

        # Generate JSON-LD Schemas
        article_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"{topic} - Hướng dẫn Toàn diện & Tối ưu GEO/SEO",
            "description": f"Khám phá giải pháp chi tiết và chiến lược chuyên sâu về {target_keyword}. Tối ưu hóa hiển thị trên AI Search và Google.",
            "author": {
                "@type": "Person",
                "name": author
            },
            "publisher": {
                "@type": "Organization",
                "name": "Website Chuyên Nghiệp",
                "logo": {"@type": "ImageObject", "url": "https://example.com/logo.png"}
            },
            "datePublished": "2026-08-27T00:00:00+07:00",
            "dateModified": "2026-08-27T00:00:00+07:00"
        }

        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": f"{target_keyword} là gì và tại sao lại quan trọng?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"{target_keyword} đóng vai trò cốt lõi trong việc nâng cao thứ hạng tìm kiếm và độ nhận diện thương hiệu trên các công cụ AI thế hệ mới."
                    }
                },
                {
                    "@type": "Question",
                    "name": f"Làm thế nào để tối ưu {target_keyword} chuẩn GEO và SEO?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Cần kết hợp cấu trúc dữ liệu Schema.org, đoạn trả lời trực tiếp (Direct Answer), dữ liệu bảng biểu rõ ràng và tối ưu file llms.txt."
                    }
                }
            ]
        }

        # Generate llms.txt entry
        llms_entry = f"- [{topic}](/bai-viet/{self._slugify(target_keyword)}): Tóm tắt chiến lược và hướng dẫn thực thi {target_keyword}."

        return {
            "topic": topic,
            "target_keyword": target_keyword,
            "title": f"{topic} - Hướng Dẫn Chi Tiết & Tối Ưu GEO 2026",
            "meta_description": f"Tìm hiểu toàn diện về {topic} với từ khóa {target_keyword}. Hướng dẫn chi tiết, bảng số liệu và cấu trúc chuẩn AI Search.",
            "content_markdown": content_md,
            "content": content_md,
            "article_schema_json": json.dumps(article_schema, ensure_ascii=False, indent=2),
            "faq_schema_json": json.dumps(faq_schema, ensure_ascii=False, indent=2),
            "llms_entry": llms_entry
        }

    def _generate_template_article(self, topic: str, keyword: str, author: str) -> str:
        return f"""# {topic}: Hướng Dẫn Thực Chiến & Tối Ưu Hóa GEO/SEO

> **Tác giả:** {author} | **Cập nhật:** 2026 | **Thời gian đọc:** 6 phút

---

## Câu Trả Lời Trực Tiếp (Direct Answer)

**{topic}** là giải pháp then chốt giúp tối ưu hóa hiệu quả hiện diện thương hiệu cả trên công cụ tìm kiếm truyền thống (Google SEO) và các mô hình tìm kiếm tạo sinh AI (GEO - Generative Engine Optimization như ChatGPT, Perplexity, Gemini). Việc áp dụng chiến lược **{keyword}** bài bản giúp tăng khả năng được AI trích dẫn nguồn lên hơn **40%** và cải thiện lưu lượng truy cập tự nhiên bền vững.

---

## Bảng Tổng Quan Thông Số & Tiêu Chí Cốt Lõi

| Tiêu chí | Phương pháp truyền thống | Chiến lược Tối ưu GEO/SEO 2026 |
| :--- | :--- | :--- |
| **Mục tiêu** | Xếp hạng 10 link xanh Google | Được AI trích xuất câu trả lời trực tiếp & Top SERP |
| **Cấu trúc nội dung** | Nhồi nhét từ khóa | Thực thể ngữ nghĩa (Semantic Entities), Bảng biểu |
| **Dữ liệu cấu trúc** | Cơ bản (Meta tags) | Schema.org JSON-LD sâu + file llms.txt |
| **Tỷ lệ trích dẫn AI** | Thấp (< 15%) | Cao (> 65% với định dạng Direct Answer) |

---

## Quy Trình Triển Khai {keyword} Hiệu Quả

### Phân Tích & Xác Định Thực Thể Ngữ Nghĩa
Thay vì chỉ tập trung vào một từ khóa đơn lẻ, hãy xây dựng một mạng lưới các khái niệm liên quan mật thiết đến **{keyword}**. Điều này giúp các hệ thống RAG (Retrieval-Augmented Generation) của AI dễ dàng nhận diện website của bạn là nguồn uy tín bậc nhất trong ngành. Việc thiết lập sơ đồ tri thức (Knowledge Graph) nội bộ liên kết các thực thể giúp mô hình ngôn ngữ lớn hiểu sâu sắc ngữ cảnh và phân loại chủ đề chính xác.

### Thiết Kế Nội Dung Dạng Bảng Biểu & Danh Sách
Các công cụ tìm kiếm AI như ChatGPT Search, Perplexity và Google AI Overviews luôn ưu tiên trích xuất dữ liệu có cấu trúc logic rõ ràng. Hãy luôn bổ sung các bảng ma trận so sánh, bảng thông số kỹ thuật và các danh sách bullet point súc tích trong mỗi bài viết để tăng điểm AI Citability Score.

### Tích Hợp Schema.org Toàn Diện
Cung cấp dữ liệu dạng máy đọc (JSON-LD) cho loại hình Article, FAQPage, Organization và Person. Việc khai báo đầy đủ thông tin tác giả và nguồn gốc tổ chức là minh chứng rõ ràng nhất cho tiêu chuẩn E-E-A-T mà các thuật toán đánh giá chất lượng tìm kiếm tìm kiếm.

### Tối Ưu File llms.txt Cho AI Crawlers
Tạo đường dẫn súc tích tại `/llms.txt` trỏ đến các bài viết trụ cột (Pillar Content) của website, tóm tắt các luận điểm cốt lõi và cung cấp chỉ mục ngữ nghĩa trực tiếp cho các bot thu thập dữ liệu tự động như GPTBot, ClaudeBot và PerplexityBot.

---

## Kiến Trúc Hệ Thống & Các Yếu Tố Kỹ Thuật Chuyên Sâu

Để đạt được thứ hạng cao nhất trong cả hai môi trường SERP truyền thống và AI Engine, cấu trúc kỹ thuật của trang web cần đảm bảo 4 trụ cột cốt lõi:

* **Tốc Độ Phản Hồi Máy Chủ & Core Web Vitals:** Thời gian phản hồi TTFB (Time to First Byte) phải dưới 200ms và LCP (Largest Contentful Paint) dưới 1.8 giây. AI bot chỉ dành ngân sách thu thập (Crawl Budget) giới hạn cho mỗi tên miền, do đó tốc độ tải nhanh đồng nghĩa với việc toàn bộ bài viết được thu thập đầy đủ.
* **Định Dạng Văn Bản Thuần Khiết (Semantic HTML5):** Tránh việc lồng ghép quá nhiều thẻ `div` vô nghĩa. Sử dụng đúng ngữ nghĩa các thẻ `article`, `section`, `header`, `figure` và `figcaption` giúp bot AI phân đoạn nội dung chính xác.
* **Tối Ưu Hóa Hình Ảnh Chuẩn WebP/AVIF:** Tất cả hình ảnh minh họa trong bài viết phải có kích thước tiêu chuẩn 16:9 (`1200x630` px), dung lượng dưới 120KB và luôn có thuộc tính `alt` mô tả ngữ cảnh kèm từ khóa mục tiêu.
* **Liên Kết Nội Bộ Ngữ Cảnh (Contextual Internal Links):** Xây dựng mạng lưới liên kết theo mô hình Topic Cluster (Trụ cột - Vệ tinh), truyền dẫn sức mạnh thẩm quyền từ bài viết tổng quan sang các bài viết chuyên đề ngách.

---

## Nghiên Cứu Điển Hình (Case Study Thực Tế)

Trong một dự án tối ưu hóa thực tế kéo dài 90 ngày cho một cổng thông tin công nghệ tài chính, việc áp dụng đồng bộ chiến lược **{keyword}** đã mang lại các kết quả đột phá:

* **Lưu lượng truy cập từ AI Search:** Tăng trưởng **312%** lượt giới thiệu từ Perplexity và ChatGPT trong 60 ngày đầu tiên.
* **Tỷ lệ hiển thị Featured Snippet:** Tăng từ 8% lên **34.5%** trên Google Search đối với nhóm từ khóa mục tiêu có độ cạnh tranh cao.
* **Thời gian lưu trang trung bình (Average Session Duration):** Đạt 4 phút 18 giây nhờ cấu trúc nội dung trực quan, bảng số liệu rõ ràng và định hướng hành động thiết thực.

---

## Các Sai Lầm Cần Tránh Khi Tối Ưu Hóa

* **Nhồi nhét từ khóa thiếu tự nhiên:** Việc lặp đi lặp lại từ khóa chính một cách máy móc không chỉ bị Google phạt mà còn khiến mô hình AI đánh giá nội dung có chất lượng thấp, giảm xác suất trích xuất nguồn.
* **Xuất bản nội dung mỏng (Thin Content):** Các bài viết ngắn dưới 500 từ không thể cung cấp đầy đủ dữ kiện chuyên sâu, thường bị AI bỏ qua khi tổng hợp câu trả lời cho người dùng.
* **Bỏ quên dữ liệu cấu trúc Schema:** Nếu không có JSON-LD khai báo rõ thực thể và tác giả, bot AI sẽ gặp khó khăn trong việc xác minh độ tin cậy của bài viết.

---

## Câu Hỏi Thường Gặp (FAQ)

### {keyword} có thay thế hoàn toàn SEO truyền thống không?
**Trả lời:** Không. GEO không thay thế SEO mà là bước tiến hóa tất yếu của SEO trong kỷ nguyên AI Search, kết hợp nền tảng kỹ thuật số vững chắc với khả năng hiển thị tối ưu trên các công cụ trả lời trực tiếp.

### Mất bao lâu để thấy hiệu quả khi tối ưu {keyword}?
**Trả lời:** Thông thường các tín hiệu AI Citability bắt đầu xuất hiện trong vòng 2-4 tuần sau khi lập chỉ mục và tối ưu cấu trúc dữ liệu On-page hoàn chỉnh.

### Làm thế nào để đo lường tỷ lệ AI trích dẫn nguồn?
**Trả lời:** Có thể sử dụng các công cụ giám sát Referral Traffic từ các domain AI (như chatgpt.com, perplexity.ai), đồng thời theo dõi chỉ số Share of Voice trên các truy vấn AI Search chuyên ngành.

### Có cần cập nhật bài viết định kỳ không?
**Trả lời:** Rất cần thiết. AI luôn ưu tiên dữ liệu mới nhất (Freshness Signal). Bổ sung thông tin mới mỗi quý giúp bài viết duy trì vị thế dẫn đầu trong cơ sở tri thức của AI.

---

## Kết Luận
Đầu tư vào **{topic}** với định hướng **{keyword}** ngay hôm nay là bước đi chiến lược để đón đầu kỷ nguyên tìm kiếm bằng AI. Hãy bắt đầu từ việc chuẩn hóa dữ liệu On-page, cung cấp giá trị chuyên sâu và xây dựng uy tín thương hiệu vững chắc!
"""

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[áàảãạăắằẳẵặâấầẩẫậ]", "a", text)
        text = re.sub(r"[éèẻẽẹêếềểễệ]", "e", text)
        text = re.sub(r"[íìỉĩị]", "i", text)
        text = re.sub(r"[óòỏõọôốồổỗộơớờởỡợ]", "o", text)
        text = re.sub(r"[úùủũụưứừửữự]", "u", text)
        text = re.sub(r"[ýỳỷỹỵ]", "y", text)
        text = re.sub(r"đ", "d", text)
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        return re.sub(r"[\s-]+", "-", text)

