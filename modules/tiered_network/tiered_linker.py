"""
Automated Tiered Satellite Network Flow Controller
Orchestrates high-authority, non-reciprocal link pyramids:
Tier 2 (Niche Satellites) -> Tier 1 (High Authority Hubs) -> Money Site.
Strictly controls natural Anchor Text ratios (70% keyword, 20% brand, 10% naked URL).
"""

import random
from typing import Dict, List, Any

class TieredNetworkLinker:
    def __init__(self, network_config: Dict[str, Any]):
        self.network = network_config

    def generate_safe_anchor(self, target_title: str, brand_name: str, target_url: str) -> str:
        """Enforces natural anchor text ratio: 70% longtail keyword, 20% brand, 10% naked URL."""
        rand = random.random()
        if rand < 0.70:
            # Contextual natural keyword
            words = target_title.split()[:4]
            return " ".join(words)
        elif rand < 0.90:
            # Brand anchor
            return brand_name
        else:
            # Naked URL
            return target_url

    def plan_tier_link_injection(self, source_site_tier: str, target_site_tier: str, 
                                 target_post: Dict[str, Any], brand_name: str) -> Dict[str, Any]:
        """
        Validates whether link flow is legitimate under tiered SEO rules:
        - Tier 2 can link to Tier 1
        - Tier 1 can link to Money Site
        - Money Site NEVER links down to satellites
        """
        valid_flows = [
            ("tier_2", "tier_1"),
            ("tier_1", "money_site"),
            ("tier_2", "money_site")
        ]

        if (source_site_tier, target_site_tier) not in valid_flows:
            return {
                "allowed": False,
                "reason": f"Invalid link flow from {source_site_tier} to {target_site_tier}. Upward flow only."
            }

        target_url = target_post.get("link", "")
        target_title = target_post.get("title", {}).get("rendered", "")
        anchor = self.generate_safe_anchor(target_title, brand_name, target_url)

        callout_html = (
            f'<div class="authoritative-source-callout" style="background:#0f172a; border-left:4px solid #38bdf8; padding:14px 18px; margin:24px 0; border-radius:6px;">'
            f'💡 <strong>Tham khảo chuyên sâu:</strong> '
            f'<a href="{target_url}" target="_blank" rel="noopener" style="color:#38bdf8; font-weight:600; text-decoration:underline;">{anchor}</a>.'
            f'</div>'
        )

        return {
            "allowed": True,
            "anchor_text": anchor,
            "target_url": target_url,
            "callout_html": callout_html
        }
