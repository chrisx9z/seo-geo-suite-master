"""
Rich Snippets & GEO Schema Generator (v2.5 — May 2026 Schema Policy & GEO Citation Compliant)
Generates multi-entity JSON-LD (Article with Wikidata `about`/`mentions`, `speakable`, `citation`,
BreadcrumbList, Niche Person/Profile Entities, optional FAQPage).
"""

import json
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional

from modules.geo_knowledge_graph.entity_linker import GeoEntityLinker


class RichSnippetsGenerator:
    def __init__(self, site_name: str, site_url: str, publisher_name: str, logo_url: str, niche: str = "", lang: str = "vi"):
        self.site_name = site_name
        self.site_url = site_url.rstrip("/")
        self.publisher_name = publisher_name
        self.logo_url = logo_url
        self.niche = niche.lower().strip()
        self.lang = lang.lower().strip()
        self.entity_linker = GeoEntityLinker()

    def _resolve_niche_author(self) -> Dict[str, Any]:
        """Returns a niche-accurate Person entity with E-E-A-T knowsAbout metadata without hardcoding private domains."""
        ctx = f"{self.niche} {self.site_name} {self.publisher_name}".lower()
        is_en = self.lang.startswith("en") or any(w in ctx for w in ("travel", "guide", "world", "english"))
        if any(k in ctx for k in ("travel", "du lịch", "lữ hành", "tour", "itinerary", "điểm đến")):
            return {
                "@type": "Person",
                "@id": f"{self.site_url}/#editorial-author",
                "name": f"{self.site_name} Travel Editorial" if is_en else f"Ban Biên Tập Du Lịch {self.site_name}",
                "jobTitle": "Senior Travel & Destination Editor" if is_en else "Biên Tập Viên Lữ Hành Thực Địa",
                "url": f"{self.site_url}/",
                "knowsAbout": ["Travel Itineraries", "Destination Guides", "Local Cuisine", "Budget Travel"],
            }
        if any(k in ctx for k in ("record", "kỷ lục", "nhất thế giới", "bách khoa", "wonders")):
            return {
                "@type": "Person",
                "@id": f"{self.site_url}/#editorial-author",
                "name": f"Hội Đồng Biên Tập {self.site_name}",
                "jobTitle": "Biên Tập Viên Khoa Học & Bách Khoa Kỷ Lục",
                "url": f"{self.site_url}/",
                "knowsAbout": ["World Records", "Natural Wonders", "Geography", "Scientific Benchmarks"],
            }
        return {
            "@type": "Person",
            "@id": f"{self.site_url}/#editorial-author",
            "name": f"Ban Kỹ Thuật {self.site_name}",
            "jobTitle": "Senior AI & Software Engineering Advisor",
            "url": f"{self.site_url}/",
            "knowsAbout": ["Artificial Intelligence", "Software Engineering", "System Troubleshooting", "Automation"],
        }

    def extract_faq_items(self, html_content: str) -> List[Dict[str, str]]:
        """Extracts Q&A pairs from HTML."""
        if not html_content or not isinstance(html_content, str):
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        faq_items = []

        faq_container = soup.find("div", class_="faq-section")
        if faq_container:
            for p in faq_container.find_all("p"):
                strong = p.find("strong")
                if strong:
                    q_text = strong.get_text().strip().lstrip("0123456789. :")
                    full_text = p.get_text()
                    a_text = full_text.replace(strong.get_text(), "").strip()
                    if q_text and a_text:
                        faq_items.append({"question": q_text, "answer": a_text})

        return faq_items

    def generate_schema_graph(self, post_data: Dict[str, Any], include_faq_schema: bool = False) -> str:
        """Constructs a complete Schema.org @graph JSON-LD string with GEO Entity Linking & Speakable."""
        post_url = post_data.get("link", f"{self.site_url}/{post_data.get('slug', '')}/")

        title = post_data.get("title", "")
        if isinstance(title, dict):
            title = title.get("rendered", "")

        excerpt = post_data.get("excerpt", "")
        if isinstance(excerpt, dict):
            excerpt = excerpt.get("rendered", "")

        featured_image = post_data.get("featured_image_url", f"{self.site_url}/wp-content/uploads/featured.jpg")
        date_published = post_data.get("date", "2026-09-02T00:00:00+07:00")
        date_modified = post_data.get("modified", date_published)

        html_content = post_data.get("content", "")
        if isinstance(html_content, dict):
            html_content = html_content.get("rendered", "")

        author_entity = post_data.get("author_entity") or self._resolve_niche_author()
        plain_words = re.sub(r"<[^>]+>", " ", html_content or "").split()

        article_node: Dict[str, Any] = {
            "@type": "Article",
            "@id": f"{post_url}#article",
            "isPartOf": {"@id": f"{self.site_url}/#website"},
            "headline": title,
            "description": excerpt,
            "url": post_url,
            "mainEntityOfPage": post_url,
            "datePublished": date_published,
            "dateModified": date_modified,
            "image": featured_image,
            "inLanguage": "en-US" if self.lang.startswith("en") else "vi-VN",
            "isAccessibleForFree": True,
            "wordCount": len(plain_words),
            "publisher": {"@id": f"{self.site_url}/#organization"},
            "author": author_entity,
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": [".entry-title", ".geo-quotable-summary", "article p:first-of-type"],
            },
        }

        # Attach Wikidata Knowledge Graph entities (`about` for title matches, `mentions` for body matches)
        title_entities = self.entity_linker.extract_entities(title)
        body_entities = self.entity_linker.extract_entities(f"{title} {html_content}")
        if title_entities:
            article_node["about"] = title_entities[:3]
        if body_entities:
            article_node["mentions"] = body_entities[:8]

        citations = self.entity_linker.extract_authoritative_citations(html_content)
        if citations:
            article_node["citation"] = citations

        graph = [
            {
                "@type": "WebSite",
                "@id": f"{self.site_url}/#website",
                "url": self.site_url,
                "name": self.site_name,
                "publisher": {
                    "@type": "Organization",
                    "@id": f"{self.site_url}/#organization",
                    "name": self.publisher_name,
                    "logo": {
                        "@type": "ImageObject",
                        "url": self.logo_url,
                    },
                },
            },
            article_node,
            {
                "@type": "BreadcrumbList",
                "@id": f"{post_url}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home" if self.lang.startswith("en") else "Trang Chủ",
                        "item": self.site_url,
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": title,
                        "item": post_url,
                    },
                ],
            },
        ]

        if include_faq_schema:
            faqs = self.extract_faq_items(html_content)
            if faqs:
                faq_schema = {
                    "@type": "FAQPage",
                    "@id": f"{post_url}#faq",
                    "mainEntity": [],
                }
                for item in faqs:
                    faq_schema["mainEntity"].append(
                        {
                            "@type": "Question",
                            "name": item["question"],
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": item["answer"],
                            },
                        }
                    )
                graph.append(faq_schema)

        schema_payload = {
            "@context": "https://schema.org",
            "@graph": graph,
        }

        return f'<script type="application/ld+json">\n{json.dumps(schema_payload, indent=2, ensure_ascii=False)}\n</script>'
