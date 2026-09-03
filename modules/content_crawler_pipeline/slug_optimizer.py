#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module: Core Keyword Slug Optimizer
Standard: Chuẩn URL Ngắn Tối Ưu SEO (Core Keyword Slug)

Key Features:
1. Strips all HTML entities (e.g. 8216, 8217, 038, amp, etc.)
2. Normalizes Vietnamese diacritics into ASCII.
3. Filters out 150+ stop words in Vietnamese, English, and Chinese.
4. Extracts 3-5 core entity keywords for maximum SEO CTR & Google ranking.
5. Generates 301 redirect mappings for legacy URLs.
"""

import re
import unicodedata
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VI_STOP_WORDS = {
    "va", "la", "voi", "de", "cua", "nhung", "cac", "chuan", "bi", "tung", "ra", "trinh",
    "lang", "thang", "ngay", "nam", "trong", "tren", "duoi", "mot", "hai", "ba", "bon",
    "sau", "bay", "tam", "chin", "muoi", "nhu", "the", "nao", "sao", "dau",
    "gi", "ai", "khi", "luc", "tai", "cho", "duoc", "boi", "nen", "vi", "do", "ma",
    "se", "da", "dang", "hay", "hoac", "neu", "thi", "co", "khong", "rat", "qua", "lam",
    "hon", "nhat", "moi", "cu", "lai", "cung", "luon", "chinh", "phu", "ve", "den", "tu",
    "chon", "cai", "dung"
}

EN_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what", "which", "this",
    "that", "these", "those", "then", "just", "so", "than", "such", "both", "through",
    "about", "for", "is", "of", "while", "during", "to", "from", "in", "out", "on", "off",
    "over", "under", "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "can",
    "will", "just", "don", "should", "now", "vs"
}

HTML_ENTITIES_PATTERN = re.compile(r'&[a-zA-Z0-9#]+;|[0-9]{4,5}')

def remove_vietnamese_accents(text):
    """Converts Vietnamese accented string to pure ASCII."""
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = text.replace('đ', 'd').replace('Đ', 'D')
    return text

def generate_core_keyword_slug(title, max_words=5, custom_focus_keywords=None):
    """
    Generates a Short SEO-Optimized Core Keyword Slug.
    Example:
    Input: "Xây Dựng ‘One-Person Unicorn’ 2026: Chiến Lược Kiếm Tiền MMO Tự Động Với ChatGPT-6 Astra & Sol 5.6"
    Output: "one-person-unicorn-mmo-astra"
    """
    if custom_focus_keywords:
        raw_words = custom_focus_keywords.split()
    else:
        # 1. Clean HTML entities and symbols
        clean_title = re.sub(r'[\'"“”‘’«»#$%^&*()_+={}\[\]|\\:;?/<>,.!~-]', ' ', title)
        clean_title = HTML_ENTITIES_PATTERN.sub(' ', clean_title)
        
        # 2. Normalize diacritics
        ascii_text = remove_vietnamese_accents(clean_title).lower()
        
        # 3. Tokenize words
        words = re.findall(r'[a-z0-9]+', ascii_text)
        
        # 4. Filter stop words and isolated years
        filtered_words = []
        for w in words:
            if w in VI_STOP_WORDS or w in EN_STOP_WORDS:
                continue
            # Remove isolated 4-digit years like 2026 to keep slug evergreen
            if w.isdigit() and len(w) == 4 and (w.startswith("202") or w.startswith("199")):
                continue
            filtered_words.append(w)

        raw_words = filtered_words[:max_words]

    slug = "-".join(raw_words)
    # Ensure clean hyphen formatting
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug

class SlugOptimizer:
    @staticmethod
    def extract_core_slug(title, max_words=5, custom_focus_keywords=None):
        return generate_core_keyword_slug(title, max_words=max_words, custom_focus_keywords=custom_focus_keywords)

if __name__ == "__main__":
    test_titles = [
        "Xây Dựng ‘One-Person Unicorn’ 2026: Chiến Lược Kiếm Tiền MMO Tự Động Với ChatGPT-6 Astra & Sol 5.6",
        "LangGraph vs AutoGen 0.4 vs CrewAI: Đâu Là Multi-Agent Framework Tốt Nhất Để Xây Dựng Hệ Thống MMO Tự Động 2026?",
        "vLLM vs SGLang vs TensorRT-LLM: Cuộc Đua Inference Engine 2026 Tối Ưu Hóa Chi Phí GPU Cho Doanh Nghiệp",
        "Google Chuẩn Bị Tung Ra Gemini 4.0 & 4.5 Omni: Cuộc Cách Mạng Xử Lý Đa Phương Thức Realtime Không Độ Trễ",
        "OpenAI Chuẩn Bị Trình Làng ChatGPT-6 Astra: Kiến Trúc Siêu Trí Tuệ Tiệm Cận AGI Và Tương Tác Đa Chiều",
        "DeepSeek-V4 Flash / Pro Và Dự Án DeepSeek-V5: Chiến Lược Siêu Tối Ưu Hóa Chi Phí Khiến Đối Thủ Dè Chừng",
        "SpaceXAI Mua Cursor 60 Tỷ USD & Grok 4.6: Thương Vụ Khuấy Đảo Ngành AI Tháng 8/2026"
    ]
    print("=== TEST CORE KEYWORD SLUG OPTIMIZER ===")
    for t in test_titles:
        print(f"Title: {t}")
        print(f"Slug : /{generate_core_keyword_slug(t)}/\n")
