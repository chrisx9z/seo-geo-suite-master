import os
import json
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, List

class AssetBuilder:
    """Generates modern SEO/GEO Web Components (Header, Footer, Menu, Breadcrumbs) and optimizes image assets."""

    def generate_menu_component(self, brand_name: str = "MyBrand", menu_items: List[Dict[str, str]] = None) -> str:
        if not menu_items:
            menu_items = [
                {"label": "Trang Chủ", "url": "/"},
                {"label": "Dịch Vụ & Giải Pháp", "url": "/dich-vu"},
                {"label": "Kiến Thức & Tin Tức", "url": "/bai-viet"},
                {"label": "Về Chúng Tôi", "url": "/gioi-thieu"},
                {"label": "Liên Hệ", "url": "/lien-he"}
            ]

        items_html = "\n".join([
            f'        <li><a href="{it["url"]}" class="text-gray-700 hover:text-blue-600 font-medium transition-colors">{it["label"]}</a></li>'
            for it in menu_items
        ])

        mobile_items_html = "\n".join([
            f'      <a href="{it["url"]}" class="block px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg">{it["label"]}</a>'
            for it in menu_items
        ])

        return f"""<!-- HEADER & NAVIGATION COMPONENT (Tailwind CSS + SEO Schema) -->
<header class="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-100 shadow-sm" itemscope itemtype="https://schema.org/SiteNavigationElement">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <!-- Brand Logo -->
      <div class="flex items-center gap-3">
        <a href="/" class="flex items-center gap-2" title="{brand_name}">
          <span class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">{brand_name}</span>
        </a>
      </div>

      <!-- Desktop Navigation Menu -->
      <nav class="hidden md:flex items-center gap-8">
        <ul class="flex items-center gap-6 list-none m-0 p-0">
{items_html}
        </ul>
        <a href="/lien-he" class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-xl shadow-md transition-all">Bắt Đầu Ngay</a>
      </nav>

      <!-- Mobile Hamburger Button -->
      <div class="md:hidden flex items-center">
        <button id="mobile-menu-btn" aria-label="Mở menu điều hướng" class="p-2 rounded-lg text-gray-600 hover:bg-gray-100">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Mobile Drawer Menu -->
  <div id="mobile-menu" class="hidden md:hidden px-4 pt-2 pb-4 space-y-1 bg-white border-b border-gray-200">
{mobile_items_html}
  </div>
</header>
<script>
  document.getElementById('mobile-menu-btn')?.addEventListener('click', () => {{
    document.getElementById('mobile-menu')?.classList.toggle('hidden');
  }});
</script>
"""

    def generate_footer_component(self, brand_name: str = "MyBrand", description: str = "Giải pháp chuyển đổi số và tối ưu SEO/GEO toàn diện.") -> str:
        return f"""<!-- FOOTER COMPONENT (SEO & Schema.org Organization) -->
<footer class="bg-slate-900 text-gray-300 pt-16 pb-12 border-t border-slate-800" itemscope itemtype="https://schema.org/WPFooter">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">
      
      <!-- Brand & Organization Schema -->
      <div class="space-y-4" itemscope itemtype="https://schema.org/Organization">
        <span class="text-2xl font-bold text-white" itemprop="name">{brand_name}</span>
        <p class="text-sm text-gray-400 leading-relaxed" itemprop="description">{description}</p>
        <div class="flex gap-4 pt-2">
          <a href="#" aria-label="Facebook" class="w-9 h-9 flex items-center justify-center rounded-lg bg-slate-800 hover:bg-blue-600 text-gray-300 hover:text-white transition-all">f</a>
          <a href="#" aria-label="YouTube" class="w-9 h-9 flex items-center justify-center rounded-lg bg-slate-800 hover:bg-red-600 text-gray-300 hover:text-white transition-all">▶</a>
          <a href="#" aria-label="LinkedIn" class="w-9 h-9 flex items-center justify-center rounded-lg bg-slate-800 hover:bg-blue-500 text-gray-300 hover:text-white transition-all">in</a>
        </div>
      </div>

      <!-- Column 2: Giải Pháp & Dịch Vụ -->
      <div>
        <h4 class="text-white font-semibold text-base mb-4">Giải Pháp Cốt Lõi</h4>
        <ul class="space-y-2.5 text-sm list-none p-0">
          <li><a href="/seo-audit" class="hover:text-blue-400 transition-colors">Audit Website & Core Web Vitals</a></li>
          <li><a href="/geo-optimization" class="hover:text-blue-400 transition-colors">Tối Ưu AI Citability (GEO)</a></li>
          <li><a href="/content-marketing" class="hover:text-blue-400 transition-colors">Chiến Lược Content E-E-A-T</a></li>
          <li><a href="/keyword-clustering" class="hover:text-blue-400 transition-colors">Gom Nhóm Từ Khóa Ngữ Nghĩa</a></li>
        </ul>
      </div>

      <!-- Column 3: Tài Nguyên & Liên Kết -->
      <div>
        <h4 class="text-white font-semibold text-base mb-4">Tài Nguyên SEO/GEO</h4>
        <ul class="space-y-2.5 text-sm list-none p-0">
          <li><a href="/llms.txt" class="hover:text-blue-400 transition-colors">File llms.txt Cho AI Crawlers</a></li>
          <li><a href="/sitemap.xml" class="hover:text-blue-400 transition-colors">Sitemap XML</a></li>
          <li><a href="/huong-dan-seo" class="hover:text-blue-400 transition-colors">Cẩm Nang SEO 2026</a></li>
          <li><a href="/chinh-sach-bao-mat" class="hover:text-blue-400 transition-colors">Chính Sách Bảo Mật</a></li>
        </ul>
      </div>

      <!-- Column 4: Đăng Ký Bản Tin -->
      <div class="space-y-3">
        <h4 class="text-white font-semibold text-base mb-2">Nhận Bản Tin Cập Nhật</h4>
        <p class="text-xs text-gray-400">Nhận các mẹo tối ưu hóa GEO và thuật toán AI mới nhất mỗi tuần.</p>
        <form class="flex flex-col gap-2">
          <input type="email" placeholder="Nhập email của bạn..." class="px-3.5 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500">
          <button type="submit" class="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg shadow transition-all">Đăng Ký</button>
        </form>
      </div>

    </div>

    <!-- Copyright & Disclaimer -->
    <div class="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-500 gap-4">
      <p>© 2026 {brand_name}. Tất cả các quyền được bảo lưu.</p>
      <p>Thiết kế chuẩn Responsive, E-E-A-T & Generative Engine Optimization.</p>
    </div>
  </div>
</footer>
"""

    def generate_breadcrumbs(self, items: List[Dict[str, str]]) -> str:
        """Generates HTML breadcrumbs with BreadcrumbList JSON-LD schema."""
        schema_elements = []
        html_links = []
        for idx, item in enumerate(items, 1):
            schema_elements.append({
                "@type": "ListItem",
                "position": idx,
                "name": item["name"],
                "item": item.get("url", "")
            })
            if idx < len(items):
                html_links.append(f'<li><a href="{item["url"]}" class="hover:text-blue-600">{item["name"]}</a><span class="mx-2 text-gray-400">/</span></li>')
            else:
                html_links.append(f'<li class="text-gray-800 font-medium" aria-current="page">{item["name"]}</li>')

        schema_json = json.dumps({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": schema_elements
        }, ensure_ascii=False, indent=2)

        return f"""<!-- BREADCRUMBS WITH JSON-LD SCHEMA -->
<nav aria-label="Breadcrumb" class="py-3 text-sm text-gray-500">
  <ol class="flex flex-wrap items-center list-none p-0 m-0">
    {''.join(html_links)}
  </ol>
</nav>
<script type="application/ld+json">
{schema_json}
</script>
"""

    def convert_image_to_webp(self, input_path: str, output_path: str = None, quality: int = 85) -> str:
        """Converts PNG/JPG to WebP format for fast web delivery."""
        if not output_path:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}.webp"

        with Image.open(input_path) as img:
            img.save(output_path, "WEBP", quality=quality)
        return output_path

    def generate_og_image(self, title: str, subtitle: str = "", brand: str = "Brand", output_path: str = "reports/og-image.png") -> str:
        """Generates a 1200x630 OpenGraph social share card."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        width, height = 1200, 630
        
        # Create image with modern gradient background
        img = Image.new("RGB", (width, height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)

        # Draw decorative gradient accents
        draw.rectangle([(0, 0), (width, 8)], fill=(59, 130, 246))
        draw.rectangle([(60, 60), (200, 64)], fill=(99, 102, 241))

        # Text information
        draw.text((60, 90), brand.upper(), fill=(96, 165, 250))
        draw.text((60, 180), title[:80], fill=(255, 255, 255))
        if subtitle:
            draw.text((60, 320), subtitle[:120], fill=(148, 163, 184))

        draw.text((60, 540), "SEO & GEO Optimized | High Performance", fill=(100, 116, 139))

        img.save(output_path, "PNG")
        return output_path
