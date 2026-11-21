"""Step 2a: find active English YouTube channels that post GTA videos.

Free replacement for Apify: yt-dlp search + each channel's public RSS feed.
Writes data/channels.csv. Usage: python3 scripts/find_channels.py
"""
import csv
import json
import re
import statistics
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "channels.csv"

QUERIES = [
    "GTA 6", "GTA 6 gameplay", "GTA 6 funny moments", "GTA 6 secrets",
    "GTA 6 easter eggs", "GTA 6 map", "GTA 6 tips and tricks", "GTA 6 best moments",
    "GTA 6 cars", "GTA 6 money guide", "GTA 6 news", "GTA 6 clips",
    "GTA 6 vs GTA 5", "GTA 6 things you missed", "GTA 6 stunts",
]
PER_QUERY = 50
ACTIVE_DAYS = 14
EN_WORDS = set("the a an and of to in is you this i my we how what all every best new vs with for on it".split())
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "m": "http://search.yahoo.com/mrss/"}


def search(q):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "--dump-json", f"ytsearch{PER_QUERY}:{q}"],
                       capture_output=True, text=True, timeout=300)
    return [json.loads(l) for l in r.stdout.splitlines() if l.strip()]


def is_english(title):
    if not title:
        return False
    ascii_ratio = sum(c.isascii() for c in title) / len(title)
    words = set(re.findall(r"[a-z]+", title.lower()))
    return ascii_ratio > 0.9 and bool(words & EN_WORDS)


def is_gta(title):
    return bool(re.search(r"\bgta\b|grand theft auto|vice city|leonida|lucia|jason", title, re.I))


def feed(cid):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
    try:
        xml = urllib.request.urlopen(url, timeout=30).read()
    except Exception as e:
        print(f"feed failed {cid}: {e}", file=sys.stderr)
        return []
    vids = []
    for e in ET.fromstring(xml).findall("a:entry", NS):
        stats = e.find("m:group/m:community/m:statistics", NS)
        vids.append({
            "title": e.findtext("a:title", "", NS),
            "published": datetime.fromisoformat(e.findtext("a:published", "", NS)),
            "views": int(stats.get("views", 0)) if stats is not None else 0,
            "shorts": "/shorts/" in (e.find("a:link", NS).get("href") or ""),
        })
    return vids


def main():
    seen = {}
    with ThreadPoolExecutor(5) as ex:
        for results in ex.map(search, QUERIES):
            for v in results:
                cid = v.get("channel_id")
                if cid and is_english(v.get("title", "")):
                    seen.setdefault(cid, {"channel": v.get("channel"), "url": v.get("uploader_url") or v.get("channel_url"),
                                          "hits": 0})["hits"] += 1
    print(f"{len(seen)} English candidate channels from search", file=sys.stderr)

    now = datetime.now(timezone.utc)
    with ThreadPoolExecutor(8) as ex:
        feeds = dict(zip(seen, ex.map(feed, seen)))

    rows = []
    for cid, info in seen.items():
        vids = feeds[cid]
        if not vids:
            continue
        latest = max(v["published"] for v in vids)
        days = (now - latest).days
        gta_share = sum(is_gta(v["title"]) for v in vids) / len(vids)
        en_share = sum(is_english(v["title"]) for v in vids) / len(vids)
        if days > ACTIVE_DAYS or gta_share < 0.3 or en_share < 0.6:
            continue
        rows.append({
            "channel": info["channel"], "channel_id": cid, "url": info["url"],
            "median_views_recent15": int(statistics.median(v["views"] for v in vids)),
            "uploads_last_14d": sum((now - v["published"]).days <= 14 for v in vids),
            "gta_share": round(gta_share, 2), "latest_upload": latest.date().isoformat(),
            "search_hits": info["hits"],
        })
    rows.sort(key=lambda r: r["median_views_recent15"], reverse=True)
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} active English GTA channels -> {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
