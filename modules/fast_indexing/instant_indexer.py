"""
Instant Indexer Module (Google Indexing API & Bing IndexNow)
Supports immediate URL submission to search engine bots within minutes of publication.
"""

import os
import sys
import json
import time
import requests
import hashlib
from typing import List, Dict, Any, Optional

class InstantIndexer:
    def __init__(self, host: str, indexnow_key: Optional[str] = None, google_credentials_path: Optional[str] = None):
        self.host = host.replace("https://", "").replace("http://", "").strip("/ ")
        self.indexnow_key = indexnow_key or self._generate_or_get_default_key()
        self.google_credentials_path = google_credentials_path
        
    def _generate_or_get_default_key(self) -> str:
        """Generates a deterministic 32-char hex IndexNow key based on host."""
        return hashlib.md5(f"indexnow_key_{self.host}".encode("utf-8")).hexdigest()

    def submit_bing_indexnow(self, url_list: List[str]) -> Dict[str, Any]:
        """
        Submits a batch of URLs to the Bing IndexNow API.
        IndexNow notifies Bing, Yandex, Naver, and Seznam simultaneously.
        """
        if not url_list:
            return {"status": "skipped", "message": "URL list is empty"}

        payload = {
            "host": self.host,
            "key": self.indexnow_key,
            "keyLocation": f"https://{self.host}/{self.indexnow_key}.txt",
            "urlList": url_list
        }
        
        headers = {"Content-Type": "application/json; charset=utf-8"}
        
        endpoints = [
            "https://api.indexnow.org/indexnow",
            "https://www.bing.com/indexnow"
        ]
        
        results = {}
        for ep in endpoints:
            try:
                r = requests.post(ep, json=payload, headers=headers, timeout=15)
                success = r.status_code in [200, 202]
                results[ep] = {
                    "status_code": r.status_code,
                    "success": success,
                    "response": r.text[:200] if r.text else "OK"
                }
            except Exception as e:
                results[ep] = {"error": str(e), "success": False}
                
        return {
            "service": "Bing IndexNow",
            "total_urls": len(url_list),
            "results": results
        }

    def submit_google_indexing(self, url: str, action: str = "URL_UPDATED") -> Dict[str, Any]:
        """
        Submits a URL to the Google Indexing API using OAuth2 Service Account credentials.
        """
        if not self.google_credentials_path or not os.path.exists(self.google_credentials_path):
            return {
                "service": "Google Indexing API",
                "status": "config_missing",
                "message": "Google Service Account credentials JSON not provided or not found."
            }

        try:
            from google.oauth2 import service_account
            import google.auth.transport.requests

            SCOPES = ["https://www.googleapis.com/auth/indexing"]
            creds = service_account.Credentials.from_service_account_file(
                self.google_credentials_path, scopes=SCOPES
            )
            request = google.auth.transport.requests.Request()
            creds.refresh(request)
            
            endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {creds.token}"
            }
            body = {
                "url": url,
                "type": action
            }
            
            r = requests.post(endpoint, json=body, headers=headers, timeout=15)
            return {
                "service": "Google Indexing API",
                "url": url,
                "status_code": r.status_code,
                "success": r.status_code == 200,
                "response": r.json() if r.status_code == 200 else r.text[:200]
            }
        except Exception as e:
            return {
                "service": "Google Indexing API",
                "status": "error",
                "error": str(e)
            }

    def index_all(self, url_list: List[str]) -> Dict[str, Any]:
        """Runs both Bing IndexNow and Google Indexing on the URL list."""
        bing_res = self.submit_bing_indexnow(url_list)
        google_res = []
        for u in url_list:
            google_res.append(self.submit_google_indexing(u))
            
        return {
            "host": self.host,
            "bing_indexnow": bing_res,
            "google_indexing": google_res
        }
