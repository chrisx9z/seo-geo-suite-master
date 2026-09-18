#!/usr/bin/env bash
# ==============================================================================
# WP-CLEAN-POSTS: AN TOÀN XÓA BÀI VIẾT & DỌN DẸP CACHE WORDPRESS TRÊN AAPANEL
# Tuyệt đối bảo toàn: Pages, tdb_templates (Newspaper), Menus, Attachments
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DOMAIN=$1
FORCE_FLAG=$2

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}[LỖI] Thiếu tên miền!${NC}"
    echo -e "Cú pháp: ${YELLOW}wp-clean-posts <domain.com> [--force]${NC}"
    exit 1
fi

WEB_ROOT="/www/wwwroot/${DOMAIN}"
WP_CONFIG="${WEB_ROOT}/wp-config.php"

if [ ! -f "$WP_CONFIG" ]; then
    echo -e "${RED}[LỖI] Không tìm thấy wp-config.php tại ${WEB_ROOT}${NC}"
    exit 1
fi

# Tự động đọc thông tin kết nối DB từ wp-config.php
DB_NAME=$(grep -E "DB_NAME" "$WP_CONFIG" | awk -F"'" '{print $4}')
DB_USER=$(grep -E "DB_USER" "$WP_CONFIG" | awk -F"'" '{print $4}')
DB_PASS=$(grep -E "DB_PASSWORD" "$WP_CONFIG" | awk -F"'" '{print $4}')
DB_HOST=$(grep -E "DB_HOST" "$WP_CONFIG" | awk -F"'" '{print $4}')
[ -z "$DB_HOST" ] && DB_HOST="127.0.0.1"

echo -e "${BLUE}=====================================================${NC}"
echo -e "${YELLOW}  BẮT ĐẦU DỌN DẸP BÀI VIẾT CHO SITE: ${DOMAIN}${NC}"
echo -e "${BLUE}=====================================================${NC}"

# Hiển thị số lượng trước khi xóa
echo -e "${YELLOW}[1/4] Thống kê post_type hiện tại trong Database (${DB_NAME}):${NC}"
mysql -h "${DB_HOST}" -u "${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" -e \
  "SELECT post_type, count(*) as count FROM wp_posts GROUP BY post_type;"

if [ "$FORCE_FLAG" != "--force" ]; then
    read -r -p "⚠️ Bạn có CHẮC CHẮN muốn xóa toàn bộ 'post' & 'revision' (giữ lại tdb_templates & page)? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Đã hủy thao tác.${NC}"
        exit 0
    fi
fi

# Thực thi xóa an toàn
echo -e "${YELLOW}[2/4] Đang xóa các bài viết (post) & bản nháp (revision)...${NC}"
mysql -h "${DB_HOST}" -u "${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" << 'EOF'
DELETE FROM wp_posts WHERE post_type IN ('post', 'revision');
DELETE pm FROM wp_postmeta pm LEFT JOIN wp_posts wp ON wp.ID = pm.post_id WHERE wp.ID IS NULL;
DELETE tr FROM wp_term_relationships tr LEFT JOIN wp_posts wp ON wp.ID = tr.object_id WHERE wp.ID IS NULL;
DELETE c FROM wp_comments c LEFT JOIN wp_posts wp ON wp.ID = c.comment_post_ID WHERE wp.ID IS NULL;
DELETE cm FROM wp_commentmeta cm LEFT JOIN wp_comments c ON c.comment_ID = cm.comment_id WHERE c.comment_ID IS NULL;
EOF

echo -e "${GREEN}--> Đã dọn sạch bảng wp_posts, wp_postmeta, wp_term_relationships, wp_comments!${NC}"

# Dọn dẹp cache
echo -e "${YELLOW}[3/4] Đang xóa toàn bộ bộ nhớ đệm (WP Rocket, Nginx, WP-CLI)...${NC}"
rm -rf "${WEB_ROOT}/wp-content/cache/"* 2>/dev/null || true
if command -v wp &> /dev/null; then
    wp cache flush --path="${WEB_ROOT}" --allow-root 2>/dev/null || true
fi

# Thống kê sau khi xóa
echo -e "${YELLOW}[4/4] Thống kê post_type sau khi dọn dẹp:${NC}"
mysql -h "${DB_HOST}" -u "${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" -e \
  "SELECT post_type, count(*) as count FROM wp_posts GROUP BY post_type;"

echo -e "\n${GREEN}=====================================================${NC}"
echo -e "${GREEN}  THÀNH CÔNG! Đã dọn sạch bài viết cho ${DOMAIN}.${NC}"
echo -e "${GREEN}  Tất cả templates giao diện, pages và media vẫn an toàn.${NC}"
echo -e "${GREEN}=====================================================${NC}\n"
