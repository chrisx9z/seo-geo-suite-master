#!/usr/bin/env bash
# ==============================================================================
# VPS AUTO TOOLKIT - MASTER INSTALLER (Ubuntu 24.04 / 22.04 & aaPanel)
# ==============================================================================
set -e

# Màu sắc thông báo
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}  CÀI ĐẶT BỘ TOOLKIT TỰ ĐỘNG HÓA VPS / AAPANEL / WP ${NC}"
echo -e "${BLUE}=====================================================${NC}"

# Kiểm tra quyền root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[LỖI] Vui lòng chạy script với quyền root (sudo bash install.sh)${NC}"
  exit 1
fi

# 1. Cập nhật gói và cài đặt dependencies cơ bản
echo -e "${YELLOW}[1/5] Đang cập nhật gói hệ thống và cài đặt công cụ cần thiết...${NC}"
apt update -y
apt install -y curl wget unzip git jq rsync fail2ban python3-pip python3-venv dnsutils

# Hỗ trợ Python 3.12 trên Ubuntu 24.04 (PEP 668)
pip3 install cloudflare --break-system-packages 2>/dev/null || true

# 2. Cài đặt WP-CLI (Quản trị & Clone WordPress siêu tốc)
echo -e "${YELLOW}[2/5] Đang tải và cài đặt WP-CLI (Official Repo)...${NC}"
if ! command -v wp &> /dev/null; then
    curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
    chmod +x wp-cli.phar
    mv wp-cli.phar /usr/local/bin/wp
    echo -e "${GREEN}--> WP-CLI đã được cài đặt thành công tại /usr/local/bin/wp${NC}"
else
    echo -e "${GREEN}--> WP-CLI đã tồn tại, tiến hành cập nhật...${NC}"
    wp cli update --allow-root --yes || true
fi

# 3. Cài đặt Rclone (Auto Backup Cloud)
echo -e "${YELLOW}[3/5] Đang tải và cài đặt Rclone (Official Repo)...${NC}"
if ! command -v rclone &> /dev/null; then
    curl https://rclone.org/install.sh | bash
    echo -e "${GREEN}--> Rclone đã được cài đặt thành công!${NC}"
else
    echo -e "${GREEN}--> Rclone đã tồn tại.${NC}"
fi

# 4. Cài đặt Nginx Ultimate Bad Bot Blocker (Chống DDoS Lớp 7 & Scan Bot)
echo -e "${YELLOW}[4/5] Đang cài đặt Nginx Ultimate Bad Bot Blocker...${NC}"
if [ -d "/www/server/nginx" ] || [ -d "/etc/nginx" ]; then
    cd /usr/local/sbin
    wget -q https://raw.githubusercontent.com/mitchellkrogza/nginx-ultimate-bad-bot-blocker/master/install-ngxblocker -O install-ngxblocker
    chmod +x install-ngxblocker
    ./install-ngxblocker -x || true
    if [ -f "/usr/local/sbin/setup-ngxblocker" ]; then
        /usr/local/sbin/setup-ngxblocker -x -e conf || true
        echo -e "${GREEN}--> Nginx Bad Bot Blocker đã sẵn sàng!${NC}"
    fi
else
    echo -e "${YELLOW}--> Chưa phát hiện Nginx của aaPanel, bạn có thể chạy lại setup sau khi cài Nginx trên aaPanel.${NC}"
fi

# 5. Cài đặt các công cụ trợ lý lệnh
echo -e "${YELLOW}[5/5] Đang cấu hình các lệnh tiện ích nhanh...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for cmd in wp-clone wp-backup setup-cloudflare-waf cf-dns wp-clean-posts auto-site install-child-theme; do
    if [ -f "$SCRIPT_DIR/${cmd}.sh" ]; then
        cp "$SCRIPT_DIR/${cmd}.sh" "/usr/local/bin/${cmd}"
        chmod +x "/usr/local/bin/${cmd}"
    fi
done

echo -e "\n${GREEN}=====================================================${NC}"
echo -e "${GREEN}  CÀI ĐẶT THÀNH CÔNG TẤT CẢ CÁC CÔNG CỤ!             ${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo -e "Các lệnh bạn có thể sử dụng ngay:"
echo -e "  1. ${YELLOW}auto-site <domain.com>${NC}                    : Tự động cài đặt 100% website mới trên aaPanel"
echo -e "  2. ${YELLOW}cf-dns <domain.com>${NC}                       : Tự động trỏ DNS & bật Proxy cam Cloudflare"
echo -e "  3. ${YELLOW}wp-clone <site_cu.com> <site_moi.com>${NC}     : Clone website trong 10 giây"
echo -e "  4. ${YELLOW}wp-clean-posts <domain.com>${NC}               : Xóa toàn bộ bài viết, bảo toàn giao diện"
echo -e "  5. ${YELLOW}install-child-theme <domain.com>${NC}          : Tự động tạo & kích hoạt Newspaper Child Theme"
echo -e "  6. ${YELLOW}wp-backup${NC}                                 : Backup toàn bộ site + DB và sync lên Cloud"
echo -e "  7. ${YELLOW}setup-cloudflare-waf${NC}                      : Kích hoạt chặn IP qua Cloudflare API"
echo -e "${GREEN}=====================================================${NC}\n"
