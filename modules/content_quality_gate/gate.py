# -*- coding: utf-8 -*-
"""
Content Quality Gate — MANDATORY pre-publish filter for every pipeline.

Every scheduler / autopilot MUST call `enforce_publish_payload()` right before
POSTing to `/wp-json/wp/v2/posts`. There is intentionally NO bypass flag.

A post is classified as JUNK (rejected, never published) when:
  1. It contains Mad-Libs boilerplate templates (fake "Guinness", "Vị trí Quán Quân",
     generic "Khám phá toàn diện về <keyword>" shells, generic step templates...).
  2. Title/keyword and body do not match: the body does not actually explain the
     keyword (low keyword-token coverage, keyword absent from headings, a "Top N"
     title with no real list...).
  3. It contains Vietnamese political content/imagery (site policy).
  4. It is thin (< MIN_WORDS) or largely repeated sentences.
  5. It uses text-only placeholder images instead of real/designed images.

Auto-repaired (not rejected):
  * Geographic hallucination paragraphs copied from another destination
    (e.g. "Nằm cách trung tâm thủ đô không quá xa" on a Phú Quốc post) are stripped.
    If the post becomes too thin after stripping, it is rejected.
  * Slugs are normalised to a short keyword slug (ASCII, <= 7 words, no year,
    no "038" HTML-entity residue, no dangling truncated words).
"""

from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

MIN_WORDS = 600
MAX_SLUG_WORDS = 7
MIN_KEYWORD_COVERAGE = 0.6
MAX_DUPLICATE_SENTENCE_RATIO = 0.15


class JunkContentError(Exception):
    """Raised when a post is classified as junk and must not be published."""

    def __init__(self, issues: List[str]):
        self.issues = issues
        super().__init__("Junk content blocked: " + " | ".join(issues))


# --------------------------------------------------------------------------- #
# Rule data
# --------------------------------------------------------------------------- #
BOILERPLATE_PATTERNS: List[str] = [
    r"chuẩn xác thực guinness",
    r"kỷ lục guinness 2026",
    r"vị trí quán quân",
    r"vị trí á quân",
    r"vị trí thứ ba",
    r"tóm tắt nhanh \(direct answer\):\s*khám phá toàn diện về",
    r"khám phá toàn diện về\s*<strong>?[^<]{0,120}</strong>?\s*với đầy đủ số liệu",
    r"hạng mục\s*/\s*tiêu chí",
    r"class=[\"']geo-direct-answer",
    r"cẩm nang kỹ thuật\s*&(amp;)?\s*thực chiến",
    r"bước 1\s*[–-]\s*khởi tạo ý tưởng",
    r"vị thế dẫn đầu:\s*</?strong>?\s*đạt kỷ lục cao nhất về quy mô",
    r"top kỷ lục\s*&(amp;)?\s*sự thật thú vị",
]

# (phrase regex, destination keywords for which the phrase is legitimate)
_KARST = ["ninh bình", "tràng an", "tam cốc", "bái đính", "hạ long", "lan hạ", "cát bà",
          "bái tử long", "phong nha", "quảng bình", "hà giang", "cao bằng", "đồng văn",
          "ninh binh", "trang an", "tam coc", "halong", "ha long", "lan ha", "cat ba",
          "phong nha", "ha giang", "cao bang", "dong van", "karst"]
GEO_HALLUCINATIONS: List[Tuple[str, List[str]]] = [
    (r"nằm cách trung tâm thủ đô không quá xa", ["hà nội", "ba vì", "chùa hương", "đường lâm",
                                                  "bát tràng", "ninh bình", "tràng an", "mai châu"]),
    (r"dãy núi đá vôi triệu năm tuổi", _KARST),
    (r"thung lũng karst đá vôi ngập nước", _KARST),
    (r"vách đá vôi sừng sững,? đèo cao mây phủ", _KARST),
    (r"vòm hang thạch nhũ lung linh", _KARST),
    (r"dấu tích vàng son của các vương triều phong kiến", ["huế", "hà nội", "thăng long", "ninh bình", "hoa lư"]),
    (r"triều đại đinh, tiền lê", ["ninh bình", "hoa lư", "bái đính", "tràng an"]),
    (r"towering limestone spires rising out of tranquil rivers", _KARST),
    (r"mastering vietnam e-visa", ["visa", "e-visa", "evisa", "entry", "immigration"]),
]

# Vietnamese political content is banned site-wide (images + text).
POLITICAL_PATTERNS: List[str] = [
    r"bác hồ",
    r"lăng bác",
    r"chủ tịch hồ chí minh",
    r"đảng cộng sản",
    r"tổng bí thư",
    r"bộ chính trị",
    r"ho chi minh mausoleum",
    r"uncle ho",
    r"communist party",
]  # bare "Hồ Chí Minh" is NOT listed: it is usually the city or the highway

PLACEHOLDER_IMAGE_PATTERNS: List[str] = [
    r"placehold", r"dummyimage", r"via\.placeholder", r"text[-_]card", r"text[-_]banner",
    r"fakeimg", r"placeimg",
]

STOPWORDS_VI = {
    "và", "của", "cho", "các", "những", "một", "là", "có", "ở", "tại", "với", "trong", "khi",
    "nào", "gì", "the", "mới", "nhất", "2025", "2026", "top", "hay", "đẹp", "cách", "kinh",
    "nghiệm", "hướng", "dẫn", "review", "a", "an", "of", "to", "in", "for", "and", "on", "how",
    "best", "guide", "what", "is", "từ", "đến", "bằng", "về", "này", "đó", "như", "thế", "nên",
}
SLUG_DROP = {"2024", "2025", "2026", "038", "8211", "amp"}
# Superlative keyword anchor: the keyword ends right after this phrase ("...-nhat-the-gioi")
SLUG_ANCHOR = re.compile(r"-nhat-(the-gioi|viet-nam|chau-a|chau-au|chau-phi|dong-nam-a)(?=-|$)")
SLUG_LEAD_FILLER = {"top", "nhung", "cac", "nao", "co", "la", "gi", "ai"}
SLUG_FILLER_PREFIX = re.compile(
    r"^(bat-mi-\d+-(loai-)?|nghien-ngay-\d+-|review-|kham-pha-|trai-nghiem-(an-tuong-khi-toi-|cac-diem-den-khi-)?|"
    r"huong-dan-|cam-nang-)"
)
SLUG_FILLER_SUFFIX = re.compile(
    r"(-chi-tiet-nhat-hien-nay|-chi-tiet-nhat|-hien-nay|-moi-nhat|-tron-goi|-tu-a-(toi|den)-z|-a-z|"
    r"-cuc-chi-tiet|-khong-the-bo-qua|-phai-thuong-thuc|-ly-tuong-nhat|-tu-tuc|-20\d\d)$"
)
SLUG_LOW_VALUE = {"chi", "tiet", "sieu", "va", "cua", "cac", "nhung",
                  "dot", "pha", "complete", "ultimate", "guide", "vs"}
DANGLING_TAIL = {"the", "va", "cua", "cho", "cac", "nhung", "mot", "o", "tai", "voi", "trong", "khi", "nao", "la"}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _strip_tags(s: str) -> str:
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\[[a-z_-]+[^\]]*\]", " ", s)  # shortcodes like [ez-toc]
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def _ascii(s: str) -> str:
    s = s.replace("đ", "d").replace("Đ", "D")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(s or "").lower()).strip()


def keyword_tokens(keyword: str) -> List[str]:
    toks = re.findall(r"[\wÀ-ỹ]+", _norm(keyword))
    return [t for t in toks if t not in STOPWORDS_VI and not t.isdigit() and len(t) > 1]


def normalize_slug(slug: str, keyword: str = "") -> str:
    """Return a clean short-keyword slug (ASCII, <= MAX_SLUG_WORDS words)."""
    base = slug or keyword or ""
    base = _ascii(html.unescape(base)).lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    # Drop single-word / truncated slugs in favour of the keyword
    if keyword and (len(base.split("-")) < 2):
        base = re.sub(r"[^a-z0-9]+", "-", _ascii(keyword).lower()).strip("-")
    prev = None
    while prev != base:
        prev = base
        base = SLUG_FILLER_PREFIX.sub("", base)
        base = SLUG_FILLER_SUFFIX.sub("", base)
    words = [w for w in base.split("-") if w and w not in SLUG_DROP]
    # "top-10-xxx" -> "xxx" (number-led listicle prefixes are not keywords)
    if len(words) > 2 and words[0] == "top" and words[1].isdigit():
        words = words[2:]
    # Truncated "...-nhat-the" (thế giới cut off) -> complete it
    if len(words) >= 2 and words[-2] == "nhat" and words[-1] == "the":
        words.append("gioi")
    # Too long: cut after the superlative anchor, drop fillers, then truncate
    if len(words) > MAX_SLUG_WORDS:
        joined = "-".join(words)
        m = SLUG_ANCHOR.search(joined)
        if m:
            words = joined[:m.end()].split("-")
    if len(words) > MAX_SLUG_WORDS:
        words = [w for w in words if w not in SLUG_LOW_VALUE] or words
    while len(words) > MAX_SLUG_WORDS and (words[0].isdigit() or words[0] in SLUG_LEAD_FILLER):
        words.pop(0)
    if len(words) > MAX_SLUG_WORDS:
        words = [w for w in words if w not in SLUG_LEAD_FILLER] or words
    words = words[:MAX_SLUG_WORDS]
    while words and (words[-1] in DANGLING_TAIL or words[-1].isdigit()):
        words.pop()
    return "-".join(words)


def is_bad_slug(slug: str) -> bool:
    """True only for slugs that violate the short-keyword-slug standard (avoid needless URL churn)."""
    words = [w for w in (slug or "").split("-") if w]
    return (
        len(words) < 2
        or len(words) > MAX_SLUG_WORDS
        or bool(re.search(r"[^a-z0-9-]", slug))
        or any(w in SLUG_DROP or re.fullmatch(r"20\d\d", w) for w in words)
        or words[-1] in DANGLING_TAIL
        or bool(SLUG_FILLER_SUFFIX.search(slug))
    )


def _strip_blocks(content: str, pattern: str) -> str:
    """Remove <p>/<li>/<figure> blocks (or bare sentences) that match `pattern`."""
    rx = re.compile(pattern, re.I)
    content = re.sub(r"<(p|li|figure)\b[^>]*>.*?</\1>",
                     lambda m: "" if rx.search(_norm(m.group(0))) else m.group(0),
                     content, flags=re.S | re.I)
    if rx.search(_norm(content)):
        content = re.sub(r"[^.!?<>]*" + pattern + r"[^.!?<>]*[.!?]?", "", content, flags=re.I)
    return content


def strip_geo_hallucinations(content: str, context: str) -> Tuple[str, List[str]]:
    """Remove paragraphs/list items that contain destination-copied boilerplate."""
    ctx = _norm(context)
    removed: List[str] = []
    for pattern, allowed in GEO_HALLUCINATIONS:
        if any(a in ctx for a in allowed):
            continue
        rx = re.compile(pattern, re.I)
        if not rx.search(_norm(content)):
            continue

        def _drop(m: "re.Match[str]") -> str:
            if rx.search(_norm(m.group(0))):
                removed.append(pattern)
                return ""
            return m.group(0)

        content = re.sub(r"<(p|li)\b[^>]*>.*?</\1>", _drop, content, flags=re.S | re.I)
        # Fallback: sentence-level removal for text outside <p>
        if rx.search(_norm(content)):
            content = re.sub(r"[^.!?<>]*" + pattern + r"[^.!?<>]*[.!?]?", "", content, flags=re.I)
            removed.append(pattern)
    return content, sorted(set(removed))


# --------------------------------------------------------------------------- #
# Gate
# --------------------------------------------------------------------------- #
@dataclass
class GateResult:
    passed: bool
    issues: List[str] = field(default_factory=list)
    repairs: List[str] = field(default_factory=list)
    slug: str = ""
    content: str = ""
    word_count: int = 0


def check_post(title: str, content: str, keyword: str = "", slug: str = "",
               destination: str = "") -> GateResult:
    keyword = keyword or title
    issues: List[str] = []
    repairs: List[str] = []

    # --- Auto-repair: geographic hallucinations -------------------------------
    context = " ".join([title, keyword, destination])
    content, removed = strip_geo_hallucinations(content or "", context)
    if removed:
        repairs.append(f"stripped_geo_hallucination:{len(removed)}")

    low = _norm(content)
    text = _strip_tags(content)
    text_low = text.lower()
    words = text.split()
    wc = len(words)

    # 1. Boilerplate / Mad-Libs templates
    hits = [p for p in BOILERPLATE_PATTERNS if re.search(p, low, re.I)]
    if hits:
        issues.append(f"boilerplate_template:{len(hits)}")

    # 2. Political content: block if in title or any image; otherwise strip the paragraph
    img_tags = " ".join(re.findall(r"<img[^>]*>", low))
    if any(re.search(p, _norm(title) + " " + img_tags, re.I) for p in POLITICAL_PATTERNS):
        issues.append("political_content")
    else:
        n_before = len(content)
        for p in POLITICAL_PATTERNS:
            if re.search(p, low, re.I):
                content = _strip_blocks(content, p)
        if len(content) != n_before:
            repairs.append("stripped_political_paragraph")
            low = _norm(content)
            text = _strip_tags(content)
            text_low = text.lower()
            words = text.split()
            wc = len(words)
        if any(re.search(p, low, re.I) for p in POLITICAL_PATTERNS):
            issues.append("political_content")

    # 3. Thin content
    if wc < MIN_WORDS:
        issues.append(f"thin_content:{wc}w")

    # 4. Duplicate sentences (spun / template padding)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text_low) if len(s.split()) >= 6]
    if len(sents) >= 10:
        dup_ratio = 1 - len(set(sents)) / len(sents)
        if dup_ratio > MAX_DUPLICATE_SENTENCE_RATIO:
            issues.append(f"duplicate_sentences:{dup_ratio:.0%}")

    # 5. Title / keyword vs body relevance
    toks = keyword_tokens(keyword)
    if toks:
        covered = [t for t in toks if t in text_low]
        coverage = len(covered) / len(toks)
        if coverage < MIN_KEYWORD_COVERAGE:
            issues.append(f"off_topic_body:coverage={coverage:.0%}")
        heading_parts = re.findall(r"<h[2-4][^>]*>(.*?)</h[2-4]>", content, flags=re.S | re.I)
        # Legacy/classic posts use a standalone bold paragraph as a sub-heading.
        for pseudo in re.findall(r"<p[^>]*>\s*<(?:strong|b)>(.*?)</(?:strong|b)>\s*</p>", content, flags=re.S | re.I):
            if "<strong" not in pseudo.lower() and "<b>" not in pseudo.lower() \
                    and 0 < len(_strip_tags(pseudo).split()) <= 15:
                heading_parts.append(pseudo)
        headings = _strip_tags(" ".join(heading_parts)).lower()
        if headings:
            h_cov = sum(1 for t in toks if t in headings) / len(toks)
            if h_cov == 0:
                issues.append(f"keyword_absent_from_headings:{h_cov:.0%}")
        else:
            issues.append("no_headings")

    # 6. "Top N" promise must be fulfilled with a real list
    m = re.search(r"\btop\s*(\d{1,3})\b", _norm(title)) or re.search(r"^\s*(\d{1,3})\s+\w", _norm(title))
    if m:
        n = int(min(int(m.group(1)), 10) * 0.7)
        items = len(re.findall(r"<h[23]\b", content, re.I)) - 1 + len(re.findall(r"<li\b", content, re.I)) \
            + len(re.findall(r"<tr\b", content, re.I))
        if items < n:
            issues.append(f"top_list_unfulfilled:{items}<{n}")

    # 7. Text-only placeholder images
    srcs = re.findall(r"<img[^>]+src=[\"']([^\"']+)", content, re.I)
    if any(re.search(p, s, re.I) for s in srcs for p in PLACEHOLDER_IMAGE_PATTERNS):
        issues.append("placeholder_text_image")

    # --- Slug normalisation (auto-repair) ------------------------------------
    new_slug = normalize_slug(slug, keyword) if (not slug or is_bad_slug(slug)) else slug
    if slug and new_slug and new_slug != slug:
        repairs.append(f"slug:{slug}->{new_slug}")

    return GateResult(passed=not issues, issues=issues, repairs=repairs,
                      slug=new_slug or slug, content=content, word_count=wc)


def enforce_publish_payload(payload: Dict[str, Any], keyword: str = "", destination: str = "",
                            log=print) -> Dict[str, Any]:
    """Validate + repair a WP REST post payload in-place. Raises JunkContentError.

    This is the single mandatory entry point used by all publishing pipelines.
    """
    title = _strip_tags(str(payload.get("title", "")))
    kw = keyword or (payload.get("meta") or {}).get("rank_math_focus_keyword", "") or title
    res = check_post(title=title, content=str(payload.get("content", "")), keyword=kw,
                     slug=str(payload.get("slug", "")), destination=destination)
    if not res.passed:
        log(f"  [QUALITY GATE] BLOCKED '{title[:70]}': {', '.join(res.issues)}")
        raise JunkContentError(res.issues)
    payload["content"] = res.content
    if res.slug:
        payload["slug"] = res.slug
    if res.repairs:
        log(f"  [QUALITY GATE] Repaired: {', '.join(res.repairs)}")
    log(f"  [QUALITY GATE] PASSED ({res.word_count} words)")
    return payload
