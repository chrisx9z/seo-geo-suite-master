"""
AI Interactive Widget & Calculator Synthesizer
Generates responsive, self-contained HTML5/CSS/JavaScript interactive tools
to embed directly into WordPress posts, dramatically boosting Time-on-Page (3-5 mins).
"""

from typing import Dict, Any

class InteractiveWidgetGenerator:
    def __init__(self):
        pass

    def generate_gpu_vram_calculator(self) -> str:
        """Interactive Calculator for GPU VRAM Requirements & Inference Cost."""
        return """
<div class="interactive-seo-widget" style="background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:24px; margin:32px 0; color:#f8fafc; font-family:system-ui, sans-serif; box-shadow:0 10px 25px -5px rgba(0,0,0,0.3);">
  <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
    <span style="font-size:24px;">🧮</span>
    <div>
      <h3 style="margin:0; font-size:1.2em; color:#38bdf8;">Bảng Tính Dung Lượng VRAM & Chi Phí Thuê GPU Theo Giờ</h3>
      <p style="margin:4px 0 0 0; font-size:0.88em; color:#94a3b8;">Công cụ định lượng tài nguyên chạy LLM (Qwen, DeepSeek, Llama-3)</p>
    </div>
  </div>

  <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:20px;">
    <div>
      <label style="display:block; font-size:0.85em; color:#cbd5e1; margin-bottom:6px;">Số Lượng Tham Số (Billion Parameters):</label>
      <select id="gpu_params" onchange="calcGpuVram()" style="width:100%; background:#1e293b; color:#fff; border:1px solid #334155; padding:10px; border-radius:6px;">
        <option value="7">7B Parameters</option>
        <option value="14">14B Parameters</option>
        <option value="27" selected>27B - 32B Parameters (Qwen 2.5 / 3.8)</option>
        <option value="70">70B Parameters (Llama-3 70B)</option>
      </select>
    </div>

    <div>
      <label style="display:block; font-size:0.85em; color:#cbd5e1; margin-bottom:6px;">Định Dạng Lượng Tử Hóa (Quantization):</label>
      <select id="gpu_quant" onchange="calcGpuVram()" style="width:100%; background:#1e293b; color:#fff; border:1px solid #334155; padding:10px; border-radius:6px;">
        <option value="16">FP16 / BF16 (16-bit)</option>
        <option value="8">Q8 / Int8 (8-bit)</option>
        <option value="4" selected>Q4_K_M / AWQ (4-bit)</option>
        <option value="3">IQ3 / GGUF (3-bit Superfast)</option>
      </select>
    </div>
  </div>

  <div style="background:#1e293b; padding:16px; border-radius:8px; border-left:4px solid #38bdf8;">
    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
      <span style="color:#94a3b8;">Dung Lượng VRAM Tối Thiểu Cần Thiết:</span>
      <strong id="res_vram" style="color:#38bdf8; font-size:1.15em;">14.2 GB VRAM</strong>
    </div>
    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
      <span style="color:#94a3b8;">Card Đồ Họa Đề Xuất Phù Hợp:</span>
      <strong id="res_card" style="color:#4ade80;">RTX 4080 (16GB) / RTX 3090 (24GB)</strong>
    </div>
    <div style="display:flex; justify-content:space-between;">
      <span style="color:#94a3b8;">Chi Phí Thuê Cloud GPU Ước Tính:</span>
      <strong id="res_cost" style="color:#facc15;">~$0.22 - $0.35 / Giờ (RunPod / Vast.ai)</strong>
    </div>
  </div>

  <script>
    function calcGpuVram() {
      var params = parseFloat(document.getElementById('gpu_params').value);
      var bits = parseFloat(document.getElementById('gpu_quant').value);
      var modelBytes = params * (bits / 8);
      var contextOverhead = 2.5; // KV cache buffer
      var totalVram = (modelBytes * 1.15 + contextOverhead).toFixed(1);
      
      document.getElementById('res_vram').innerText = totalVram + " GB VRAM";
      
      var card = "RTX 4060 Ti (16GB)";
      var cost = "~$0.15 - $0.20 / Giờ";
      if (totalVram > 40) {
        card = "A100 (80GB) hoặc 2x RTX 3090";
        cost = "~$1.20 - $1.80 / Giờ";
      } else if (totalVram > 20) {
        card = "RTX 3090 / 4090 (24GB)";
        cost = "~$0.35 - $0.55 / Giờ";
      } else if (totalVram > 12) {
        card = "RTX 4080 (16GB) / RTX 3090 (24GB)";
        cost = "~$0.22 - $0.35 / Giờ";
      }
      document.getElementById('res_card').innerText = card;
      document.getElementById('res_cost').innerText = cost;
    }
  </script>
</div>
"""

    def generate_futures_risk_calculator(self) -> str:
        """Interactive Calculator for Crypto Futures Position Size & Liquidation Risk."""
        return """
<div class="interactive-seo-widget" style="background:#0b1329; border:1px solid #1d283a; border-radius:12px; padding:24px; margin:32px 0; color:#f8fafc; font-family:system-ui, sans-serif; box-shadow:0 10px 25px -5px rgba(0,0,0,0.3);">
  <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
    <span style="font-size:24px;">📈</span>
    <div>
      <h3 style="margin:0; font-size:1.2em; color:#10b981;">Bảng Tính Quản Lý Rủi Ro Vị Thế & Đòn Bẩy Futures</h3>
      <p style="margin:4px 0 0 0; font-size:0.88em; color:#94a3b8;">Tính khối lượng vào lệnh (Position Size) bảo toàn vốn theo quy tắc 1%</p>
    </div>
  </div>

  <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:16px; margin-bottom:20px;">
    <div>
      <label style="display:block; font-size:0.85em; color:#cbd5e1; margin-bottom:6px;">Tổng Vốn Tài Khoản ($):</label>
      <input type="number" id="trade_capital" value="1000" oninput="calcFuturesRisk()" style="width:100%; background:#1e293b; color:#fff; border:1px solid #334155; padding:10px; border-radius:6px;" />
    </div>
    <div>
      <label style="display:block; font-size:0.85em; color:#cbd5e1; margin-bottom:6px;">Rủi Ro Chấp Nhận / Lệnh (%):</label>
      <input type="number" id="trade_risk_pct" value="1.5" step="0.5" oninput="calcFuturesRisk()" style="width:100%; background:#1e293b; color:#fff; border:1px solid #334155; padding:10px; border-radius:6px;" />
    </div>
    <div>
      <label style="display:block; font-size:0.85em; color:#cbd5e1; margin-bottom:6px;">Khoảng Cách Cắt Lỗ (Stop-Loss %):</label>
      <input type="number" id="trade_sl_pct" value="2.0" step="0.5" oninput="calcFuturesRisk()" style="width:100%; background:#1e293b; color:#fff; border:1px solid #334155; padding:10px; border-radius:6px;" />
    </div>
  </div>

  <div style="background:#1e293b; padding:16px; border-radius:8px; border-left:4px solid #10b981;">
    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
      <span style="color:#94a3b8;">Số Tiền Tối Đa Có Thể Mất Khi Chạm SL:</span>
      <strong id="res_max_loss" style="color:#ef4444; font-size:1.1em;">$15.00</strong>
    </div>
    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
      <span style="color:#94a3b8;">Quy Mô Vị Thế Được Phép Mở (Position Size):</span>
      <strong id="res_pos_size" style="color:#10b981; font-size:1.15em;">$750.00</strong>
    </div>
    <div style="display:flex; justify-content:space-between;">
      <span style="color:#94a3b8;">Đòn Bẩy Thực Tế (Effective Leverage):</span>
      <strong id="res_leverage" style="color:#38bdf8;">0.75x (Cực Kỳ An Toàn)</strong>
    </div>
  </div>

  <script>
    function calcFuturesRisk() {
      var cap = parseFloat(document.getElementById('trade_capital').value) || 0;
      var riskPct = parseFloat(document.getElementById('trade_risk_pct').value) || 0;
      var slPct = parseFloat(document.getElementById('trade_sl_pct').value) || 0;
      
      var maxLoss = cap * (riskPct / 100);
      var posSize = slPct > 0 ? (maxLoss / (slPct / 100)) : 0;
      var effLev = cap > 0 ? (posSize / cap).toFixed(2) : 0;

      document.getElementById('res_max_loss').innerText = "$" + maxLoss.toFixed(2);
      document.getElementById('res_pos_size').innerText = "$" + posSize.toFixed(2);
      document.getElementById('res_leverage').innerText = effLev + "x (" + (effLev <= 3 ? "Cực Kỳ An Toàn" : (effLev <= 7 ? "Mức Độ Trung Bình" : "Rủi Ro Cao")) + ")";
    }
  </script>
</div>
"""
