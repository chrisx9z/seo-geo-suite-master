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
import subprocess

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Import DevOps Suite Modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from modules.vps_cloudflare_aapanel.vps_automation import CloudflareManager, AaPanelManager, WPCleaner, DevOpsOrchestrator
    from modules.migration.wp_clone_packager import WPClonePackager
    from modules.codebase_security.auditor import CodebaseSecurityAuditor
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
            "provision",
            "security-audit",
            "validate-findings",
            "validate-ledger"
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
    parser.add_argument("--target", default=".", help="Target file or directory for security-audit")
    parser.add_argument("--output", help="Optional output path to export findings.json")
    parser.add_argument("--file", help="Path to findings.json or coverage-ledger.json for validation")
    parser.add_argument("--validate", action="store_true", help="Run Cloudflare validator after audit")

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

    elif args.command == "security-audit":
        auditor = CodebaseSecurityAuditor()
        target = args.target
        print(f"\n{'='*75}")
        print(f"🛡️ CLOUDFLARE CODEBASE SECURITY AUDIT: {target}")
        print(f"{'='*75}")
        findings = auditor.scan_path(target)

        if not findings:
            print(f"✅ Zero high-risk vulnerabilities or exposed secrets found in: {target}\n")
        else:
            print(f"⚠️ Detected {len(findings)} potential security findings:\n")
            for idx, f in enumerate(findings, 1):
                sev = f['severity'].upper()
                print(f"[{idx}] [{sev}] {f['title']}")
                print(f"    File: {f['file']}:{f['line']}")
                print(f"    Code: {f['snippet']}")
                print(f"    Remediation: {f['remediation']}\n")

        if args.output:
            cf_json = auditor.to_cloudflare_findings_json(findings)
            with open(args.output, "w", encoding="utf-8") as out_f:
                json.dump(cf_json, out_f, indent=2)
            print(f"[*] Exported Cloudflare findings to: {args.output}")

            if args.validate:
                ret, v_out, v_err = auditor.validate_with_cloudflare_validator(args.output)
                if ret == 0:
                    print(f"[*] Cloudflare Findings Validator: {v_out.strip()}")
                else:
                    print(f"[!] Validation Error:\n{v_err.strip()}")

    elif args.command == "validate-findings":
        if not args.file:
            print("Error: --file <path_to_findings.json> is required.")
            sys.exit(1)
        auditor = CodebaseSecurityAuditor()
        ret, out, err = auditor.validate_with_cloudflare_validator(args.file)
        if ret == 0:
            print(f"✅ PASS: {out.strip()}")
        else:
            print(f"❌ FAIL: {err.strip() or out.strip()}")
            sys.exit(ret)

    elif args.command == "validate-ledger":
        if not args.file:
            print("Error: --file <path_to_ledger.json> is required.")
            sys.exit(1)
        validator_script = os.path.join(
            os.path.dirname(__file__), "..", ".agents", "skills", "security-audit", "validate-coverage-ledger.cjs"
        )
        p = subprocess.run(["node", validator_script, os.path.abspath(args.file)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if p.returncode == 0:
            print(f"✅ PASS: {p.stdout.strip()}")
        else:
            print(f"❌ FAIL: {p.stderr.strip() or p.stdout.strip()}")
            sys.exit(p.returncode)

if __name__ == "__main__":
    main()
