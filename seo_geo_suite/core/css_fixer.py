import os
import re
import subprocess
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class CssFixer:
    """Audits, fixes, and optimizes CSS rules, responsive layouts, and overflow bugs."""

    def check_css_string(self, css_content: str) -> Dict[str, Any]:
        """Checks CSS for common mistakes, vendor prefixes, and z-index issues."""
        issues = []
        recommendations = []

        # Check for !important overusage
        important_count = len(re.findall(r"!important", css_content, re.I))
        if important_count > 5:
            issues.append(f"Phát hiện quá nhiều '!important' ({important_count} lần) gây khó khăn trong việc ghi đè class.")
            recommendations.append("Hãy tăng tính đặc hiệu của selector (CSS specificity) thay vì lạm dụng !important.")

        # Check for fixed pixel widths that break mobile responsiveness
        large_fixed_widths = re.findall(r"width:\s*([6-9]\d{2}|[1-9]\d{3,})px", css_content)
        if large_fixed_widths:
            issues.append(f"Có {len(large_fixed_widths)} giá trị width cố định lớn (>600px) có nguy cơ gây vỡ layout mobile.")
            recommendations.append("Sử dụng 'max-width: 100%' hoặc đơn vị linh hoạt như 'rem', '%', 'vw'.")

        # Check for extreme z-index values
        extreme_z = re.findall(r"z-index:\s*([1-9]\d{4,})", css_content)
        if extreme_z:
            issues.append(f"Có z-index cực đại (z-index: {extreme_z[0]}) dễ gây lỗi chồng chéo modal/menu.")
            recommendations.append("Chuẩn hóa z-index theo thang: 10 (dropdown), 20 (sticky header), 50 (modal), 100 (toast).")

        # Basic syntax checks (mismatched braces)
        open_braces = css_content.count("{")
        close_braces = css_content.count("}")
        if open_braces != close_braces:
            issues.append(f"Lỗi cú pháp: Số dấu mở '{{' ({open_braces}) không khớp với số dấu đóng '}}' ({close_braces}).")

        return {
            "status": "checked",
            "total_rules_estimate": len(re.findall(r"\{[^}]+\}", css_content)),
            "important_count": important_count,
            "issues": issues,
            "recommendations": recommendations
        }

    def audit_html_layout_and_responsive(self, html_content: str) -> Dict[str, Any]:
        """Detects mobile responsiveness and layout issues in HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        issues = []
        recommendations = []

        # 1. Viewport meta
        viewport = soup.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
        if not viewport or "width=device-width" not in viewport.get("content", ""):
            issues.append("Thiếu thẻ meta viewport chuẩn 'width=device-width, initial-scale=1.0'.")
            recommendations.append("Thêm <meta name='viewport' content='width=device-width, initial-scale=1.0'> vào thẻ <head>.")

        # 2. Images without max-width responsive style
        images = soup.find_all("img")
        fixed_size_imgs = 0
        for img in images:
            w = img.get("width")
            style = img.get("style", "")
            if w and int(w) > 400 and "max-width" not in style:
                fixed_size_imgs += 1
        if fixed_size_imgs > 0:
            issues.append(f"Có {fixed_size_imgs} hình ảnh có chiều rộng lớn nhưng chưa có CSS 'max-width: 100%; height: auto'.")

        # 3. Check for inline styles
        inline_elements = soup.find_all(style=True)
        if len(inline_elements) > 10:
            issues.append(f"Phát hiện {len(inline_elements)} phần tử sử dụng inline style trực tiếp.")
            recommendations.append("Nên chuyển inline styles sang file CSS hoặc class Tailwind để tối ưu tốc độ render.")

        return {
            "viewport_found": bool(viewport),
            "inline_styles_count": len(inline_elements),
            "issues": issues,
            "recommendations": recommendations
        }

    def run_stylelint(self, css_filepath: str) -> Dict[str, Any]:
        """Runs stylelint CLI on a CSS file."""
        if not os.path.exists(css_filepath):
            return {"status": "error", "message": f"File {css_filepath} không tồn tại."}

        cmd = f'npx stylelint "{css_filepath}" --formatter json'
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            output = res.stdout or res.stderr
            try:
                lint_data = json.loads(output)
                return {"status": "success", "results": lint_data}
            except Exception:
                return {"status": "completed", "raw_output": output}
        except Exception as e:
            return {"status": "error", "error": str(e)}
