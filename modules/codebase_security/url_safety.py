#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical URL safety module for seo-geo-suite-master (integrated from AgriciDaniel/claude-seo).

Centralizes SSRF protection, DNS rebinding mitigation, and DNS-pinned HTTP
fetching. Every script or module in this repository that accepts a user-supplied URL
can validate it through this module before issuing any network request.

Public API
==========
- validate_url(url) -> bool
- validate_url_strict(url) -> tuple[str, str]
- safe_requests_get(url, *, timeout=30, **kwargs) -> requests.Response
- safe_requests_head(url, *, timeout=30, **kwargs) -> requests.Response
- safe_requests_session(url) -> context manager yielding requests.Session
- is_safe_ip(ip_str) -> bool
- decode_response_text(response) -> str
- decode_body(raw, content_type="") -> str
- read_bounded(response, max_bytes) -> tuple[bytes, bool]
- json_depth_exceeds(text, max_depth=256) -> bool
- URLSafetyError
"""

from __future__ import annotations

import ipaddress
import os
import re
import socket
import threading
from contextlib import contextmanager
from typing import Iterator, Optional
from urllib.parse import urlparse

try:
    import requests
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "modules/codebase_security/url_safety.py requires the 'requests' package."
    ) from exc


__all__ = [
    "URLSafetyError",
    "is_safe_ip",
    "normalize_hostname",
    "validate_url",
    "validate_url_strict",
    "safe_requests_get",
    "safe_requests_head",
    "safe_requests_session",
    "make_safe_playwright_route_handler",
    "new_guarded_context",
    "decode_response_text",
    "decode_body",
    "read_bounded",
    "json_depth_exceeds",
    "MAX_PAGE_BYTES",
    "MAX_JSON_DEPTH",
    "DEFAULT_USER_AGENT",
    "DEFAULT_REQUEST_HEADERS",
]

_IPV4_OBFUSCATED_RE = re.compile(
    r"^(?:0x[0-9a-f]+|[0-9]+)(?:\.(?:0x[0-9a-f]+|[0-9]+)){0,3}$",
    re.IGNORECASE,
)

_BLOCKED_HOSTNAMES: frozenset[str] = frozenset(
    {
        "localhost",
        "ip6-localhost",
        "ip6-loopback",
        "metadata.google.internal",
        "metadata.goog",
        "metadata",
        "metadata.azure.com",
        "metadata.ec2.internal",
        "metadata.oraclecloud.com",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "169.254.169.254",
        "fd00:ec2::254",
    }
)


class URLSafetyError(ValueError):
    """Raised when a URL fails SSRF safety checks."""


def _raw_authority(url: str) -> str:
    match = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://([^/?#]*)", url)
    return match.group(1) if match else ""


def _reject_authority_confusion(url: str, parsed) -> None:
    authority = _raw_authority(url)
    authority_lower = authority.lower()
    url_lower = url.lower()

    if "\\" in authority or "%5c" in authority_lower:
        raise URLSafetyError("URL authority contains a backslash")
    if "%" in authority:
        raise URLSafetyError("URL authority contains percent-encoding")
    if parsed.username is not None or parsed.password is not None or "@" in authority:
        raise URLSafetyError("URL userinfo is not allowed")
    if "#@" in url or "%23@" in url_lower:
        raise URLSafetyError("URL fragment/userinfo confusion refused")


_SHARED_ADDRESS_SPACE = ipaddress.ip_network("100.64.0.0/10")


def is_safe_ip(ip_str: str) -> bool:
    """Return True iff ``ip_str`` is a public unicast address."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return not (
        ip.is_private
        or (ip.version == 4 and ip in _SHARED_ADDRESS_SPACE)
        or ip.is_loopback
        or ip.is_reserved
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_unspecified
    )


_LOCAL_TARGETS_ENV = "CLAUDE_SEO_LOCAL_TARGETS"

_NEVER_ALLOWLISTABLE_HOSTNAMES: frozenset[str] = frozenset(
    {
        "metadata",
        "metadata.goog",
        "metadata.google.internal",
        "metadata.azure.com",
        "metadata.ec2.internal",
        "metadata.oraclecloud.com",
        "169.254.169.254",
        "100.100.100.200",
        "fd00:ec2::254",
        "0.0.0.0",
    }
)


def _is_allowlistable_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    if str(ip) in _NEVER_ALLOWLISTABLE_HOSTNAMES:
        return False
    if ip.is_link_local or ip.is_multicast or ip.is_unspecified:
        return False
    if ip.is_loopback:
        return True
    return not ip.is_reserved


def _parse_local_target(entry: str) -> Optional[tuple[str, Optional[int]]]:
    entry = entry.strip()
    if not entry:
        return None
    if entry.count(":") > 1 and "[" not in entry:
        candidate, port = entry, None
    else:
        try:
            parsed = urlparse(f"//{entry}")
            candidate, port = parsed.hostname, parsed.port
        except ValueError:
            return None
        if not candidate:
            return None
    try:
        return normalize_hostname(candidate), port
    except URLSafetyError:
        return None


def _local_targets() -> tuple[tuple[str, Optional[int]], ...]:
    raw = os.environ.get(_LOCAL_TARGETS_ENV, "")
    if not raw.strip():
        return ()
    parsed = (_parse_local_target(part) for part in raw.split(","))
    return tuple(entry for entry in parsed if entry is not None)


def _looks_like_ip(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        return False
    return True


def _is_allowlisted_local_target(hostname: str, port: Optional[int]) -> bool:
    if hostname in _NEVER_ALLOWLISTABLE_HOSTNAMES:
        return False
    if not _is_allowlistable_ip(hostname) and _looks_like_ip(hostname):
        return False
    for entry_host, entry_port in _local_targets():
        if entry_host != hostname:
            continue
        if entry_port is None or entry_port == port:
            return True
    return False


def _url_port(parsed) -> Optional[int]:
    try:
        explicit = parsed.port
    except ValueError:
        return None
    if explicit is not None:
        return explicit
    return 443 if parsed.scheme == "https" else 80


def normalize_hostname(hostname: str) -> str:
    if not hostname:
        raise URLSafetyError("Empty hostname")

    h = hostname.lower().strip()
    if h.endswith(".") and not h.endswith(".."):
        h = h[:-1]

    if _IPV4_OBFUSCATED_RE.match(h):
        try:
            packed = socket.inet_aton(h)
        except OSError as exc:
            raise URLSafetyError(
                f"Malformed IPv4 obfuscation refused: {hostname!r} ({exc})"
            ) from exc
        h = socket.inet_ntoa(packed)
    return h


def validate_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        _reject_authority_confusion(url, parsed)
        if parsed.scheme not in ("http", "https"):
            return False
        if not parsed.hostname:
            return False
        hostname = normalize_hostname(parsed.hostname)
    except URLSafetyError:
        return False
    port = _url_port(parsed)
    allowlisted = port is not None and _is_allowlisted_local_target(hostname, port)
    if hostname in _BLOCKED_HOSTNAMES and not allowlisted:
        return False
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        return True
    if is_safe_ip(hostname):
        return True
    return allowlisted and _is_allowlistable_ip(hostname)


def validate_url_strict(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    _reject_authority_confusion(url, parsed)
    if parsed.scheme not in ("http", "https"):
        raise URLSafetyError(f"Invalid URL scheme: {parsed.scheme!r}")
    if not parsed.hostname:
        raise URLSafetyError("URL has no hostname")

    hostname = normalize_hostname(parsed.hostname)
    port = _url_port(parsed)
    if port is None:
        raise URLSafetyError(f"Invalid port in URL authority: {url!r}")

    allowlisted = _is_allowlisted_local_target(hostname, port)
    if hostname in _BLOCKED_HOSTNAMES and not allowlisted:
        raise URLSafetyError(f"Blocked hostname: {hostname}")

    try:
        literal = ipaddress.ip_address(hostname)
    except ValueError:
        literal = None

    if literal is not None:
        if not is_safe_ip(hostname) and not (
            allowlisted and _is_allowlistable_ip(hostname)
        ):
            raise URLSafetyError(f"Blocked IP literal: {hostname}")
        return url, str(literal)

    try:
        addrinfo = socket.getaddrinfo(
            hostname,
            port,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    except (socket.gaierror, UnicodeError) as exc:
        raise URLSafetyError(f"DNS resolution failed for {hostname}: {exc}") from exc

    resolved_ips = sorted({info[4][0] for info in addrinfo})
    if not resolved_ips:
        raise URLSafetyError(f"No A records for {hostname}")

    for ip_str in resolved_ips:
        if is_safe_ip(ip_str):
            continue
        if allowlisted and _is_allowlistable_ip(ip_str):
            continue
        raise URLSafetyError(
            f"DNS rebinding refused: {hostname} resolves to non-public IP {ip_str}"
        )

    pinned = resolved_ips[0]
    return url, pinned


def _proxy_hosts(url: str, proxies: Optional[dict] = None) -> frozenset:
    merged = dict(requests.utils.get_environ_proxies(url))
    if proxies:
        merged.update(proxies)
    proxy = requests.utils.select_proxy(url, merged)
    if not proxy:
        return frozenset()
    host = urlparse(requests.utils.prepend_scheme_if_needed(proxy, "http")).hostname
    return frozenset({host.lower()}) if host else frozenset()


def _assert_proxy_host_is_public(host: str) -> str:
    normalized = normalize_hostname(host)
    hint = (
        "Point the proxy environment variable at a publicly routable "
        "address, or unset it."
    )
    if normalized in _BLOCKED_HOSTNAMES:
        raise URLSafetyError(
            f"Refusing configured HTTP proxy {host!r}: blocked hostname {normalized}. {hint}"
        )

    try:
        literal = ipaddress.ip_address(normalized)
    except ValueError:
        literal = None

    if literal is not None:
        if not is_safe_ip(normalized):
            raise URLSafetyError(
                f"Refusing configured HTTP proxy {host!r}: non-public address {normalized}. {hint}"
            )
        return normalized

    try:
        addrinfo = socket.getaddrinfo(
            normalized,
            None,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM,
        )
    except (socket.gaierror, UnicodeError) as exc:
        raise URLSafetyError(
            f"Refusing configured HTTP proxy {host!r}: DNS resolution failed ({exc}). {hint}"
        ) from exc

    resolved_ips = sorted({info[4][0] for info in addrinfo if info[4]})
    if not resolved_ips:
        raise URLSafetyError(
            f"Refusing configured HTTP proxy {host!r}: no address records. {hint}"
        )
    for ip_str in resolved_ips:
        if not is_safe_ip(ip_str):
            raise URLSafetyError(
                f"Refusing configured HTTP proxy {host!r}: it resolves to non-public IP {ip_str}. {hint}"
            )
    return normalized


def _validated_proxy_hosts(url: str, proxies: Optional[dict] = None) -> frozenset:
    return frozenset(
        _assert_proxy_host_is_public(host) for host in _proxy_hosts(url, proxies)
    )


_dns_patch_lock = threading.Lock()


@contextmanager
def _pin_dns(
    hostname: str,
    pinned_ip: str,
    port: int,
    exempt_hosts: frozenset = frozenset(),
) -> Iterator[None]:
    if not _dns_patch_lock.acquire(blocking=False):
        raise URLSafetyError(
            "DNS-pinned fetch already in progress on another thread; "
            "url_safety is not thread-safe by design."
        )

    original_getaddrinfo = socket.getaddrinfo
    target = hostname.lower()

    def patched(host, requested_port, *args, **kwargs):
        if host and host.lower() == target:
            family = kwargs.get("family", args[0] if args else 0)
            if family in (0, socket.AF_UNSPEC, socket.AF_INET):
                return [(
                    socket.AF_INET,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                    "",
                    (pinned_ip, requested_port or port),
                )]
            raise socket.gaierror(
                socket.EAI_FAIL,
                f"url_safety: address family {family} refused for pinned IPv4 host {host}",
            )

        if host and host.lower() in exempt_hosts:
            result = original_getaddrinfo(host, requested_port, *args, **kwargs)
            try:
                ipaddress.ip_address(host.strip("[]"))
            except ValueError:
                for info in result:
                    sockaddr = info[4]
                    if sockaddr and not is_safe_ip(sockaddr[0]):
                        raise socket.gaierror(
                            socket.EAI_FAIL,
                            f"url_safety: exempt proxy host {host} resolved to "
                            f"non-public IP {sockaddr[0]} after validation",
                        )
            return result

        result = original_getaddrinfo(host, requested_port, *args, **kwargs)
        for info in result:
            sockaddr = info[4]
            if not sockaddr:
                continue
            ip_str = sockaddr[0]
            if not is_safe_ip(ip_str):
                raise socket.gaierror(
                    socket.EAI_FAIL,
                    f"url_safety: refused to resolve {host!r} to non-public IP {ip_str}",
                )
        return result

    socket.getaddrinfo = patched  # type: ignore[assignment]
    try:
        yield
    finally:
        socket.getaddrinfo = original_getaddrinfo  # type: ignore[assignment]
        _dns_patch_lock.release()


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/150.0.7871.114 Safari/537.36 SEOGEOSuite/2.5"
)

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

_CONTENT_TYPE_CHARSET_RE = re.compile(r"charset\s*=\s*['\"]?([^;,'\"\s>]+)", re.IGNORECASE)
_META_CHARSET_RE = re.compile(
    r"<meta[^>]+charset\s*=\s*['\"]?([^;,'\"\s/>]+)",
    re.IGNORECASE,
)
_BOMS = (
    (b"\xef\xbb\xbf", "utf-8-sig"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
)


def _decode_bytes(raw: bytes, encoding: str) -> str:
    try:
        return raw.decode(encoding, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


def _extract_charset_from_content_type(content_type: str) -> str | None:
    match = _CONTENT_TYPE_CHARSET_RE.search(content_type or "")
    return match.group(1).strip() if match else None


def _extract_meta_charset(raw: bytes) -> str | None:
    head = raw[:4096].decode("ascii", errors="ignore")
    match = _META_CHARSET_RE.search(head)
    return match.group(1).strip() if match else None


def decode_response_text(response) -> str:
    content_type = response.headers.get("Content-Type", "") if response.headers else ""
    return decode_body(response.content or b"", content_type)


def decode_body(raw: bytes, content_type: str = "") -> str:
    raw = raw or b""
    for marker, encoding in _BOMS:
        if raw.startswith(marker):
            return _decode_bytes(raw[len(marker):], encoding.replace("-sig", ""))

    charset = _extract_charset_from_content_type(content_type)
    if charset:
        return _decode_bytes(raw, charset)

    charset = _extract_meta_charset(raw)
    if charset:
        return _decode_bytes(raw, charset)

    return raw.decode("utf-8", errors="replace")


MAX_PAGE_BYTES = 10 * 1024 * 1024
MAX_REDIRECT_BODY_BYTES = 64 * 1024


def read_bounded(response, max_bytes: int) -> tuple[bytes, bool]:
    chunks = []
    size = 0
    too_large = False
    for chunk in response.iter_content(chunk_size=65536):
        if not chunk:
            continue
        size += len(chunk)
        if size > max_bytes:
            too_large = True
            break
        chunks.append(chunk)
    return b"".join(chunks), too_large


MAX_JSON_DEPTH = 256
_JSON_DEPTH_TOKEN_RE = re.compile(r'"(?:[^"\\]|\\[\s\S])*"?|[\[\]{}]')


def json_depth_exceeds(text: str, max_depth: int = MAX_JSON_DEPTH) -> bool:
    depth = 0
    for match in _JSON_DEPTH_TOKEN_RE.finditer(text):
        token = match.group()
        if token in "[{":
            depth += 1
            if depth > max_depth:
                return True
        elif token in "]}":
            depth -= 1
    return False


def _bound_redirect_body(response, *args, **kwargs):
    if not response.is_redirect or response._content is not False:
        return response
    try:
        body, _too_large = read_bounded(response, MAX_REDIRECT_BODY_BYTES)
    except (requests.RequestException, RuntimeError):
        body = b""
    if response.raw is not None:
        response.raw.close()
    response._content = body
    response._content_consumed = True
    return response


def _with_redirect_body_cap(kwargs: dict) -> dict:
    hooks = dict(kwargs.get("hooks") or {})
    existing = hooks.get("response") or []
    if callable(existing):
        existing = [existing]
    hooks["response"] = [_bound_redirect_body, *existing]
    kwargs["hooks"] = hooks
    return kwargs


def _with_default_headers(kwargs: dict) -> dict:
    headers = dict(DEFAULT_REQUEST_HEADERS)
    headers.update(kwargs.get("headers") or {})
    kwargs["headers"] = headers
    return kwargs


def safe_requests_get(
    url: str,
    *,
    timeout: int = 30,
    **kwargs,
) -> requests.Response:
    norm_url, pinned_ip = validate_url_strict(url)
    parsed = urlparse(norm_url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    assert parsed.hostname is not None
    kwargs = _with_redirect_body_cap(_with_default_headers(kwargs))
    exempt = _validated_proxy_hosts(norm_url, kwargs.get("proxies"))
    with _pin_dns(parsed.hostname, pinned_ip, port, exempt_hosts=exempt):
        return requests.get(norm_url, timeout=timeout, **kwargs)


def safe_requests_head(
    url: str,
    *,
    timeout: int = 30,
    **kwargs,
) -> requests.Response:
    norm_url, pinned_ip = validate_url_strict(url)
    parsed = urlparse(norm_url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    assert parsed.hostname is not None
    kwargs = _with_default_headers(kwargs)
    exempt = _validated_proxy_hosts(norm_url, kwargs.get("proxies"))
    with _pin_dns(parsed.hostname, pinned_ip, port, exempt_hosts=exempt):
        return requests.head(norm_url, timeout=timeout, **kwargs)


@contextmanager
def safe_requests_session(url: str) -> Iterator[requests.Session]:
    norm_url, pinned_ip = validate_url_strict(url)
    parsed = urlparse(norm_url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    assert parsed.hostname is not None
    session = requests.Session()
    session.hooks["response"].append(_bound_redirect_body)
    exempt = _validated_proxy_hosts(norm_url, session.proxies)
    with _pin_dns(parsed.hostname, pinned_ip, port, exempt_hosts=exempt):
        try:
            yield session
        finally:
            session.close()


def make_safe_playwright_route_handler(
    blocked_resource_types: Optional[set] = None,
):
    blocked = set(blocked_resource_types or ())

    def handler(route, request):
        try:
            if blocked and request.resource_type in blocked:
                route.abort()
                return

            parsed = urlparse(request.url)
            if parsed.scheme not in ("http", "https"):
                route.continue_()
                return
            host = parsed.hostname
            if not host:
                route.abort()
                return

            try:
                normalized = normalize_hostname(host)
            except URLSafetyError:
                route.abort()
                return

            if normalized in _BLOCKED_HOSTNAMES:
                route.abort()
                return

            try:
                addrinfo = socket.getaddrinfo(
                    normalized,
                    None,
                    family=socket.AF_UNSPEC,
                    type=socket.SOCK_STREAM,
                )
            except socket.gaierror:
                route.abort()
                return
            ips = {info[4][0] for info in addrinfo}
            if not ips or any(not is_safe_ip(ip) for ip in ips):
                route.abort()
                return
            route.continue_()
        except Exception:
            try:
                route.abort()
            except Exception:
                pass

    return handler


def _never_connect_web_socket(ws) -> None:
    return None


def new_guarded_context(browser, route_handler, **context_kwargs):
    context = browser.new_context(service_workers="block", **context_kwargs)
    context.route("**/*", route_handler)
    context.route_web_socket("**/*", _never_connect_web_socket)
    return context
