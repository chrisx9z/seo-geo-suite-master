import re
import math
import json
import time
import os
import sys
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup

# Regex patterns for Heading numbering and icons/emojis
HEADING_NUMBER_REGEX = re.compile(
    r"^\s*(\d+(\.\d+)*[\.\-\:\)\s]|bước\s*\d+|phần\s*\d+|step\s*\d+|part\s*\d+|chapter\s*\d+|tiêu\s*mục\s*\d+)",
    re.IGNORECASE
)

# Common decorative icons/emojis found in robotic headings
EMOJI_REGEX = re.compile(
    r"^[\s\u2000-\u3300\U00010000-\U0010ffff]*[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF\U0001FA00-\U0001FAFF]"
)

# Rule 1: Marketing hype and buzzwords
MARKETING_BUZZWORDS_VI = [
    "giải pháp đỉnh cao", "hoàn hảo nhất", "tuyệt vời nhất", "không thể bỏ lỡ",
    "sự lựa chọn hoàn hảo", "bước ngoặt đột phá", "chuyên nghiệp hàng đầu",
    "vượt trội", "hàng đầu thế giới", "đẳng cấp quốc tế", "siêu phẩm",
    "bí quyết vàng", "thần thánh", "đỉnh nóc kịch trần", "sự lựa chọn số 1",
    "cực phẩm", "không đối thủ", "cam kết 100%", "hiệu quả vượt bậc",
    "bất khả chiến bại", "đẳng cấp 5 sao", "thiên đường hạ giới",
    "đẹp ngất ngây", "mê hoặc lòng người", "đỉnh cao công nghệ"
]

MARKETING_BUZZWORDS_EN = [
    "ultimate solution", "game-changer", "game changer", "unparalleled",
    "must-visit", "must visit", "hidden gem", "breathtaking paradise",
    "world-class", "revolutionary", "best-in-class", "state-of-the-art",
    "look no further", "second to none", "nestled in the heart of",
    "once-in-a-lifetime", "paradise on earth", "miracle cure",
    "groundbreaking", "unrivaled", "seamless experience"
]

# Rule 6: Anti-AI Fingerprints
# Generic AI Leads (Intro)
AI_LEAD_CLICHES_VI = [
    "trong kỷ nguyên số", "trong thời đại", "trong thế giới",
    "ngày nay, khi mà", "ngày nay, trong bối cảnh", "bạn có bao giờ tự hỏi",
    "khi nhắc đến", "chào mừng bạn đến với", "như chúng ta đã biết",
    "từ lâu nay", "trong xã hội hiện đại", "trong cuộc sống hiện đại"
]

AI_LEAD_CLICHES_EN = [
    "in today's fast-paced", "in today's world", "in today's digital age",
    "in the ever-evolving", "in recent years", "when it comes to",
    "welcome to the ultimate", "have you ever wondered", "in an era where",
    "it is no secret that", "nestled in the heart of", "in a world where"
]

# Filler transitional words
AI_TRANSITION_FILLERS_VI = [
    "hơn nữa,", "bên cạnh đó,", "đáng chú ý là,", "không chỉ vậy,",
    "chưa dừng lại ở đó,", "mặt khác,", "điều quan trọng cần lưu ý là,",
    "thêm vào đó,", "ngoài ra, cần phải nói rằng"
]

AI_TRANSITION_FILLERS_EN = [
    "furthermore,", "moreover,", "additionally,", "in addition,",
    "it is worth noting that,", "not only that, but", "delve into",
    "a testament to", "beacon of", "rich tapestry", "symphony of",
    "plethora of"
]

# Redundant AI Conclusions
AI_CONCLUSION_CLICHES_VI = [
    "tóm lại, qua bài viết", "tóm lại,", "hy vọng bài viết này đã cung cấp",
    "hy vọng qua bài viết", "nhìn chung, bài viết", "như vậy, chúng ta đã cùng tìm hiểu",
    "lời kết: trên đây là", "chúc bạn có những trải nghiệm tuyệt vời",
    "hy vọng thông tin trên sẽ hữu ích", "kết luận lại,"
]

AI_CONCLUSION_CLICHES_EN = [
    "in conclusion,", "to sum up,", "all in all,", "wrapping up,",
    "in summary,", "hopefully, this guide has provided", "final thoughts:",
    "in essence,", "as we have seen,"
]


class ContentAuditor:
    """Audits WordPress content against repo content and anti-AI guidelines."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 Master-Auto-SEO-GEO-Suite ContentAuditor/2.0"
        }

    def fetch_all_posts(self, site_url: str, max_posts: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetches all published posts from WordPress REST API."""
        base_url = site_url.rstrip("/")
        api_url = f"{base_url}/wp-json/wp/v2/posts"
        posts = []
        page = 1
        per_page = 100

        while True:
            params = {
                "per_page": per_page,
                "page": page,
                "status": "publish",
                "_fields": "id,date,link,title,content,excerpt,featured_media"
            }
            try:
                resp = requests.get(api_url, params=params, headers=self.headers, timeout=self.timeout)
                if resp.status_code != 200:
                    break
                
                batch = resp.json()
                if not batch or not isinstance(batch, list):
                    break

                posts.extend(batch)
                total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
                
                if max_posts and len(posts) >= max_posts:
                    posts = posts[:max_posts]
                    break

                if page >= total_pages:
                    break
                page += 1
            except Exception as e:
                print(f"  [!] Error fetching page {page} from {site_url}: {e}")
                break

        return posts

    def analyze_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes a single post against the content guidelines."""
        post_id = post.get("id")
        title = post.get("title", {}).get("rendered", "") if isinstance(post.get("title"), dict) else str(post.get("title", ""))
        link = post.get("link", "")
        raw_html = post.get("content", {}).get("rendered", "") if isinstance(post.get("content"), dict) else str(post.get("content", ""))
        featured_media = post.get("featured_media", 0)

        soup = BeautifulSoup(raw_html, "html.parser")
        
        # 1. Text & Word Count
        # Remove scripts & styles
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        
        plain_text = soup.get_text(separator=" ", strip=True)
        # Tokenize words
        words = [w for w in re.split(r"[\s,;:.?!()\[\]{}\"\u201c\u201d\u2018\u2019/\\<>]+", plain_text) if len(w) > 0]
        word_count = len(words)

        # 2. Image Audit
        # In-content images
        images = soup.find_all("img")
        in_content_img_count = len(images)
        images_missing_alt = [img.get("src", "unknown") for img in images if not img.get("alt", "").strip()]
        
        # Rule: Minimum 1 image per 500 words
        required_images = max(1, math.ceil(word_count / 500)) if word_count > 0 else 1
        img_density_pass = in_content_img_count >= required_images
        has_featured_image = bool(featured_media and featured_media > 0)

        # 3. Headings Audit
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        total_headings = len(headings)
        numbered_or_icon_headings = []

        for h in headings:
            htext = h.get_text(strip=True)
            has_num = bool(HEADING_NUMBER_REGEX.search(htext))
            has_emoji = bool(EMOJI_REGEX.search(htext))
            if has_num or has_emoji:
                numbered_or_icon_headings.append({
                    "tag": h.name,
                    "text": htext,
                    "has_num": has_num,
                    "has_emoji": has_emoji
                })

        heading_violation_ratio = (len(numbered_or_icon_headings) / total_headings) if total_headings > 0 else 0.0
        heading_standards_pass = heading_violation_ratio <= 0.20

        # 4. Marketing Hype & Buzzwords (Rule 1)
        lower_text = plain_text.lower()
        found_buzzwords = []
        all_buzzwords = MARKETING_BUZZWORDS_VI + MARKETING_BUZZWORDS_EN
        for bw in all_buzzwords:
            matches = len(re.findall(re.escape(bw), lower_text, re.IGNORECASE))
            if matches > 0:
                found_buzzwords.append({"buzzword": bw, "count": matches})

        # 5. Anti-AI Lead / Intro Clichés (Rule 6)
        # Check first 250 words
        intro_text = " ".join(words[:250]).lower()
        found_ai_leads = []
        for lead in (AI_LEAD_CLICHES_VI + AI_LEAD_CLICHES_EN):
            if lead in intro_text:
                found_ai_leads.append(lead)

        # 6. Anti-AI Filler Transitions (Rule 6)
        found_fillers = []
        for filler in (AI_TRANSITION_FILLERS_VI + AI_TRANSITION_FILLERS_EN):
            matches = len(re.findall(re.escape(filler), lower_text, re.IGNORECASE))
            if matches > 0:
                found_fillers.append({"filler": filler, "count": matches})

        # 7. Redundant AI Conclusion Clichés (Rule 6)
        # Check last 300 words
        conclusion_text = " ".join(words[-300:]).lower() if len(words) > 300 else lower_text
        found_ai_conclusions = []
        for concl in (AI_CONCLUSION_CLICHES_VI + AI_CONCLUSION_CLICHES_EN):
            if concl in conclusion_text:
                found_ai_conclusions.append(concl)

        # 8. Sentence Rhythm Analysis (Rule 3)
        sentences = [s.strip() for s in re.split(r"[.!?\n]+", plain_text) if len(s.strip().split()) >= 3]
        sentence_lengths = [len(s.split()) for s in sentences]
        sentence_count = len(sentence_lengths)
        if sentence_count >= 10:
            avg_sentence_len = sum(sentence_lengths) / sentence_count
            variance = sum((l - avg_sentence_len) ** 2 for l in sentence_lengths) / sentence_count
            std_dev = math.sqrt(variance)
            # A very low standard deviation (< 3.8) with moderate sentence count indicates robotic uniformity
            rhythm_monotonous = bool(std_dev < 3.8)
        else:
            avg_sentence_len = sum(sentence_lengths) / sentence_count if sentence_count > 0 else 0
            std_dev = 0
            rhythm_monotonous = False

        # 9. Thin Content Check (Rule 2)
        thin_content = word_count < 1000

        # 10. Overall Violations List & Penalty Calculation
        violations = []
        if not has_featured_image:
            violations.append({"rule": "Rule 1.1: Missing Featured Image", "severity": "HIGH", "desc": "Post has no featured image attached."})
        if not img_density_pass:
            violations.append({"rule": "Rule 1.2: Image Density Deficit", "severity": "HIGH", "desc": f"Found {in_content_img_count} images; required at least {required_images} (1 per 500w for {word_count} words)."})
        if thin_content:
            violations.append({"rule": "Rule 2: Thin Content", "severity": "HIGH" if word_count < 600 else "MEDIUM", "desc": f"Word count ({word_count}) is below minimum requirement of 1,000 words."})
        if not heading_standards_pass:
            violations.append({"rule": "Rule 5: Robotic Heading Formatting", "severity": "HIGH", "desc": f"{len(numbered_or_icon_headings)}/{total_headings} headings ({heading_violation_ratio*100:.1f}%) have mechanical numbers/icons (max 20% allowed)."})
        if found_buzzwords:
            total_bw = sum(item["count"] for item in found_buzzwords)
            violations.append({"rule": "Rule 6.1: Marketing Hype & Buzzwords", "severity": "MEDIUM", "desc": f"Found {total_bw} instances of marketing buzzwords ({', '.join([item['buzzword'] for item in found_buzzwords[:3]])})."})
        if found_ai_leads:
            violations.append({"rule": "Rule 6.6: AI Cliché Lead", "severity": "MEDIUM", "desc": f"Intro contains textbook AI opening: {', '.join(found_ai_leads)}."})
        if found_ai_conclusions:
            violations.append({"rule": "Rule 6.6: Redundant AI Conclusion", "severity": "MEDIUM", "desc": f"Ending contains textbook AI conclusion phrase: {', '.join(found_ai_conclusions)}."})
        if rhythm_monotonous:
            violations.append({"rule": "Rule 6.3: Monotonous Sentence Rhythm", "severity": "LOW", "desc": f"Sentence length std dev is unusually low ({std_dev:.1f}), indicating robotic sentence pacing."})
        if len(found_fillers) >= 4:
            violations.append({"rule": "Rule 6.6: Excessive AI Filler Transitions", "severity": "LOW", "desc": f"Found {sum(f['count'] for f in found_fillers)} filler transitions ({', '.join([f['filler'] for f in found_fillers[:3]])})."})

        # Calculate score (100 base)
        penalty = 0
        for v in violations:
            if v["severity"] == "HIGH":
                penalty += 25
            elif v["severity"] == "MEDIUM":
                penalty += 15
            elif v["severity"] == "LOW":
                penalty += 5
        score = max(0, 100 - penalty)
        compliance_status = "PASS" if score >= 80 and not any(v["severity"] == "HIGH" for v in violations) else ("WARNING" if score >= 50 else "FAIL")

        return {
            "id": post_id,
            "title": title,
            "link": link,
            "word_count": word_count,
            "has_featured_image": has_featured_image,
            "in_content_img_count": in_content_img_count,
            "required_images": required_images,
            "img_density_pass": img_density_pass,
            "images_missing_alt_count": len(images_missing_alt),
            "total_headings": total_headings,
            "numbered_or_icon_headings_count": len(numbered_or_icon_headings),
            "heading_violation_ratio": round(heading_violation_ratio, 3),
            "heading_standards_pass": heading_standards_pass,
            "found_buzzwords": found_buzzwords,
            "found_ai_leads": found_ai_leads,
            "found_ai_conclusions": found_ai_conclusions,
            "found_fillers": found_fillers,
            "avg_sentence_len": round(avg_sentence_len, 1),
            "sentence_std_dev": round(std_dev, 2),
            "rhythm_monotonous": rhythm_monotonous,
            "thin_content": thin_content,
            "violations": violations,
            "score": score,
            "status": compliance_status
        }

    def audit_site(self, site: Dict[str, Any], max_posts: Optional[int] = None) -> Dict[str, Any]:
        """Runs full content audit on a site."""
        site_id = site.get("site_id", "unknown")
        name = site.get("name", site_id)
        url = site.get("url", "")
        print(f"\n==================================================")
        print(f"🔍 Auditing Content for [{name}] ({url})")
        print(f"==================================================")
        
        posts = self.fetch_all_posts(url, max_posts=max_posts)
        print(f"-> Fetched {len(posts)} published posts from {url}")
        
        results = []
        for idx, p in enumerate(posts, 1):
            analysis = self.analyze_post(p)
            results.append(analysis)
            if idx % 50 == 0 or idx == len(posts):
                print(f"   Processed {idx}/{len(posts)} posts...")

        # Site-wide Aggregations
        total_scanned = len(results)
        passed_posts = sum(1 for r in results if r["status"] == "PASS")
        warning_posts = sum(1 for r in results if r["status"] == "WARNING")
        failed_posts = sum(1 for r in results if r["status"] == "FAIL")
        
        # Rule Specific Statistics
        missing_featured_total = sum(1 for r in results if not r["has_featured_image"])
        density_deficit_total = sum(1 for r in results if not r["img_density_pass"])
        thin_content_total = sum(1 for r in results if r["thin_content"])
        heading_violating_total = sum(1 for r in results if not r["heading_standards_pass"])
        buzzwords_detected_total = sum(1 for r in results if len(r["found_buzzwords"]) > 0)
        ai_leads_total = sum(1 for r in results if len(r["found_ai_leads"]) > 0)
        ai_conclusions_total = sum(1 for r in results if len(r["found_ai_conclusions"]) > 0)
        monotonous_rhythm_total = sum(1 for r in results if r["rhythm_monotonous"])
        
        avg_score = round(sum(r["score"] for r in results) / total_scanned, 1) if total_scanned > 0 else 0
        pass_rate = round((passed_posts / total_scanned) * 100, 1) if total_scanned > 0 else 0

        summary = {
            "site_id": site_id,
            "site_name": name,
            "site_url": url,
            "total_posts_scanned": total_scanned,
            "passed_posts": passed_posts,
            "warning_posts": warning_posts,
            "failed_posts": failed_posts,
            "pass_rate_pct": pass_rate,
            "average_score": avg_score,
            "metrics": {
                "missing_featured_image": missing_featured_total,
                "image_density_deficit": density_deficit_total,
                "thin_content_less_1000w": thin_content_total,
                "heading_robotic_formatting": heading_violating_total,
                "marketing_buzzwords": buzzwords_detected_total,
                "ai_cliche_lead": ai_leads_total,
                "ai_redundant_conclusion": ai_conclusions_total,
                "monotonous_rhythm": monotonous_rhythm_total
            },
            "posts": results
        }

        print(f"\n--- Audit Summary for {name} ---")
        print(f"  Total Scanned: {total_scanned} posts")
        print(f"  Average Score: {avg_score}/100")
        print(f"  Pass Rate: {pass_rate}% ({passed_posts} Pass, {warning_posts} Warning, {failed_posts} Fail)")
        print(f"  Missing Featured Image: {missing_featured_total}")
        print(f"  Image Density Deficit (<1 img/500w): {density_deficit_total}")
        print(f"  Thin Content (<1,000w): {thin_content_total}")
        print(f"  Robotic Headings (>20% numbers/icons): {heading_violating_total}")
        print(f"  Marketing Buzzwords: {buzzwords_detected_total}")
        print(f"  AI Cliché Leads: {ai_leads_total}")
        print(f"  AI Redundant Conclusions: {ai_conclusions_total}")

        return summary
