#!/usr/bin/env bash
# ==============================================================================
# SCRIPT TẠO WEBSITE WORDPRESS TỰ ĐỘNG 100% (MULTI-TENANT ISOLATED V3)
# Đảm bảo cô lập tuyệt đối - Không bao giờ ảnh hưởng tới các website cũ
# ==============================================================================

set -e

DOMAIN=$1
if [ -z "$DOMAIN" ]; then
    echo "❌ Lỗi: Vui lòng nhập tên miền. Cú pháp: auto-site domain.com"
    exit 1
fi

ROOT_DOMAIN=$(echo "$DOMAIN" | awk -F. '{if (NF>2) print $(NF-1)"."$NF; else print $0}')
WEB_ROOT="/www/wwwroot/${DOMAIN}"
DB_NAME="db_${DOMAIN//./_}"; DB_NAME=${DB_NAME:0:15}
DB_USER="u_${DOMAIN//./_}"; DB_USER=${DB_USER:0:15}
DB_PASS=$(openssl rand -base64 12)
ADMIN_USER="${WP_DEFAULT_ADMIN_USER:-admin}"
ADMIN_PASS="${WP_DEFAULT_ADMIN_PASS:-$(openssl rand -base64 16)}"
ADMIN_EMAIL="${WP_DEFAULT_ADMIN_EMAIL:-admin@${DOMAIN}}"
SITE_TITLE="${DOMAIN}"

echo "=========================================================="
echo "  🚀 BẮT ĐẦU TẠO WEBSITE MỚI: ${DOMAIN}"
echo "=========================================================="

# 1. Trỏ DNS Cloudflare
echo "[1/6] Trỏ DNS Cloudflare & Bật SSL Flexible..."
cf-dns "${DOMAIN}" 2>/dev/null || true

# 2. Tạo Database MariaDB 10.11 chuẩn cú pháp tách biệt
echo "[2/6] Tạo Database & Cấp quyền MariaDB chuẩn..."
MYSQL_ROOT_PASS=$(python3 -c "import sqlite3; conn=sqlite3.connect('/www/server/panel/data/default.db'); c=conn.cursor(); print(c.execute('SELECT mysql_root FROM config LIMIT 1').fetchone()[0])" 2>/dev/null || cat /www/server/data/default.pl 2>/dev/null || echo "")

mysql -u root -p"${MYSQL_ROOT_PASS}" << EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
ALTER USER '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';

CREATE USER IF NOT EXISTS '${DB_USER}'@'127.0.0.1' IDENTIFIED BY '${DB_PASS}';
ALTER USER '${DB_USER}'@'127.0.0.1' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'127.0.0.1';

FLUSH PRIVILEGES;
EOF

# 3. Tải & Cài đặt WordPress Core
echo "[3/6] Cài đặt WordPress Core & Khởi tạo Admin Account (${ADMIN_USER})..."
mkdir -p "${WEB_ROOT}"
cd "${WEB_ROOT}"

if [ ! -f "${WEB_ROOT}/wp-config.php" ]; then
    wp core download --locale=vi --path="${WEB_ROOT}" --allow-root 2>/dev/null || wp core download --path="${WEB_ROOT}" --allow-root
    wp config create --dbname="${DB_NAME}" --dbuser="${DB_USER}" --dbpass="${DB_PASS}" --dbhost="127.0.0.1" --path="${WEB_ROOT}" --allow-root
    sed -i "/<?php/a if (isset(\$_SERVER['HTTP_CF_VISITOR']) && strpos(\$_SERVER['HTTP_CF_VISITOR'], 'https') !== false) { \$_SERVER['HTTPS'] = 'on'; }" "${WEB_ROOT}/wp-config.php"
    sed -i "/<?php/a define('DISALLOW_FILE_EDIT', true);" "${WEB_ROOT}/wp-config.php"
    
    wp core install --url="https://${DOMAIN}" --title="${SITE_TITLE}" --admin_user="${ADMIN_USER}" --admin_password="${ADMIN_PASS}" --admin_email="${ADMIN_EMAIL}" --skip-email --path="${WEB_ROOT}" --allow-root
fi

# 4. Cài đặt 4 Plugin thiết yếu
echo "[4/6] Cài đặt 4 Plugin thiết yếu (RankMath, Pretty Links, Classic Editor, TOC)..."
wp plugin install pretty-link seo-by-rank-math easy-table-of-contents classic-editor astra --activate --path="${WEB_ROOT}" --allow-root 2>/dev/null || true
wp theme activate astra --path="${WEB_ROOT}" --allow-root 2>/dev/null || true

# 5. Tạo SSL riêng biệt & Cấu hình Nginx VHost chống DDoS
echo "[5/6] Cấu hình Nginx Armor & SSL riêng biệt..."
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout "/etc/nginx/ssl/${DOMAIN}.key" \
  -out "/etc/nginx/ssl/${DOMAIN}.crt" \
  -subj "/C=VN/ST=HCM/L=HCM/O=Cloudflare/CN=${DOMAIN}" 2>/dev/null || true

cat << EOF > "/www/server/panel/vhost/nginx/${DOMAIN}.conf"
server {
    listen 80;
    listen 443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};
    root ${WEB_ROOT};
    index index.php index.html index.htm;

    ssl_certificate /etc/nginx/ssl/${DOMAIN}.crt;
    ssl_certificate_key /etc/nginx/ssl/${DOMAIN}.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    include /www/server/nginx/conf/cloudflare_ips.conf;

    # Bảo mật: Chặn XML-RPC & Chặn thực thi PHP trong thư mục ảnh
    location = /xmlrpc.php { deny all; }
    location ~* /(?:uploads|files|wp-content/uploads)/.*\.php$ { deny all; }
    location ~* /(\.git|\.env|\.user\.ini|\.htaccess|wp-config\.php|readme\.html|license\.txt) { deny all; return 404; }

    # Permalinks
    location / {
        try_files \$uri \$uri/ /index.php?\$args;
    }

    # FastCGI PHP 8.4
    location ~ \.php$ {
        try_files \$uri =404;
        fastcgi_pass unix:/tmp/php-cgi-84.sock;
        fastcgi_index index.php;
        include fastcgi.conf;
    }

    access_log /www/wwwlogs/${DOMAIN}.log;
    error_log /www/wwwlogs/${DOMAIN}.error.log;
}
EOF

# 6. Phân quyền và reload
echo "[6/6] Hoàn tất phân quyền & Khởi động Webserver..."
chown -R www:www "${WEB_ROOT}"
chmod -R 755 "${WEB_ROOT}"
find "${WEB_ROOT}" -name "wp-config.php" -exec chmod 600 {} + 2>/dev/null || true
/etc/init.d/nginx reload 2>/dev/null || nginx -s reload

echo "=========================================================="
echo "  🎉 ĐÃ TẠO WEBSITE MỚI THÀNH CÔNG 100%!"
echo "  🌐 Link Web:       https://${DOMAIN}"
echo "  🔑 Link Admin:     https://${DOMAIN}/wp-admin"
echo "  👤 Tài khoản:      ${ADMIN_USER}"
echo "  🔑 Mật khẩu:       ${ADMIN_PASS}"
echo "=========================================================="
