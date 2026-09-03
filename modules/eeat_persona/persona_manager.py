"""
Dynamic E-E-A-T Author Persona Manager
Injects verified author credentials, professional bio, and Schema.org Person metadata
to satisfy Google Search Quality Rater Guidelines (Experience, Expertise, Authoritativeness, Trust).
"""

from typing import Dict, Any

PERSONAS = {
    "ai_engineer": {
        "name": "Alex Nguyen",
        "job_title": "Principal AI & Systems Architect",
        "bio": "Kỹ sư trưởng với hơn 10 năm kinh nghiệm trong lĩnh vực kiến trúc mô hình ngôn ngữ lớn (LLM), tối ưu hóa GPU inference và xây dựng hạ tầng AI tự động hóa cao cấp.",
        "avatar": "https://example.com/assets/author_alex.jpg",
        "same_as": [
            "https://github.com/example-author",
            "https://linkedin.com/in/example-author"
        ],
        "knows_about": ["Artificial Intelligence", "Large Language Models", "Quantization", "vLLM", "Distributed Systems"]
    },
    "mmo_strategist": {
        "name": "Marcus Tran",
        "job_title": "Senior Quantitative Trader & Growth Lead",
        "bio": "Chuyên gia cố vấn tài chính định lượng và phát triển hệ sinh thái Micro-SaaS. Đã vận hành các thuật toán giao dịch tự động và chiến lược tiếp thị liên kết đa kênh toàn cầu.",
        "avatar": "https://example.com/assets/author_marcus.jpg",
        "same_as": [
            "https://twitter.com/example_author"
        ],
        "knows_about": ["Quantitative Trading", "Algorithmic Finance", "Digital Marketing", "Micro-SaaS"]
    }
}

class EeatPersonaManager:
    def __init__(self):
        self.personas = PERSONAS

    def get_persona(self, persona_type: str = "ai_engineer") -> Dict[str, Any]:
        return self.personas.get(persona_type, self.personas["ai_engineer"])

    def generate_author_box_html(self, persona_type: str = "ai_engineer") -> str:
        p = self.get_persona(persona_type)
        knows_tags = "".join([f'<span style="background:#1e293b; color:#38bdf8; padding:3px 8px; border-radius:4px; font-size:0.8em; margin-right:6px;">{k}</span>' for k in p["knows_about"][:4]])

        return f"""
<div class="eeat-author-box" style="background:#0b1329; border:1px solid #1e293b; border-left:4px solid #38bdf8; border-radius:10px; padding:20px; margin:36px 0; color:#e2e8f0; font-family:system-ui, sans-serif;">
  <div style="display:flex; align-items:flex-start; gap:16px;">
    <div style="width:60px; height:60px; border-radius:50%; background:linear-gradient(135deg, #38bdf8, #818cf8); display:flex; align-items:center; justify-content:center; font-size:24px; flex-shrink:0; font-weight:bold; color:#0f172a;">
      {p['name'][0]}
    </div>
    <div style="flex:1;">
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
        <h4 style="margin:0; font-size:1.15em; color:#fff;">{p['name']}</h4>
        <span style="background:#059669; color:#fff; font-size:0.75em; padding:2px 6px; border-radius:12px; display:inline-flex; align-items:center; gap:3px;">
          ✓ Verified Expert
        </span>
      </div>
      <p style="margin:0 0 8px 0; font-size:0.88em; color:#94a3b8; font-weight:500;">{p['job_title']}</p>
      <p style="margin:0 0 12px 0; font-size:0.92em; line-height:1.55; color:#cbd5e1;">{p['bio']}</p>
      <div style="display:flex; flex-wrap:wrap; gap:4px; align-items:center;">
        <span style="font-size:0.8em; color:#94a3b8; margin-right:4px;">Lĩnh vực chuyên môn:</span>
        {knows_tags}
      </div>
    </div>
  </div>
</div>
"""

    def generate_person_schema(self, persona_type: str = "ai_engineer") -> Dict[str, Any]:
        p = self.get_persona(persona_type)
        return {
            "@type": "Person",
            "name": p["name"],
            "jobTitle": p["job_title"],
            "description": p["bio"],
            "sameAs": p["same_as"],
            "knowsAbout": p["knows_about"]
        }
