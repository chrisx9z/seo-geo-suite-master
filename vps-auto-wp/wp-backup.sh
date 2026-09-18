#!/usr/bin/env bash
# ==============================================================================
# WP-BACKUP: TỰ ĐỘNG SAO LƯU LÊN GOOGLE DRIVE & CHỈ LƯU 3 NGÀY GẦN NHẤT
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DATE_STR=$(date +%Y-%m-%d)
BACKUP_ROOT="/www/backup/wp_daily"
BACKUP_DIR="${BACKUP_ROOT}/${DATE_STR}"
RETENTION_DAYS=3 # Chỉ lưu 3 ngày gần nhất
RCLONE_REMOTE="gdrive:VPS_Backups/wp_daily" # Tên Remote Google Drive

mkdir -p "$BACKUP_DIR"

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}  BẮT ĐẦU SAO LƯU TOÀN BỘ WEBSITE (${DATE_STR})       ${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 1. Quét và sao lưu toàn bộ mã nguồn + Database của tất cả site
for SITE_DIR in /www/wwwroot/*; do
    if [ -d "$SITE_DIR" ] && [ -f "$SITE_DIR/wp-config.php" ]; then
        DOMAIN=$(basename "$SITE_DIR")
        TEMP_DIR="/tmp/bk_${DOMAIN}"
        mkdir -p "$TEMP_DIR"
        
        echo -e "${YELLOW}--> Đang sao lưu: ${DOMAIN}...${NC}"
        
        # Xuất Database
        wp db export "${TEMP_DIR}/db.sql" --path="$SITE_DIR" --allow-root 2>/dev/null || true
        
        # Nén toàn bộ Source Code + Database vào 1 file duy nhất
        TAR_FILE="${BACKUP_DIR}/${DOMAIN}_${DATE_STR}.tar.gz"
        tar -czf "$TAR_FILE" \
            --exclude="wp-content/cache/*" \
            --exclude="*.log" \
            -C "$SITE_DIR" . \
            -C "$TEMP_DIR" db.sql
            
        rm -rf "$TEMP_DIR"
        echo -e "${GREEN}    [OK] Đã tạo file: ${TAR_FILE}${NC}"
    fi
done

# 2. Xóa các bản backup trên VPS cũ hơn 3 ngày
echo -e "${YELLOW}--> Dọn dẹp bản backup trên VPS cũ hơn ${RETENTION_DAYS} ngày...${NC}"
find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d -mtime +2 -exec rm -rf {} + 2>/dev/null || true

# 3. Đồng bộ lên Google Drive qua Rclone (Nếu đã liên kết)
if command -v rclone &> /dev/null && rclone listremotes | grep -q "gdrive:"; then
    echo -e "${YELLOW}--> Đang đồng bộ lên Google Drive (${RCLONE_REMOTE})...${NC}"
    # Dùng rclone sync: Tự động tải bản mới và TỰ ĐỘNG XÓA trên Google Drive các file cũ quá 3 ngày
    rclone sync "${BACKUP_ROOT}" "${RCLONE_REMOTE}" --transfers=4 --checkers=8
    echo -e "${GREEN}--> [THÀNH CÔNG] Đã đồng bộ lên Google Drive và xóa sạch bản cũ!${NC}"
else
    echo -e "${YELLOW}--> Lưu ý: Chưa kết nối Google Drive (gdrive:). File được lưu an toàn tại ${BACKUP_DIR}${NC}"
fi

echo -e "\n${GREEN}=====================================================${NC}"
echo -e "${GREEN}  HOÀN TẤT SAO LƯU! CHỈ GIỮ LẠI 3 NGÀY GẦN NHẤT.     ${NC}"
echo -e "${GREEN}=====================================================${NC}\n"
