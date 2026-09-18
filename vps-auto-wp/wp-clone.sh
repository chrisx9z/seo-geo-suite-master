#!/usr/bin/env bash
# ==============================================================================
# WP-CLONE: TỰ ĐỘNG CLONE WEBSITE WORDPRESS TRÊN AAPANEL TRONG 10 GIÂY
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SRC_DOMAIN=$1
DST_DOMAIN=$2

if [ -z "$SRC_DOMAIN" ] || [ -z "$DST_DOMAIN" ]; then
    echo -e "${RED}[LỖI] Thiếu tham số!${NC}"
    echo -e "Cú pháp sử dụng: ${YELLOW}wp-clone <domain-nguon> <domain-dich>${NC}"
    echo -e "Ví dụ: ${GREEN}wp-clone site1.com site2.com${NC}"
    exit 1
fi

SRC_PATH="/www/wwwroot/${SRC_DOMAIN}"
DST_PATH="/www/wwwroot/${DST_DOMAIN}"

if [ ! -d "$SRC_PATH" ]; then
    echo -e "${RED}[LỖI] Không tìm thấy thư mục nguồn: ${SRC_PATH}${NC}"
    exit 1
fi

echo -e "${BLUE}=====================================================${NC}"
echo -e "${YELLOW}BẮT ĐẦU CLONE: ${SRC_DOMAIN}  --->  ${DST_DOMAIN}${NC}"
echo -e "${BLUE}=====================================================${NC}"

# Tạo thư mục đích nếu chưa có
mkdir -p "$DST_PATH"

# 1. Export database nguồn
TEMP_SQL="/tmp/clone_${SRC_DOMAIN}_$(date +%s).sql"
echo -e "${YELLOW}[1/5] Đang xuất database từ ${SRC_DOMAIN}...${NC}"
wp db export "$TEMP_SQL" --path="$SRC_PATH" --allow-root

# 2. Đồng bộ mã nguồn
echo -e "${YELLOW}[2/5] Đang đồng bộ mã nguồn sang ${DST_PATH}...${NC}"
rsync -av --delete \
    --exclude="wp-content/cache/*" \
    --exclude="*.log" \
    --exclude="wp-content/uploads/cache/*" \
    "$SRC_PATH/" "$DST_PATH/"

# 3. Tạo hoặc cấu hình Database cho Site mới
echo -e "${YELLOW}[3/5] Đang cấu hình Database cho site mới...${NC}"
DB_NAME="db_${DST_DOMAIN//./_}"
DB_NAME=${DB_NAME:0:15}
DB_USER="u_${DST_DOMAIN//./_}"
DB_USER=${DB_USER:0:15}
DB_PASS=$(openssl rand -base64 12)

# Lấy mật khẩu root MySQL của aaPanel nếu có
MYSQL_ROOT_PASS=$(cat /www/server/data/default.pl 2>/dev/null || echo "")

if [ -n "$MYSQL_ROOT_PASS" ]; then
    mysql -u root -p"${MYSQL_ROOT_PASS}" -e "CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}'; FLUSH PRIVILEGES;" 2>/dev/null || true
    
    # Cập nhật wp-config.php của site mới
    wp config set DB_NAME "${DB_NAME}" --path="$DST_PATH" --allow-root
    wp config set DB_USER "${DB_USER}" --path="$DST_PATH" --allow-root
    wp config set DB_PASSWORD "${DB_PASS}" --path="$DST_PATH" --allow-root
fi

# 4. Import Database và Search-Replace Domain
echo -e "${YELLOW}[4/5] Đang import Database và đổi URL mới...${NC}"
wp db import "$TEMP_SQL" --path="$DST_PATH" --allow-root
rm -f "$TEMP_SQL"

# Lấy URL gốc của site nguồn
SRC_URL=$(wp option get siteurl --path="$SRC_PATH" --allow-root 2>/dev/null || echo "http://${SRC_DOMAIN}")
# Xác định URL mới (ưu tiên https)
DST_URL="https://${DST_DOMAIN}"

echo -e "--> Thay thế: ${SRC_URL} thành ${DST_URL}"
wp search-replace "${SRC_URL}" "${DST_URL}" --path="$DST_PATH" --allow-root --precise --recurse-objects

# Trường hợp site cũ có link dạng http:// hoặc không có www
wp search-replace "http://${SRC_DOMAIN}" "${DST_URL}" --path="$DST_PATH" --allow-root --precise --recurse-objects || true
wp search-replace "https://${SRC_DOMAIN}" "${DST_URL}" --path="$DST_PATH" --allow-root --precise --recurse-objects || true
wp search-replace "http://www.${SRC_DOMAIN}" "${DST_URL}" --path="$DST_PATH" --allow-root --precise --recurse-objects || true
wp search-replace "https://www.${SRC_DOMAIN}" "${DST_URL}" --path="$DST_PATH" --allow-root --precise --recurse-objects || true

# Xóa cache WordPress
wp cache flush --path="$DST_PATH" --allow-root || true

# 5. Phân quyền chuẩn cho Nginx / aaPanel
echo -e "${YELLOW}[5/5] Phân quyền chuẩn cho thư mục web...${NC}"
chown -R www:www "$DST_PATH"
find "$DST_PATH" -type d -exec chmod 755 {} \;
find "$DST_PATH" -type f -exec chmod 644 {} \;

echo -e "\n${GREEN}=====================================================${NC}"
echo -e "${GREEN}  CLONE WEBSITE THÀNH CÔNG!                          ${NC}"
echo -e "${GREEN}  Website mới: ${DST_URL}                             ${NC}"
echo -e "${GREEN}  Thư mục:     ${DST_PATH}                            ${NC}"
echo -e "${GREEN}=====================================================${NC}\n"
