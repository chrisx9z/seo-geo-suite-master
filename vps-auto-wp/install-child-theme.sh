#!/usr/bin/env bash
# ==============================================================================
# SCRIPT TỰ ĐỘNG TẠO & KÍCH HOẠT CHILD THEME NEWSPAPER CHO WORDPRESS
# ==============================================================================

set -e

DOMAIN=$1
if [ -z "$DOMAIN" ]; then
    echo "❌ Lỗi: Vui lòng nhập domain. Cú pháp: install-child-theme <domain.com>"
    exit 1
fi

WEB_ROOT="/www/wwwroot/${DOMAIN}"
THEMES_DIR="${WEB_ROOT}/wp-content/themes"
CHILD_DIR="${THEMES_DIR}/newspaper-child"

echo "=========================================================="
echo "  🚀 BẮT ĐẦU CÀI ĐẶT CHILD THEME CHO: ${DOMAIN}"
echo "=========================================================="

if [ ! -d "${THEMES_DIR}" ]; then
    echo "❌ Lỗi: Không tìm thấy thư mục themes tại ${THEMES_DIR}"
    exit 1
fi

# Tự động phát hiện tên thư mục theme Newspaper cha (viết hoa hay thường)
PARENT_THEME="Newspaper"
if [ -d "${THEMES_DIR}/newspaper" ]; then
    PARENT_THEME="newspaper"
elif [ -d "${THEMES_DIR}/Newspaper" ]; then
    PARENT_THEME="Newspaper"
fi

echo "🔍 Theme cha được phát hiện: ${PARENT_THEME}"

# Tạo thư mục Child Theme
mkdir -p "${CHILD_DIR}"

# 1. Tạo file style.css
cat << EOF > "${CHILD_DIR}/style.css"
/*
Theme Name: Newspaper Child
Theme URI: https://tagdiv.com/newspaper/
Description: Newspaper Child Theme by tagDiv
Author: tagDiv
Author URI: https://tagdiv.com
Template: ${PARENT_THEME}
Version: 1.0.0
Text Domain: newspaper-child
*/

/* ==========================================================================
   Tùy chỉnh CSS của bạn bắt đầu từ đây:
   ========================================================================== */
EOF

# 2. Tạo file functions.php
cat << 'EOF' > "${CHILD_DIR}/functions.php"
<?php
/**
 * Newspaper Child Theme Functions
 */

if ( !defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Nạp stylesheet của Child Theme
 */
add_action( 'wp_enqueue_scripts', 'newspaper_child_theme_enqueue_styles', 11 );
function newspaper_child_theme_enqueue_styles() {
    wp_enqueue_style( 'newspaper-child-style', get_stylesheet_directory_uri() . '/style.css', array( 'td-theme' ), wp_get_theme()->get('Version') );
}

/* ==========================================================================
   Viết các hàm tùy chỉnh PHP của bạn bên dưới:
   ========================================================================== */
EOF

# 3. Phân quyền chuẩn www:www 755
chown -R www:www "${CHILD_DIR}"
chmod -R 755 "${CHILD_DIR}"

# 4. Kích hoạt theme bằng WP-CLI nếu có
if command -v wp &> /dev/null; then
    echo "⚡ Đang kích hoạt Newspaper Child qua WP-CLI..."
    wp theme activate newspaper-child --path="${WEB_ROOT}" --allow-root || true
fi

echo "=========================================================="
echo "  🎉 HOÀN TẤT! Child Theme Newspaper đã được cài đặt & kích hoạt."
echo "  📁 Đường dẫn: ${CHILD_DIR}"
echo "=========================================================="
