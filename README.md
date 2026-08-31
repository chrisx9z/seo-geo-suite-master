<div align="center">

# ⚡ SEO GEO Suite Master

**🌐 [Tiếng Việt](#-tiếng-việt) &nbsp;|&nbsp; [中文](#-中文) &nbsp;|&nbsp; [English](#-english)**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-chrisx9z-181717?style=for-the-badge&logo=github)](https://github.com/chrisx9z)

> SEO truyền thống + GEO (Generative Engine Optimization) — tối ưu cho cả Google lẫn ChatGPT, Perplexity, Gemini, Claude AI Search.

</div>

---

## 🇻🇳 Tiếng Việt

### Giới Thiệu

**SEO GEO Suite Master** là bộ công cụ Python mã nguồn mở kết hợp **SEO truyền thống** và **GEO (Generative Engine Optimization)** — chiến lược tối ưu hóa nội dung để được trích dẫn bởi các AI tìm kiếm thế hệ mới như ChatGPT Search, Perplexity, Google AI Overviews, Gemini và Claude.

Bộ công cụ bao gồm CLI tương tác, Web Dashboard trực quan, và engine tự động đồng bộ WordPress — tất cả **không cần hardcode bất kỳ thông tin đăng nhập** nào.

---

### 6 Module Cốt Lõi

| # | Module | Chức Năng |
|:-:|:---|:---|
| 1 | **Audit Website & Technical SEO** | Kiểm tra Robots.txt, Sitemap.xml, quyền truy cập AI Bots (GPTBot, ClaudeBot, PerplexityBot), link hỏng |
| 2 | **Kiểm Tra On-page & Schema** | Đánh giá Title, Meta, H1-H6, Canonical, Alt ảnh, JSON-LD Schema, tính điểm GEO Citability |
| 3 | **Viết Bài Chuẩn GEO & SEO** | Sinh bài E-E-A-T với Direct Answer, bảng so sánh, FAQ, Schema JSON-LD, llms.txt |
| 4 | **Kế Hoạch Từ Khóa & Roadmap** | Google Suggest, PAA clustering, Semantic TF-IDF/KMeans, lộ trình 30 ngày |
| 5 | **Tạo Assets & Featured Image** | Tự động sinh ảnh đại diện 1200×630 WebP bằng Pillow, không cần API ngoài |
| 6 | **Sửa Lỗi CSS & Đồng Bộ WP** | Phát hiện lỗi CSS layout, đồng bộ bài viết/ảnh lên WordPress qua REST API |

---

### Khởi Chạy Nhanh

**Cách 1 — Web Dashboard (khuyến nghị):**
```bash
.\run_dashboard.bat
# Mở http://localhost:8000
```

**Cách 2 — Interactive CLI:**
```bash
.\run_cli.bat
```

**Cách 3 — Lệnh trực tiếp:**
```bash
# Phân tích On-page
.\run_cli.bat onpage https://example.com

# Viết bài SEO/GEO mới
.\run_cli.bat write --topic "Chiến lược SEO 2026" --keyword "tối ưu GEO"

# Lập kế hoạch từ khóa
.\run_cli.bat plan --seed "seo content"

# Kiểm tra lỗi CSS
.\run_cli.bat css path/to/style.css
```

---

### Cài Đặt

```bash
git clone https://github.com/chrisx9z/seo-geo-suite-master.git
cd seo-geo-suite-master
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

**Biến môi trường (tùy chọn):**
```bash
# .env (KHÔNG commit file này lên git)
GEMINI_API_KEY=your_key_here
```

---

### Những Gì Đã Học & Cải Tiến

- ✅ URL slug chuẩn `/tu-khoa-chinh/` — bỏ dấu tiếng Việt, viết liền bằng gạch ngang
- ✅ WP REST API nonce phải lấy fresh mỗi session, không tái sử dụng
- ✅ `_elementor_data` là protected meta — chỉ update được qua Elementor AJAX nonce riêng
- ✅ Purge WP Rocket cache sau mỗi thay đổi nội dung
- ✅ Ảnh đại diện: dùng ảnh thật (Wikimedia/Unsplash), không dùng text banner
- ✅ `sync_wp.py`: credentials nhận qua params — không hardcode domain hay mật khẩu
- ✅ `geo_writer.py`: API key đọc từ `os.environ`, không inline trong code

---

## 🇨🇳 中文

### 简介

**SEO GEO Suite Master** 是一套开源 Python 工具，融合**传统 SEO** 与 **GEO（生成式引擎优化）**——专为让内容被 ChatGPT Search、Perplexity、Google AI Overviews、Gemini、Claude 等新一代 AI 搜索引擎引用而设计。

包含交互式命令行（CLI）、可视化 Web 控制台，以及 WordPress 自动同步引擎——**所有凭据均通过参数传入，代码中零硬编码**。

---

### 六大核心模块

| # | 模块 | 功能 |
|:-:|:---|:---|
| 1 | **网站审计 & 技术 SEO** | 检查 Robots.txt、Sitemap.xml、AI Bot 访问权限（GPTBot、ClaudeBot、PerplexityBot）、死链 |
| 2 | **On-page & Schema 检测** | 分析 Title、Meta、H1-H6、Canonical、图片 Alt、JSON-LD Schema，输出 GEO 可引用分数 |
| 3 | **GEO & SEO 文章写作** | 自动生成符合 E-E-A-T 标准的文章，包含直接答案段落、对比表格、FAQ、Schema JSON-LD、llms.txt |
| 4 | **关键词规划 & 路线图** | Google Suggest 抓取、PAA 聚类、语义 TF-IDF/KMeans 分组、30 天内容计划 |
| 5 | **资产生成 & 特色图片** | 用 Pillow 本地生成 1200×630 WebP 特色图，无需外部 API |
| 6 | **CSS 修复 & WP 同步** | 检测 CSS 布局错误，通过 WordPress REST API 同步文章与媒体 |

---

### 快速启动

**方式一 — Web 控制台（推荐）：**
```bash
.\run_dashboard.bat
# 浏览器访问 http://localhost:8000
```

**方式二 — 交互式 CLI：**
```bash
.\run_cli.bat
```

**方式三 — 直接命令：**
```bash
# On-page 分析
.\run_cli.bat onpage https://example.com

# 生成 SEO/GEO 文章
.\run_cli.bat write --topic "2026 SEO 策略" --keyword "GEO 优化"

# 关键词规划
.\run_cli.bat plan --seed "content seo"

# CSS 检查
.\run_cli.bat css path/to/style.css
```

---

### 安装

```bash
git clone https://github.com/chrisx9z/seo-geo-suite-master.git
cd seo-geo-suite-master
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

**环境变量（可选）：**
```bash
# .env（请勿提交至 git）
GEMINI_API_KEY=your_key_here
```

---

### 学习记录与改进

- ✅ URL slug 规范：`/keyword-slug/`，连字符分隔，去除变音符号
- ✅ WP REST API nonce 每次会话重新获取，禁止复用
- ✅ `_elementor_data` 为 protected meta，只能通过 Elementor 专属 AJAX nonce 更新
- ✅ 内容变更后必须清除 WP Rocket 缓存
- ✅ 特色图片：使用真实照片（Wikimedia/Unsplash），禁用文字卡片
- ✅ `sync_wp.py`：凭据通过参数传入，域名与密码不得硬编码
- ✅ `geo_writer.py`：API Key 通过 `os.environ` 读取，禁止内联写死

---

## 🇬🇧 English

### Overview

**SEO GEO Suite Master** is an open-source Python toolkit combining **traditional SEO** with **GEO (Generative Engine Optimization)** — the strategy of optimizing content to be cited by next-generation AI search engines: ChatGPT Search, Perplexity, Google AI Overviews, Gemini, and Claude.

It ships with an interactive CLI, a visual Web Dashboard, and a WordPress REST API sync engine — **zero hardcoded credentials anywhere in the codebase**.

---

### 6 Core Modules

| # | Module | Function |
|:-:|:---|:---|
| 1 | **Website Audit & Technical SEO** | Validates Robots.txt, Sitemap.xml, AI bot access (GPTBot, ClaudeBot, PerplexityBot), broken links |
| 2 | **On-page & Schema Checker** | Scores Title, Meta, H1-H6, Canonical, image Alt, JSON-LD Schema, GEO Citability index |
| 3 | **GEO & SEO Article Writer** | Generates E-E-A-T articles with Direct Answer blocks, comparison tables, FAQ, Schema JSON-LD, llms.txt |
| 4 | **Keyword Planner & Roadmap** | Google Suggest scraping, PAA clustering, semantic TF-IDF/KMeans grouping, 30-day content plan |
| 5 | **Asset Builder & Featured Images** | Local 1200×630 WebP generation via Pillow — no external API required |
| 6 | **CSS Fixer & WP Sync** | Detects layout-breaking CSS, syncs posts & media to WordPress via REST API |

---

### Quick Start

**Option 1 — Web Dashboard (recommended):**
```bash
.\run_dashboard.bat
# Open http://localhost:8000
```

**Option 2 — Interactive CLI:**
```bash
.\run_cli.bat
```

**Option 3 — Direct commands:**
```bash
# Analyze on-page SEO
.\run_cli.bat onpage https://example.com

# Generate a GEO/SEO article
.\run_cli.bat write --topic "SEO Strategy 2026" --keyword "geo optimization"

# Keyword planning
.\run_cli.bat plan --seed "seo content"

# Audit CSS file
.\run_cli.bat css path/to/style.css
```

---

### Installation

```bash
git clone https://github.com/chrisx9z/seo-geo-suite-master.git
cd seo-geo-suite-master
python -m venv venv
venv\Scripts\activate          # Windows / macOS: source venv/bin/activate
pip install -r requirements.txt
```

**Environment variables (optional):**
```bash
# .env  ← DO NOT commit this file
GEMINI_API_KEY=your_key_here
```

---

### Project Structure

```
seo-geo-suite-master/
├── seo_geo_suite/
│   ├── core/
│   │   ├── onpage.py          # On-page SEO + GEO citability analysis
│   │   ├── auditor.py         # Full technical SEO audit
│   │   ├── geo_writer.py      # Gemini-powered article generator
│   │   ├── css_fixer.py       # CSS lint & auto-fix
│   │   ├── asset_builder.py   # Featured image generator (Pillow)
│   │   └── keyword_planner.py # Keyword clustering & slug generator
│   ├── dashboard/
│   │   ├── app.py             # Flask web dashboard
│   │   └── templates/         # Dashboard HTML UI
│   ├── sync_wp.py             # WordPress REST API sync engine
│   ├── cli.py                 # Rich interactive CLI
│   └── __main__.py
├── run_cli.bat                # Windows CLI launcher
├── run_dashboard.bat          # Windows dashboard launcher
├── requirements.txt
└── .gitignore                 # Excludes all credentials & personal data
```

---

### Lessons Learned (Real-world fixes)

- ✅ URL slugs must be `/keyword-slug/` — lowercase, hyphenated, no diacritics
- ✅ WP REST API nonce must be fetched fresh per session — never reused
- ✅ `_elementor_data` is a protected meta key — only writable via Elementor's own AJAX nonce
- ✅ Always purge WP Rocket cache after any content change
- ✅ Featured images: use real photos (Wikimedia/Unsplash), not text-card banners
- ✅ `sync_wp.py`: credentials injected via constructor params — no hardcoded domains or passwords
- ✅ `geo_writer.py`: API key read from `os.environ("GEMINI_API_KEY")` — never inline

---

### Security

- 🔒 No passwords, API keys, or site URLs hardcoded in any source file
- 🔒 All credentials provided at runtime via CLI args or environment variables
- 🔒 `.gitignore` covers `.env`, `config.json`, `secrets.json`, and all credential files

---

<div align="center">

**MIT License** · Made with ❤️ by [chrisx9z](https://github.com/chrisx9z)

</div>
