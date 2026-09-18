# 📜 QUY TẮC BẤT DI BẤT DỊCH QUẢN TRỊ VPS & WORDPRESS (MULTI-TENANT RULES)

Tài liệu này ghi nhớ toàn bộ bài học và kinh nghiệm thực chiến trên VPS Ubuntu 24.04 (aaPanel LNMP: Nginx 1.30, MariaDB 10.11, PHP 8.4) để đảm bảo **khi thêm website mới KHÔNG BAO GIỜ ảnh hưởng, xóa đè hoặc làm hỏng các website cũ**.

---

## 1. NGUYÊN TẮC CÔ LẬP TUYỆT ĐỐI (ZERO CROSS-IMPACT)
- **Không bao giờ chạy vòng lặp ghi đè toàn bộ `/www/wwwroot/*`**: Mọi lệnh tạo mới, cập nhật hoặc sửa lỗi chỉ được phép thao tác trên đúng 1 thư mục tên miền mục tiêu (`/www/wwwroot/$DOMAIN`).
- **Nginx `00_default.conf` luôn phải tồn tại**:
  Bắt buộc phải có block `default_server` trả về `return 444;` để khi có truy cập không rõ nguồn gốc hoặc lỗi SSL, Nginx **tuyệt đối không bao giờ chuyển hướng 301 nhầm sang website khác**.

---

## 2. NGUYÊN TẮC CẤU HÌNH MARIADB 10.11+
- **Cú pháp cấp quyền chuẩn bắt buộc**:
  Tuyệt đối không dùng cú pháp cũ `GRANT ... IDENTIFIED BY` (sẽ bị lỗi cú pháp MariaDB 10.11 và không cấp được quyền).
  Luôn dùng cú pháp 3 bước tách biệt:
  ```sql
  CREATE DATABASE IF NOT EXISTS `db_name`;
  CREATE USER IF NOT EXISTS 'db_user'@'localhost' IDENTIFIED BY 'password';
  ALTER USER 'db_user'@'localhost' IDENTIFIED BY 'password';
  GRANT ALL PRIVILEGES ON `db_name`.* TO 'db_user'@'localhost';

  CREATE USER IF NOT EXISTS 'db_user'@'127.0.0.1' IDENTIFIED BY 'password';
  ALTER USER 'db_user'@'127.0.0.1' IDENTIFIED BY 'password';
  GRANT ALL PRIVILEGES ON `db_name`.* TO 'db_user'@'127.0.0.1';
  FLUSH PRIVILEGES;
  ```
- **DB_HOST luôn là `127.0.0.1`**: Tránh hoàn toàn lỗi lệch Socket MySQL (`/tmp/mysql.sock` vs `/run/mysqld/mysqld.sock`).

---

## 3. NGUYÊN TẮC BẢO VỆ HIỆU NĂNG & TỐI ƯU PHP 8.4
- **Tắt JIT (`opcache.jit = 0`)**: JIT trên PHP 8.4 gây xung đột `SIGSEGV (core dumped)` làm sập worker PHP khi chạy WordPress.
- **Tắt Slowlog Tracing (`request_slowlog_timeout = 0`)**: Mặc định aaPanel bật tính năng này làm đóng băng tiến trình PHP tới 35 giây, gây lỗi 502/524 cho người dùng.
- **Tiến trình sao lưu phải chạy nền nhẹ**: Luôn sử dụng `ionice -c 3` và `nice -n 19` khi nén dữ liệu để 100% CPU/Ổ cứng ưu tiên phục vụ khách truy cập web.

---

## 4. NGUYÊN TẮC CLOUDFLARE & CHỐNG VỠ CSS WP ROCKET
- **Xóa Cache 301**: Khi thay đổi cấu hình VHost, luôn gửi lệnh Purge Everything qua Cloudflare API để xóa sạch cache chuyển hướng 301 trên máy chủ Edge.
- **Quy tắc vàng WP Rocket**:
  - `Minify CSS` / `Minify JS`: BẬT (Nén nhẹ an toàn).
  - `Combine CSS` / `Combine JS`: TẮT TUYỆT ĐỐI (Chống vỡ giao diện & menu).
  - `Remove Unused CSS`: TẮT (Chống mất CSS động).
  - `LazyLoad` + `Defer JS` + `Link Preload`: BẬT.

---

## 5. QUẢN TRỊ THÔNG TIN XÁC THỰC & BẢO MẬT (CREDENTIALS MANAGEMENT)
- **Tuyệt đối không lưu mật khẩu tĩnh trong mã nguồn / Git**:
  - Toàn bộ script tự động lấy thông tin từ biến môi trường (`.env` hoặc `/root/.cloudflare_credentials`).
  - Mật khẩu WordPress mới khởi tạo phải được sinh ngẫu nhiên tự động (`openssl rand -base64 16`) hoặc truyền qua biến môi trường `WP_ADMIN_PASS`.
- **Cấu hình Cloudflare xác thực**:
  - Khuyến nghị sử dụng Scoped API Token hoặc lưu cấu hình riêng biệt tại `/root/.cloudflare_credentials` với phân quyền `chmod 600`.

