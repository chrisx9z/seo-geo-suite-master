<div align="center">

# ⚡ SEO GEO Suite Master

**🌐 [Tiếng Việt](#-tiếng-việt) &nbsp;|&nbsp; [中文](#-中文) &nbsp;|&nbsp; [English](#-english)**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-chrisx9z-181717?style=for-the-badge&logo=github)](https://github.com/chrisx9z)

> **Hệ Thống Tự Động Hóa SEO & GEO Toàn Diện** — Kết hợp SEO truyền thống (Google/Bing) và Tối ưu hóa Công cụ Tạo sinh (GEO: ChatGPT Search, Perplexity, Google AI Overviews, Gemini, Claude).

</div>

---

## 🇻🇳 Tiếng Việt

### Giới Thiệu

**SEO GEO Suite Master** là bộ giải pháp toàn diện mã nguồn mở kết hợp **SEO truyền thống** và **GEO (Generative Engine Optimization)**. Hệ thống bao gồm Web Dashboard FastAPI trực quan, Interactive CLI, bộ điều khiển Enterprise Master CLI (`cli/master_seo.py`), 29 module chuyên sâu và Universal WordPress Plugin độc quyền.

---

### Kiến Trúc & Tính Năng Nổi Bật

```text
seo-geo-suite-master/
├── seo_geo_suite/                  # Giao diện Web Dashboard & Core Suite
│   ├── core/                       # 6 Core Engines (Onpage, Auditor, GeoWriter, CssFixer, AssetBuilder, KeywordPlanner)
│   ├── dashboard/                  # FastAPI Dashboard & M-Auto-Pilot WP Hub
│   └── sync_wp.py                  # WordPress REST API sync engine
├── cli/
│   ├── master_seo.py               # Enterprise Orchestrator (20+ lệnh tối ưu đa site)
│   ├── wp_ai_post.py               # Autonomous AI Article Writer (1.000+ từ, Banner, Schema)
│   ├── wp-ai-post.sh / .bat        # Shell launchers cho AI writer
├── modules/                        # 29 Enterprise SEO & GEO Modules
│   ├── wp_ai_autopilot/            # Tự động hóa sản xuất nội dung chuẩn E-E-A-T
│   ├── fast_indexing/              # Bing IndexNow & Google Indexing API protocol
│   ├── internal_linking/           # Sentinel tự động liên kết nội bộ đa luồng
│   ├── auto_healer/                # Tự động phát hiện và chuyển hướng 301 link hỏng 404
│   ├── cannibalization_detector/   # Quét và cảnh báo ăn thịt từ khóa (Keyword Cannibalization)
│   ├── semantic_silo/              # Xây dựng Topic Clusters & Silo cấu trúc phân tầng
│   ├── orphan_healer/              # Cứu bài viết mồ côi (Orphan Posts) liên kết về Pillar
│   ├── cloudflare_edge/            # Worker CDN Edge Caching & Edge Warming
│   ├── sitemap_engine/             # Google News & Video XML Sitemap
│   ├── serp_gap_hunter/            # Quét khoảng trống từ khóa đối thủ (SERP Gap)
│   ├── eeat_persona/               # Quản lý tác giả chuyên gia & nhúng tín hiệu E-E-A-T
│   ├── core_web_vitals/            # Tối ưu LCP, CLS, FID & tốc độ tải trang
│   ├── travel_scheduler/           # Lên lịch tự động 30 ngày bài viết du lịch/tin tức
│   └── migration/                  # Đóng gói và di chuyển toàn bộ website WP tự động
├── plugins/
│   └── auto-seo-geo-master-suite/  # Universal WordPress Plugin tích hợp sâu
├── run_dashboard.sh / .bat         # Khởi chạy Web Dashboard (Cổng 8000)
├── run_cli.sh / .bat               # Khởi chạy Interactive CLI
└── requirements.txt                # Thư viện Python
```

---

### Khởi Chạy Nhanh

#### 1. Web Dashboard (Giao diện trực quan + Hub M-Auto-Pilot)
```bash
# Trên Linux/macOS:
./run_dashboard.sh

# Trên Windows:
.\run_dashboard.bat
# Mở trình duyệt tại: http://localhost:8000
```

#### 2. Interactive CLI
```bash
# Trên Linux/macOS:
./run_cli.sh

# Trên Windows:
.\run_cli.bat
```

#### 3. Master SEO Enterprise CLI (`cli/master_seo.py`)
```bash
# Tối ưu hóa toàn diện 100% tự động cho tất cả website trong config/sites.json:
python cli/master_seo.py optimize-all

# Hoặc tối ưu cho 1 site cụ thể:
python cli/master_seo.py optimize --site "vibemmo"

# Đẩy IndexNow tức thì lên Bing/IndexNow:
python cli/master_seo.py fast-index --site "mmdidau"

# Quét và tự động liên kết nội bộ thông minh:
python cli/master_seo.py auto-link --site "triptip"

# Quét xung đột từ khóa (Cannibalization):
python cli/master_seo.py cannibalization --site "all"

# Cứu bài viết mồ côi (Orphan posts):
python cli/master_seo.py heal-orphans --site "mmdidau"

# Viết và đăng bài tự động chuẩn SEO 1000+ từ:
python cli/master_seo.py write-post --site "vibemmo" --topic "Top Game MMO Đáng Chơi 2026" --category 4 --status publish
```

---

### Quy Tắc Tiêu Chuẩn Nội Dung (SEO & GEO Rules)

- 📸 **Hình ảnh:** Tối thiểu 1 hình ảnh — tối đa 5 hình ảnh chuyên nghiệp (16:9, sơ đồ, infographic sắc nét, alt tag chuẩn).
- 🖼️ **Ảnh đại diện (Featured Image):** Bắt buộc 100% cho mọi bài viết — đây là tiêu chuẩn mặc định trong SEO.
- 📝 **Độ dài & Chống Thin Content:** Bài viết phải dài **tối thiểu 1.000 từ**, không có giới hạn tối đa (tùy thuộc độ sâu từ khóa có thể 2.000 - 5.000+ từ). Tuyệt đối không xuất bản thin content.
- ✍️ **Văn phong tiêu đề tự nhiên:** Không đánh số cơ học (1., 2., 3., 1.1) cho toàn bộ heading; tỷ lệ heading có số thứ tự hoặc icon **không được vượt quá 20%**.
- 🚫 **Tránh ăn thịt từ khóa:** Mỗi bài viết phân bổ theo 1 Search Intent độc lập, kiểm tra trùng lặp trước khi xuất bản.
- 🔗 **URL Slug:** Chuẩn tiếng Việt không dấu `/tu-khoa-chinh/`.

---

## 🇨🇳 中文

### 简介

**SEO GEO Suite Master** 是一套企业级开源 Python 工具集，全面结合**传统搜索引擎优化（SEO）**与**生成式引擎优化（GEO）**。系统包含基于 FastAPI 的可视化控制台、交互式 CLI、企业级多站点调度器（`cli/master_seo.py`）、29 个高级功能模块及配套的 WordPress 通用插件。

### 快速启动

```bash
# 启动 Web 控制台
./run_dashboard.sh    # macOS/Linux
.\run_dashboard.bat   # Windows
# 访问 http://localhost:8000

# 企业级全自动全站优化（支持多站点循环）
python cli/master_seo.py optimize-all

# 自动生成 1000+ 字 GEO 标准文章并发布
python cli/master_seo.py write-post --site "vibemmo" --topic "2026 年最佳 MMO 游戏推荐"
```

---

## 🇬🇧 English

### Overview

**SEO GEO Suite Master** is an enterprise-grade open-source automation suite merging **traditional technical SEO** with **Generative Engine Optimization (GEO)** — engineered specifically to rank on Google/Bing and secure authoritative citations on AI search engines (ChatGPT Search, Perplexity, Google AI Overviews, Gemini, and Claude).

---

### Key Capabilities

1. **Web Dashboard & M-Auto-Pilot Hub:**
   - Multi-tab FastAPI dashboard for On-page analysis, AI article generation, Keyword roadmap, Technical audits, UI asset building, and WordPress remote publishing.
2. **Master Enterprise Orchestrator (`cli/master_seo.py`):**
   - Commands: `optimize`, `optimize-all`, `deploy`, `audit`, `fast-index`, `auto-link`, `heal-404`, `news-sitemap`, `serp-gap`, `cannibalization`, `build-silo`, `inject-eeat`, `heal-orphans`, `warm-edge`, `audit-links`, `schedule-travel`, `clone-site`, `write-post`.
3. **29 Specialized Modules:**
   - E-E-A-T persona injection, Bing IndexNow protocol, smart internal link sentinel, fuzzy 301 auto-healer, keyword cannibalization detection, Cloudflare edge caching, News XML sitemap, and programmatic GEO landing pages.
4. **Universal WordPress Plugin (`auto-seo-geo-master-suite.php`):**
   - Injects Schema JSON-LD, instant.page prefetching, lazy-loading, PWA theme-color, high-res favicon, and REST endpoints.

---

### Quick Start

```bash
# Web Dashboard
./run_dashboard.sh            # Linux/macOS
.\run_dashboard.bat           # Windows
# Open http://localhost:8000

# Master Optimization for All Configured Sites
python cli/master_seo.py optimize-all

# Autonomous AI Post Generation (1,000+ words, WebP Banner, Schema)
python cli/master_seo.py write-post --site "mysite" --topic "Future of AI in SEO 2026" --status publish
```

---

### Installation

```bash
git clone https://github.com/chrisx9z/seo-geo-suite-master.git
cd seo-geo-suite-master
python3 -m venv .venv
source .venv/bin/activate       # macOS/Linux (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

---

<div align="center">

**MIT License** · Built with ❤️ by [chrisx9z](https://github.com/chrisx9z)

</div>
