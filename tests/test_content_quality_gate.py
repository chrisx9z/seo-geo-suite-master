# -*- coding: utf-8 -*-
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.content_quality_gate import (  # noqa: E402
    JunkContentError, check_post, enforce_publish_payload, normalize_slug,
)


def _body(keyword: str, n_par: int = 40, extra: str = "") -> str:
    parts = [f"<h2>{keyword.title()} là gì</h2>"]
    for i in range(n_par):
        parts.append(f"<p>Đoạn {i} phân tích {keyword} với dữ liệu số {i * 7} và ví dụ thực tế "
                     f"riêng biệt số {i}, giúp người đọc hiểu rõ chủ đề hơn ở khía cạnh {i}.</p>")
    parts.append(extra)
    return "\n".join(parts)


def test_madlibs_guinness_template_blocked():
    content = _body("bão mới nhất việt nam", extra="<p>Đạt chuẩn xác thực Guinness 2026. Vị trí Quán Quân.</p>")
    res = check_post("Bão mới nhất việt nam", content, keyword="bão mới nhất việt nam")
    assert not res.passed and any("boilerplate" in i for i in res.issues)


def test_off_topic_body_blocked():
    content = _body("du lịch đà lạt")
    res = check_post("Chạy mô hình Qwen 2.5 trên GPU 16GB", content, keyword="chạy qwen gpu 16gb")
    assert not res.passed and any("off_topic" in i for i in res.issues)


def test_top_list_without_list_blocked():
    content = _body("hãng sơn tốt nhất việt nam")
    res = check_post("Top 20 hãng sơn tốt nhất việt nam", content, keyword="hãng sơn tốt nhất việt nam")
    assert any("top_list_unfulfilled" in i for i in res.issues)


def test_political_blocked_but_city_allowed():
    ok = check_post("Du lịch thành phố hồ chí minh", _body("du lịch thành phố hồ chí minh"),
                    keyword="du lịch thành phố hồ chí minh")
    assert "political_content" not in ok.issues
    bad = check_post("Đất nước hạnh phúc", _body("đất nước hạnh phúc", extra="<img src='x.jpg' alt='Bác Hồ'>"),
                     keyword="đất nước hạnh phúc")
    assert "political_content" in bad.issues
    repaired = check_post("Tỉnh rộng nhất", _body("tỉnh rộng nhất", extra="<p>Quê hương của Chủ tịch Hồ Chí Minh.</p>"),
                          keyword="tỉnh rộng nhất")
    assert "political_content" not in repaired.issues and "chủ tịch" not in repaired.content.lower()
    city = check_post("Người giàu nhất", _body("người giàu nhất", extra="<p>Bangkok và Hồ Chí Minh, đường Hồ Chí Minh.</p>"),
                      keyword="người giàu nhất")
    assert "political_content" not in city.issues and "Hồ Chí Minh" in city.content


def test_geo_hallucination_stripped_for_non_karst_destination():
    extra = "<p>Nằm cách trung tâm thủ đô không quá xa, vùng đất này có núi đá vôi.</p>"
    res = check_post("Kinh nghiệm du lịch Phú Quốc", _body("du lịch phú quốc", extra=extra),
                     keyword="du lịch phú quốc", destination="Phú Quốc")
    assert "thủ đô không quá xa" not in res.content
    assert res.passed, res.issues


def test_geo_phrase_kept_for_matching_destination():
    extra = "<p>Những dãy núi đá vôi triệu năm tuổi bao quanh.</p>"
    res = check_post("Du lịch Tràng An Ninh Bình", _body("du lịch tràng an", extra=extra),
                     keyword="du lịch tràng an", destination="Ninh Bình")
    assert "triệu năm tuổi" in res.content


def test_thin_content_blocked():
    res = check_post("Du lịch Huế", "<h2>Du lịch Huế</h2><p>Ngắn.</p>", keyword="du lịch huế")
    assert any("thin_content" in i for i in res.issues)


@pytest.mark.parametrize("slug,kw,expected", [
    ("openai-cong-bo-sieu-mo-hinh-o3-038-he-thong-tac-tu-tu-tri-operator-2026", "",
     None),
    ("top-10-luong-cau-thu-cao-nhat-the", "", "luong-cau-thu-cao-nhat-the-gioi"),
    ("bao", "bão mới nhất việt nam", "bao-moi-nhat-viet-nam"),
    ("kinh-nghiem-du-lich-dao-cat-ba-tu-tuc-2026", "", "kinh-nghiem-du-lich-dao-cat-ba"),
    ("du-lich-hue", "", "du-lich-hue"),
])
def test_normalize_slug(slug, kw, expected):
    out = normalize_slug(slug, kw)
    assert len(out.split("-")) <= 7
    assert "038" not in out and "2026" not in out
    if expected is not None:
        assert out == expected


def test_enforce_raises_and_repairs():
    payload = {"title": "Bão mới nhất", "content": "<p>Vị trí Quán Quân</p>", "slug": "bao"}
    with pytest.raises(JunkContentError):
        enforce_publish_payload(payload, keyword="bão mới nhất", log=lambda *_: None)

    good = {"title": "Du lịch Phú Quốc", "content": _body("du lịch phú quốc"),
            "slug": "kinh-nghiem-du-lich-phu-quoc-tu-tuc-2026"}
    enforce_publish_payload(good, keyword="du lịch phú quốc", log=lambda *_: None)
    assert good["slug"] == "kinh-nghiem-du-lich-phu-quoc"


def test_bold_paragraph_pseudo_headings_count_as_headings():
    kw = "cách nấu phở bò"
    body = _body(kw).replace(f"<h2>{kw.title()} là gì</h2>", f"<p><strong>{kw.title()} như thế nào?</strong></p>")
    res = check_post("Cách nấu phở bò", body, keyword=kw)
    assert "no_headings" not in res.issues
    assert not any("keyword_absent_from_headings" in i for i in res.issues)
    mixed = _body(kw).replace(f"<h2>{kw.title()} là gì</h2>",
                              "<p><strong>a</strong> nấu phở bò <strong>b</strong></p>")
    assert "no_headings" in check_post("Cách nấu phở bò", mixed, keyword=kw).issues
