"""
Rich Snippets & GEO Schema Generator
Generates multi-entity JSON-LD (FAQPage, NewsArticle, BreadcrumbList, Knowledge Entities).
"""

import json
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional

class RichSnippetsGenerator:
    def __init__(self, site_name: str, site_url: str, publisher_name: str, logo_url: str):
        self.site_name = site_name
        self.site_url = site_url.rstrip("/")
        self.publisher_name = publisher_name
        self.logo_url = logo_url

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

    def generate_schema_graph(self, post_data: Dict[str, Any]) -> str:
        """Constructs a complete Schema.org @graph JSON-LD string."""
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
                        "url": self.logo_url
                    }
                }
            },
            {
                "@type": "NewsArticle",
                "@id": f"{post_url}#article",
                "isPartOf": {"@id": f"{self.site_url}/#website"},
                "headline": title,
                "description": excerpt,
                "url": post_url,
                "mainEntityOfPage": post_url,
                "datePublished": date_published,
                "dateModified": date_modified,
                "image": featured_image,
                "publisher": {"@id": f"{self.site_url}/#organization"},
                "author": {
                    "@type": "Person",
                    "name": "Admin Master SEO",
                    "jobTitle": "Senior AI & SEO Engineer"
                }
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{post_url}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Trang Chủ",
                        "item": self.site_url
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": title,
                        "item": post_url
                    }
                ]
            }
        ]

        faqs = self.extract_faq_items(html_content)
        if faqs:
            faq_schema = {
                "@type": "FAQPage",
                "@id": f"{post_url}#faq",
                "mainEntity": []
            }
            for item in faqs:
                faq_schema["mainEntity"].append({
                    "@type": "Question",
                    "name": item["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item["answer"]
                    }
                })
            graph.append(faq_schema)

        schema_payload = {
            "@context": "https://schema.org",
            "@graph": graph
        }
        
        return f'<script type="application/ld+json">\n{json.dumps(schema_payload, indent=2, ensure_ascii=False)}\n</script>'
