"""
Content Freshness & Evergreen Refresh Engine
Scans older posts, injects recent insights, updates modified timestamps and triggers re-indexing.
"""

from datetime import datetime, timezone
import requests
from typing import Dict, Any, List

class ContentRefresher:
    def __init__(self, wp_session: requests.Session, wp_base_url: str, nonce: str):
        self.session = wp_session
        self.base_url = wp_base_url.rstrip("/")
        self.nonce = nonce

    def refresh_post(self, post_id: int, new_section_html: str) -> Dict[str, Any]:
        """Appends new insights, bumps modified date and saves."""
        r_get = self.session.get(f"{self.base_url}/wp-json/wp/v2/posts/{post_id}")
        if r_get.status_code != 200:
            return {"status": "error", "message": f"Post {post_id} not found"}

        post = r_get.json()
        current_content = post["content"]["rendered"]
        
        updated_content = current_content + f"\n\n<!-- Content Refreshed -->\n{new_section_html}"
        
        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "content": updated_content,
            "modified": now_iso
        }
        
        r_up = self.session.post(
            f"{self.base_url}/wp-json/wp/v2/posts/{post_id}",
            headers={"X-WP-Nonce": self.nonce},
            json=payload,
            timeout=25
        )
        
        return {
            "post_id": post_id,
            "status": "success" if r_up.status_code == 200 else "failed",
            "modified_time": now_iso
        }
