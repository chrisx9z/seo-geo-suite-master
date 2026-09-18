#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Master Cloud & VPS DevOps Suite CLI
Multi-site automation tool for Cloudflare DNS/WAF, aaPanel Nginx, WP Migration, and Safe Database Sanitization.

Usage:
    python master_devops.py cf-dns         --domain example.com --ip 1.2.3.4 [--proxy]
    python master_devops.py cf-purge       --domain example.com
    python master_devops.py cf-ssl         --domain example.com --mode full
    python master_devops.py clone-site     --from-site <site_id> --to-domain <domain> --to-brand <name>
    python master_devops.py clean-posts-sql
    python master_devops.py generate-vhost --domain example.com
"""

import argparse
import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Import DevOps Suite Modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from modules.vps_cloudflare_aapanel.vps_automation import CloudflareManager, AaPanelManager, WPCleaner, DevOpsOrchestrator
    from modules.migration.wp_clone_packager import WPClonePackager
except ImportError as e:
    print(f"Warning: Module import error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Master Cloud & VPS DevOps Suite CLI")
    parser.add_argument(
        "command",
        choices=[
            "cf-dns",
            "cf-purge",
            "cf-ssl",
            "clone-site",
            "clean-posts-sql",
            "generate-vhost",
            "provision"
        ],
        help="DevOps action to perform"
    )
    parser.add_argument("--domain", help="Target domain (e.g. example.com)")
    parser.add_argument("--ip", help="Server IPv4 address for DNS records")
    parser.add_argument("--proxy", action="store_true", default=True, help="Enable Cloudflare Proxy (default: True)")
    parser.add_argument("--no-proxy", action="store_false", dest="proxy", help="Disable Cloudflare Proxy (DNS only)")
    parser.add_argument("--mode", default="full", choices=["off", "flexible", "full", "strict"], help="Cloudflare SSL mode")
    parser.add_argument("--from-site", default="mmdidau", help="Source site ID in sites.json for cloning")
    parser.add_argument("--to-domain", default="triptip.cc", help="Target domain for cloned site")
    parser.add_argument("--to-brand", default="TripTip", help="Target brand name for cloned site")

    args = parser.parse_args()

    cf = CloudflareManager()
    aapanel = AaPanelManager()

    if args.command == "cf-dns":
        if not args.domain or not args.ip:
            print("Error: --domain and --ip are required for cf-dns.")
            sys.exit(1)
        print(f"[*] Updating Cloudflare DNS for {args.domain} -> {args.ip} (Proxied: {args.proxy})...")
        res = cf.add_or_update_dns_record(args.domain, args.ip, proxied=args.proxy)
        print(json.dumps(res, indent=2))

    elif args.command == "cf-purge":
        if not args.domain:
            print("Error: --domain is required for cf-purge.")
            sys.exit(1)
        print(f"[*] Purging Cloudflare Edge Cache for {args.domain}...")
        res = cf.purge_cache(args.domain)
        print(json.dumps(res, indent=2))

    elif args.command == "cf-ssl":
        if not args.domain:
            print("Error: --domain is required for cf-ssl.")
            sys.exit(1)
        print(f"[*] Setting Cloudflare SSL mode for {args.domain} to '{args.mode}'...")
        res = cf.set_ssl_mode(args.domain, mode=args.mode)
        print(json.dumps(res, indent=2))

    elif args.command == "clone-site":
        print(f"[*] Starting WP Clone Packager from '{args.from_site}' to '{args.to_domain}'...")
        packager = WPClonePackager(
            source_site_id=args.from_site,
            target_domain=args.to_domain,
            target_name=args.to_brand
        )
        packager.run_all()

    elif args.command == "clean-posts-sql":
        print("=== SAFE WORDPRESS POST WIPING & PURGING SQL ===")
        print("Guaranteed to PRESERVE: tdb_templates, pages, menus, attachments.")
        print("----------------------------------------------------------------")
        print(WPCleaner.get_cleanup_sql())
        print("----------------------------------------------------------------")

    elif args.command == "generate-vhost":
        if not args.domain:
            print("Error: --domain is required for generate-vhost.")
            sys.exit(1)
        print(f"[*] Generating Nginx Virtual Host config for {args.domain}...")
        vhost = aapanel.generate_nginx_vhost(args.domain)
        print(vhost)

    elif args.command == "provision":
        if not args.domain:
            print("Error: --domain is required for provision.")
            sys.exit(1)
        orchestrator = DevOpsOrchestrator()
        res = orchestrator.provision_new_site(args.domain, server_ip=args.ip, enable_proxy=args.proxy)
        print(f"[*] Provisioning plan generated successfully for {args.domain}.")

if __name__ == "__main__":
    main()
