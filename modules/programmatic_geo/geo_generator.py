"""
Programmatic Multi-Location GEO Engine
Generates hyper-localized landing pages and articles targeting regions/cities,
with automated GPS coordinates, postal codes, and local business schema.
"""

from typing import Dict, List, Any

VIETNAM_PROVINCES = [
    {"city": "Hà Nội", "slug": "ha-noi", "lat": 21.0285, "lng": 105.8542, "postal": "100000", "region": "Miền Bắc"},
    {"city": "TP. Hồ Chí Minh", "slug": "ho-chi-minh", "lat": 10.8231, "lng": 106.6297, "postal": "700000", "region": "Miền Nam"},
    {"city": "Đà Nẵng", "slug": "da-nang", "lat": 16.0544, "lng": 108.2022, "postal": "550000", "region": "Miền Trung"},
    {"city": "Cần Thơ", "slug": "can-tho", "lat": 10.0452, "lng": 105.7469, "postal": "900000", "region": "Tây Nam Bộ"},
    {"city": "Hải Phòng", "slug": "hai-phong", "lat": 20.8449, "lng": 106.6881, "postal": "180000", "region": "Miền Bắc"}
]

class ProgrammaticGeoEngine:
    def __init__(self):
        self.provinces = VIETNAM_PROVINCES

    def generate_localized_landing_data(self, service_name: str, province_slug: str) -> Dict[str, Any]:
        """Generates hyper-localized content package and LocalBusiness Schema."""
        loc = next((p for p in self.provinces if p["slug"] == province_slug), self.provinces[0])

        title = f"{service_name} Tại {loc['city']} (Chuẩn Quốc Tế, Uy Tín 2026)"
        slug = f"{service_name.lower().replace(' ', '-')}-{loc['slug']}"

        schema_local = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": f"{service_name} - Chi Nhánh {loc['city']}",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": loc["city"],
                "addressRegion": loc["region"],
                "postalCode": loc["postal"],
                "addressCountry": "VN"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": loc["lat"],
                "longitude": loc["lng"]
            }
        }

        return {
            "title": title,
            "slug": slug,
            "location": loc,
            "schema_json": schema_local
        }
