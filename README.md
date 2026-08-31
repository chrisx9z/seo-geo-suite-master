# ⚡ SEO & GEO Master Suite (Generative Engine Optimization)

Hệ thống toàn diện kết hợp **SEO truyền thống** và **GEO (Generative Engine Optimization)** tối ưu cho các công cụ tìm kiếm tạo sinh bằng AI (ChatGPT Search, Perplexity, Google AI Overviews, Gemini, Claude).

---

## 🌟 6 Module Cốt Lõi Tích Hợp

| Module | Chức Năng | Lệnh Thực Thi |
| :--- | :--- | :--- |
| **1. Audit Website & Technical SEO** | Kiểm tra Robots.txt, Sitemap.xml, quyền truy cập của AI Bots (GPTBot, ClaudeBot, PerplexityBot) và link hỏng. | .\run_cli.bat audit <url> |
| **2. Kiểm Tra Lỗi On-page & Schema** | Đánh giá Title, Meta Description, Thẻ Heading (H1-H6), Canonical, Hình ảnh thiếu Alt, JSON-LD Schema.org và tính điểm GEO Citability. | .\run_cli.bat onpage <url> |
| **3. Viết Bài Chuẩn GEO & SEO** | Tự động sinh bài viết chuyên sâu E-E-A-T với đoạn trả lời trực tiếp (Direct Answer), bảng số liệu so sánh, FAQ và Schema JSON-LD + Entry file llms.txt. | .\run_cli.bat write --topic \"...\" --keyword \"...\" |
| **4. Kế Hoạch Từ Khóa & Roadmap** | Cào gợi ý từ Google Suggest & PAA, gom nhóm ngữ nghĩa (Semantic Clustering TF-IDF/KMeans) và lập kế hoạch phát triển 30 ngày. | .\run_cli.bat plan --seed \"...\" |
| **5. Tạo Menu, Footer, Breadcrumbs** | Sinh mã HTML + Tailwind CSS kèm Schema SiteNavigationElement, WPFooter và BreadcrumbList. | .\run_cli.bat ui --type menu/footer/breadcrumbs |
| **6. Chuẩn Đoán & Sửa Lỗi CSS** | Phát hiện width cố định gây vỡ layout mobile, lạm dụng !important, xung đột z-index, CSS thừa. | .\run_cli.bat css <duong_dan_file_css> |

---

## 🚀 Hướng Dẫn Khởi Chạy Nhanh

### Cách 1: Sử Dụng Web Dashboard Trực Quan (Khuyên Dùng)
Nhấp đúp chuột vào file **un_dashboard.bat** hoặc chạy lệnh:
`ash
.\run_dashboard.bat
`
👉 Mở trình duyệt truy cập: **[http://localhost:8000](http://localhost:8000)** để sử dụng đầy đủ 6 tính năng với giao diện đồ họa hiện đại.

---

### Cách 2: Sử Dụng Giao Diện Dòng Lệnh Interactive CLI
Nhấp đúp chuột vào file **un_cli.bat** hoặc chạy:
`ash
.\run_cli.bat
`
Menu tương tác bằng số sẽ xuất hiện để bạn chọn tính năng.

---

### Cách 3: Chạy Trực Tiếp Từng Lệnh CLI

1. **Kiểm tra On-page một trang web:**
   `ash
   .\run_cli.bat onpage https://example.com
   `

2. **Tạo bài viết SEO/GEO mới:**
   `ash
   .\run_cli.bat write --topic "Chiến lược SEO & GEO 2026" --keyword "tối ưu hóa GEO"
   `

3. **Lập kế hoạch từ khóa & Topic Clusters:**
   `ash
   .\run_cli.bat plan --seed "khoa hoc seo"
   `

4. **Tạo Header & Menu điều hướng:**
   `ash
   .\run_cli.bat ui --type menu --brand "MyCompany"
   `

5. **Tạo Footer đa cột chuẩn SEO:**
   `ash
   .\run_cli.bat ui --type footer --brand "MyCompany"
   `

6. **Tạo Breadcrumbs có Schema:**
   `ash
   .\run_cli.bat ui --type breadcrumbs
   `

7. **Kiểm tra lỗi CSS:**
   `ash
   .\run_cli.bat css reports/sample.css
   `

---

## 📂 Các Repository Mở Đã Cài Đặt Trong epos/

- **epos/ultimate-seo-geo/**: Bộ công cụ với 55+ script chuyên sâu về SEO & GEO, kiểm tra citability, llms.txt, entity markup, audit programmatic SEO.
- **epos/geo-seo-claude/**: Bộ công cụ tính điểm Citability Score, crawl bot analysis, báo cáo audit trực quan.
