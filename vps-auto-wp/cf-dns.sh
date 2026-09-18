#!/usr/bin/env bash
# ==============================================================================
# CF-DNS: TỰ ĐỘNG TRỎ DNS VÀ BẬT PROXY CLOUDFLARE BẰNG GLOBAL API KEY
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DOMAIN=$1
SERVER_IP=$(curl -s https://api.ipify.org || curl -s https://ifconfig.me)

CF_CONFIG_FILE="/root/.cloudflare_credentials"

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}[LỖI] Thiếu tên miền!${NC}"
    echo -e "Cú pháp: ${YELLOW}cf-dns <domain.com>${NC}"
    exit 1
fi

# Tự động lấy cấu hình nếu đã lưu trước đó
if [ -f "$CF_CONFIG_FILE" ]; then
    source "$CF_CONFIG_FILE"
fi

if [ -z "$CF_EMAIL" ] || [ -z "$CF_KEY" ]; then
    echo -e "${YELLOW}Nhập thông tin Cloudflare Global API của bạn:${NC}"
    read -r -p "Email Cloudflare: " CF_EMAIL
    read -r -p "Global API Key: " CF_KEY
    
    # Lưu lại để lần sau không cần nhập lại
    cat << EOF > "$CF_CONFIG_FILE"
CF_EMAIL="${CF_EMAIL}"
CF_KEY="${CF_KEY}"
EOF
    chmod 600 "$CF_CONFIG_FILE"
    echo -e "${GREEN}--> Đã lưu thông tin xác thực vào ${CF_CONFIG_FILE}${NC}"
fi

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}  ĐANG KẾT NỐI CLOUDFLARE CHO DOMAIN: ${DOMAIN}${NC}"
echo -e "${GREEN}  IP VPS của bạn: ${SERVER_IP}${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 1. Tìm Zone ID của domain
# Trích xuất root domain (ví dụ: sub.domain.com -> domain.com)
ROOT_DOMAIN=$(echo "$DOMAIN" | awk -F. '{if (NF>2) print $(NF-1)"."$NF; else print $0}')

ZONE_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=${ROOT_DOMAIN}" \
     -H "X-Auth-Email: ${CF_EMAIL}" \
     -H "X-Auth-Key: ${CF_KEY}" \
     -H "Content-Type: application/json" | jq -r '.result[0].id // empty')

if [ -z "$ZONE_ID" ]; then
    echo -e "${RED}[LỖI] Không tìm thấy tên miền ${ROOT_DOMAIN} trong tài khoản Cloudflare!${NC}"
    echo -e "${YELLOW}Vui lòng đảm bảo bạn đã Add site ${ROOT_DOMAIN} vào Cloudflare trước.${NC}"
    exit 1
fi

echo -e "${GREEN}--> Tìm thấy Zone ID: ${ZONE_ID}${NC}"

# 2. Kiểm tra xem bản ghi A đã tồn tại chưa
RECORD_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records?type=A&name=${DOMAIN}" \
     -H "X-Auth-Email: ${CF_EMAIL}" \
     -H "X-Auth-Key: ${CF_KEY}" \
     -H "Content-Type: application/json" | jq -r '.result[0].id // empty')

if [ -n "$RECORD_ID" ]; then
    echo -e "${YELLOW}--> Đang cập nhật bản ghi A trỏ về IP ${SERVER_IP} (Bật Proxy Cam)...${NC}"
    curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${RECORD_ID}" \
         -H "X-Auth-Email: ${CF_EMAIL}" \
         -H "X-Auth-Key: ${CF_KEY}" \
         -H "Content-Type: application/json" \
         --data "{\"type\":\"A\",\"name\":\"${DOMAIN}\",\"content\":\"${SERVER_IP}\",\"ttl\":1,\"proxied\":true}" > /dev/null
else
    echo -e "${YELLOW}--> Đang tạo mới bản ghi A trỏ về IP ${SERVER_IP} (Bật Proxy Cam)...${NC}"
    curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
         -H "X-Auth-Email: ${CF_EMAIL}" \
         -H "X-Auth-Key: ${CF_KEY}" \
         -H "Content-Type: application/json" \
         --data "{\"type\":\"A\",\"name\":\"${DOMAIN}\",\"content\":\"${SERVER_IP}\",\"ttl\":1,\"proxied\":true}" > /dev/null
fi

# 3. Tự động bật chế độ SSL Full
echo -e "${YELLOW}--> Đang tự động cấu hình SSL sang chế độ Full trên Cloudflare...${NC}"
curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/settings/ssl" \
     -H "X-Auth-Email: ${CF_EMAIL}" \
     -H "X-Auth-Key: ${CF_KEY}" \
     -H "Content-Type: application/json" \
     --data '{"value":"full"}' > /dev/null

echo -e "\n${GREEN}=====================================================${NC}"
echo -e "${GREEN}  THÀNH CÔNG! Đã trỏ ${DOMAIN} về VPS (${SERVER_IP})${NC}"
echo -e "${GREEN}  Proxy Cloudflare (Đám mây cam): ĐÃ BẬT           ${NC}"
echo -e "${GREEN}  SSL Full:                       ĐÃ BẬT           ${NC}"
echo -e "${GREEN}=====================================================${NC}\n"
