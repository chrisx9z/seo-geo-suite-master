import re
import math
import json
import time
import os
import sys
import socket
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

# Rule 2: Personal Perspective Markers (Selective)
PERSPECTIVE_PATTERNS_VI = [
    r"\b(tôi thấy|mình thấy|theo kinh nghiệm của mình|lời khuyên thật lòng|cá nhân tôi|trải nghiệm thực tế|điểm mình thích|điểm mình chưa ưng|lưu ý riêng|thực tế thì|lần đầu mình|mình khuyên|mình nhận thấy)\b"
]
PERSPECTIVE_PATTERNS_EN = [
    r"\b(in my experience|i found that|personally,|honest take|what i liked|what i noticed|from my point of view|my recommendation|i would suggest|having visited|during my trip|i noticed)\b"
]

# Rule 4: Concrete Data & Specific Details
DATA_PATTERNS = [
    r"\b\d+([\.,]\d+)?\s*(vnđ|vnd|đ|k|triệu|nghìn|\$|usd|eur|%|km|m|ha|m2|kg|g|giờ|h|phút|ngày|tháng|năm|°c|bước)\b",
    r"\b(giá vé|chi phí|khoảng|tầm)\s*\d+",
    r"\b\d{1,2}:\d{2}\b"
]

# Rule 5: Conversational Voice Markers (>50% target)
CONVERSATIONAL_WORDS_VI = [
    r"\b(bạn|mình|chúng ta|nhé|nha|đấy|thực ra|nói thật|hãy thử|hãy cùng|hãy nhớ|đừng lo|bạn có thể|nếu bạn|cùng mình)\b"
]
CONVERSATIONAL_WORDS_EN = [
    r"\b(you|your|we|our|let's|actually,|to be honest|here's why|don't worry|keep in mind|if you're|you'll|we'll)\b"
]
# Direct Answer / Key Takeaways Patterns (E-E-A-T & GEO)
DIRECT_ANSWER_PATTERNS = [
    r"geo-key-takeaways",
    r"direct-answer",
    r"key\s*takeaways",
    r"câu\s*trả\s*lời\s*trực\s*tiếp",
    r"tóm\s*tắt\s*định\s*lượng",
    r"trả\s*lời\s*nhanh",
    r"quick\s*answer",
    r"at\s*a\s*glance",
    r"essential\s*takeaways",
    r"fast\s*facts",
    r"class=[\"']lead[\"']"
]


class ContentAuditor:
    """Audits WordPress content against repo content and anti-AI guidelines."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 Master-Auto-SEO-GEO-Suite ContentAuditor/2.0"
        }

    def fetch_all_posts(self, site_url: str, max_posts: Optional[int] = None, host_ip: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetches all published posts from WordPress REST API."""
        base_url = site_url.rstrip("/")
        api_url = f"{base_url}/wp-json/wp/v2/posts"
        posts = []
        page = 1
        per_page = 100

        orig_getaddrinfo = socket.getaddrinfo
        if host_ip:
            domain = base_url.replace("https://", "").replace("http://", "").split("/")[0]
            def patched_getaddrinfo(h, port, *args, **kwargs):
                if h == domain:
                    return orig_getaddrinfo(host_ip, port, *args, **kwargs)
                return orig_getaddrinfo(h, port, *args, **kwargs)
            socket.getaddrinfo = patched_getaddrinfo

        try:
            while True:
                params = {
                    "per_page": per_page,
                    "page": page,
                    "status": "publish",
                    "_fields": "id,date,link,title,content,excerpt,featured_media"
                }
                try:
                    resp = requests.get(api_url, params=params, headers=self.headers, timeout=self.timeout, verify=False if host_ip else True)
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
        finally:
            if host_ip:
                socket.getaddrinfo = orig_getaddrinfo

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

        # Dual AVIF/WebP Syntax or Modern Formats
        pictures = soup.find_all("picture")
        has_avif = ".avif" in raw_html
        has_webp = ".webp" in raw_html
        has_dual_avif_webp = bool(len(pictures) > 0 or has_avif or (has_webp and in_content_img_count > 0))

        # Direct Answer E-E-A-T Block
        has_direct_answer = False
        for pat in DIRECT_ANSWER_PATTERNS:
            if re.search(pat, raw_html, re.I):
                has_direct_answer = True
                break
        if not has_direct_answer:
            first_p = soup.find("p")
            if first_p and 40 <= len(first_p.get_text().split()) <= 100:
                has_direct_answer = True

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
        short_count = sum(1 for l in sentence_lengths if l < 10)
        med_count = sum(1 for l in sentence_lengths if 10 <= l <= 22)
        long_count = sum(1 for l in sentence_lengths if l > 22)

        if sentence_count >= 10:
            avg_sentence_len = sum(sentence_lengths) / sentence_count
            variance = sum((l - avg_sentence_len) ** 2 for l in sentence_lengths) / sentence_count
            std_dev = math.sqrt(variance)
            short_pct = round((short_count / sentence_count) * 100, 1)
            med_pct = round((med_count / sentence_count) * 100, 1)
            long_pct = round((long_count / sentence_count) * 100, 1)
            # A very low standard deviation (< 3.8) or excessive long sentences (>65%) indicates poor rhythm
            rhythm_monotonous = bool(std_dev < 3.8 or long_pct > 65.0)
        else:
            avg_sentence_len = sum(sentence_lengths) / sentence_count if sentence_count > 0 else 0
            std_dev = 0
            short_pct, med_pct, long_pct = 0.0, 0.0, 0.0
            rhythm_monotonous = False

        # 9. Personal Perspective Analysis (Rule 2)
        persp_matches = len(re.findall("|".join(PERSPECTIVE_PATTERNS_VI + PERSPECTIVE_PATTERNS_EN), plain_text, re.IGNORECASE))
        has_personal_perspective = persp_matches > 0

        # 10. Concrete Specificity & Data (Rule 4)
        concrete_data_matches = 0
        for pat in DATA_PATTERNS:
            concrete_data_matches += len(re.findall(pat, plain_text, re.IGNORECASE))
        concrete_data_density = round((concrete_data_matches / (word_count / 1000.0)), 1) if word_count > 0 else 0.0
        concrete_data_pass = concrete_data_density >= 2.0 or concrete_data_matches >= 4

        # 11. Conversational Voice Analysis (Rule 5)
        conv_matches = len(re.findall("|".join(CONVERSATIONAL_WORDS_VI + CONVERSATIONAL_WORDS_EN), plain_text, re.IGNORECASE))
        conversational_ratio = round((conv_matches / sentence_count) * 100, 1) if sentence_count > 0 else 0.0
        conversational_pass = conversational_ratio >= 30.0

        # 12. Thin Content Check (Rule 2)
        thin_content = word_count < 1000
        severe_thin_content = word_count < 600

        # 13. Overall Violations List & Penalty Calculation
        violations = []
        if not has_featured_image:
            violations.append({"rule": "Rule 1.1: Missing Featured Image", "severity": "HIGH", "desc": "Post has no featured image attached."})
        
        if not img_density_pass:
            if in_content_img_count == 0:
                violations.append({"rule": "Rule 1.2: Zero In-Content Images", "severity": "HIGH", "desc": f"Post has 0 in-content images; required at least {required_images} (1 per 500w for {word_count} words)."})
            else:
                violations.append({"rule": "Rule 1.2: Image Density Deficit", "severity": "MEDIUM", "desc": f"Found {in_content_img_count} images; required at least {required_images} (1 per 500w for {word_count} words)."})

        if thin_content:
            violations.append({"rule": "Rule 2: Thin Content", "severity": "HIGH" if severe_thin_content else "MEDIUM", "desc": f"Word count ({word_count}) is below minimum requirement of 1,000 words."})
        
        if not heading_standards_pass:
            violations.append({"rule": "Rule 5: Robotic Heading Formatting", "severity": "MEDIUM", "desc": f"{len(numbered_or_icon_headings)}/{total_headings} headings ({heading_violation_ratio*100:.1f}%) have mechanical numbers/icons (max 20% allowed)."})
        
        if found_buzzwords:
            total_bw = sum(item["count"] for item in found_buzzwords)
            severity = "MEDIUM" if total_bw >= 3 else "LOW"
            violations.append({"rule": "Rule 6.1: Marketing Hype & Buzzwords", "severity": severity, "desc": f"Found {total_bw} instances of marketing buzzwords ({', '.join([item['buzzword'] for item in found_buzzwords[:3]])})."})
        
        if found_ai_leads:
            violations.append({"rule": "Rule 6.6: AI Cliché Lead", "severity": "MEDIUM", "desc": f"Intro contains textbook AI opening: {', '.join(found_ai_leads)}."})
        
        if found_ai_conclusions:
            violations.append({"rule": "Rule 6.6: Redundant AI Conclusion", "severity": "MEDIUM", "desc": f"Ending contains textbook AI conclusion phrase: {', '.join(found_ai_conclusions)}."})
        
        if rhythm_monotonous:
            violations.append({"rule": "Rule 6.3: Monotonous / Overlong Sentence Rhythm", "severity": "LOW", "desc": f"Sentence lengths lack variation (Long sentences: {long_pct}%, std dev: {std_dev:.1f})."})
        
        if not concrete_data_pass and word_count >= 1000:
            violations.append({"rule": "Rule 6.4: Low Concrete Specificity", "severity": "LOW", "desc": f"Low density of numbers/prices/concrete facts ({concrete_data_density} per 1k words)."})

        if not conversational_pass and word_count >= 1000:
            violations.append({"rule": "Rule 6.5: Low Conversational Voice", "severity": "LOW", "desc": f"Conversational marker ratio is low ({conversational_ratio}%)."})

        if len(found_fillers) >= 4:
            violations.append({"rule": "Rule 6.6: Excessive AI Filler Transitions", "severity": "LOW", "desc": f"Found {sum(f['count'] for f in found_fillers)} filler transitions ({', '.join([f['filler'] for f in found_fillers[:3]])})."})

        # Calculate score (100 base)
        penalty = 0
        has_fatal_violation = not has_featured_image or severe_thin_content
        for v in violations:
            if v["severity"] == "HIGH":
                penalty += 25
            elif v["severity"] == "MEDIUM":
                penalty += 12
            elif v["severity"] == "LOW":
                penalty += 5
        score = max(0, 100 - penalty)
        
        if has_fatal_violation or score < 60:
            compliance_status = "FAIL"
        elif score >= 80 and not any(v["severity"] == "HIGH" for v in violations):
            compliance_status = "PASS"
        else:
            compliance_status = "WARNING"

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
            "sentence_rhythm": {
                "short_pct": short_pct,
                "med_pct": med_pct,
                "long_pct": long_pct,
                "monotonous": rhythm_monotonous
            },
            "personal_perspective": {
                "count": persp_matches,
                "has_perspective": has_personal_perspective
            },
            "concrete_data": {
                "matches": concrete_data_matches,
                "density_per_1kw": concrete_data_density,
                "pass": concrete_data_pass
            },
            "conversational": {
                "matches": conv_matches,
                "ratio_pct": conversational_ratio,
                "pass": conversational_pass
            },
            "thin_content": thin_content,
            "has_dual_avif_webp": has_dual_avif_webp,
            "has_direct_answer": has_direct_answer,
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
        
        host_ip = site.get("host_ip")
        posts = self.fetch_all_posts(url, max_posts=max_posts, host_ip=host_ip)
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
        monotonous_rhythm_total = sum(1 for r in results if r["sentence_rhythm"]["monotonous"])
        
        avg_score = round(sum(r["score"] for r in results) / total_scanned, 1) if total_scanned > 0 else 0
        pass_rate = round((passed_posts / total_scanned) * 100, 1) if total_scanned > 0 else 0

        zero_in_content_img_total = sum(1 for r in results if r["in_content_img_count"] == 0)
        has_perspective_total = sum(1 for r in results if r["personal_perspective"]["has_perspective"])
        concrete_data_pass_total = sum(1 for r in results if r["concrete_data"]["pass"])
        conversational_pass_total = sum(1 for r in results if r["conversational"]["pass"])
        dual_avif_webp_total = sum(1 for r in results if r.get("has_dual_avif_webp", False))
        direct_answer_total = sum(1 for r in results if r.get("has_direct_answer", False))
        total_headings_site = sum(r["total_headings"] for r in results)
        violating_headings_site = sum(r["numbered_or_icon_headings_count"] for r in results)
        site_heading_violation_rate = round((violating_headings_site / total_headings_site * 100), 1) if total_headings_site > 0 else 0.0

        avg_word_count = round(sum(r["word_count"] for r in results) / total_scanned, 0) if total_scanned > 0 else 0
        avg_img_count = round(sum(r["in_content_img_count"] for r in results) / total_scanned, 1) if total_scanned > 0 else 0

        summary = {
            "site_id": site_id,
            "site_name": name,
            "site_url": url,
            "category": site.get("category", "PBN"),
            "total_posts_scanned": total_scanned,
            "passed_posts": passed_posts,
            "warning_posts": warning_posts,
            "failed_posts": failed_posts,
            "pass_rate_pct": pass_rate,
            "average_score": avg_score,
            "avg_word_count": avg_word_count,
            "avg_img_count": avg_img_count,
            "total_headings_site": total_headings_site,
            "violating_headings_site": violating_headings_site,
            "site_heading_violation_rate_pct": site_heading_violation_rate,
            "metrics": {
                "missing_featured_image": missing_featured_total,
                "zero_in_content_images": zero_in_content_img_total,
                "image_density_deficit": density_deficit_total,
                "dual_avif_webp": dual_avif_webp_total,
                "direct_answer_eeat": direct_answer_total,
                "thin_content_less_1000w": thin_content_total,
                "heading_robotic_formatting": heading_violating_total,
                "marketing_buzzwords": buzzwords_detected_total,
                "has_personal_perspective": has_perspective_total,
                "monotonous_rhythm": monotonous_rhythm_total,
                "concrete_data_pass": concrete_data_pass_total,
                "conversational_pass": conversational_pass_total,
                "ai_cliche_lead": ai_leads_total,
                "ai_redundant_conclusion": ai_conclusions_total
            },
            "posts": results
        }

        print(f"\n--- Audit Summary for {name} ---")
        print(f"  Total Scanned: {total_scanned} posts")
        print(f"  Average Score: {avg_score}/100")
        print(f"  Pass Rate: {pass_rate}% ({passed_posts} Pass, {warning_posts} Warning, {failed_posts} Fail)")
        print(f"  Avg Word Count: {avg_word_count} words | Avg Images: {avg_img_count} imgs")
        print(f"  Missing Featured Image: {missing_featured_total}")
        print(f"  Zero In-Content Images: {zero_in_content_img_total}")
        print(f"  Image Density Deficit (<1 img/500w): {density_deficit_total}")
        print(f"  Dual AVIF/WebP Format: {dual_avif_webp_total}/{total_scanned} ({(dual_avif_webp_total/total_scanned*100):.1f}%)")
        print(f"  Direct Answer E-E-A-T: {direct_answer_total}/{total_scanned} ({(direct_answer_total/total_scanned*100):.1f}%)")
        print(f"  Site Headings Number/Icon Rate: {site_heading_violation_rate}% ({violating_headings_site}/{total_headings_site})")
        print(f"  Thin Content (<1,000w): {thin_content_total}")
        print(f"  Marketing Buzzwords: {buzzwords_detected_total}")
        print(f"  Has Personal Perspective: {has_perspective_total}/{total_scanned}")
        print(f"  Concrete Data Density Pass: {concrete_data_pass_total}/{total_scanned}")
        print(f"  Conversational Tone Pass: {conversational_pass_total}/{total_scanned}")
        print(f"  AI Cliché Leads: {ai_leads_total}")
        print(f"  AI Redundant Conclusions: {ai_conclusions_total}")

        return summary
