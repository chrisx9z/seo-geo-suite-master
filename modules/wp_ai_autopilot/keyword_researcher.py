"""
Keyword Researcher & SEO Onpage Outline Engine
Analyzes search intent, extracts LSI keywords and builds an Anti-AI structured outline.
"""

import re
from typing import Dict, List, Any

class KeywordResearcher:
    def __init__(self):
        pass

    def analyze_topic(self, topic: str) -> Dict[str, Any]:
        """
        Extracts primary keyword, secondary keywords, search intent,
        and constructs an Onpage SEO outline.
        """
        cleaned = re.sub(r"[\(\)\[\]\{\}\:\?\!\|\,\.]", " ", topic)
        words = [w.strip() for w in cleaned.split() if len(w.strip()) > 2]
        
        primary_kw = " ".join(words[:4]) if len(words) >= 4 else topic
        
        # Build secondary / LSI keyword pool
        lsi_keywords = [
            f"{primary_kw} xu hướng",
            f"{primary_kw} chi tiết",
            f"cách tối ưu {primary_kw}",
            f"hướng dẫn {primary_kw} thực chiến",
            f"đánh giá {primary_kw} chuyên sâu"
        ]
        
        # Construct structured outline with Anti-AI rules (headings < 20% numbered)
        outline = [
            {
                "heading": f"Bản Chất & Xu Hướng Phát Triển Của {topic}",
                "level": "h2",
                "intent": "Định nghĩa thực thể, khái quát bối cảnh công nghệ và tầm quan trọng"
            },
            {
                "heading": f"Kiến Trúc Kỹ Thuật & Cơ Chế Hoạt Động Cốt Lõi",
                "level": "h2",
                "intent": "Phân tích sâu giải thuật, luồng dữ liệu và các thành phần kỹ thuật"
            },
            {
                "heading": f"So Sánh Đột Phá & Ưu Nhược Điểm Thực Chiến",
                "level": "h2",
                "intent": "Bảng đối soát benchmark, thông số hiệu năng và so sánh với giải pháp khác"
            },
            {
                "heading": f"Quy Trình Triển Khai Thực Tế Từng Bước",
                "level": "h2",
                "intent": "Hướng dẫn thực thi chi tiết kèm code mẫu, cấu hình và lệnh terminal"
            },
            {
                "heading": f"Chiến Lược Khai Thác MMO, Tối Ưu Chi Phí & Doanh Thu 2026",
                "level": "h2",
                "intent": "Ứng dụng kiếm tiền online, xây dựng SaaS hoặc tự động hóa dịch vụ"
            },
            {
                "heading": f"Những Câu Hỏi Thường Gặp (FAQ) Về {topic}",
                "level": "h2",
                "intent": "Khung hỏi đáp chuẩn FAQ Schema giải đáp các thắc mắc phổ biến nhất"
            }
        ]
        
        return {
            "topic": topic,
            "primary_keyword": primary_kw,
            "lsi_keywords": lsi_keywords,
            "outline": outline,
            "search_intent": "Informational & Commercial Investigation"
        }
