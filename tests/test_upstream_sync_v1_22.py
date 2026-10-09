# -*- coding: utf-8 -*-
"""Regression tests for behaviour ported from ultimate-seo-geo v1.19 – v1.22.1."""
import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from modules.ai_crawler_access.url_safety import (  # noqa: E402
    get_validated, is_crawlable_href, is_refusal, normalize_url, validate_url,
)
from modules.link_sentinel.link_sentinel import InternalLinkSentinel  # noqa: E402


# ---- url_safety (1.21.1 security fixes + 1.19.x helpers) -------------------
def test_invalid_port_is_refused_not_raised():
    assert validate_url("http://example.com:99999/", resolve_dns=False).ok is False


def test_cgnat_and_mapped_loopback_blocked():
    assert validate_url("http://100.64.1.1/", resolve_dns=False).ok is False
    assert validate_url("http://[::ffff:127.0.0.1]/", resolve_dns=False).ok is False


def test_public_ipv6_literal_keeps_brackets():
    assert normalize_url("http://[2606:4700::1111]/").startswith("http://[2606:4700::1111]")


def test_redirect_into_metadata_ip_is_refused():
    class R:
        def __init__(self, url, loc=None):
            self.url, self.headers, self.is_redirect = url, ({"Location": loc} if loc else {}), bool(loc)
    calls = []

    def fake_get(u):
        calls.append(u)
        return R(u, "http://169.254.169.254/latest/meta-data/")

    resp, err = get_validated(fake_get, "http://93.184.216.34/")
    assert resp is None and "safety" in err and len(calls) == 1


def test_crawlable_href_and_refusal():
    assert not is_crawlable_href("/cdn-cgi/l/email-protection#abc")
    assert not is_crawlable_href("mailto:a@b.c") and not is_crawlable_href("tel:123")
    assert is_crawlable_href("/bai-viet/")
    assert is_refusal(429, internal=True) and not is_refusal(403, internal=True)
    assert is_refusal(999, internal=False)


# ---- link_sentinel: never unlink on unreliable HEAD / refusal / error -------
class _Resp:
    def __init__(self, code, loc=None):
        self.status_code, self.headers = code, ({"Location": loc} if loc else {})

    def close(self):
        pass


class _Session:
    def __init__(self, head, get):
        self._head, self._get = head, get

    def head(self, url, **kw):
        return _Resp(self._head.get(url, 200))

    def get(self, url, **kw):
        v = self._get.get(url, 200)
        if isinstance(v, Exception):
            raise v
        return _Resp(v)


def _post(href):
    return {"id": 1, "slug": "p", "link": "https://site.vn/p/", "title": {"rendered": "P"},
            "content": {"rendered": f'<p><a href="{href}">x</a></p>'}}


def test_head_404_but_get_200_is_not_unlinked():
    s = _Session({"https://site.vn/ok/": 404}, {"https://site.vn/ok/": 200})
    rep = InternalLinkSentinel("https://site.vn").audit_and_heal_posts([_post("https://site.vn/ok/")], s)
    assert rep["broken_links_found"] == 0 and rep["healed_posts"] == []


def test_confirmed_404_is_healed():
    s = _Session({"https://site.vn/gone/": 404}, {"https://site.vn/gone/": 404})
    rep = InternalLinkSentinel("https://site.vn").audit_and_heal_posts([_post("https://site.vn/gone/")], s)
    assert rep["broken_links_found"] == 1


def test_rate_limited_and_email_protection_untouched():
    s = _Session({"https://site.vn/busy/": 429}, {})
    sentinel = InternalLinkSentinel("https://site.vn")
    rep = sentinel.audit_and_heal_posts([_post("https://site.vn/busy/"),
                                         _post("/cdn-cgi/l/email-protection#x")], s)
    assert rep["healed_posts"] == [] and rep["total_links_checked"] == 1


# ---- onpage: SVG <title> and odd-case JSON-LD type --------------------------
def _onpage():
    spec = importlib.util.spec_from_file_location("onpage", os.path.join(ROOT, "seo_geo_suite", "core", "onpage.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.OnpageChecker()


def test_svg_title_not_read_as_page_title_and_ld_case():
    html = ('<html><body><svg><title>icon</title></svg><title>Trang chủ du lịch Việt Nam đẹp nhất</title>'
            '<script type=" application/LD+json ">{"@graph":[{"@type":"Article"}]}</script></body></html>')
    res = _onpage().analyze_html(html, url="https://site.vn/")
    assert res["title"]["text"].startswith("Trang chủ")
    assert "Article" in str(res)
