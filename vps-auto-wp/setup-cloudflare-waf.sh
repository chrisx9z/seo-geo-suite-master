#!/usr/bin/env bash
# ==============================================================================
# SETUP-CLOUDFLARE-WAF: FAIL2BAN + CLOUDFLARE GLOBAL API KEY CHẶN IP TỰ ĐỘNG
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}  CẤU HÌNH FAIL2BAN + CLOUDFLARE GLOBAL API KEY      ${NC}"
echo -e "${BLUE}=====================================================${NC}"

if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[LỖI] Vui lòng chạy với quyền root (sudo setup-cloudflare-waf)${NC}"
  exit 1
fi

CF_CONFIG_FILE="/root/.cloudflare_credentials"

# Tự động lấy cấu hình nếu đã lưu trước đó
if [ -f "$CF_CONFIG_FILE" ]; then
    source "$CF_CONFIG_FILE"
fi

if [ -z "$CF_EMAIL" ] || [ -z "$CF_KEY" ]; then
    echo -e "${YELLOW}Nhập thông tin Cloudflare của bạn:${NC}"
    read -r -p "Email Cloudflare: " CF_EMAIL
    read -r -p "Global API Key: " CF_KEY
    
    cat << EOF > "$CF_CONFIG_FILE"
CF_EMAIL="${CF_EMAIL}"
CF_KEY="${CF_KEY}"
EOF
    chmod 600 "$CF_CONFIG_FILE"
fi

# 1. Cấu hình Action Cloudflare trong Fail2ban dùng Global API Key
echo -e "${YELLOW}[1/4] Đang cập nhật cấu hình /etc/fail2ban/action.d/cloudflare.conf...${NC}"
cat << EOF > /etc/fail2ban/action.d/cloudflare.conf
[Definition]
actionstart = 
actionstop = 
actioncheck = 

actionban = curl -s -X POST "https://api.cloudflare.com/client/v4/user/firewall/access_rules/rules" \\
            -H "X-Auth-Email: <cfuser>" \\
            -H "X-Auth-Key: <cfkey>" \\
            -H "Content-Type: application/json" \\
            --data '{"mode":"block","configuration":{"target":"ip","value":"<ip>"},"notes":"Fail2ban auto ban on aaPanel"}'

actionunban = RULE_ID=\$(curl -s -X GET "https://api.cloudflare.com/client/v4/user/firewall/access_rules/rules?configuration.value=<ip>" \\
              -H "X-Auth-Email: <cfuser>" \\
              -H "X-Auth-Key: <cfkey>" \\
              -H "Content-Type: application/json" | jq -r '.result[0].id // empty') ; \\
              if [ -n "\$RULE_ID" ]; then \\
                curl -s -X DELETE "https://api.cloudflare.com/client/v4/user/firewall/access_rules/rules/\$RULE_ID" \\
                -H "X-Auth-Email: <cfuser>" \\
                -H "X-Auth-Key: <cfkey>" \\
                -H "Content-Type: application/json" ; \\
              fi

[Init]
cfuser = ${CF_EMAIL}
cfkey = ${CF_KEY}
EOF

# 2. Cấu hình Filter cho WordPress (Bắt các request bruteforce wp-login và xmlrpc)
echo -e "${YELLOW}[2/4] Đang tạo bộ lọc WordPress Brute-force & XML-RPC...${NC}"
cat << 'EOF' > /etc/fail2ban/filter.d/wordpress-auth.conf
[Definition]
failregex = ^<HOST> .* "POST /wp-login\.php.*" (403|401|200)
            ^<HOST> .* "POST /xmlrpc\.php.*" (403|401|200)
ignoreregex =
EOF

# 3. Kích hoạt Jail trong Fail2ban
echo -e "${YELLOW}[3/4] Đang kích hoạt Jail bảo vệ WordPress với hành động Cloudflare...${NC}"
cat << EOF > /etc/fail2ban/jail.d/wordpress.local
[wordpress-cloudflare]
enabled = true
port = http,https
filter = wordpress-auth
logpath = /www/wwwlogs/*.log
maxretry = 5
findtime = 300
bantime = 86400
action = cloudflare
EOF

# 4. Cấu hình Nginx aaPanel nhận Real IP từ Cloudflare
echo -e "${YELLOW}[4/4] Đang cập nhật dải IP Cloudflare cho Nginx aaPanel...${NC}"
CF_CONF_DIR="/www/server/nginx/conf"
if [ -d "$CF_CONF_DIR" ]; then
    CF_IP_FILE="${CF_CONF_DIR}/cloudflare_ips.conf"
    echo "# Cloudflare Real IP Configuration" > "$CF_IP_FILE"
    for ip in $(curl -s https://www.cloudflare.com/ips-v4); do
        echo "set_real_ip_from $ip;" >> "$CF_IP_FILE"
    done
    for ip in $(curl -s https://www.cloudflare.com/ips-v6); do
        echo "set_real_ip_from $ip;" >> "$CF_IP_FILE"
    done
    echo "real_ip_header CF-Connecting-IP;" >> "$CF_IP_FILE"
    echo -e "${GREEN}--> Đã lưu danh sách IP Cloudflare tại ${CF_IP_FILE}${NC}"
fi

# Khởi động lại dịch vụ
systemctl restart fail2ban
echo -e "\n${GREEN}=====================================================${NC}"
echo -e "${GREEN}  CẤU HÌNH BẢO MẬT CLOUDFLARE WAF THÀNH CÔNG!       ${NC}"
echo -e "${GREEN}  Từ nay, bất kỳ IP nào dò mật khẩu hoặc spam request${NC}"
echo -e "${GREEN}  sẽ bị chặn ngay tại tầng mạng Cloudflare Edge!     ${NC}"
echo -e "${GREEN}=====================================================${NC}\n"
