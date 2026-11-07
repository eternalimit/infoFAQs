#!/usr/bin/env python3
"""Read-only public/origin comparison for Gate 5. Never modifies DNS or hosting."""
import difflib
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

HOST = "infofaqs.com"
# IP addresses obtained in the previous Gate 5 DNS receipt for GitHub Pages.
PAGES_IPS = ["185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"]
PATHS = [("/", "index.html"), ("/marketplace-preview.html", "marketplace-preview.html")]
report = {"method": "curl with strict TLS, compare Cloudflare path to direct GitHub Pages IP, no DNS changes", "probes": []}

def probe(url, ip=None):
    with tempfile.TemporaryDirectory() as d:
        h, b = str(Path(d)/"headers"), str(Path(d)/"body")
        cmd = ["curl", "--noproxy", "*", "--silent", "--show-error", "--connect-timeout", "10",
               "--max-time", "25", "--max-redirs", "0", "--dump-header", h,
               "--output", b, "--write-out", "%{http_code}"]
        if ip:
            cmd += ["--resolve", HOST + ":443:" + ip]
        cmd.append(url)
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=35)
        raw = Path(b).read_bytes() if Path(b).exists() else b""
        headers = Path(h).read_text(errors="replace") if Path(h).exists() else ""
        keep = ("server:", "cf-ray:", "cf-cache-status:", "location:", "cache-control:", "content-type:", "last-modified:", "etag:")
        return {"url": url, "direct_pages_ip": ip, "curl_exit": p.returncode,
                "http_status": p.stdout.strip(), "stderr": p.stderr[:500],
                "response_bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest() if raw and p.returncode == 0 else None,
                "headers": [s.strip() for s in headers.splitlines() if s.lower().startswith(keep)],
                "_body": raw}

for path, source_path in PATHS:
    source = Path(source_path).read_bytes()
    url = "https://" + HOST + path
    for ip in [None] + PAGES_IPS[:2]:
        result = probe(url, ip)
        body = result.pop("_body")
        result["source_sha256"] = hashlib.sha256(source).hexdigest()
        result["matches_source"] = bool(body) and hashlib.sha256(body).hexdigest() == result["source_sha256"]
        if body and path == "/" and not result["matches_source"]:
            delta = difflib.unified_diff(source.decode("utf-8", "replace").splitlines(),
                                        body.decode("utf-8", "replace").splitlines(),
                                        fromfile="git-source", tofile="observed-response", lineterm="")
            result["diff_first_1800_chars"] = "\n".join(list(delta)[:16])[:1800]
        report["probes"].append(result)
Path("gate5-origin-diagnostics.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
