#!/usr/bin/env python3
"""Fail-closed validation of the exact InfoFAQs public Pages artifact."""
from pathlib import Path
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET

root = Path("_site")
required = ["index.html", "404.html", "robots.txt", "robot.txt", "sitemap.xml",
            "business-profile.json", "CNAME", "catbot100.html", "10-faqs.html",
            "marketplace.html", "marketplace-preview.html", "top-sites.html", "data/top-sites.json", "craft-engine.mjs", "artifact-library.mjs", "mine/uni/index.html",
            "gateway/genesis/index.html", "gateway/genesis/README.md",
            "gateway/genesis/COSMO8.md", "gateway/genesis/BACKWARDS_PROTOCOL.md", "bin/index.html", "receipt/index.html",
            "genesis/by-monroe.html", "board/lipin.html", ".nojekyll"]
errors = []
for name in required:
    p = root / name
    if not p.is_file() or p.is_symlink():
        errors.append("Missing or unsafe published file: " + name)
    elif name != ".nojekyll":
        source = Path(name)
        if not source.is_file() or source.read_bytes() != p.read_bytes():
            errors.append("Artifact/source byte mismatch: " + name)
actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
if actual != set(required):
    errors.append("Public allowlist differs: " + repr(sorted(actual ^ set(required))))
if (root / "catbot100.html").is_file():
    game = (root / "catbot100.html").read_text(encoding="utf-8")
    if 'from "./craft-engine.mjs"' not in game:
        errors.append("CAT BOT page does not load the crafting engine core")
    if "Crafting Engine" not in game or "createCraftReceipt" not in game:
        errors.append("CAT BOT crafting interface or receipt integration is missing")
if (root / "index.html").is_file():
    home = (root / "index.html").read_text(encoding="utf-8")
    if 'href="marketplace.html"' not in home:
        errors.append("Homepage does not link to final marketplace")
    if "marketplace-preview.html" in home:
        errors.append("Homepage still links to preview marketplace")
if (root / "marketplace-preview.html").is_file():
    legacy = (root / "marketplace-preview.html").read_text(encoding="utf-8")
    if 'url=https://infofaqs.com/marketplace.html' not in legacy:
        errors.append("Legacy marketplace does not redirect to official marketplace")
if (root / "mine/uni/index.html").is_file():
    course = (root / "mine/uni/index.html").read_text(encoding="utf-8")
    if "/marketplace-preview.html" in course:
        errors.append("MINE.UNI links to legacy marketplace")
if (root / "marketplace.html").is_file():
    shop = (root / "marketplace.html").read_text(encoding="utf-8")
    if 'https://infofaqs.com/marketplace.html' not in shop:
        errors.append("Marketplace canonical URL incorrect")
    lower_shop = shop.lower()
    if 'name="robots" content="noindex,nofollow"' not in lower_shop:
        errors.append("Marketplace must be excluded from search indexing")
    if "under construction" not in lower_shop:
        errors.append("Marketplace must display under-construction status")
    if "exclusively through the official yci shopify storefront" not in lower_shop:
        errors.append("Marketplace must enforce Shopify-only commerce")
    if "mailto:" in lower_shop or "type=" + '"submit"' in lower_shop:
        errors.append("Marketplace must not collect sales inquiries or orders")
    if "payment details" not in lower_shop or "does not accept orders" not in lower_shop:
        errors.append("Marketplace commerce boundary notice is missing")
if (root / "sitemap.xml").is_file():
    try:
        tree = ET.parse(root / "sitemap.xml")
        urls = [e.text for e in tree.iter() if e.tag.endswith("loc")]
        if "https://infofaqs.com/marketplace.html" in urls:
            errors.append("Under-construction marketplace must not appear in sitemap")
        if any("marketplace-preview" in (u or "") for u in urls):
            errors.append("Old preview marketplace still in sitemap")
    except ET.ParseError as exc:
        errors.append("Invalid sitemap XML: " + str(exc))
if (root / "data/top-sites.json").is_file():
    try:
        catalog = json.loads((root / "data/top-sites.json").read_text(encoding="utf-8"))
        entries = catalog.get("entries", [])
        ranks = [item.get("rank") for item in entries]
        if catalog.get("count") != 1000 or len(entries) != 1000:
            errors.append("Top Sites catalog must contain exactly 1,000 entries")
        if ranks != list(range(1, 1001)):
            errors.append("Top Sites catalog ranks must be consecutive from 1 to 1,000")
        if not catalog.get("list_id") or not catalog.get("source_download"):
            errors.append("Top Sites catalog source provenance is missing")
        if any(not item.get("domain") or not item.get("url", "").startswith("https://") for item in entries):
            errors.append("Top Sites catalog contains an invalid domain or destination")
    except (ValueError, TypeError, AttributeError) as exc:
        errors.append("Invalid Top Sites catalog JSON: " + str(exc))
# Audit every local href/src in published HTML before deployment.
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                self.links.append(value)
for html in root.rglob("*.html"):
    parser = LocalLinks()
    parser.feed(html.read_text(encoding="utf-8"))
    for link in parser.links:
        parts = urlsplit(link)
        if parts.scheme or parts.netloc or link.startswith(("#", "//")):
            continue
        target = unquote(parts.path)
        if not target:
            continue
        dest = root / target.lstrip("/") if target.startswith("/") else html.parent / target
        if dest.is_dir():
            dest = dest / "index.html"
        if not dest.is_file():
            errors.append(f"Broken local link: {html.relative_to(root)} -> {link}")
for name in required:
    p = root / name
    if p.is_file() and name != ".nojekyll":
        print(f"SHA256 {hashlib.sha256(p.read_bytes()).hexdigest()} {name}")
if errors:
    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    sys.exit(1)
print("PASS: exact public artifact is internally consistent; live HTTPS verification still required.")
