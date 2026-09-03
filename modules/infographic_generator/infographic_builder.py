"""
AI Visual Infographic & Data Chart Synthesizer
Generates lightweight SVG/HTML technical data infographics with dark cyber aesthetic,
and provides embeddable backlink attribution code snippets for natural backlink magnet acquisition.
"""

import html
from typing import Dict, List, Any

class InfographicBuilder:
    def __init__(self, brand_name: str = "Master-SEO-Suite"):
        self.brand_name = brand_name

    def generate_benchmark_infographic_html(self, title: str, metrics: List[Dict[str, Any]], source_url: str) -> str:
        """
        Generates an SVG/HTML technical data card with embed code snippet.
        """
        rows_html = ""
        for m in metrics:
            label = m.get("label", "")
            val1 = m.get("manual", "N/A")
            val2 = m.get("automated", "N/A")
            pct = m.get("improvement_pct", 85)
            
            rows_html += f"""
            <div style="margin-bottom:14px;">
              <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.9em;">
                <span style="color:#e2e8f0; font-weight:500;">{label}</span>
                <span style="color:#38bdf8; font-weight:bold;">Tối ưu +{pct}%</span>
              </div>
              <div style="background:#1e293b; height:10px; border-radius:5px; overflow:hidden; display:flex;">
                <div style="background:#ef4444; width:{100-pct}%; height:100%;"></div>
                <div style="background:#38bdf8; width:{pct}%; height:100%;"></div>
              </div>
              <div style="display:flex; justify-content:space-between; margin-top:3px; font-size:0.75em; color:#94a3b8;">
                <span>Cũ: {val1}</span>
                <span style="color:#4ade80;">Hệ thống AI 2026: {val2}</span>
              </div>
            </div>
            """

        embed_code = f'&lt;a href="{source_url}"&gt;&lt;img src="{source_url}infographic.webp" alt="{html.escape(title)}" /&gt;&lt;/a&gt;&lt;p&gt;Nguồn dữ liệu: &lt;a href="{source_url}"&gt;{self.brand_name}&lt;/a&gt;&lt;/p&gt;'

        return f"""
<div class="technical-infographic-card" style="background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:24px; margin:36px 0; color:#f8fafc; font-family:system-ui, sans-serif; box-shadow:0 10px 25px -5px rgba(0,0,0,0.3);">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:18px; border-bottom:1px solid #1e293b; padding-bottom:12px;">
    <div>
      <span style="background:#0284c7; color:#fff; font-size:0.72em; padding:2px 8px; border-radius:12px; font-weight:bold; letter-spacing:0.5px;">DATA INFOGRAPHIC</span>
      <h3 style="margin:8px 0 0 0; font-size:1.18em; color:#fff;">{title}</h3>
    </div>
    <span style="font-size:0.8em; color:#64748b; font-weight:600;">// {self.brand_name}</span>
  </div>

  <div style="margin:20px 0;">
    {rows_html}
  </div>

  <div style="background:#0b1120; border:1px dashed #334155; border-radius:6px; padding:12px; margin-top:20px;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
      <span style="font-size:0.78em; color:#94a3b8; font-weight:500;">📋 Nhúng biểu đồ này vào website của bạn (Kèm Link Nguồn):</span>
    </div>
    <textarea readonly style="width:100%; height:42px; background:#1e293b; color:#94a3b8; font-family:monospace; font-size:0.75em; border:1px solid #334155; border-radius:4px; padding:6px; resize:none;" onclick="this.select()">{embed_code}</textarea>
  </div>
</div>
"""
