"""
Omnichannel Social Auto-Syndication Module
Automatically publishes viral teasers and social signals to Telegram Channels, Discord and Webhooks.
"""

import requests
from typing import Dict, Any, Optional

class SocialAutoPoster:
    def __init__(self, telegram_bot_token: Optional[str] = None, telegram_chat_id: Optional[str] = None, webhook_url: Optional[str] = None):
        self.tg_token = telegram_bot_token
        self.tg_chat_id = telegram_chat_id
        self.webhook_url = webhook_url

    def post_to_telegram(self, title: str, summary: str, post_url: str, tags: Optional[list] = None) -> Dict[str, Any]:
        """Broadcasts a new post notification with inline link button to a Telegram Channel."""
        if not self.tg_token or not self.tg_chat_id:
            return {"status": "skipped", "message": "Telegram credentials not configured."}

        tag_str = " ".join([f"#{t.replace(' ', '')}" for t in (tags or ["AutoSEO", "TechNews"])])
        message = (
            f"🔥 <b>{title}</b>\n\n"
            f"📖 {summary}\n\n"
            f"🔗 Đọc bài viết đầy đủ tại: {post_url}\n\n"
            f"{tag_str}"
        )
        
        api_url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
        payload = {
            "chat_id": self.tg_chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        
        try:
            r = requests.post(api_url, json=payload, timeout=15)
            return {"status": "success" if r.status_code == 200 else "failed", "response": r.json()}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def trigger_webhook(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Triggers Make.com, Zapier or Discord webhook for multi-platform broadcasting."""
        if not self.webhook_url:
            return {"status": "skipped", "message": "Webhook URL not configured."}

        try:
            r = requests.post(self.webhook_url, json=post_data, timeout=15)
            return {"status": "success" if r.status_code in [200, 204] else "failed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
