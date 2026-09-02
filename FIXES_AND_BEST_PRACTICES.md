# 📘 TỔNG HỢP LỖI THƯỜNG GẶP, GIẢI PHÁP & KINH NGHIỆM TỐI ƯU (LESSONS LEARNED & BEST PRACTICES)

> **Tài liệu lưu trữ nội bộ:** Ghi nhớ các lỗi thực tế đã phát sinh, nguyên nhân gốc rễ (Root Cause), giải pháp triệt để và bộ quy tắc chuẩn cho các dự án **VibeMMO.net** và **Kinh Dịch Web App**.

---

## 📑 MỤC LỤC
1. [Dự án 1: Website VibeMMO.net (WordPress, Theme Soledad, Multilingual & SEO)](#1-dự-án-1-website-vibemmonet)
   - [Lỗi 1: Tab trình duyệt hiện dấu `-` & Thiếu Meta SEO 3 ngôn ngữ](#lỗi-1-tab-trình-duyệt-hiện-dấu----thiếu-meta-seo-3-ngôn-ngữ)
   - [Lỗi 2: Header bị lệch hẳn sang trái trên màn hình PC lớn](#lỗi-2-header-bị-lệch-hẳn-sang-trái-trên-màn-hình-pc-lớn)
   - [Lỗi 3: Giao diện Mobile kéo dài dằng dặc, chữ menu đè lên nhau](#lỗi-3-giao-diện-mobile-kéo-dài-dằng-dặc-chữ-menu-đè-lên-nhau)
   - [Lỗi 4: Nút chuyển ngôn ngữ bị Google Translate dịch đè mất nhãn](#lỗi-4-nút-chuyển-ngôn-ngữ-bị-google-translate-dịch-đè-mất-nhãn)
   - [Lỗi 5: Đánh số Heading quá nhiều (Văn phong AI) & Ảnh minh họa kém chuyên nghiệp](#lỗi-5-đánh-số-heading-quá-nhiều-văn-phong-ai--ảnh-minh-họa-kém-chuyên-nghiệp)
2. [Dự án 2: Ứng Dụng Kinh Dịch / Bát Tự Web (`d:\Vibe Code\Kinh Dịch\web`)](#2-dự-án-2-ứng-dụng-kinh-dịch--bát-tự-web)
   - [Lỗi 1: Chữ Hán-Việt bị dính liền không có dấu cách (ĐinhHợi, NhâmThìn)](#lỗi-1-chữ-hán-việt-bị-dính-liền-không-có-dấu-cách-đinhhợi-nhâmthìn)
   - [Lỗi 2: Khối "Đại Vận" bị khoảng trống lớn bên phải gây mất cân đối](#lỗi-2-khối-đại-vận-bị-khoảng-trống-lớn-bên-phải-gây-mất-cân-đối)
3. [Quy Trình Kiểm Tra Chuẩn Trước Khi Bàn Giao (Checklist)](#3-quy-trình-kiểm-tra-chuẩn-trước-khi-bàn-giao-checklist)

---

## 1. DỰ ÁN 1: WEBSITE VIBEMMO.NET

### Lỗi 1: Tab trình duyệt hiện dấu `-` & Thiếu Meta SEO 3 ngôn ngữ
* **Hiện tượng:** Tiêu đề tab trình duyệt chỉ hiện đúng một dấu gạch ngang (`-`), chia sẻ mạng xã hội không có mô tả (No description).
* **Nguyên nhân gốc rễ:** 
  - Trường `blogname` và `blogdescription` trong database WordPress (`wp_options`) bị để rỗng.
  - Rank Math / Theme lấy mặc định `%sitename% - %sitedesc%` dẫn đến chuỗi `-`.
* **Giải pháp đã xử lý:**
  1. Cập nhật `blogname` = `VibeMMO` và `blogdescription` = `Cổng Thông Tin Trí Tuệ Nhân Tạo & Kiếm Tiền Online MMO 2026`.
  2. Xây dựng bộ lọc dynamic hook `pre_get_document_title` & `rank_math/frontend/title` trong plugin `vibemmo-header-nav-master` để tự động render chuẩn Title / Description / Keywords / OpenGraph theo đúng ngôn ngữ người dùng đang xem:
     - **VI:** `VibeMMO - Cổng Thông Tin Trí Tuệ Nhân Tạo & AI MMO Hàng Đầu`
     - **EN:** `VibeMMO - Leading AI News, Top AI Tools & Digital Wealth Hub`
     - **ZH:** `VibeMMO - 前沿人工智能资讯、AI工具评测与出海商业门户`

---

### Lỗi 2: Header bị lệch hẳn sang trái trên màn hình PC lớn
* **Hiện tượng:** Logo và menu bị dạt ra sát mép ngoài cùng bên trái màn hình Full HD (1920px), không thẳng hàng với nội dung bài viết và sidebar bên dưới.
* **Nguyên nhân gốc rễ:** Container của Navbar (`#navigation .container`) đặt `width: 98%; max-width: 98%`, trong khi toàn bộ phần thân trang web (`.container`) sử dụng độ rộng cố định chuẩn `1170px` và căn giữa bằng `margin: 0 auto`.
* **Giải pháp đã xử lý:**
  - Đồng bộ `#navigation .container` theo kích thước `max-width: 1170px !important; width: 100% !important; margin: 0 auto !important;`.
  - Mép trái logo gióng thẳng hàng 1:1 với mép trái ảnh banner; mép phải (Language & Search) gióng thẳng hàng 1:1 với mép phải của sidebar.

---

### Lỗi 3: Giao diện Mobile kéo dài dằng dặc, chữ menu đè lên nhau
* **Hiện tượng:** 
  - Các chữ chuyên mục trên menu bị ép cứng vào màn hình di động 390px, tràn ra và đè lên hình ảnh/logo.
  - Người dùng phải cuộn dọc hơn 15.000px với 5 khối chuyên mục lặp đi lặp lại cùng các thẻ bài viết đen xì, kích thước khổng lồ.
* **Nguyên nhân gốc rễ:** 
  - CSS thiếu Media Query tách biệt giữa PC (`min-width: 961px`) và Mobile (`max-width: 960px`).
  - Layout di động chưa được tối ưu hóa dạng tin vắn/tạp chí hiện đại.
* **Giải pháp đã xử lý:**
  1. **Menu di động:** Ẩn toàn bộ menu ngang trên màn hình `< 960px`, kích hoạt nút **3 gạch (Hamburger)** mở thanh trượt Sidebar.
  2. **Thanh Story Pills (Category Bar):** Thêm thanh lướt ngang `⚡ Mới Nhất`, `🤖 AI & LLMs`, `💰 AI MMO`, `⚙️ SaaS Tech`, `🛠️ Top AI Tools`, `🔥 Tin Nóng` ngay dưới Header.
  3. **Cấu trúc lại Chuyên mục:** 
     - 1 Bài Tiêu Điểm dạng Spotlight Card (tỉ lệ 16:9).
     - Các bài tiếp theo hiển thị dạng **danh sách tin vắn** (Thumbnail trái `85x60px` + Tiêu đề phải 2 dòng).
     - Các chuyên mục phụ (AI MMO, Top AI Tools) chuyển thành **Thanh trượt ngang bằng ngón tay (Horizontal Swipe Carousel)**.
  4. **Giảm 60% chiều dài trang:** Ẩn nút "Read more »" thừa thãi, dọn dẹp các widget trùng lặp ở sidebar dưới chân trang.

---

### Lỗi 4: Nút chuyển ngôn ngữ bị Google Translate dịch đè mất nhãn
* **Hiện tượng:** Khi chuyển sang tiếng Anh hoặc tiếng Trung, chữ "English" hoặc "Tiếng Việt" trong dropdown bị dịch sai lệch hoặc biến thành ngôn ngữ khác, làm hỏng giao diện.
* **Nguyên nhân gốc rễ:** Google Translate API tự động quét tất cả thẻ text trên trang nếu không được gắn cờ loại trừ.
* **Giải pháp đã xử lý:**
  - Khóa chặt vùng chọn ngôn ngữ bằng thuộc tính `class="notranslate"` và `translate="no"`.
  - Đồng bộ trạng thái ngôn ngữ qua cả 2 Cookie `vbm_lang` và `googtrans` (`/vi/en`, `/vi/zh-CN`), kèm thẻ canonical và alternate hreflang chuẩn SEO cho bot Google.

---

### Lỗi 5: Đánh số Heading quá nhiều (Văn phong AI) & Ảnh minh họa kém chuyên nghiệp
* **Hiện tượng:** Bài viết có các tiêu đề lặp đi lặp lại dạng "1. Giới thiệu", "2. Tính năng", "3. Ước tính", "4. Kết luận", tạo cảm giác máy móc. Ảnh bài viết chứa text mờ nhạt hoặc ảnh ghép sơ sài.
* **Quy tắc chuẩn hóa:**
  - **Tỷ lệ đánh số Heading & Icon:** Giữ dưới **20%** tổng số heading. Dùng các câu dẫn dắt tự nhiên, hành văn chuyên gia.
  - **Hình ảnh minh họa:** Dùng ảnh render đồ họa cyberpunk/tech 3D độ phân giải cao, tỉ lệ 16:9, màu sắc hiện đại, không chèn chữ thô thiển lên ảnh.

---

## 2. DỰ ÁN 2: ỨNG DỤNG KINH DỊCH / BÁT TỰ WEB (`d:\Vibe Code\Kinh Dịch\web`)

### Lỗi 1: Chữ Hán-Việt bị dính liền không có dấu cách (ĐinhHợi, NhâmThìn)
* **Hiện tượng:** Khối Thai nguyên hiển thị `ĐinhHợi`, Cung Mệnh hiển thị `NhâmThìn`, Cách cục hiển thị `Chính Tài格`.
* **Nguyên nhân gốc rễ:**
  - `bazi.js` trả về chuỗi 2 Hán tự liền nhau (`丁亥`, `壬辰`).
  - Hàm `I18n.hanViet()` dịch từng ký tự một (`丁` -> `Đinh`, `亥` -> `Hợi`), do 2 chữ Hán ban đầu không có dấu cách nên kết quả Hán-Việt bị dính liền vào nhau.
* **Giải pháp đã xử lý:**
  - Bổ sung toàn bộ bảng tra 60 Hoa Giáp 2 chữ có sẵn khoảng trắng (`丁亥` -> `Đinh Hợi`, `壬辰` -> `Nhâm Thìn`) vào `hanVietTerms` trong `i18n.js`.
  - Do regex sắp xếp theo độ dài giảm dần (`b.length - a.length`), các cụm 2 chữ sẽ được ưu tiên match trước các ký tự đơn lẻ.
  - Bổ sung từ điển Hán-Việt cho các thuật ngữ: `格` -> ` cách`, dấu phẩy Trung Quốc `、` -> `, `.

---

### Lỗi 2: Khối "Đại Vận" bị khoảng trống lớn bên phải gây mất cân đối
* **Hiện tượng:** Khối "Đại Vận" có 8 thẻ nhưng bị cố định chiều rộng (`width: 80px`), trong khi container rộng 1100px dẫn đến mảng đen trống hoác bên phải, không ăn khớp với lưới 10 ô của khối "Lưu Niên" bên dưới.
* **Nguyên nhân gốc rễ:** `.luck-pillars-track` dùng `display: flex; gap: 0;` với `.luck-pillar-card { width: 80px; }` tĩnh.
* **Giải pháp đã xử lý:**
  - Chuyển `.luck-pillars-track` sang `display: grid; grid-template-columns: repeat(auto-fit, minmax(88px, 1fr)); width: 100%; gap: var(--space-xs);`.
  - Thẻ `.luck-pillar-card` để `width: auto; flex: 1 1 0;` giúp tự động dàn đều cân đối 100% bề ngang khung chứa.

---

## 3. QUY TRÌNH KIỂM TRA CHUẨN TRƯỚC KHI BÀN GIAO (CHECKLIST)

Mỗi khi cập nhật giao diện hoặc code tính năng, bắt buộc chạy kiểm thử tự động theo các bước:

| Bước | Hạng Mục Kiểm Tra | Công Cụ & Thao Tác | Tiêu Chuẩn Đạt |
| :--- | :--- | :--- | :--- |
| **1** | **Desktop View (1920x1080 & 1440x900)** | Playwright Browser Screenshot | Header căn giữa `1170px`, logo thẳng hàng lề trái, menu 1 hàng duy nhất |
| **2** | **Mobile View (390x844 iPhone / Android)** | Playwright Mobile Viewport | Ẩn menu ngang, hiện nút 3 gạch, có thanh category pills, không chữ tràn lề |
| **3** | **Kiểm Tra Tab Title & Meta SEO** | Inspect HTML `<title>`, `<meta>` | Có đủ Title, Description cho cả 3 ngôn ngữ (VI / EN / ZH), không rỗng |
| **4** | **Xóa Cache Hệ Thống** | Purge WP Rocket / CDN Cache | Trình duyệt ẩn danh (Incognito) nhận ngay mã nguồn và CSS mới nhất |
| **5** | **Kiểm Tra Ngôn Ngữ & Dính Chữ** | Test chuyển đổi VI ↔ EN ↔ ZH | Không bị lỗi dính chữ Can-Chi (`Đinh Hợi`), nhãn ngôn ngữ không bị dịch sai |

---
*Tài liệu được cập nhật tự động và lưu trữ tại `FIXES_AND_BEST_PRACTICES.md`.*
