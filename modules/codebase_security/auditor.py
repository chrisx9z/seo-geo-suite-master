# -*- coding: utf-8 -*-
"""
Codebase Security Auditor
Inspects repositories, plugins, theme files, and configs for vulnerabilities
using Cloudflare's security-audit-skill attack categories and validation standards.
"""

import os
import sys
import re
import json
import hashlib
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple

class CodebaseSecurityAuditor:
    """Automated security scanning engine adhering to Cloudflare's audit patterns."""

    SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "informational": 0}

    RULES = [
        # 1. Hardcoded Secrets & Credentials
        {
            "id": "SEC-SECRET-01",
            "title": "Hardcoded Private Key",
            "category": "secrets",
            "severity": "critical",
            "pattern": re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|PGP|PRIVATE) KEY-----"),
            "remediation": "Move private keys to environment variables or secret managers (e.g. Vault, Cloudflare Secrets).",
        },
        {
            "id": "SEC-SECRET-02",
            "title": "Hardcoded AWS Access Key",
            "category": "secrets",
            "severity": "critical",
            "pattern": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
            "remediation": "Revoke this key immediately and switch to IAM Roles or AWS environment credentials.",
        },
        {
            "id": "SEC-SECRET-03",
            "title": "Hardcoded AI / API Service Token",
            "category": "secrets",
            "severity": "high",
            "pattern": re.compile(r"\b(?:sk-[a-zA-Z0-9_\-]{24,}|ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{50,})\b"),
            "remediation": "Do not commit API tokens in source code. Load them dynamically via os.environ.",
        },
        {
            "id": "SEC-SECRET-04",
            "title": "Hardcoded Database Password Assignment",
            "category": "secrets",
            "severity": "high",
            "pattern": re.compile(r"""(?:DB_PASS(?:WORD)?|admin_pass(?:word)?)\s*[:=]\s*['"][^'"]{6,}['"]""", re.IGNORECASE),
            "remediation": "Store database passwords in .env or private configuration ignored by git.",
        },
        # 2. Dangerous Code Execution (PHP / Web)
        {
            "id": "SEC-EXEC-01",
            "title": "Arbitrary Code Execution Sink (PHP eval)",
            "category": "code_execution",
            "severity": "critical",
            "pattern": re.compile(r"\b(?:eval|assert)\s*\(", re.IGNORECASE),
            "extensions": [".php"],
            "remediation": "Avoid eval/assert on untrusted input; use predefined command maps or safe parsers.",
        },
        {
            "id": "SEC-EXEC-02",
            "title": "Shell Command Execution Sink (PHP exec/shell_exec/system)",
            "category": "command_injection",
            "severity": "high",
            "pattern": re.compile(r"\b(?:shell_exec|exec|passthru|system|popen|proc_open)\s*\(", re.IGNORECASE),
            "extensions": [".php"],
            "remediation": "Use escapeshellarg()/escapeshellcmd() or preferably avoid external shell invocations.",
        },
        {
            "id": "SEC-DESER-01",
            "title": "Insecure PHP Object Deserialization (unserialize)",
            "category": "deserialization",
            "severity": "high",
            "pattern": re.compile(r"\bunserialize\s*\([^;]*\)", re.IGNORECASE),
            "extensions": [".php"],
            "remediation": "Pass ['allowed_classes' => false] or switch to JSON encoding for serialized payloads.",
        },
        # 3. Dangerous Python Code Execution & Deserialization
        {
            "id": "SEC-PY-EXEC-01",
            "title": "Unsafe Python Code Execution (eval/exec)",
            "category": "code_execution",
            "severity": "high",
            "pattern": re.compile(r"\b(?:eval|exec)\s*\([^)]+\)"),
            "extensions": [".py"],
            "remediation": "Refactor to ast.literal_eval() for data parsing, or use explicit dispatch tables.",
        },
        {
            "id": "SEC-PY-DESER-01",
            "title": "Insecure Python Deserialization (pickle/yaml.load)",
            "category": "deserialization",
            "severity": "critical",
            "pattern": re.compile(r"\b(?:pickle\.loads?|_pickle\.loads?|yaml\.load\([^,)]+\))"),
            "extensions": [".py"],
            "remediation": "Never unpickle data from untrusted sources. Use yaml.safe_load() instead of yaml.load().",
        },
        {
            "id": "SEC-PY-CMD-01",
            "title": "Subprocess Shell Injection Risk",
            "category": "command_injection",
            "severity": "high",
            "pattern": re.compile(r"subprocess\.(?:Popen|run|call|check_output)\s*\([^)]*shell\s*=\s*True", re.DOTALL),
            "extensions": [".py"],
            "remediation": "Set shell=False and pass arguments as a list of strings instead of a formatted shell command.",
        },
        # 4. SQL Injection Patterns
        {
            "id": "SEC-SQLI-01",
            "title": "Potential SQL String Concatenation",
            "category": "sql_injection",
            "severity": "high",
            "pattern": re.compile(r"""(?:SELECT|INSERT|UPDATE|DELETE)\s+.*(?:FROM|INTO|TABLE)\s+.*(?:\$_(?:GET|POST|REQUEST)|["']\s*\+\s*\w+|f["'][^"']*(?:WHERE|AND|OR))""", re.IGNORECASE),
            "remediation": "Use prepared statements / parameterized queries rather than string concatenation in SQL.",
        },
        # 5. Cloudflare / Cloud Misconfigurations
        {
            "id": "SEC-CORS-01",
            "title": "Permissive Wildcard CORS with Credentials",
            "category": "cloud_security",
            "severity": "medium",
            "pattern": re.compile(r"""Access-Control-Allow-Origin['"]?\s*[:=]\s*['"]\*['"].*Access-Control-Allow-Credentials['"]?\s*[:=]\s*['"]true['"]""", re.IGNORECASE | re.DOTALL),
            "remediation": "Do not allow wildcard origins with Allow-Credentials: true. Specify explicit allowed domains.",
        },
    ]

    IGNORE_DIRS = {
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "__pycache__",
        "cache",
        ".cache",
        "temp",
        "tmp",
        "reports",
        "generated_posts",
        ".agents",
        "repos",
    }

    VALID_EXTS = {".py", ".php", ".js", ".ts", ".cjs", ".mjs", ".json", ".env", ".yaml", ".yml", ".sh", ".bat", ".sql"}

    def __init__(self, root_dir: str = None):
        self.root_dir = os.path.abspath(root_dir or os.path.join(os.path.dirname(__file__), "..", ".."))

    def scan_path(self, target_path: str) -> List[Dict[str, Any]]:
        """Scans a single file or a directory recursively for security issues."""
        abs_target = os.path.abspath(target_path)
        findings = []

        if os.path.isfile(abs_target):
            findings.extend(self._scan_file(abs_target))
        elif os.path.isdir(abs_target):
            for root, dirs, files in os.walk(abs_target):
                dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in self.VALID_EXTS:
                        full_p = os.path.join(root, file)
                        findings.extend(self._scan_file(full_p))

        # Sort findings by severity then path
        findings.sort(key=lambda x: (self.SEVERITY_ORDER.get(x["severity"], 0), x["file"]), reverse=True)
        return findings

    def _scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        findings = []
        ext = os.path.splitext(file_path)[1].lower()

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except Exception:
            return findings

        lines = content.splitlines()

        for rule in self.RULES:
            # Check extension filtering
            if "extensions" in rule and ext not in rule["extensions"]:
                continue

            pat = rule["pattern"]
            for idx, line in enumerate(lines, 1):
                # Ignore comments in test/fixture files
                if line.strip().startswith("#") or line.strip().startswith("//"):
                    if "test" in file_path.lower() or "fixture" in file_path.lower():
                        continue

                m = pat.search(line)
                if m:
                    rel_path = os.path.relpath(file_path, self.root_dir).replace("\\", "/")
                    fp_input = f"{rule['id']}:{rel_path}:{idx}"
                    fingerprint = hashlib.sha256(fp_input.encode("utf-8")).hexdigest()[:16]

                    findings.append({
                        "rule_id": rule["id"],
                        "fingerprint": f"finding.{fingerprint}",
                        "title": rule["title"],
                        "category": rule["category"],
                        "severity": rule["severity"],
                        "file": rel_path,
                        "line": idx,
                        "snippet": line.strip()[:150],
                        "remediation": rule["remediation"],
                    })

        return findings

    def to_cloudflare_findings_json(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Converts raw findings into Cloudflare report-schema.json conforming entries."""
        cf_entries = []

        for f in findings:
            safe_file = f["file"].replace("\\", "/").lstrip("./")
            entry = {
                "verdict": "needs_validation",
                "fingerprint": f["fingerprint"],
                "title": f["title"],
                "description": f"Automated static audit flagged: {f['title']} in {safe_file} (line {f['line']}).",
                "claimed_root_cause": f"Static inspection detected pattern: `{f['snippet']}`.",
                "trace": [
                    {
                        "kind": "sink",
                        "file": safe_file,
                        "line": max(1, int(f["line"])),
                        "scope": f["category"],
                        "description": f"Target pattern matched: {f['snippet']}"
                    }
                ],
                "evidence": [
                    {
                        "file": safe_file,
                        "line": max(1, int(f["line"])),
                        "description": f"Source line matched rule {f['rule_id']}: {f['snippet']}"
                    }
                ],
                "blockers": [
                    "Dynamic reachability and context need manual or sandboxed runtime validation."
                ],
                "validation_plan": {
                    "local": f"Inspect {safe_file}:{f['line']} to determine if untrusted input can reach this sink."
                }
            }
            cf_entries.append(entry)

        # Sort lexicographically by fingerprint as required by Cloudflare validator
        cf_entries.sort(key=lambda x: x["fingerprint"])
        return cf_entries

    def validate_with_cloudflare_validator(self, findings_json_path: str) -> Tuple[int, str, str]:
        """Runs Cloudflare's validate-findings.cjs on a findings JSON file."""
        validator_script = os.path.join(
            self.root_dir, ".agents", "skills", "security-audit", "validate-findings.cjs"
        )
        if not os.path.exists(validator_script):
            return 1, "", f"Validator script not found at {validator_script}"

        p = subprocess.run(
            ["node", validator_script, os.path.abspath(findings_json_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return p.returncode, p.stdout, p.stderr
