"""
Google News & Discover XML Sitemap Engine
Generates standard <news:news> XML feeds for articles published in the last 48 hours.
"""

from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

class NewsSitemapGenerator:
    def __init__(self, publication_name: str, language: str = "vi"):
        self.pub_name = publication_name
        self.language = language

    def generate_xml(self, recent_posts: List[Dict[str, Any]]) -> str:
        """Constructs Google News standard XML sitemap."""
        urlset = ET.Element("urlset", {
            "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "xmlns:news": "http://www.google.com/schemas/sitemap-news/0.9"
        })

        for p in recent_posts:
            url_el = ET.SubElement(urlset, "url")
            
            loc = ET.SubElement(url_el, "loc")
            loc.text = p.get("link", "")
            
            news = ET.SubElement(url_el, "news:news")
            
            pub = ET.SubElement(news, "news:publication")
            p_name = ET.SubElement(pub, "news:name")
            p_name.text = self.pub_name
            p_lang = ET.SubElement(pub, "news:language")
            p_lang.text = self.language
            
            pub_date = ET.SubElement(news, "news:publication_date")
            pub_date.text = p.get("date_gmt", datetime.now(timezone.utc).isoformat())
            
            title = ET.SubElement(news, "news:title")
            title.text = p.get("title", {}).get("rendered", "") if isinstance(p.get("title"), dict) else str(p.get("title", ""))

        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        return xml_declaration + ET.tostring(urlset, encoding="utf-8").decode("utf-8")
