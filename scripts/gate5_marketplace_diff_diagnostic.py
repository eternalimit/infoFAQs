#!/usr/bin/env python3
"""Read-only differential diagnosis of public Marketplace HTML.

Never prints contact addresses or full page content. No external changes.
"""
import difflib
import hashlib
import json
import urllib.request
from pathlib import Path

url = "https://infofaqs.com/marketplace.html"
source = Path("marketplace.html").read_bytes()
samples = []
for n in range(3):
    req = urllib.request.Request(url, headers={"User-Agent": "InfoFAQs-Gate5-Diagnostic/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=25) as response:
        body = response.read(100000)
        samples.append(body)
        print(json.dumps({
            "sample": n + 1,
            "http_status": response.status,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "cloudflare_email_protection_marker": b"/cdn-cgi/l/email-protection" in body or b"__cf_email__" in body,
            "cloudflare_email_decode_script": b"email-decode.min.js" in body,
            "cloudflare_rocket_loader": b"rocket-loader" in body,
            "cloudflare_challenge_marker": b"cf-chl-" in body,
            "content_encoding": response.headers.get("Content-Encoding"),
            "server": response.headers.get("Server"),
            "cf_cache_status": response.headers.get("CF-Cache-Status"),
        }))
    original_lines = source.decode("utf-8", "replace").splitlines()
    delivered_lines = body.decode("utf-8", "replace").splitlines()
    edits = list(difflib.SequenceMatcher(None, original_lines, delivered_lines, autojunk=False).get_opcodes())
    print(json.dumps({"sample": n + 1, "diff_operations": [
        {"operation": tag, "source_lines": [i1 + 1, i2], "delivered_lines": [j1 + 1, j2]}
        for tag, i1, i2, j1, j2 in edits if tag != "equal"
    ]}))
print(json.dumps({"samples_identical": len(set(samples)) == 1, "source_identical": all(s == source for s in samples)}))
