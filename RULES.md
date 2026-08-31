# 📜 BỘ QUY TẮC TIÊU CHUẨN NỘI DUNG SEO & GEO (SEO/GEO CONTENT RULES)

Tài liệu này định nghĩa các nguyên tắc cốt lõi và tiêu chuẩn kiểm duyệt chất lượng nội dung bắt buộc đối với toàn bộ bài viết, kịch bản tự động hóa và module sinh nội dung trong dự án **SEO GEO Suite Master**.

---

## 🎯 1. Quy Tắc Về Hình Ảnh & Ảnh Đại Diện (Mandatory Images & Featured Image)

1. **Ảnh đại diện (Featured Image) là BẮT BUỘC 100%:**
   - Mỗi bài viết khi xuất bản lên CMS (WordPress, Webflow, Custom Blog) **bắt buộc phải có ảnh đại diện riêng biệt**.
   - Kích thước tiêu chuẩn: `1200x630` px hoặc tỉ lệ `16:9` (`1920x1080` px).
   - Tối ưu hóa định dạng: `.webp` hoặc `.jpg` tối ưu dung lượng dưới 150KB.
   - Thẻ `og:image` và `twitter:image` phải khớp với ảnh đại diện này.

2. **Số lượng hình ảnh trong bài viết (In-Content Images):**
   - **Tối thiểu:** `1 hình ảnh` minh họa chất lượng cao.
   - **Tối đa:** `5 hình ảnh` chuyên nghiệp (để đảm bảo tốc độ tải trang Core Web Vitals tối ưu).
   - Tất cả hình ảnh trong bài phải có thuộc tính `alt="..."` mô tả chính xác thực thể và ngữ cảnh, có chứa từ khóa liên quan tự nhiên.
   - Ưu tiên ảnh chụp thực tế, infographic số liệu, sơ đồ kiến trúc quy trình, tuyệt đối không dùng ảnh chất lượng thấp hoặc text banner vỡ hạt.

---

## 📝 2. Quy Tắc Về Độ Dài & Chống "Thin Content" (No Thin Content Policy)

1. **Độ dài tối thiểu:**
   - Mỗi bài viết phải có độ dài **TỐI THIỂU 1.000 TỪ**.
   - Tuyệt đối không xuất bản các bài viết ngắn, sơ sài, mang tính chất "nhồi nhét" từ khóa nhưng không giải quyết triệt để vấn đề của người đọc (Thin Content).

2. **Không giới hạn tối đa:**
   - Bài viết **KHÔNG CÓ GIỚI HẠN TỐI ĐA**. Tùy thuộc vào độ phức tạp của chủ đề (Topic Complexity) và dung lượng của thực thể ngữ nghĩa, bài viết có thể dài từ **1.500 đến 5.000+ từ** nhằm tạo ra các bài viết trụ cột (Pillar Content / Ultimate Guide) đứng đầu bảng xếp hạng.

3. **Cấu trúc bài viết chuẩn E-E-A-T & GEO:**
   - **H1:** Tiêu đề hấp dẫn, chứa từ khóa chính.
   - **Direct Answer (60-80 từ):** Đoạn trả lời trực tiếp ngay dưới mở đầu để các mô hình AI (ChatGPT, Perplexity, Gemini) dễ dàng trích xuất làm Featured Snippet.
   - **Bảng biểu (Markdown Table / HTML Table):** Ít nhất 1 bảng số liệu so sánh, ma trận đánh giá hoặc tổng kết Key Takeaways.
   - **Các đề mục H2, H3:** Phân tích logic, có số liệu, dẫn chứng thực tế, code snippet hoặc hướng dẫn từng bước.
   - **FAQ (Hỏi & Đáp):** Ít nhất 3-5 câu hỏi thường gặp có đánh dấu Schema `FAQPage`.
   - **Kết luận:** Tóm tắt giá trị và định hướng hành động (CTA).

---

## 🚫 3. Quy Tắc Tránh Ăn Thịt Từ Khóa (Anti-Keyword Cannibalization)

1. **Phân bổ Cluster độc lập:**
   - Mỗi bài viết chỉ phụ trách một mục đích tìm kiếm duy nhất (Single Search Intent).
   - Trước khi lên bài mới, bắt buộc phải tra cứu danh sách bài viết hiện có trên hệ thống để đảm bảo không trùng lặp từ khóa chính và góc nhìn tiếp cận.

2. **Chuẩn hóa URL Slug:**
   - Đường dẫn bài viết phải là dạng tiếng Việt không dấu, nối bằng dấu gạch ngang: `/tu-khoa-chinh/`.
   - Không chứa ký tự đặc biệt, không lặp lại từ khóa thừa thãi.

---

## 🤖 4. Tối Ưu Hóa Tìm Kiếm Tạo Sinh (GEO - Generative Engine Optimization)

1. **Dữ liệu có cấu trúc (Schema.org JSON-LD):**
   - Bắt buộc khai báo Schema `Article`, `FAQPage`, `Person` (Tác giả có chuyên môn) và `Organization`.

2. **Tối ưu file `llms.txt`:**
   - Tự động cập nhật tiêu đề và tóm tắt bài viết vào `/llms.txt` để các bot thu thập dữ liệu AI (GPTBot, ClaudeBot, PerplexityBot) lập chỉ mục tức thì.

---

*Quy tắc này có hiệu lực từ tháng 08/2026 và áp dụng cho toàn bộ codebase và workflow vận hành.*
