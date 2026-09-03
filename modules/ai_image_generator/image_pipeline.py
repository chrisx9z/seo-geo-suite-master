"""
AI Featured Image Generator Pipeline
Generates 16:9 1200x675 high-definition graphics, converts to WebP and handles WP Media upload.
"""

import os
import requests
from typing import Dict, Any, Optional

class FeaturedImagePipeline:
    def __init__(self, wp_base_url: str, auth_session: Optional[requests.Session] = None):
        self.wp_base_url = wp_base_url.rstrip("/")
        self.session = auth_session or requests.Session()

    def generate_image_prompt(self, post_title: str, topic_category: str) -> str:
        """Extracts visual prompt for 3D Cyberpunk tech banner."""
        return (
            f"Futuristic 3D digital illustration representing: {post_title}. "
            f"Themes: {topic_category}, neon glowing circuits, hyper-detailed cyberpunk aesthetic, "
            f"16:9 wide aspect ratio, 8k resolution, photorealistic cinematic lighting, ultra-clean design."
        )

    def upload_to_wordpress(self, image_path: str, post_title: str, nonce: str) -> Optional[int]:
        """Uploads a local image file to the WordPress REST API Media library."""
        if not os.path.exists(image_path):
            return None

        filename = os.path.basename(image_path)
        url = f"{self.wp_base_url}/wp-json/wp/v2/media"
        
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/webp" if filename.endswith(".webp") else "image/jpeg",
            "X-WP-Nonce": nonce
        }
        
        with open(image_path, "rb") as img_file:
            r = self.session.post(url, headers=headers, data=img_file, timeout=40)
            if r.status_code in [200, 201]:
                media_data = r.json()
                media_id = media_data.get("id")
                # Update Alt text and Title
                self.session.post(
                    f"{url}/{media_id}",
                    headers={"X-WP-Nonce": nonce},
                    json={"alt_text": post_title, "title": post_title}
                )
                return media_id
        return None
