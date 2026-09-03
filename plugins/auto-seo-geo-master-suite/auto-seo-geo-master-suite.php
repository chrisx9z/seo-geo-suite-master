<?php
/**
 * Plugin Name: Auto SEO GEO Master Suite
 * Plugin URI: https://github.com/vibe-code/auto-seo-geo-suite
 * Description: Universal Multi-site SEO GEO Framework: PC 1170px Centered Header, Ultra-Modern Mobile Magazine Layout (Story Pills & Swipe Carousels), Zero-Overlap Multilingual Switcher, Dynamic 3-Language SEO Meta & Hreflang Engine.
 * Version: 5.1.0
 * Author: Master SEO GEO Architecture Suite
 * Text Domain: auto-seo-geo
 * Domain Path: /languages
 */
if (!defined('ABSPATH')) exit;

class Auto_SEO_GEO_Master_Suite {
    private static $version = '5.1.0';
    private static $site_config = null;

    public function __construct() {
        self::load_configuration();
        add_action('init', array($this, 'handle_lang_cookie'));
        add_action('init', array($this, 'register_rankmath_rest_fields'));
        add_action('init', array($this, 'handle_indexnow_verification'));
        add_action('publish_post', array($this, 'auto_ping_indexnow_on_publish'), 10, 2);
        add_action('init', array($this, 'handle_news_sitemap'));
        add_action('post_updated', array($this, 'track_slug_changes'), 10, 3);
        add_action('template_redirect', array($this, 'handle_automatic_slug_301_redirect'), 1);
        add_action('template_redirect', array($this, 'auto_heal_404_fuzzy_redirect'));
        add_action('wp_head', array($this, 'render_head_seo_tags'), 1);
        add_action('wp_head', array($this, 'render_self_canonical'), 2);
        add_action('wp_head', array($this, 'render_site_favicon'), 2);
        add_filter('rank_math/canonical', array($this, 'filter_rankmath_canonical'), 9999);
        if (!shortcode_exists('ez-toc')) {
            add_shortcode('ez-toc', array($this, 'render_ez_toc_fallback'));
        }

        add_filter('pre_get_document_title', array($this, 'filter_document_title'), 9999);
        add_filter('rank_math/frontend/title', array($this, 'filter_document_title'), 9999);
        add_filter('rank_math/frontend/description', array($this, 'filter_meta_description'), 9999);
        add_filter('language_attributes', array($this, 'filter_language_attributes'), 99);
        add_action('wp_head', array($this, 'output_master_css'), 9999);
        add_action('wp_footer', array($this, 'output_master_scripts'), 9999);
    }

    
    /**
     * Responds to IndexNow key verification requests (e.g. /<32_char_hex>.txt)
     */
    public function handle_indexnow_verification() {
        $uri = trim($_SERVER['REQUEST_URI'] ?? '', '/');
        $path = parse_url($uri, PHP_URL_PATH);
        if (preg_match('/^([a-f0-9]{16,64})\.txt$/i', $path, $matches)) {
            header('Content-Type: text/plain; charset=utf-8');
            header('X-Robots-Tag: noindex');
            echo $matches[1];
            exit;
        }
    }

    /**
     * Automatically pings Bing IndexNow when any post is published
     */
    public function auto_ping_indexnow_on_publish($post_id, $post) {
        if (wp_is_post_revision($post_id) || $post->post_status !== 'publish') {
            return;
        }
        $url = get_permalink($post_id);
        $host = parse_url(home_url(), PHP_URL_HOST);
        $key = md5('indexnow_key_' . $host);
        
        $body = json_encode(array(
            'host' => $host,
            'key' => $key,
            'keyLocation' => "https://{$host}/{$key}.txt",
            'urlList' => array($url)
        ));
        
        wp_remote_post('https://api.indexnow.org/indexnow', array(
            'headers' => array('Content-Type' => 'application/json; charset=utf-8'),
            'body' => $body,
            'timeout' => 5,
            'blocking' => false
        ));
    }

    
    /**
     * Google News XML Sitemap Endpoint (/news-sitemap.xml)
     */
    public function handle_news_sitemap() {
        $uri = trim($_SERVER['REQUEST_URI'] ?? '', '/');
        $path = parse_url($uri, PHP_URL_PATH);
        if ($path === 'news-sitemap.xml') {
            header('Content-Type: text/xml; charset=utf-8');
            header('X-Robots-Tag: noindex, follow');

            $recent_posts = get_posts(array(
                'numberposts' => 50,
                'post_status' => 'publish',
                'date_query' => array(
                    array(
                        'after' => '7 days ago'
                    )
                )
            ));
            if (empty($recent_posts)) {
                $recent_posts = get_posts(array('numberposts' => 15, 'post_status' => 'publish'));
            }

            $site_name = get_bloginfo('name');
            echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
            echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">' . "\n";
            foreach ($recent_posts as $p) {
                $url = get_permalink($p->ID);
                $pub_date = get_the_date('c', $p->ID);
                $title = htmlspecialchars($p->post_title, ENT_XML1, 'UTF-8');
                echo "  <url>\n";
                echo "    <loc>{$url}</loc>\n";
                echo "    <news:news>\n";
                echo "      <news:publication>\n";
                echo "        <news:name>" . htmlspecialchars($site_name, ENT_XML1, 'UTF-8') . "</news:name>\n";
                echo "        <news:language>vi</news:language>\n";
                echo "      </news:publication>\n";
                echo "      <news:publication_date>{$pub_date}</news:publication_date>\n";
                echo "      <news:title>{$title}</news:title>\n";
                echo "    </news:news>\n";
                echo "  </url>\n";
            }
            echo '</urlset>';
            exit;
        }
    }

    /**
     * Track post slug changes and record 301 permanent redirect mapping
     */
    public function track_slug_changes($post_id, $post_after, $post_before) {
        if (wp_is_post_revision($post_id) || empty($post_before) || empty($post_after)) {
            return;
        }
        $old_slug = $post_before->post_name;
        $new_slug = $post_after->post_name;
        if (!empty($old_slug) && !empty($new_slug) && $old_slug !== $new_slug) {
            // 1. Store in post meta history
            $history = get_post_meta($post_id, '_auto_seo_old_slugs', true);
            if (!is_array($history)) $history = array();
            if (!in_array($old_slug, $history)) {
                $history[] = $old_slug;
                update_post_meta($post_id, '_auto_seo_old_slugs', $history);
            }
            add_post_meta($post_id, '_wp_old_slug', $old_slug);

            // 2. Store in global fast-lookup table
            $redirects = get_option('auto_seo_slug_redirects', array());
            if (!is_array($redirects)) $redirects = array();
            $redirects[$old_slug] = $post_id;
            update_option('auto_seo_slug_redirects', $redirects);
        }
    }

    /**
     * Automatic 301 Permanent Redirect when an old URL / slug is requested
     */
    public function handle_automatic_slug_301_redirect() {
        $req_uri = trim($_SERVER['REQUEST_URI'] ?? '', '/');
        $req_slug = sanitize_title(basename(parse_url($req_uri, PHP_URL_PATH)));
        if (empty($req_slug)) {
            return;
        }

        // Check 1: Fast option lookup
        $redirects = get_option('auto_seo_slug_redirects', array());
        if (is_array($redirects) && isset($redirects[$req_slug])) {
            $target_id = $redirects[$req_slug];
            $target_url = get_permalink($target_id);
            if ($target_url && strpos($target_url, $req_slug) === false) {
                wp_redirect($target_url, 301);
                exit;
            }
        }

        // Check 2: Query post meta if 404
        if (is_404()) {
            $matched_posts = get_posts(array(
                'post_type' => 'post',
                'post_status' => 'publish',
                'meta_query' => array(
                    'relation' => 'OR',
                    array(
                        'key' => '_wp_old_slug',
                        'value' => $req_slug,
                        'compare' => '='
                    ),
                    array(
                        'key' => '_auto_seo_old_slugs',
                        'value' => $req_slug,
                        'compare' => 'LIKE'
                    )
                ),
                'numberposts' => 1
            ));

            if (!empty($matched_posts)) {
                $target_url = get_permalink($matched_posts[0]->ID);
                if ($target_url) {
                    wp_redirect($target_url, 301);
                    exit;
                }
            }
        }
    }

    /**
     * Auto 404 Healer with Fuzzy 301 Redirect
     */
    public function auto_heal_404_fuzzy_redirect() {
        if (!is_404()) {
            return;
        }
        $req_uri = trim($_SERVER['REQUEST_URI'] ?? '', '/');
        $slug = sanitize_title(basename(parse_url($req_uri, PHP_URL_PATH)));
        if (empty($slug)) {
            return;
        }

        $all_posts = get_posts(array(
            'numberposts' => 100,
            'post_status' => 'publish',
            'fields' => 'ids'
        ));

        $best_id = null;
        $highest_percent = 0;

        foreach ($all_posts as $pid) {
            $post_slug = get_post_field('post_name', $pid);
            similar_text($slug, $post_slug, $percent);
            if ($percent > $highest_percent) {
                $highest_percent = $percent;
                $best_id = $pid;
            }
        }

        if ($best_id && $highest_percent >= 35) {
            wp_redirect(get_permalink($best_id), 301);
            exit;
        }
    }

    
    /**
     * Expose RankMath SEO fields to WordPress REST API for automated scoring
     */
    public function register_rankmath_rest_fields() {
        $fields = array('rank_math_focus_keyword', 'rank_math_title', 'rank_math_description', 'rank_math_pillar_content');
        foreach ($fields as $field) {
            register_post_meta('post', $field, array(
                'show_in_rest' => true,
                'single' => true,
                'type' => 'string',
                'auth_callback' => function() { return current_user_can('edit_posts'); }
            ));
        }
    }

    
    /**
     * Rule 4: Self-referencing Canonical tag (strips query parameters)
     */
    public function render_self_canonical() {
        if (is_singular('post') || is_page()) {
            $canonical_url = strtok(get_permalink(), '?');
            echo '<link rel="canonical" href="' . esc_url($canonical_url) . '" />' . "\n";
        }
    }

    public function filter_rankmath_canonical($canonical) {
        if (is_singular('post') || is_page()) {
            return esc_url(strtok(get_permalink(), '?'));
        }
        return $canonical;
    }

    /**
     * Rule: Ensure High-Resolution Favicon & PWA Theme Color Meta Tags
     */
    public function render_site_favicon() {
        if (!has_site_icon()) {
            $fav = home_url('/favicon.ico');
            echo '<link rel="shortcut icon" href="' . esc_url($fav) . '" />' . "\n";
        }
        echo '<meta name="theme-color" content="#0f172a" />' . "\n";
    }

    /**
     * Rule 1: Fallback shortcode for [ez-toc] (Easy Table of Contents standard)
     */
    public function render_ez_toc_fallback() {
        global $post;
        if (!$post || empty($post->post_content)) return '';

        preg_match_all('/<h([2-3])([^>]*)>(.*?)<\/h\1>/is', $post->post_content, $matches, PREG_SET_ORDER);
        if (empty($matches)) return '';

        $html = '<div class="ez-toc-container" style="background:#0f172a; border:1px solid #1e293b; border-radius:8px; padding:18px 24px; margin:24px 0;">';
        $html .= '<p class="ez-toc-title" style="margin:0 0 10px 0; color:#38bdf8; font-weight:700; font-size:1.05em;">📑 Mục Lục Nội Dung</p>';
        $html .= '<ul class="ez-toc-list" style="margin:0; padding-left:18px; line-height:1.8; color:#cbd5e1; font-size:0.92em;">';
        foreach ($matches as $m) {
            $level = $m[1];
            $title = strip_tags($m[3]);
            $anchor = sanitize_title($title);
            $indent = ($level == '3') ? 'style="margin-left:16px;"' : '';
            $html .= "<li {$indent}><a href='#{$anchor}' style='color:#38bdf8; text-decoration:none;'>{$title}</a></li>";
        }
        $html .= '</ul></div>';
        return $html;
    }

    private static function load_configuration() {
        $site_name = get_bloginfo('name');
        $site_desc = get_bloginfo('description');
        
        self::$site_config = array(
            'brand' => array(
                'favicon' => get_site_icon_url(512),
                'logo' => get_header_image() ? get_header_image() : '',
                'container_width' => '1170px'
            ),
            'seo' => array(
                'vi' => array(
                    'title' => !empty($site_name) ? $site_name . ' - ' . $site_desc : 'Cổng Thông Tin Công Nghệ & AI',
                    'tagline' => $site_desc,
                    'description' => !empty($site_desc) ? $site_desc : 'Chuyên trang cập nhật tin tức công nghệ, AI và giải pháp tự động hóa.',
                    'keywords' => 'công nghệ, trí tuệ nhân tạo, AI tools, SaaS, tự động hóa'
                ),
                'en' => array(
                    'title' => !empty($site_name) ? $site_name . ' - Leading Tech & AI Innovation Hub' : 'Leading Tech & AI Innovation Hub',
                    'tagline' => 'The Future of Technology & Automated Systems',
                    'description' => 'The premier hub for cutting-edge Artificial Intelligence insights, tech reviews, and automated systems.',
                    'keywords' => 'artificial intelligence, tech innovation, top AI tools, automation'
                ),
                'zh' => array(
                    'title' => !empty($site_name) ? $site_name . ' - 前沿科技与人工智能商业门户' : '前沿科技与人工智能商业门户',
                    'tagline' => '聚焦最新科技前沿与数字化商业',
                    'description' => '领先的科技与人工智能商业门户，专注于前沿技术洞察与数字化商业策略。',
                    'keywords' => '人工智能, 科技资讯, 数字化商业, 自动化'
                )
            )
        );
    }

    public static function get_current_lang() {
        if (!empty($_GET['lang']) && in_array($_GET['lang'], array('vi', 'en', 'zh'))) {
            return sanitize_text_field($_GET['lang']);
        }
        if (!empty($_COOKIE['vbm_lang']) && in_array($_COOKIE['vbm_lang'], array('vi', 'en', 'zh'))) {
            return sanitize_text_field($_COOKIE['vbm_lang']);
        }
        if (!empty($_COOKIE['googtrans'])) {
            if (strpos($_COOKIE['googtrans'], 'zh') !== false) return 'zh';
            if (strpos($_COOKIE['googtrans'], 'en') !== false) return 'en';
            if (strpos($_COOKIE['googtrans'], 'vi') !== false) return 'vi';
        }
        $browser_lang = !empty($_SERVER['HTTP_ACCEPT_LANGUAGE']) ? $_SERVER['HTTP_ACCEPT_LANGUAGE'] : '';
        if (preg_match('/^(zh|zh-cn|zh-tw|zh-hk)/i', $browser_lang)) return 'zh';
        if (preg_match('/^(en|en-us|en-gb)/i', $browser_lang)) return 'en';
        return 'vi';
    }

    public function handle_lang_cookie() {
        if (is_admin()) return;
        if (!empty($_GET['lang']) && in_array($_GET['lang'], array('vi', 'en', 'zh'))) {
            $lang = sanitize_text_field($_GET['lang']);
            setcookie('vbm_lang', $lang, time() + (86400 * 30), '/');
            if ($lang === 'vi') {
                setcookie('googtrans', '', time() - 3600, '/');
                setcookie('googtrans', '', time() - 3600, '/', '.' . $_SERVER['HTTP_HOST']);
            } elseif ($lang === 'en') {
                setcookie('googtrans', '/vi/en', time() + (86400 * 30), '/');
                setcookie('googtrans', '/vi/en', time() + (86400 * 30), '/', '.' . $_SERVER['HTTP_HOST']);
            } elseif ($lang === 'zh') {
                setcookie('googtrans', '/vi/zh-CN', time() + (86400 * 30), '/');
                setcookie('googtrans', '/vi/zh-CN', time() + (86400 * 30), '/', '.' . $_SERVER['HTTP_HOST']);
            }
        }
    }

    public function filter_document_title($title) {
        $lang = self::get_current_lang();
        $seo = isset(self::$site_config['seo'][$lang]) ? self::$site_config['seo'][$lang] : self::$site_config['seo']['vi'];
        if (is_front_page() || is_home()) {
            return $seo['title'];
        }
        if (is_singular()) {
            $post_title = get_the_title();
            return $post_title ? $post_title . ' - ' . get_bloginfo('name') : $seo['title'];
        }
        return !empty($title) && $title !== '-' ? $title . ' - ' . get_bloginfo('name') : $seo['title'];
    }

    public function filter_meta_description($description) {
        $lang = self::get_current_lang();
        $seo = isset(self::$site_config['seo'][$lang]) ? self::$site_config['seo'][$lang] : self::$site_config['seo']['vi'];
        if (is_front_page() || is_home()) {
            return $seo['description'];
        }
        return $description;
    }

    public function filter_language_attributes($output) {
        $lang = self::get_current_lang();
        $map = array('vi' => 'lang="vi-VN"', 'en' => 'lang="en-US"', 'zh' => 'lang="zh-CN"');
        $tag = isset($map[$lang]) ? $map[$lang] : 'lang="vi-VN"';
        return preg_replace('/lang="[^"]*"/', $tag, $output);
    }

    public function render_head_seo_tags() {
        global $wp;
        $lang = self::get_current_lang();
        $seo = isset(self::$site_config['seo'][$lang]) ? self::$site_config['seo'][$lang] : self::$site_config['seo']['vi'];
        $brand = self::$site_config['brand'];

        $current_url = home_url(add_query_arg(array(), $wp->request));
        $clean_url = remove_query_arg('lang', $current_url);
        $clean_url = ($clean_url === home_url() || $clean_url === home_url('/')) ? home_url('/') : trailingslashit($clean_url);

        $url_vi = add_query_arg('lang', 'vi', $clean_url);
        $url_en = add_query_arg('lang', 'en', $clean_url);
        $url_zh = add_query_arg('lang', 'zh', $clean_url);

        if (!empty($brand['favicon'])) {
            echo '<link rel="icon" type="image/png" sizes="512x512" href="' . esc_url($brand['favicon']) . '" />' . "\n";
            echo '<link rel="apple-touch-icon" href="' . esc_url($brand['favicon']) . '" />' . "\n";
        }

        if (is_front_page() || is_home()) {
            echo '<meta name="description" content="' . esc_attr($seo['description']) . '" />' . "\n";
            echo '<meta name="keywords" content="' . esc_attr($seo['keywords']) . '" />' . "\n";
            echo '<meta property="og:title" content="' . esc_attr($seo['title']) . '" />' . "\n";
            echo '<meta property="og:description" content="' . esc_attr($seo['description']) . '" />' . "\n";
            echo '<meta property="og:site_name" content="' . esc_attr(get_bloginfo('name')) . '" />' . "\n";
            echo '<meta name="twitter:title" content="' . esc_attr($seo['title']) . '" />' . "\n";
            echo '<meta name="twitter:description" content="' . esc_attr($seo['description']) . '" />' . "\n";
        }

        echo '<link rel="alternate" hreflang="vi" href="' . esc_url($url_vi) . '" />' . "\n";
        echo '<link rel="alternate" hreflang="en" href="' . esc_url($url_en) . '" />' . "\n";
        echo '<link rel="alternate" hreflang="zh-CN" href="' . esc_url($url_zh) . '" />' . "\n";
        echo '<link rel="alternate" hreflang="zh" href="' . esc_url($url_zh) . '" />' . "\n";
        echo '<link rel="alternate" hreflang="x-default" href="' . esc_url($url_en) . '" />' . "\n";
    }

    public function output_master_css() {
        ?>
        <style id="auto-seo-geo-master-style">
        header#header .inner-header, header#header .header-wrap { display: none !important; height: 0 !important; padding: 0 !important; margin: 0 !important; }

        #navigation, #navigation.header-3, .navigation_bar {
            background: linear-gradient(90deg, #ff9800 0%, #ffa726 100%) !important;
            border-bottom: 2px solid #e68900 !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35) !important;
            min-height: 58px !important;
            display: block !important;
            padding: 0 !important;
            margin: 0 !important;
            width: 100% !important;
        }

        #navigation .container, #navigation.header-3 .container, .navigation_bar .container {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: space-between !important;
            min-height: 58px !important;
            max-width: 1170px !important;
            width: 100% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding-left: 15px !important;
            padding-right: 15px !important;
            position: relative !important;
            box-sizing: border-box !important;
        }

        .vbm-nav-logo-wrap {
            display: inline-flex !important;
            align-items: center !important;
            flex: 0 0 auto !important;
            text-decoration: none !important;
            margin-right: 18px !important;
        }
        .vbm-nav-logo-wrap img {
            height: 34px !important;
            width: auto !important;
            max-width: 160px !important;
            display: block !important;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)) !important;
            transition: transform 0.2s ease !important;
        }

        @media (min-width: 961px) {
            .button-menu-mobile { display: none !important; }
            .vbm-mobile-pills-bar { display: none !important; }
            #navigation ul.menu, #navigation.header-3 ul.menu, .penci-navigation-wrap ul.menu {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                align-items: center !important;
                margin: 0 !important;
                padding: 0 !important;
                float: none !important;
                flex: 1 1 auto !important;
                gap: 2px !important;
            }
            #navigation ul.menu > li, #navigation.header-3 ul.menu > li {
                display: inline-flex !important;
                float: none !important;
                margin: 0 !important;
                padding: 0 !important;
                flex-shrink: 0 !important;
            }
            #navigation ul.menu > li > a, #navigation.header-3 ul.menu > li > a {
                font-size: 13px !important;
                font-weight: 800 !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
                color: #111111 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.2px !important;
                padding: 6px 9px !important;
                line-height: 1.2 !important;
                white-space: nowrap !important;
                border-radius: 6px !important;
                transition: all 0.2s ease-in-out !important;
            }
            #navigation ul.menu > li > a:hover, #navigation ul.menu > li.current-menu-item > a, #navigation ul.menu > li.current-menu-parent > a {
                color: #000000 !important;
                background: rgba(0, 0, 0, 0.12) !important;
                box-shadow: inset 0 0 0 1px rgba(0,0,0,0.18) !important;
            }
        }

        #navigation .main-nav-social, .main-nav-social, .header-social, .penci-header-social { display: none !important; }
        .vbm-nav-right-wrap { display: inline-flex !important; align-items: center !important; margin-left: auto !important; flex: 0 0 auto !important; gap: 8px !important; }
        #top-search, .penci-top-search { margin: 0 !important; color: #111111 !important; }
        #top-search a.search-click, .penci-top-search a.search-click {
            color: #111111 !important;
            font-size: 15px !important;
            padding: 5px 8px !important;
            background: rgba(0, 0, 0, 0.08) !important;
            border-radius: 6px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease !important;
        }
        #top-search a.search-click:hover { background: #111111 !important; color: #ff9800 !important; }

        .vbm-lang-switcher-wrap { position: relative; display: inline-flex; align-items: center; }
        .vbm-lang-btn {
            background: #111111 !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            padding: 5px 12px !important;
            border-radius: 18px !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
            transition: all 0.2s ease !important;
            line-height: 1.3 !important;
        }
        .vbm-lang-btn:hover { background: #000000 !important; border-color: #ffffff !important; color: #ff9800 !important; }
        .vbm-lang-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            margin-top: 6px;
            background: #181a1e;
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            min-width: 140px;
            display: none;
            flex-direction: column;
            overflow: hidden;
            z-index: 9999999;
        }
        .vbm-lang-dropdown.active { display: flex; }
        .vbm-lang-item {
            padding: 9px 14px;
            color: #dddddd !important;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            text-decoration: none !important;
            transition: background 0.2s;
            cursor: pointer;
        }
        .vbm-lang-item:hover, .vbm-lang-item.current { background: rgba(255, 152, 0, 0.18); color: #ff9800 !important; font-weight: 700; }

        @media (max-width: 960px) {
            #navigation .container, #navigation.header-3 .container, .navigation_bar .container {
                max-width: 100% !important;
                padding-left: 12px !important;
                padding-right: 12px !important;
                min-height: 52px !important;
            }
            #navigation ul.menu, #navigation.header-3 ul.menu, .penci-navigation-wrap ul.menu, #navigation .navigation {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
                width: 0 !important;
                overflow: hidden !important;
                opacity: 0 !important;
            }
            .button-menu-mobile, .button-menu-mobile.header-3 {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 36px !important;
                height: 36px !important;
                padding: 4px !important;
                margin-right: 8px !important;
                cursor: pointer !important;
                background: rgba(0, 0, 0, 0.08) !important;
                border-radius: 6px !important;
                flex-shrink: 0 !important;
            }
            .button-menu-mobile svg rect { fill: #111111 !important; }
            .vbm-nav-logo-wrap { margin-right: auto !important; }
            .vbm-nav-logo-wrap img { height: 28px !important; max-width: 125px !important; }
            .vbm-nav-right-wrap { gap: 5px !important; }
            .vbm-lang-btn { padding: 4px 7px !important; font-size: 11px !important; }
            #top-search a.search-click { padding: 4px 6px !important; font-size: 13px !important; }

            .vbm-mobile-pills-bar {
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
                padding: 8px 12px !important;
                background: #141619 !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch !important;
                scrollbar-width: none !important;
                position: sticky !important;
                top: 0 !important;
                z-index: 9999 !important;
            }
            .vbm-mobile-pills-bar::-webkit-scrollbar { display: none !important; }
            .vbm-pill {
                display: inline-flex !important;
                align-items: center !important;
                gap: 4px !important;
                padding: 5px 12px !important;
                background: rgba(255, 255, 255, 0.05) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                border-radius: 20px !important;
                color: #cccccc !important;
                font-size: 12px !important;
                font-weight: 700 !important;
                white-space: nowrap !important;
                text-decoration: none !important;
                transition: all 0.2s ease !important;
                flex-shrink: 0 !important;
            }
            .vbm-pill.active, .vbm-pill:hover {
                background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%) !important;
                border-color: #ff9800 !important;
                color: #111111 !important;
                box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3) !important;
            }

            .home-featured-cat { margin-bottom: 22px !important; padding-bottom: 4px !important; }
            .penci-border-arrow.penci-homepage-title { margin-bottom: 12px !important; border-bottom: 2px solid #ff9800 !important; }
            .penci-border-arrow.penci-homepage-title .inner-arrow a span {
                background: #ff9800 !important;
                color: #111111 !important;
                font-size: 13px !important;
                font-weight: 800 !important;
                padding: 4px 10px !important;
                border-radius: 4px 4px 0 0 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.3px !important;
            }

            .home-featured-cat:nth-of-type(1) .cat-left .mag-post-box.first-post,
            .home-featured-cat:nth-of-type(3) .cat-left .mag-post-box.first-post,
            .home-featured-cat:nth-of-type(5) .cat-left .mag-post-box.first-post {
                background: #16181b !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 12px !important;
                overflow: hidden !important;
                margin-bottom: 10px !important;
                padding: 0 0 10px 0 !important;
            }
            .home-featured-cat .cat-left .mag-post-box.first-post .magcat-thumb a {
                border-radius: 12px 12px 0 0 !important;
                aspect-ratio: 16/9 !important;
                width: 100% !important;
                display: block !important;
            }
            .home-featured-cat .cat-left .mag-post-box.first-post .magcat-detail { padding: 10px 12px 0 !important; }
            .home-featured-cat .cat-left .mag-post-box.first-post h3.magcat-titlte a {
                font-size: 14.5px !important;
                font-weight: 700 !important;
                line-height: 1.35 !important;
                color: #ffffff !important;
            }
            .home-featured-cat .cat-left .mag-post-box.first-post .mag-excerpt {
                display: -webkit-box !important;
                -webkit-line-clamp: 2 !important;
                -webkit-box-orient: vertical !important;
                overflow: hidden !important;
                font-size: 12px !important;
                color: #aaaaaa !important;
                line-height: 1.4 !important;
                margin-top: 5px !important;
            }

            .home-featured-cat:nth-of-type(1) .cat-right,
            .home-featured-cat:nth-of-type(3) .cat-right,
            .home-featured-cat:nth-of-type(5) .cat-right {
                display: flex !important;
                flex-direction: column !important;
                gap: 8px !important;
            }
            .home-featured-cat:nth-of-type(1) .cat-right .mag-post-box,
            .home-featured-cat:nth-of-type(3) .cat-right .mag-post-box,
            .home-featured-cat:nth-of-type(5) .cat-right .mag-post-box {
                display: flex !important;
                flex-direction: row !important;
                align-items: center !important;
                gap: 12px !important;
                background: #141619 !important;
                border: 1px solid rgba(255, 255, 255, 0.05) !important;
                border-radius: 10px !important;
                padding: 8px 10px !important;
                margin: 0 !important;
            }
            .home-featured-cat .cat-right .mag-post-box .magcat-thumb {
                flex: 0 0 85px !important;
                width: 85px !important;
                height: 60px !important;
                margin: 0 !important;
            }
            .home-featured-cat .cat-right .mag-post-box .magcat-thumb a {
                width: 85px !important;
                height: 60px !important;
                border-radius: 8px !important;
                display: block !important;
            }
            .home-featured-cat .cat-right .mag-post-box .magcat-detail { flex: 1 1 auto !important; padding: 0 !important; }
            .home-featured-cat .cat-right .mag-post-box h3.magcat-titlte a {
                font-size: 13px !important;
                font-weight: 600 !important;
                line-height: 1.3 !important;
                color: #e6e6e6 !important;
                display: -webkit-box !important;
                -webkit-line-clamp: 2 !important;
                -webkit-box-orient: vertical !important;
                overflow: hidden !important;
            }

            .home-featured-cat:nth-of-type(2) .home-featured-cat-content,
            .home-featured-cat:nth-of-type(4) .home-featured-cat-content {
                display: flex !important;
                flex-direction: row !important;
                overflow-x: auto !important;
                scroll-snap-type: x mandatory !important;
                gap: 12px !important;
                padding: 4px 2px 10px !important;
                -webkit-overflow-scrolling: touch !important;
                scrollbar-width: none !important;
            }
            .home-featured-cat:nth-of-type(2) .home-featured-cat-content::-webkit-scrollbar,
            .home-featured-cat:nth-of-type(4) .home-featured-cat-content::-webkit-scrollbar { display: none !important; }
            .home-featured-cat:nth-of-type(2) .cat-left, .home-featured-cat:nth-of-type(2) .cat-right,
            .home-featured-cat:nth-of-type(4) .cat-left, .home-featured-cat:nth-of-type(4) .cat-right { display: contents !important; }
            .home-featured-cat:nth-of-type(2) .mag-post-box,
            .home-featured-cat:nth-of-type(4) .mag-post-box {
                flex: 0 0 210px !important;
                min-width: 210px !important;
                max-width: 210px !important;
                scroll-snap-align: start !important;
                background: #181a1e !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 12px !important;
                padding: 8px !important;
                display: flex !important;
                flex-direction: column !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
            }
            .home-featured-cat:nth-of-type(2) .magcat-thumb, .home-featured-cat:nth-of-type(4) .magcat-thumb { width: 100% !important; height: 120px !important; margin-bottom: 8px !important; }
            .home-featured-cat:nth-of-type(2) .magcat-thumb a, .home-featured-cat:nth-of-type(4) .magcat-thumb a { width: 100% !important; height: 120px !important; border-radius: 8px !important; display: block !important; }
            .home-featured-cat:nth-of-type(2) h3.magcat-titlte a, .home-featured-cat:nth-of-type(4) h3.magcat-titlte a {
                font-size: 12.5px !important;
                font-weight: 700 !important;
                line-height: 1.35 !important;
                color: #ffffff !important;
                display: -webkit-box !important;
                -webkit-line-clamp: 2 !important;
                -webkit-box-orient: vertical !important;
                overflow: hidden !important;
            }
            .home-featured-cat:nth-of-type(2) .mag-excerpt, .home-featured-cat:nth-of-type(4) .mag-excerpt { display: none !important; }

            .penci-wrapper-posts-content { display: flex !important; flex-direction: column !important; gap: 10px !important; }
            .penci-wrapper-posts-content article.item {
                display: flex !important;
                flex-direction: row !important;
                align-items: center !important;
                gap: 12px !important;
                background: #141619 !important;
                border: 1px solid rgba(255, 255, 255, 0.06) !important;
                border-radius: 12px !important;
                padding: 10px !important;
                margin: 0 !important;
            }
            .penci-wrapper-posts-content article.item .thumbnail { flex: 0 0 100px !important; width: 100px !important; height: 72px !important; margin: 0 !important; }
            .penci-wrapper-posts-content article.item .thumbnail a { width: 100px !important; height: 72px !important; border-radius: 8px !important; display: block !important; }
            .penci-wrapper-posts-content article.item .grid-header-box { flex: 1 1 auto !important; padding: 0 !important; text-align: left !important; }
            .penci-wrapper-posts-content article.item .cat { margin-bottom: 3px !important; display: block !important; }
            .penci-wrapper-posts-content article.item .cat a { font-size: 10.5px !important; font-weight: 700 !important; color: #ff9800 !important; text-transform: uppercase !important; }
            .penci-wrapper-posts-content article.item h2.penci-entry-title { margin: 0 !important; }
            .penci-wrapper-posts-content article.item h2.penci-entry-title a {
                font-size: 13.5px !important;
                font-weight: 700 !important;
                line-height: 1.3 !important;
                color: #f0f0f0 !important;
                display: -webkit-box !important;
                -webkit-line-clamp: 2 !important;
                -webkit-box-orient: vertical !important;
                overflow: hidden !important;
            }
            .penci-wrapper-posts-content article.item .grid-post-box-meta { font-size: 11px !important; color: #777777 !important; margin-top: 3px !important; }
            .penci-wrapper-posts-content article.item .item-content, .penci-wrapper-posts-content article.item .penci-readmore-btn { display: none !important; }

            #sidebar { margin-top: 20px !important; padding-top: 14px !important; border-top: 1px solid rgba(255, 255, 255, 0.1) !important; }
            #sidebar .widget_recent_entries, #sidebar .wp-block-latest-posts, #sidebar .widget_search, #sidebar .widget_block:has(.wp-block-search) { display: none !important; }
            #sidebar .penci_popular_news_widget .side-item { display: flex !important; align-items: center !important; gap: 10px !important; padding: 8px 0 !important; border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important; }
            #sidebar .penci_popular_news_widget .side-item-thumb { flex: 0 0 75px !important; width: 75px !important; height: 55px !important; }
            #sidebar .penci_popular_news_widget .side-item-thumb a { border-radius: 6px !important; }
        }

        .goog-te-banner-frame.skiptranslate, body > .skiptranslate, #goog-gt-tt, .goog-te-balloon-frame { display: none !important; }
        body { top: 0px !important; }
        .goog-text-highlight { background: none !important; box-shadow: none !important; }
        </style>
        <?php
    }

    public function output_master_scripts() {
        $lang = self::get_current_lang();
        $seo = isset(self::$site_config['seo'][$lang]) ? self::$site_config['seo'][$lang] : self::$site_config['seo']['vi'];
        $brand = self::$site_config['brand'];
        ?>
        <div id="google_translate_element" style="display:none;" class="notranslate" translate="no"></div>
        <script type="text/javascript">
            function googleTranslateElementInit() {
                new google.translate.TranslateElement({
                    pageLanguage: "vi",
                    includedLanguages: "vi,en,zh-CN",
                    autoDisplay: false
                }, "google_translate_element");
            }
        </script>
        <script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>

        <script>
        (function() {
            var seoTitles = <?php echo json_encode(array(
                'vi' => self::$site_config['seo']['vi']['title'],
                'en' => self::$site_config['seo']['en']['title'],
                'zh' => self::$site_config['seo']['zh']['title']
            )); ?>;

            function getActiveLang() {
                var urlParams = new URLSearchParams(window.location.search);
                if (urlParams.has('lang')) return urlParams.get('lang');
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var c = cookies[i].trim();
                    if (c.indexOf('vbm_lang=') === 0) return c.substring(9);
                    if (c.indexOf('googtrans=') === 0) {
                        if (c.indexOf('zh-CN') !== -1 || c.indexOf('zh') !== -1) return 'zh';
                        if (c.indexOf('en') !== -1) return 'en';
                        if (c.indexOf('vi') !== -1) return 'vi';
                    }
                }
                return 'vi';
            }

            var currentLang = getActiveLang();
            var labelMap = { 'vi': '🇻🇳 Tiếng Việt', 'en': '🇬🇧 English', 'zh': '🇨🇳 简体中文' };
            var currentLabel = labelMap[currentLang] || labelMap['vi'];

            if (window.location.pathname === '/' || window.location.pathname === '') {
                if (seoTitles[currentLang]) document.title = seoTitles[currentLang];
            }

            document.addEventListener("DOMContentLoaded", function() {
                // 1. Dynamic Logo
                var navContainer = document.querySelector("#navigation .container, .navigation_bar .container");
                if (navContainer && !document.querySelector(".vbm-nav-logo-wrap")) {
                    var logoSrc = "<?php echo esc_url($brand['logo']); ?>";
                    if (logoSrc) {
                        var logoLink = document.createElement("a");
                        logoLink.className = "vbm-nav-logo-wrap notranslate";
                        logoLink.setAttribute("translate", "no");
                        logoLink.href = "<?php echo esc_url(home_url('/')); ?>";
                        logoLink.innerHTML = '<img src="' + logoSrc + '" alt="<?php echo esc_attr(get_bloginfo("name")); ?>" />';
                        
                        var mobBtn = navContainer.querySelector(".button-menu-mobile");
                        if (mobBtn && mobBtn.nextSibling) {
                            navContainer.insertBefore(logoLink, mobBtn.nextSibling);
                        } else {
                            navContainer.insertBefore(logoLink, navContainer.firstChild);
                        }
                    }
                }

                // 2. Language Switcher
                var searchElem = document.querySelector("#top-search, .penci-top-search");
                if (searchElem && !document.querySelector(".vbm-lang-switcher-wrap")) {
                    var rightWrap = document.createElement("div");
                    rightWrap.className = "vbm-nav-right-wrap notranslate";
                    rightWrap.setAttribute("translate", "no");
                    
                    var switcherHtml = `
                        <div class="vbm-lang-switcher-wrap notranslate" translate="no">
                            <button class="vbm-lang-btn notranslate" translate="no" id="vbmLangBtn" type="button">
                                <span id="vbmActiveLabel">${currentLabel}</span>
                                <i class="penci-faicon fa fa-angle-down" style="font-size:9px;margin-left:3px;"></i>
                            </button>
                            <div class="vbm-lang-dropdown notranslate" translate="no" id="vbmLangDropdown">
                                <a href="javascript:void(0)" class="vbm-lang-item notranslate ${currentLang === 'vi' ? 'current' : ''}" translate="no" onclick="vbmSwitchLang('vi')">🇻🇳 Tiếng Việt</a>
                                <a href="javascript:void(0)" class="vbm-lang-item notranslate ${currentLang === 'en' ? 'current' : ''}" translate="no" onclick="vbmSwitchLang('en')">🇬🇧 English</a>
                                <a href="javascript:void(0)" class="vbm-lang-item notranslate ${currentLang === 'zh' ? 'current' : ''}" translate="no" onclick="vbmSwitchLang('zh')">🇨🇳 简体中文</a>
                            </div>
                        </div>
                    `;
                    searchElem.parentNode.insertBefore(rightWrap, searchElem);
                    rightWrap.innerHTML = switcherHtml;
                    rightWrap.appendChild(searchElem);
                }

                // Dropdown Toggle
                document.addEventListener("click", function(e) {
                    var btn = document.getElementById("vbmLangBtn");
                    var dd = document.getElementById("vbmLangDropdown");
                    if (btn && dd) {
                        if (btn.contains(e.target)) dd.classList.toggle("active");
                        else if (!dd.contains(e.target)) dd.classList.remove("active");
                    }
                });

                // Auto-trigger translation
                if (currentLang === "en" || currentLang === "zh") {
                    var googleLang = currentLang === "zh" ? "zh-CN" : "en";
                    var checkGoogle = setInterval(function() {
                        var select = document.querySelector(".goog-te-combo");
                        if (select) {
                            select.value = googleLang;
                            select.dispatchEvent(new Event("change"));
                            clearInterval(checkGoogle);
                        }
                    }, 200);
                    setTimeout(function() { clearInterval(checkGoogle); }, 8000);
                }
            });

            window.vbmSwitchLang = function(lang) {
                var url = new URL(window.location.href);
                url.searchParams.set('lang', lang);
                var exp = new Date(Date.now() + 30 * 86400 * 1000).toUTCString();
                document.cookie = "vbm_lang=" + lang + "; expires=" + exp + "; path=/;";
                if (lang === 'vi') {
                    document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                    document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=" + window.location.hostname;
                } else if (lang === 'en') {
                    document.cookie = "googtrans=/vi/en; expires=" + exp + "; path=/;";
                    document.cookie = "googtrans=/vi/en; expires=" + exp + "; path=/; domain=" + window.location.hostname;
                } else if (lang === 'zh') {
                    document.cookie = "googtrans=/vi/zh-CN; expires=" + exp + "; path=/;";
                    document.cookie = "googtrans=/vi/zh-CN; expires=" + exp + "; path=/; domain=" + window.location.hostname;
                }
                window.location.href = url.toString();
            };
        })();
        </script>
        <?php
    }
}

new Auto_SEO_GEO_Master_Suite();
