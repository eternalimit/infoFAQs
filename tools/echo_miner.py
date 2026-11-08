#!/usr/bin/env python3
"""Build a ranked, outbound-link directory from Tranco.

This tool does not clone websites, proxy traffic, copy page HTML, or bypass
robots.txt. Optional enrichment reads only page title and meta description
where robots.txt permits crawling.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "top-sites.json"
USER_AGENT = "InfoFAQsEchoMiner/1.0 (+https://infofaqs.com/)"
SOURCE = "https://tranco-list.eu/"
MAX_BYTES = 512_000

class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = []
        self.description = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "meta":
            name = (attrs.get("name") or attrs.get("property") or "").lower()
            if name in ("description", "og:description") and not self.description:
                self.description = attrs.get("content", "").strip()

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and len("".join(self.title)) < 300:
            self.title.append(data.strip())

def fetch(url: str, limit: int = MAX_BYTES):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=12) as response:
        return response.status, response.geturl(), response.read(limit)

def load_domains(list_id: str, count: int):
    url = f"https://tranco-list.eu/download/{list_id}/{count}"
    status, final_url, raw = fetch(url, 2_000_000)
    if status != 200:
        raise RuntimeError(f"Tranco download returned HTTP {status}")
    rows = []
    text = raw.decode("utf-8-sig", errors="replace")
    for row in csv.reader(text.splitlines()):
        if len(row) < 2:
            continue
        try:
            rank = int(row[0].strip())
        except ValueError:
            continue
        domain = row[1].strip().lower().rstrip(".")
        if domain and rank <= count:
            rows.append({"rank": rank, "domain": domain,
                         "url": f"https://{domain}/",
                         "title": "", "description": "",
                         "metadata_status": "not_checked"})
    rows.sort(key=lambda item: item["rank"])
    if len(rows) != count:
        raise RuntimeError(f"Expected {count} ranked domains; received {len(rows)}. No partial catalog written.")
    return final_url, rows

def robots_allows(domain: str, target: str):
    robots_url = f"https://{domain}/robots.txt"
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        _, final_url, raw = fetch(robots_url, 256_000)
        parser.parse(raw.decode("utf-8", errors="replace").splitlines())
        return parser.can_fetch(USER_AGENT, target), parser, final_url
    except HTTPError as exc:
        # RFC 9309: 4xx means robots is unavailable; 5xx means unreachable.
        if 400 <= exc.code < 500 and exc.code != 429:
            return True, parser, robots_url
        return False, parser, robots_url
    except (URLError, TimeoutError, OSError):
        return False, parser, robots_url

def enrich(entry):
    domain = entry["domain"]
    allowed, robots, robots_url = robots_allows(domain, entry["url"])
    if not allowed:
        entry["metadata_status"] = "skipped_robots_or_unreachable"
        entry["robots_url"] = robots_url
        return entry
    delay = robots.crawl_delay(USER_AGENT) or robots.crawl_delay("*") or 1
    time.sleep(min(max(delay, 1), 10))
    try:
        status, final_url, raw = fetch(entry["url"])
        parser = MetadataParser()
        parser.feed(raw.decode("utf-8", errors="replace"))
        entry["url"] = final_url
        entry["title"] = " ".join(" ".join(parser.title).split())[:300]
        entry["description"] = parser.description[:500]
        entry["metadata_status"] = f"http_{status}"
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        entry["metadata_status"] = "fetch_failed"
    return entry

def main():
    ap = argparse.ArgumentParser(description="Create InfoFAQs top-sites directory data.")
    ap.add_argument("--list-id", default="latest", help="Permanent Tranco list ID, or latest (default: latest)")
    ap.add_argument("--count", type=int, default=1000, choices=range(1, 1001))
    ap.add_argument("--enrich", action="store_true",
                    help="Read title/description only, after robots.txt permission checks.")
    args = ap.parse_args()

    list_id = args.list_id
    if list_id == "latest":
        _, _, raw_id = fetch("https://tranco-list.eu/top-1m-id", 256)
        list_id = raw_id.decode("utf-8", errors="replace").strip()
        if not list_id or any(ch not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for ch in list_id):
            raise RuntimeError("Could not resolve a valid current Tranco list ID.")
    download_url, entries = load_domains(list_id, args.count)
    if args.enrich:
        for index, entry in enumerate(entries, 1):
            enrich(entry)
            if index % 50 == 0:
                print(f"Processed {index}/{len(entries)}")

    payload = {
        "name": "InfoFAQs Top Sites Directory",
        "description": "Ranked outbound links; not mirrors or copies of third-party websites.",
        "source": SOURCE,
        "source_download": download_url,
        "ranking": "Tranco",
        "list_id": list_id,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "count": len(entries),
        "enrichment": "robots.txt-respecting title/description only" if args.enrich else "ranked domains only",
        "entries": entries,
    }
    DATA.parent.mkdir(parents=True, exist_ok=True)
    temp = DATA.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(DATA)
    print(f"Wrote {len(entries)} entries to {DATA}")

if __name__ == "__main__":
    main()
