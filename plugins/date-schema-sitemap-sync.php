<?php
/**
 * Plugin Name: Single Source of Truth Date & Schema Synchronizer
 * Description: Guarantees 100% consistency across UI, Meta Tags, Schema JSON-LD, and XML Sitemaps using post_date and post_modified from Database. Formats strictly to ISO 8601 (+07:00).
 * Version: 1.1.0
 * Author: Core SEO Infrastructure
 */

if (!defined('ABSPATH')) exit;

class Single_Source_Date_Sync {

    public function __construct() {
        // 0. Auto-Heal Post Date Anomalies on Insert / Update
        add_filter('wp_insert_post_data', array($this, 'auto_heal_post_date_anomalies'), 10, 2);

        // 1. Rank Math OpenGraph Facebook / Twitter Meta
        add_filter('rank_math/opengraph/facebook/article_published_time', array($this, 'filter_og_published_time'), 9999);
        add_filter('rank_math/opengraph/facebook/article_modified_time', array($this, 'filter_og_modified_time'), 9999);

        // 2. Rank Math JSON-LD Schema (Article, BlogPosting, NewsArticle, WebPage)
        add_filter('rank_math/snippet/rich_snippet_article_entity', array($this, 'filter_schema_article_entity'), 9999);
        add_filter('rank_math/json_ld', array($this, 'filter_all_json_ld_schemas'), 9999, 2);

        // 3. Rank Math XML Sitemap synchronization & disable stale sitemap file cache
        add_filter('rank_math/sitemap/enable_caching', '__return_false', 9999);
        add_filter('rank_math/sitemap/entry', array($this, 'filter_sitemap_entry'), 9999, 3);

        // 4. HTML Meta & UI Normalization via Output Buffer
        add_action('template_redirect', array($this, 'start_output_buffer'), 1);

        // 5. Watchdog to eliminate rogue plugins and cron hooks
        add_action('admin_init', array($this, 'run_watchdog'));
    }

    /**
     * Auto-heal post date anomalies on insert/update
     */
    public function auto_heal_post_date_anomalies($data, $postarr) {
        if (!empty($data['post_date']) && !empty($data['post_modified'])) {
            $ts_date = strtotime($data['post_date']);
            $ts_mod  = strtotime($data['post_modified']);
            if ($ts_mod < $ts_date) {
                $data['post_modified'] = $data['post_date'];
                if (!empty($data['post_date_gmt'])) {
                    $data['post_modified_gmt'] = $data['post_date_gmt'];
                }
            }
        }
        return $data;
    }

    /**
     * Watchdog to remove rogue plugins and cron hooks
     */
    public function run_watchdog() {
        if (!current_user_can('manage_options')) return;
        $rogue_plugins = array('random-post-publish-time/random-post-publish-time.php', 'random-post-publish-time.php');
        require_once ABSPATH . 'wp-admin/includes/plugin.php';
        foreach ($rogue_plugins as $r) {
            if (is_plugin_active($r)) {
                deactivate_plugins($r, true);
            }
        }
        if (wp_next_scheduled('rppt_final_cron_hook')) {
            wp_clear_scheduled_hook('rppt_final_cron_hook');
        }
    }

    /**
     * Helper to get synchronized dates for any post
     */
    public static function get_dates($post = null) {
        $p = get_post($post);
        if (!$p) return null;

        $pub_c = get_post_time('c', false, $p);
        $mod_c = get_post_modified_time('c', false, $p);

        // Ensure dateModified is never earlier than datePublished
        if (strtotime($mod_c) < strtotime($pub_c)) {
            $mod_c = $pub_c;
        }

        return array(
            'published' => $pub_c,
            'modified'  => $mod_c,
            'published_ts' => strtotime($pub_c),
            'modified_ts'  => strtotime($mod_c),
            'has_been_modified' => (strtotime($mod_c) > (strtotime($pub_c) + 300))
        );
    }

    public function filter_og_published_time($time) {
        $dates = self::get_dates();
        return $dates ? $dates['published'] : $time;
    }

    public function filter_og_modified_time($time) {
        $dates = self::get_dates();
        return $dates ? $dates['modified'] : $time;
    }

    public function filter_schema_article_entity($entity) {
        $dates = self::get_dates();
        if ($dates && is_array($entity)) {
            $entity['datePublished'] = $dates['published'];
            $entity['dateModified']  = $dates['modified'];
        }
        return $entity;
    }

    public function filter_all_json_ld_schemas($data, $context) {
        if (!is_singular('post')) {
            return $data;
        }
        $dates = self::get_dates();
        if (!$dates || !is_array($data)) {
            return $data;
        }

        foreach ($data as $key => &$node) {
            if (is_array($node)) {
                if (isset($node['datePublished'])) {
                    $node['datePublished'] = $dates['published'];
                }
                if (isset($node['dateModified'])) {
                    $node['dateModified'] = $dates['modified'];
                }
            }
        }
        return $data;
    }

    public function filter_sitemap_entry($url, $type, $object) {
        if ($type === 'post' && is_object($object) && isset($object->ID)) {
            $dates = self::get_dates($object);
            if ($dates) {
                $url['mod'] = $dates['modified'];
            }
        }
        return $url;
    }

    public function start_output_buffer() {
        if (!is_singular('post') || is_admin() || wp_doing_ajax() || (defined('REST_REQUEST') && REST_REQUEST)) {
            return;
        }
        ob_start(array($this, 'process_html_dates'));
    }

    public function process_html_dates($html) {
        if (empty($html) || !is_singular('post')) {
            return $html;
        }
        $dates = self::get_dates();
        if (!$dates) {
            return $html;
        }

        $pub = esc_attr($dates['published']);
        $mod = esc_attr($dates['modified']);

        // 1. DEDUPLICATE / NORMALIZE HTML META TAGS IN <head>
        // Strip existing article:published_time, article:modified_time, og:updated_time
        $html = preg_replace('/<meta\s+property=["\']article:published_time["\'][^>]*>/i', '', $html);
        $html = preg_replace('/<meta\s+property=["\']article:modified_time["\'][^>]*>/i', '', $html);
        $html = preg_replace('/<meta\s+property=["\']og:updated_time["\'][^>]*>/i', '', $html);

        // Inject standardized single-source meta tags into <head>
        $meta_tags  = "\n<!-- Single Source of Truth Date Synchronization -->\n";
        $meta_tags .= '<meta property="article:published_time" content="' . $pub . '" />' . "\n";
        $meta_tags .= '<meta property="article:modified_time" content="' . $mod . '" />' . "\n";
        $meta_tags .= '<meta property="og:updated_time" content="' . $mod . '" />' . "\n";

        if (stripos($html, '</head>') !== false) {
            $html = preg_replace('/<\/head>/i', $meta_tags . '</head>', $html, 1);
        }

        // 2. FIX UI MICRODATA / THEME CLASS BUGS
        // Fix Newspaper theme: class="entry-date updated td-module-date" -> class="entry-date published td-module-date"
        $html = preg_replace(
            '/(<time[^>]*class=["\'][^"\']*\bentry-date\b)\s+updated(\b[^"\']*["\'])/i',
            '$1 published$2',
            $html
        );

        // Ensure datetime attribute on entry-date published matches $dates['published']
        $html = preg_replace(
            '/(<time[^>]*class=["\'][^"\']*\bentry-date\b[^"\']*["\'][^>]*)\bdatetime=["\'][^"\']+["\']/i',
            '$1datetime="' . $pub . '"',
            $html
        );

        return $html;
    }
}

new Single_Source_Date_Sync();
