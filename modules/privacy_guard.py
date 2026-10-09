# -*- coding: utf-8 -*-
"""
Privacy guard: the repository must never contain personal / site-specific data.

Forbidden tokens are derived at runtime from the gitignored `private/sites.local.json`
(site ids, domains, brand names, direct IPs, admin users, passwords), so this file itself
never lists any real site. Also flags public IPv4 addresses and hard-coded credentials.

    python -m modules.privacy_guard            # scan tracked + staged files, exit 1 on leak
"""
from __future__ import annotations

import ipaddress
import json
import os
import re
import subprocess
import sys
from typing import Dict, Iterable, List, Set, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRIVATE_CONFIG = os.path.join(BASE_DIR, "private", "sites.local.json")

# Documentation / test IPs that are fine to keep in code.
ALLOWED_IPS = {"1.2.3.4", "93.184.216.34", "169.254.169.254", "8.8.8.8", "1.1.1.1"}
IPV4 = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])")
SKIP_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".mp4", ".zip", ".gz", ".blend", ".pdf", ".woff", ".woff2", ".ttf"}
GENERIC_WORDS = {"admin", "administrator", "root", "user", "example", "www", "site", "test", "demo"}


def _host(url: str) -> str:
    m = re.match(r"^\w+://([^/:]+)", url or "")
    return (m.group(1) if m else "").lower().removeprefix("www.")


def forbidden_tokens(config_path: str = PRIVATE_CONFIG) -> Dict[str, str]:
    """token(lowercase) -> reason. Empty when no private config is present."""
    if not os.path.exists(config_path):
        return {}
    with open(config_path, encoding="utf-8") as f:
        sites = json.load(f).get("sites", [])
    out: Dict[str, str] = {}

    def add(tok, why):
        tok = (tok or "").strip().lower()
        if len(tok) >= 5 and tok not in GENERIC_WORDS:
            out[tok] = why

    for s in sites:
        sid = s.get("site_id", "?")
        add(s.get("site_id"), f"site_id of {sid}")
        host = _host(s.get("url", ""))
        add(host, f"domain of {sid}")
        add(host.split(".")[0], f"brand of {sid}")
        add(s.get("direct_ip"), f"server IP of {sid}")
        add(s.get("admin_user"), f"admin user of {sid}")
        for k, v in s.items():
            if isinstance(v, str) and any(x in k.lower() for x in ("pass", "secret", "token", "api_key")):
                add(v, f"credential {k} of {sid}")
    return out


def tracked_files() -> List[str]:
    res = subprocess.run(["git", "ls-files", "--cached"], cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8")
    return [f for f in res.stdout.splitlines() if f]


def _public_ip(ip: str) -> bool:
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return False
    if ip in ALLOWED_IPS or not a.is_global:
        return False
    parts = ip.split(".")
    return not (parts[1:] == ["0", "0", "0"])  # version strings like Chrome/131.0.0.0


def scan(files: Iterable[str] = None, tokens: Dict[str, str] = None) -> List[Tuple[str, int, str]]:
    files = tracked_files() if files is None else list(files)
    tokens = forbidden_tokens() if tokens is None else tokens
    tok_re = re.compile("|".join(re.escape(t) for t in sorted(tokens, key=len, reverse=True)), re.I) if tokens else None
    leaks: List[Tuple[str, int, str]] = []
    for rel in files:
        if os.path.splitext(rel)[1].lower() in SKIP_EXT or rel.startswith("private/"):
            continue
        fp = os.path.join(BASE_DIR, rel)
        try:
            with open(fp, encoding="utf-8", errors="ignore") as f:
                lines = f.read().splitlines()
        except (OSError, IsADirectoryError):
            continue
        for i, line in enumerate(lines, 1):
            if tok_re:
                for m in tok_re.finditer(line):
                    leaks.append((rel, i, tokens[m.group(0).lower()]))
            for m in IPV4.finditer(line):
                if re.search(r"(sec(tion)?|§|rfc\s*\d+)\s*$", line[:m.start()], re.I):
                    continue  # RFC section numbers like "sec 2.3.1.3"
                if _public_ip(m.group(1)):
                    leaks.append((rel, i, f"public IP {m.group(1)}"))
    return leaks


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    leaks = scan()
    for rel, line, why in leaks:
        print(f"PRIVATE DATA: {rel}:{line}: {why}")
    if leaks:
        print(f"\n{len(leaks)} leak(s). Move site data to private/ (gitignored) or use placeholders (example.com, <site_id>).")
        return 1
    print("privacy_guard: OK (no personal / site-specific data in tracked files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
