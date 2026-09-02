import os
import sys
import base64
import requests
import json
from PIL import Image, ImageDraw, ImageFont

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

class WordPressSyncEngine:
    def __init__(self, base_url='', username='', app_password=''):
        self.base_url = base_url.rstrip('/') + '/'
        self.username = username
        self.app_password = app_password
        self.token = base64.b64encode(f'{username}:{app_password}'.encode()).decode() if app_password else ''
        self.headers = {
            'Authorization': f'Basic {self.token}' if self.token else '',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def generate_featured_banner(self, title, site_name='My Website', category='Top List', output_path='reports/temp_banner.webp'):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        w, h = 1200, 630
        img = Image.new('RGB', (w, h), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)
        
        # Load fonts with fallback
        try:
            font_title = ImageFont.truetype("arial.ttf", 36)
            font_sub = ImageFont.truetype("arial.ttf", 22)
            font_footer = ImageFont.truetype("arial.ttf", 18)
        except Exception:
            font_title = ImageFont.load_default()
            font_sub = font_title
            font_footer = font_title

        # Decorative accents
        draw.rectangle([(0, 0), (w, 10)], fill=(59, 130, 246))
        draw.rectangle([(80, 80), (320, 84)], fill=(99, 102, 241))
        
        draw.text((80, 110), f'{site_name.upper()} | {category.upper()}', fill=(96, 165, 250), font=font_sub)
        draw.text((80, 200), title[:70], fill=(255, 255, 255), font=font_title)
        if len(title) > 70:
            draw.text((80, 260), title[70:140], fill=(255, 255, 255), font=font_title)
            
        draw.text((80, 520), f'{site_name} - Powered by SEO & GEO Suite', fill=(148, 163, 184), font=font_footer)
        
        # Save as optimized WebP
        webp_path = os.path.splitext(output_path)[0] + '.webp'
        img.save(webp_path, 'WEBP', quality=88)
        return webp_path

    def upload_media(self, image_path, alt_text=''):
        filename = os.path.basename(image_path)
        with open(image_path, 'rb') as f:
            img_data = f.read()

        upload_headers = {
            'Authorization': self.headers['Authorization'],
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'image/webp',
            'User-Agent': self.headers['User-Agent']
        }
        
        resp = requests.post(f'{self.base_url}media', data=img_data, headers=upload_headers, timeout=30)
        if resp.status_code in [200, 201]:
            media_obj = resp.json()
            media_id = media_obj['id']
            # Update alt text
            if alt_text:
                requests.post(f'{self.base_url}media/{media_id}', json={'alt_text': alt_text}, headers=self.headers)
            return media_id
        return None

    def update_post_featured_media(self, post_id, media_id):
        resp = requests.post(f'{self.base_url}posts/{post_id}', json={'featured_media': media_id}, headers=self.headers)
        return resp.status_code == 200

if __name__ == '__main__':
    engine = WordPressSyncEngine()
    print('WordPress Sync Engine initialized.')
