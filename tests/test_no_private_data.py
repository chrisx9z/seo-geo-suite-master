# -*- coding: utf-8 -*-
"""Repo must not contain personal / site-specific data (derived from private/sites.local.json)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules import privacy_guard as pg  # noqa: E402


def test_tracked_files_have_no_private_data():
    leaks = pg.scan()
    assert not leaks, "\n".join(f"{f}:{n}: {why}" for f, n, why in leaks[:50])


def test_guard_detects_tokens_from_config(tmp_path):
    cfg = tmp_path / "sites.json"
    cfg.write_text('{"sites":[{"site_id":"acmeblog","url":"https://acmeblog.io","admin_user":"admin",'
                   '"admin_pass":"S3cretPassw0rd","direct_ip":"203.0.113.77"}]}', encoding="utf-8")
    toks = pg.forbidden_tokens(str(cfg))
    assert {"acmeblog", "acmeblog.io", "s3cretpassw0rd", "203.0.113.77"} <= set(toks)
    assert "admin" not in toks  # generic usernames are not flagged


def test_public_ip_rules():
    assert pg._public_ip(".".join(["8", "26", "1", "9"]))
    assert not pg._public_ip("192.168.1.10")
    assert not pg._public_ip("131.0.0.0")  # browser version strings
    assert not pg._public_ip("1.2.3.4")    # documentation placeholder
