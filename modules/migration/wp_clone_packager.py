# -*- coding: utf-8 -*-
"""
WP Clone Packager Engine v1.0.1
Automated cloning tool: connects to source site (mmdidau.com),
deploys WP Site Porter, runs diagnostics, exports converted database (with serialized search-replace),
exports themes & plugins, and packages everything locally for triptip.cc.
"""

import os
import io
import sys
import zipfile
import json
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class WPClonePackager:
    def __init__(self, source_site_id='mmdidau', target_domain='triptip.cc', target_name='TripTip'):
        self.source_site_id = source_site_id
        self.target_domain = target_domain
        self.target_name = target_name
        self.target_url = f'https://{target_domain}'
        self.config = self._load_config(source_site_id)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) WPClonePackager/1.0'})
        self.local_export_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'cache', 'clones', target_domain)
        )
        os.makedirs(self.local_export_dir, exist_ok=True)
        self._authenticate()

    def _load_config(self, site_id):
        conf_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'private', 'sites.local.json'))
        with open(conf_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for s in data.get('sites', []):
            if s.get('site_id') == site_id:
                return s
        raise ValueError(f"Site '{site_id}' not found in sites.local.json")

    def _authenticate(self):
        url = self.config['url']
        user = self.config['admin_user']
        pwd = self.config['admin_pass']
        print(f"[*] Authenticating to {url} as {user}...")
        self.session.post(
            f"{url}/wp-login.php",
            data={'log': user, 'pwd': pwd, 'wp-submit': 'Log In'},
            timeout=25
        )
        r = self.session.get(f"{url}/wp-admin/index.php", timeout=25)
        if 'wp-login.php' in r.url:
            raise Exception("Failed to authenticate to WordPress admin.")
        print("  [+] Authenticated successfully.")

    def deploy_porter_plugin(self):
        url = self.config['url']
        print("[*] Packaging WP Site Porter helper plugin...")
        porter_plugin_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'wp-site-porter', 'wp-site-porter.php')
        )
        with open(porter_plugin_path, 'r', encoding='utf-8') as pf:
            plugin_code = pf.read()

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('wp-site-porter/wp-site-porter.php', plugin_code)
        zip_buf.seek(0)
        zip_data = zip_buf.read()

        print(f"[*] Deploying WP Site Porter ({len(zip_data)} bytes) to {url}...")
        r_up_page = self.session.get(f"{url}/wp-admin/plugin-install.php?tab=upload", timeout=20)
        soup = BeautifulSoup(r_up_page.text, 'html.parser')
        nonce_in = soup.find('input', {'name': '_wpnonce'})
        if not nonce_in:
            raise Exception("Could not find upload nonce on plugin-install.php")

        r_upload = self.session.post(
            f"{url}/wp-admin/update.php?action=upload-plugin",
            data={'_wpnonce': nonce_in.get('value', ''), 'install-plugin-submit': 'Install Now'},
            files={'pluginzip': ('wp-site-porter.zip', zip_data, 'application/zip')},
            timeout=45
        )

        soup_res = BeautifulSoup(r_upload.text, 'html.parser')
        for a in soup_res.find_all('a', href=True):
            href = a.get('href')
            if any(k in href for k in ['overwrite', 'update-selected', 'activate']):
                full_url = href if href.startswith('http') else f"{url}/wp-admin/" + href
                self.session.get(full_url, timeout=25)

        print("  [+] WP Site Porter deployed & activated successfully.")

    def run_diagnostics(self):
        url = self.config['url']
        print("\n[*] Running remote server diagnostics...")
        r = self.session.get(f"{url}/?site_porter_action=diagnostics", timeout=30)
        if r.status_code != 200:
            raise Exception(f"Diagnostics request failed with status {r.status_code}: {r.text[:300]}")
        
        # Clean JSON if any PHP notices precede it
        text = r.text.strip()
        if not text.startswith('{'):
            import re
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                text = m.group(0)

        res = json.loads(text)
        if not res.get('success'):
            raise Exception(f"Diagnostics returned error: {res}")
        data = res['data']
        print(f"  - Server Public IP   : {data.get('public_ip')}")
        print(f"  - Server Address     : {data.get('server_addr')}")
        print(f"  - Server Software    : {data.get('server_software')}")
        print(f"  - PHP Version        : {data.get('php_version')}")
        print(f"  - MySQL Version      : {data.get('mysql_version')}")
        print(f"  - ABSPATH            : {data.get('abspath')}")
        print(f"  - Free Disk Space    : {data.get('free_disk_space_mb')} MB")
        print(f"  - Active Theme       : {data.get('active_theme', {}).get('name')} (Template: {data.get('active_theme', {}).get('template')})")
        print(f"  - Active Plugins     : {len(data.get('active_plugins', []))} plugins active")
        print(f"  - Uploads Media      : {data.get('uploads', {}).get('count')} files ({data.get('uploads', {}).get('total_mb')} MB)")
        return data

    def export_database(self):
        url = self.config['url']
        print(f"\n[*] Exporting database with serialized replacement for '{self.target_domain}'...")
        r = self.session.get(
            f"{url}/?site_porter_action=export_db&target_domain={self.target_domain}&target_name={self.target_name}",
            timeout=300
        )
        if r.status_code != 200:
            raise Exception(f"Database export failed: status {r.status_code}: {r.text[:300]}")
        
        text = r.text.strip()
        if not text.startswith('{'):
            import re
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                text = m.group(0)

        res = json.loads(text)
        if not res.get('success'):
            raise Exception(f"Database export failed: {res}")
        data = res['data']
        print(f"  [+] Dump completed: {data.get('tables_count')} tables, {data.get('rows_count')} rows written.")
        print(f"  [+] Remote file: {data.get('filename')} ({data.get('size_mb')} MB)")

        file_url = data.get('url')
        local_file = os.path.join(self.local_export_dir, data.get('filename'))
        print(f"  [*] Downloading {file_url} -> {local_file}...")
        r_dl = self.session.get(file_url, stream=True, timeout=180)
        with open(local_file, 'wb') as f:
            for chunk in r_dl.iter_content(chunk_size=65536):
                f.write(chunk)
        print(f"  [+] Downloaded local file: {local_file} ({round(os.path.getsize(local_file) / (1024 * 1024), 2)} MB)")
        return local_file

    def export_themes(self):
        url = self.config['url']
        print("\n[*] Packaging active themes (Newspaper, Newspaper-child)...")
        r = self.session.get(f"{url}/?site_porter_action=export_themes", timeout=300)
        if r.status_code != 200:
            raise Exception(f"Theme export failed: status {r.status_code}: {r.text[:300]}")
        
        text = r.text.strip()
        if not text.startswith('{'):
            import re
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                text = m.group(0)

        res = json.loads(text)
        if not res.get('success'):
            raise Exception(f"Theme export failed: {res}")
        data = res['data']
        print(f"  [+] Themes zipped: {data.get('files_count')} files ({data.get('size_mb')} MB)")

        file_url = data.get('url')
        local_file = os.path.join(self.local_export_dir, data.get('filename'))
        print(f"  [*] Downloading {file_url} -> {local_file}...")
        r_dl = self.session.get(file_url, stream=True, timeout=180)
        with open(local_file, 'wb') as f:
            for chunk in r_dl.iter_content(chunk_size=65536):
                f.write(chunk)
        print(f"  [+] Downloaded local themes zip: {local_file} ({round(os.path.getsize(local_file) / (1024 * 1024), 2)} MB)")
        return local_file

    def export_plugins(self):
        url = self.config['url']
        print("\n[*] Packaging active plugins (tagDiv Composer, Cloud Library, RankMath PRO, etc.)...")
        r = self.session.get(f"{url}/?site_porter_action=export_plugins", timeout=300)
        if r.status_code != 200:
            raise Exception(f"Plugin export failed: status {r.status_code}: {r.text[:300]}")
        
        text = r.text.strip()
        if not text.startswith('{'):
            import re
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                text = m.group(0)

        res = json.loads(text)
        if not res.get('success'):
            raise Exception(f"Plugin export failed: {res}")
        data = res['data']
        print(f"  [+] Plugins zipped: {data.get('files_count')} files ({data.get('size_mb')} MB)")

        file_url = data.get('url')
        local_file = os.path.join(self.local_export_dir, data.get('filename'))
        print(f"  [*] Downloading {file_url} -> {local_file}...")
        r_dl = self.session.get(file_url, stream=True, timeout=180)
        with open(local_file, 'wb') as f:
            for chunk in r_dl.iter_content(chunk_size=65536):
                f.write(chunk)
        print(f"  [+] Downloaded local plugins zip: {local_file} ({round(os.path.getsize(local_file) / (1024 * 1024), 2)} MB)")
        return local_file

    def cleanup_remote(self):
        url = self.config['url']
        print("\n[*] Cleaning up temporary export files on source server...")
        try:
            r = self.session.get(f"{url}/?site_porter_action=cleanup", timeout=30)
            print(f"  [+] Cleanup requested.")
        except Exception as e:
            print(f"  [-] Cleanup error: {e}")

    def run_all(self):
        print(f"================================================================")
        print(f" WP CLONE PACKAGER: {self.source_site_id} -> {self.target_domain}")
        print(f" Target Brand: {self.target_name}")
        print(f" Local cache : {self.local_export_dir}")
        print(f"================================================================")

        self.deploy_porter_plugin()
        diag = self.run_diagnostics()

        # Database export with serialized replacement
        db_file = self.export_database()

        # Themes export
        themes_file = self.export_themes()

        # Plugins export
        plugins_file = self.export_plugins()

        # Cleanup source server exports
        self.cleanup_remote()

        print("\n================================================================")
        print(" CLONE PACKAGING COMPLETE!")
        print(f" Server Public IP : {diag.get('public_ip')}")
        print(f" Local files saved in: {self.local_export_dir}")
        for f in os.listdir(self.local_export_dir):
            fp = os.path.join(self.local_export_dir, f)
            print(f"   - {f} ({round(os.path.getsize(fp) / (1024 * 1024), 2)} MB)")
        print("================================================================")
        return diag


if __name__ == '__main__':
    packager = WPClonePackager(source_site_id='mmdidau', target_domain='triptip.cc', target_name='TripTip')
    packager.run_all()
