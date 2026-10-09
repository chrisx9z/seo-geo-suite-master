# SEO & GEO Content Generation Rules

1. **Mandatory Featured Image:** 100% of published posts must have a unique featured image (16:9 / 1200x630, high quality, no text banner).
2. **In-Content Images:** Minimum 1 image, Maximum 5 professional images per post with descriptive SEO alt tags.
3. **Strict No Thin Content:** Minimum 1,000 words per article. No maximum limit (expand to 2,000 - 5,000+ words based on entity depth).
4. **Anti-Keyword Cannibalization:** Distinct search intent per post. Check existing posts before writing.
5. **URL Slugs:** Lowercase hyphenated Vietnamese without diacritics: /tu-khoa-chinh/.
6. **Natural Heading Tone (Max 20% Numbers/Icons):** Do NOT mechanically number headings (1., 2., 3., 1.1). Avoid excessive heading icons. Keep numbered headings + icons under 20% total. Use natural, engaging journalistic titles.
7. **E-E-A-T & GEO Structure:** Direct answer paragraph (60-80 words), comparison markdown table, detailed H2/H3 sections, FAQ with Schema.org JSON-LD (Article, FAQPage).
8. **Mandatory Junk-Content Quality Gate (default, no bypass):** Every publish path MUST call `enforce_publish_payload()` from `modules/content_quality_gate` before POSTing to WordPress. Posts whose body does not explain the title/keyword, Mad-Libs boilerplate (fake Guinness, "Vị trí Quán Quân", "Khám phá toàn diện về…"), unfulfilled "Top N" lists, Vietnamese political content, thin/duplicated text or text-placeholder images are blocked. Geo-hallucination paragraphs are stripped and bad slugs are normalised to short keyword slugs (<= 7 words, no year, no `038`). Never hard-code one destination's geography into shared templates. Audit existing posts with `python -m modules.content_quality_gate.audit_cli`. See RULES.md section 7.
