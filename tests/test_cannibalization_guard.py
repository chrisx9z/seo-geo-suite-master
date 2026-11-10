# -*- coding: utf-8 -*-
"""Unit tests for same-site keyword cannibalization and cross-site keyword copying guard."""
import json
import os
import tempfile
from modules.content_quality_gate.cannibalization import (
    check_keyword_cannibalization,
    core_entity_key,
    normalize_keyword_key,
)


def test_normalize_keyword_key_strips_years_and_punctuation():
    assert normalize_keyword_key("Kinh nghiệm du lịch Đà Lạt 2026: A-Z!") == "kinh nghiệm du lịch đà lạt a z"


def test_core_entity_key_strips_travel_prefixes():
    assert core_entity_key("kinh nghiệm du lịch đền tanah lot", "kinh-nghiem-du-lich-den-tanah-lot") == "den-tanah-lot"
    assert core_entity_key("du lịch đền tanah lot tự túc", "du-lich-den-tanah-lot-tu-tuc") == "den-tanah-lot"


def test_same_site_and_cross_site_cannibalization_blocked():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = os.path.join(tmpdir, "cache")
        os.makedirs(cache_dir, exist_ok=True)

        # Seed site A (alpha_example_com)
        site_a_log = {
            "scheduled_posts": [
                {
                    "id": 101,
                    "title": "Đền Tanah Lot ngắm hoàng hôn Bali",
                    "keyword": "đền tanah lot ngắm hoàng hôn trên biển bali",
                    "slug": "den-tanah-lot-ngam-hoang-hon",
                }
            ]
        }
        with open(os.path.join(cache_dir, "scheduled_alpha_example_com.json"), "w", encoding="utf-8") as f:
            json.dump(site_a_log, f, ensure_ascii=False)

        # 1. Same-site duplicate keyword -> blocked
        ok1, issues1 = check_keyword_cannibalization(
            site_url="https://alpha.example.com",
            keyword="đền tanah lot ngắm hoàng hôn trên biển bali 2026",
            slug="den-tanah-lot-bali-moi",
            base_dir=tmpdir,
        )
        assert not ok1
        assert any("same_site_keyword_cannibalization" in x for x in issues1)

        # 2. Same-site duplicate slug (including -2 suffix attempt) -> blocked
        ok2, issues2 = check_keyword_cannibalization(
            site_url="https://alpha.example.com",
            keyword="khám phá tanah lot hoàng hôn",
            slug="den-tanah-lot-ngam-hoang-hon-2",
            base_dir=tmpdir,
        )
        assert not ok2
        assert any("same_site_slug_cannibalization" in x for x in issues2)

        # 3. Cross-site keyword copy on site B (beta.example.com) -> blocked
        ok3, issues3 = check_keyword_cannibalization(
            site_url="https://beta.example.com",
            keyword="đền tanah lot ngắm hoàng hôn trên biển bali",
            slug="du-lich-den-tanah-lot-ngam-hoang-hon",
            base_dir=tmpdir,
        )
        assert not ok3
        assert any("cross_site_" in x for x in issues3)

        # 4. Completely unique topic on site B (Japan) -> allowed
        ok4, issues4 = check_keyword_cannibalization(
            site_url="https://beta.example.com",
            keyword="núi phú sĩ nhật bản lịch trình ngắm hồ kawaguchiko",
            slug="nui-phu-si-nhat-ban",
            base_dir=tmpdir,
        )
        assert ok4
        assert issues4 == []
