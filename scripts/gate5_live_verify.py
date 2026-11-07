#!/usr/bin/env python3
"""Gate 5 live HTTPS/DNS/source receipts. Read-only, fail closed."""
import datetime
import hashlib
import json
import os
import socket
import ssl
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://infofaqs.com"
URLS = [
    BASE + "/",
    "https://www.infofaqs.com/",
    BASE + "/robots.txt",
    BASE + "/sitemap.xml",
    BASE + "/10-faqs.html",
    BASE + "/catbot100.html",
    BASE + "/marketplace.html",
    BASE + "/mine/uni/",
]
report = {
    "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "repository": os.getenv("GITHUB_REPOSITORY", "unknown"),
    "source_commit": os.getenv("SOURCE_COMMIT", os.getenv("GITHUB_SHA", "unknown")),
    "dns": {},
    "tls": {},
    "http": {},
    "checks": {},
}
failures = []

for host in ("infofaqs.com", "www.infofaqs.com"):
    report["dns"][host] = {}
    for record_type in ("A", "AAAA", "CNAME", "NS"):
        try:
            p = subprocess.run(
                ["dig", "+time=5", "+tries=2", "+short", host, record_type],
                capture_output=True, text=True, timeout=15,
            )
            report["dns"][host][record_type] = p.stdout.strip().splitlines()
        except Exception as exc:
            report["dns"][host][record_type] = {"error": str(exc)}
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=15) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as tls:
                cert = tls.getpeercert()
                report["tls"][host] = {
                    "validated": True,
                    "protocol": tls.version(),
                    "notAfter": cert.get("notAfter"),
                    "subject": str(cert.get("subject", "")),
                    "issuer": str(cert.get("issuer", "")),
                }
    except Exception as exc:
        report["tls"][host] = {"validated": False, "error": str(exc)}
        failures.append("TLS trust failed: " + host)

for url in URLS:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "InfoFAQs-Gate5-ReadOnly/1.0",
            "Cache-Control": "no-cache",
        })
        with urllib.request.urlopen(req, timeout=25) as response:
            data = response.read(3_000_001)
            truncated = len(data) > 3_000_000
            item = {
                "status": response.status,
                "final_url": response.url,
                "content_type": response.headers.get("Content-Type"),
                "bytes_read": len(data),
                "sha256": hashlib.sha256(data).hexdigest() if not truncated else None,
                "truncated": truncated,
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
            }
            report["http"][url] = item
            if truncated or response.status != 200:
                failures.append("Unexpected response: " + url)
            if url == BASE + "/":
                html = data.decode("utf-8", errors="replace").lower()
                for name, token in (
                    ("catbot100", "catbot"),
                    ("ten_faqs", "10-faqs"),
                    ("human_green_button", "human"),
                    ("mind_uni", "mine/uni"),
                ):
                    found = token in html
                    report["checks"]["homepage_" + name] = found
                    if not found:
                        failures.append("Homepage feature missing: " + name)
            if url == "https://www.infofaqs.com/":
                canonical = response.url.rstrip("/") == BASE
                report["checks"]["www_redirects_to_apex"] = canonical
                if not canonical:
                    failures.append("WWW does not redirect to canonical apex")
            if url.endswith("/robots.txt"):
                ok = b"Sitemap: https://infofaqs.com/sitemap.xml" in data
                report["checks"]["robots_sitemap_declaration"] = ok
                if not ok:
                    failures.append("Robots sitemap declaration missing")
            if url.endswith("/sitemap.xml"):
                ok = b"https://infofaqs.com/" in data
                report["checks"]["sitemap_canonical_present"] = ok
                if not ok:
                    failures.append("Canonical sitemap URL missing")
    except Exception as exc:
        report["http"][url] = {"error": str(exc)}
        failures.append("Fetch failed: " + url)


# Compare deployed bytes against the exact checked-out public allowlist.
for url, relative in (
    (BASE + "/", "index.html"),
    (BASE + "/robots.txt", "robots.txt"),
    (BASE + "/sitemap.xml", "sitemap.xml"),
    (BASE + "/10-faqs.html", "10-faqs.html"),
    (BASE + "/catbot100.html", "catbot100.html"),
    (BASE + "/marketplace.html", "marketplace.html"),
    (BASE + "/mine/uni/", "mine/uni/index.html"),
):
    source = Path(relative)
    if not source.is_file():
        failures.append("Expected source missing: " + relative)
        continue
    expected_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    actual_sha = report["http"].get(url, {}).get("sha256")
    report["checks"]["source_" + relative] = {
        "source_sha256": expected_sha,
        "production_sha256": actual_sha,
        "match": expected_sha == actual_sha,
    }
    if expected_sha != actual_sha:
        failures.append("Production/source mismatch: " + relative)

report["failures"] = failures
report["gate5_status"] = "PASS" if not failures else "HOLD"
Path("gate5-receipt.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
if failures:
    raise SystemExit(1)
