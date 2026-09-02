import re
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class OnpageChecker:
    """Checks on-page SEO & GEO health for any URL or raw HTML."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

    def analyze_url(self, url: str) -> Dict[str, Any]:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            html = resp.text
            status_code = resp.status_code
            response_time_ms = int(resp.elapsed.total_seconds() * 1000)
        except Exception as e:
            return {
                "url": url,
                "status": "error",
                "error": str(e),
                "score": 0
            }
        
        return self.analyze_html(html, url=url, status_code=status_code, response_time_ms=response_time_ms)

    def analyze_html(self, html: str, url: str = "", status_code: int = 200, response_time_ms: int = 0) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Title
        title_tag = soup.find("title")
        title_text = title_tag.get_text().strip() if title_tag else ""
        title_len = len(title_text)
        title_status = "pass" if 30 <= title_len <= 65 else ("warning" if title_len > 0 else "error")

        # 2. Meta Description
        meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        desc_text = meta_desc.get("content", "").strip() if meta_desc else ""
        desc_len = len(desc_text)
        desc_status = "pass" if 120 <= desc_len <= 160 else ("warning" if desc_len > 0 else "error")

        # 3. Headings H1 - H6
        headings = {}
        for h in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            tags = soup.find_all(h)
            headings[h] = [t.get_text().strip() for t in tags if t.get_text().strip()]
        
        h1_count = len(headings.get("h1", []))
        h1_status = "pass" if h1_count == 1 else ("error" if h1_count == 0 else "warning")

        # 4. Canonical & Robots
        canonical_tag = soup.find("link", attrs={"rel": "canonical"})
        canonical_url = canonical_tag.get("href", "") if canonical_tag else ""
        
        robots_meta = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
        robots_content = robots_meta.get("content", "") if robots_meta else ""

        # 5. OpenGraph & Twitter
        og_tags = {}
        for prop in ["og:title", "og:description", "og:image", "og:url", "og:type", "og:site_name"]:
            tag = soup.find("meta", property=prop)
            if tag and tag.get("content"):
                og_tags[prop] = tag.get("content")

        twitter_tags = {}
        for name in ["twitter:card", "twitter:title", "twitter:description", "twitter:image"]:
            tag = soup.find("meta", attrs={"name": name})
            if tag and tag.get("content"):
                twitter_tags[name] = tag.get("content")

        # 6. JSON-LD Schemas
        json_ld_schemas = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
                json_ld_schemas.append(data)
            except Exception:
                pass

        schema_types = []
        for s in json_ld_schemas:
            if isinstance(s, dict):
                st = s.get("@type")
                if st:
                    schema_types.append(st if isinstance(st, str) else str(st))
            elif isinstance(s, list):
                for item in s:
                    if isinstance(item, dict) and item.get("@type"):
                        schema_types.append(item.get("@type"))

        # 7. Images & Alt tags
        images = soup.find_all("img")
        total_images = len(images)
        missing_alt = []
        for img in images:
            src = img.get("src", "") or img.get("data-src", "")
            alt = img.get("alt", None)
            if alt is None or alt.strip() == "":
                missing_alt.append(src)

        # 8. Links
        links = soup.find_all("a", href=True)
        total_links = len(links)
        internal_links = 0
        external_links = 0
        for a in links:
            href = a.get("href", "")
            if href.startswith(("http://", "https://")):
                if url and (url.split("//")[1].split("/")[0] in href):
                    internal_links += 1
                else:
                    external_links += 1
            elif href.startswith(("/", "#", "./", "../")):
                internal_links += 1

        # 9. GEO & Citability signals
        geo_signals = {
            "has_structured_data": len(json_ld_schemas) > 0,
            "has_direct_faq": bool(soup.find(attrs={"class": re.compile(r"faq", re.I)}) or "FAQPage" in str(schema_types)),
            "has_tables_or_lists": len(soup.find_all(["table", "ul", "ol"])) > 0,
            "has_author_or_entity": bool(soup.find(attrs={"class": re.compile(r"author|byline|profile", re.I)}) or "Person" in str(schema_types) or "Organization" in str(schema_types)),
            "content_word_count": len(re.findall(r"\\w+", soup.get_text())),
            "schema_types_found": schema_types
        }

        # Calculate Overall SEO Score (0-100)
        score = 100
        issues = []
        recommendations = []

        # Check Thin Content (< 1000 words)
        word_count = geo_signals["content_word_count"]
        if word_count < 500:
            score -= 25
            issues.append(f"Cảnh báo Thin Content nghiêm trọng ({word_count} từ, yêu cầu tối thiểu 1.000 từ)")
            recommendations.append("Mở rộng nội dung bài viết chuyên sâu tối thiểu 1.000 từ để đảm bảo E-E-A-T và tránh bị phạt Thin Content.")
        elif word_count < 1000:
            score -= 10
            issues.append(f"Nội dung hơi ngắn ({word_count} từ, khuyến nghị tối thiểu 1.000 từ)")
            recommendations.append("Bổ sung thêm phân tích thực tế, case studies và câu hỏi thường gặp để đạt độ dài chuẩn trên 1.000 từ.")

        # Check Images Count (1 - 5 images)
        if total_images < 1:
            score -= 15
            issues.append("Bài viết chưa có hình ảnh minh họa nào (yêu cầu 1-5 hình ảnh chuyên nghiệp)")
            recommendations.append("Bổ sung ít nhất 1-5 hình ảnh hoặc infographic chuyên nghiệp (16:9) kèm thẻ alt chuẩn SEO.")
        elif total_images > 5:
            score -= 5
            issues.append(f"Có quá nhiều hình ảnh trong bài viết ({total_images} ảnh, khuyến nghị tối đa 5 ảnh để tối ưu tốc độ tải trang)")
            recommendations.append("Cân nhắc rút gọn hoặc tối ưu số lượng hình ảnh về mức 1-5 ảnh trọng tâm.")

        # Check Natural Heading Standards (RULES.md Section 5)
        all_subheadings = []
        for h_level in ["h2", "h3", "h4"]:
            all_subheadings.extend(headings.get(h_level, []))
        if all_subheadings:
            numbered_or_icon_count = 0
            for h_text in all_subheadings:
                if re.match(r"^(\d+[\.\)]|\d+\.\d+|[IVXLCDM]+[\.\)]|[A-Z][\.\)])\s+", h_text) or \
                   re.match(r"^[\U00010000-\U0010ffff\u2600-\u27bf\ufe0f\u200d\u2300-\u23ff\u2b50\u2b55]", h_text):
                    numbered_or_icon_count += 1
            heading_ratio = numbered_or_icon_count / len(all_subheadings)
            if len(all_subheadings) >= 3 and heading_ratio > 0.20:
                score -= 10
                issues.append(f"Tỷ lệ tiêu đề đánh số cơ học hoặc icon vượt quá mức cho phép ({int(heading_ratio * 100)}% > 20% theo RULES.md)")
                recommendations.append("Hạn chế đánh số 1., 2., 3. và lạm dụng icon ở thẻ H2, H3 để văn phong bài viết tự nhiên chuẩn báo chí.")

        if title_status == "error":
            score -= 20
            issues.append("Thiếu thẻ Title (<title>)")
            recommendations.append("Thêm thẻ Title dài 50-60 ký tự chứa từ khóa chính.")
        elif title_status == "warning":
            score -= 5
            issues.append(f"Độ dài Title chưa tối ưu ({title_len} ký tự, khuyến nghị 30-65 ký tự)")

        if desc_status == "error":
            score -= 15
            issues.append("Thiếu thẻ Meta Description")
            recommendations.append("Thêm thẻ Meta Description 120-160 ký tự tóm tắt nội dung hấp dẫn.")
        elif desc_status == "warning":
            score -= 5
            issues.append(f"Độ dài Meta Description ({desc_len} ký tự, khuyến nghị 120-160 ký tự)")

        if h1_status == "error":
            score -= 15
            issues.append("Trang không có thẻ H1 nào")
            recommendations.append("Bổ sung chính xác 1 thẻ H1 duy nhất đại diện cho tiêu đề chính.")
        elif h1_status == "warning":
            score -= 8
            issues.append(f"Có quá nhiều thẻ H1 ({h1_count} thẻ H1)")
            recommendations.append("Chỉ nên dùng duy nhất 1 thẻ H1, chuyển các tiêu đề khác thành H2, H3.")

        if not canonical_url:
            score -= 10
            issues.append("Thiếu thẻ rel='canonical'")
            recommendations.append("Khai báo thẻ canonical để tránh trùng lặp nội dung.")

        if missing_alt:
            score -= min(15, len(missing_alt) * 3)
            issues.append(f"Có {len(missing_alt)}/{total_images} hình ảnh thiếu thuộc tính alt")
            recommendations.append("Thêm thuộc tính alt mô tả nội dung cho tất cả hình ảnh.")

        if not json_ld_schemas:
            score -= 10
            issues.append("Chưa có Structured Data (JSON-LD Schema.org)")
            recommendations.append("Bổ sung Schema Article/Organization/FAQPage để hỗ trợ AI bot trích xuất.")

        if not og_tags.get("og:image"):
            score -= 10
            issues.append("Thiếu thẻ OpenGraph Image (og:image) / Ảnh đại diện (Featured Image)")
            recommendations.append("Bắt buộc phải có ảnh đại diện (Featured Image) và thẻ og:image để hiển thị thumbnail chuẩn trên mạng xã hội và SERP.")

        score = max(0, min(100, score))

        # Citability Rating for GEO
        geo_score = 0
        if geo_signals["has_structured_data"]: geo_score += 25
        if geo_signals["has_author_or_entity"]: geo_score += 25
        if geo_signals["has_direct_faq"]: geo_score += 20
        if geo_signals["has_tables_or_lists"]: geo_score += 15
        if geo_signals["content_word_count"] >= 1000: geo_score += 15
        elif geo_signals["content_word_count"] >= 500: geo_score += 8

        return {
            "url": url,
            "status": "success",
            "response_time_ms": response_time_ms,
            "seo_score": score,
            "score": score,
            "geo_citability_score": geo_score,
            "title": {"text": title_text, "length": title_len, "status": title_status},
            "meta_description": {"text": desc_text, "length": desc_len, "status": desc_status},
            "headings": headings,
            "h1_status": h1_status,
            "canonical": canonical_url,
            "robots": robots_content,
            "opengraph": og_tags,
            "twitter": twitter_tags,
            "schemas": json_ld_schemas,
            "images": {"total": total_images, "missing_alt_count": len(missing_alt), "missing_alt": missing_alt[:10]},
            "links": {"total": total_links, "internal": internal_links, "external": external_links},
            "geo_signals": geo_signals,
            "issues": issues,
            "recommendations": recommendations
        }
