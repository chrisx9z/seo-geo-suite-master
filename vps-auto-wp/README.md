# 🚀 Bộ Toolkit Tự Động Hóa VPS WordPress (Ubuntu 22.04 + aaPanel)

Hệ thống script tự động hóa 100% dành cho **VPS Contabo**, tích hợp các Repositories mã nguồn mở hàng đầu thế giới:
- **[WP-CLI](https://github.com/wp-cli/wp-cli)**: Quản trị, cài đặt và clone WordPress siêu tốc.
- **[Rclone](https://github.com/rclone/rclone)**: Tự động sao lưu và đẩy dữ liệu lên Cloud (Google Drive / S3 / R2).
- **[Nginx Ultimate Bad Bot Blocker](https://github.com/mitchellkrogza/nginx-ultimate-bad-bot-blocker)**: Chặn bot rác, scan bot, cào dữ liệu và DDoS Lớp 7.
- **[Fail2ban](https://github.com/fail2ban/fail2ban) + Cloudflare API**: Bắt IP tấn công và chặn trực tiếp tại Cloudflare Firewall.

---

## 🛠 Hướng Dẫn Cài Đặt 1-Click Lên VPS

### Bước 1: SSH vào VPS và tải bộ toolkit
Chạy các lệnh sau trên terminal của VPS:

```bash
# Tạo thư mục và tải các script về VPS
mkdir -p /root/vps-auto-wp && cd /root/vps-auto-wp

# Cấp quyền thực thi và chạy cài đặt
chmod +x *.sh
sudo bash install.sh
```

---

## 📋 Các Lệnh Sử Dụng Hàng Ngày

### 1. 🚀 Tạo Website Mới Tự Động 100% (`auto-site`)
Khởi tạo site WordPress cô lập hoàn toàn trên aaPanel:
```bash
auto-site domain.com
```
*Tự động trỏ DNS Cloudflare, tạo MariaDB 10.11 user/db riêng, tải WP-Core, kích hoạt 4 plugin thiết yếu và tạo VHost Nginx bảo mật.*

---

### 2. 🌐 Trỏ DNS & Bật Proxy Cloudflare Tự Động (`cf-dns`)
Trỏ bản ghi A về IP VPS và tự động bật Cloudflare Proxy + SSL Full:
```bash
cf-dns domain.com
```

---

### 3. ⚡ Clone Website Trong 10 Giây (`wp-clone`)
Khi bạn muốn tạo một site mới dựa trên 1 site có sẵn (clone toàn bộ theme, plugin, giao diện và tự đổi toàn bộ link sang domain mới):
```bash
wp-clone site-cu.com site-moi.com
```
*Script sẽ tự động: Export DB -> Copy source -> Tạo DB mới -> Import DB -> Chạy search-replace domain chuẩn xác -> Phân quyền 755/644.*

---

### 4. 🧹 Dọn Sạch Bài Viết An Toàn (`wp-clean-posts`)
Xóa sạch bài viết blog (`post`, `revision`), dọn dẹp bảng quan hệ và metadata, **tuyệt đối bảo toàn giao diện templates, pages, menu và media**:
```bash
wp-clean-posts domain.com
# Hoặc bỏ qua bước hỏi xác nhận:
wp-clean-posts domain.com --force
```

---

### 5. 🎨 Tạo & Kích Hoạt Newspaper Child Theme (`install-child-theme`)
Tự động tạo child theme cho Newspaper, thiết lập nạp stylesheet đúng chuẩn và kích hoạt ngay:
```bash
install-child-theme domain.com
```

---

### 6. 🛡 Tự Động Chặn Kẻ Tấn Công Qua Cloudflare WAF (`setup-cloudflare-waf`)
Kích hoạt tính năng bắt IP dò pass admin hoặc spam request và tự động chặn tại Cloudflare Firewall:
```bash
setup-cloudflare-waf
```

---

### 7. ☁️ Sao Lưu Tự Động Lên Cloud (`wp-backup`)
Sao lưu toàn bộ các site WordPress và database, nén gọn và dọn dẹp các bản backup cũ quá 3 ngày:
```bash
wp-backup
```

**Để tự động chạy mỗi đêm lúc 02:00 sáng:**
Mở `crontab -e` hoặc vào menu **Cron** trong **aaPanel** và thêm:
```bash
0 2 * * * /usr/local/bin/wp-backup >/dev/null 2>&1
```

---

## 🔒 3 Quy Tắc Vàng Khi Bật Cloudflare Cho aaPanel

1. **Bật Proxy (Đám mây cam 🟧)** cho domain trên Cloudflare.
2. **Cấu hình SSL trên Cloudflare**: Chọn chế độ **Full (Strict)** hoặc **Full**.
3. **WAF Custom Rules (Khuyên dùng)**:
   - Vào Cloudflare -> **Security** -> **WAF** -> **Custom Rules** -> Tạo rule:
     - Biểu thức: `(http.request.uri.path contains "/xmlrpc.php")`
     - Action: **Block** (Chặn đứng 90% các cuộc tấn công Brute-force & DDoS WordPress).
