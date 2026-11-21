"""Step 2b: pull recent videos from approved channels and keep the outliers.

Free replacement for Apify's YouTube channel scraper: yt-dlp flat channel listing.
Reads data/channels_approved.csv (column: url). Writes data/outliers.csv and prints
what changed since the previous run (kept in data/outliers_prev.csv).

Outlier = a video whose views are >= OUTLIER_X times that channel's median for the
same format (long-form vs Shorts), across its last N uploads. Only GTA titles are kept;
the median uses every upload so it reflects the channel's usual views.
Usage: python3 scripts/find_outliers.py
"""
import csv
import json
import re
import shutil
import statistics
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
APPROVED = DATA / "channels_approved.csv"
OUT = DATA / "outliers.csv"
PREV = DATA / "outliers_prev.csv"
N = 30
OUTLIER_X = 3.0
MIN_VIEWS = 10_000
GTA = re.compile(r"\bgta\b|grand theft auto|vice city|leonida|lucia|jason", re.I)


def listing(url, tab):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "--dump-json", "--playlist-end", str(N),
                        f"{url.rstrip('/')}/{tab}"], capture_output=True, text=True, timeout=300)
    return [json.loads(l) for l in r.stdout.splitlines() if l.strip()]


def channel_outliers(row):
    url, name = row["url"], row.get("channel") or row["url"]
    rows = []
    for tab, fmt in (("videos", "long"), ("shorts", "short")):
        vids = [v for v in listing(url, tab) if v.get("view_count")]
        if len(vids) < 5:
            continue
        med = statistics.median(v["view_count"] for v in vids)
        for v in vids:
            ratio = v["view_count"] / med if med else 0
            if ratio >= OUTLIER_X and v["view_count"] >= MIN_VIEWS and GTA.search(v.get("title") or ""):
                thumbs = v.get("thumbnails") or []
                rows.append({
                    "channel": name, "format": fmt,
                    "title": v.get("title"), "views": v["view_count"], "channel_median": int(med),
                    "ratio": round(ratio, 1), "duration_s": int(v.get("duration") or 0),
                    "url": f"https://www.youtube.com/watch?v={v['id']}",
                    "thumbnail": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" if fmt == "long"
                                 else (thumbs[-1]["url"] if thumbs else ""),
                })
    return rows


def main():
    chans = list(csv.DictReader(APPROVED.open()))
    with ThreadPoolExecutor(6) as ex:
        rows = [r for rs in ex.map(channel_outliers, chans) for r in rs]
    rows.sort(key=lambda r: r["ratio"], reverse=True)

    old = {r["url"]: r for r in csv.DictReader(OUT.open())} if OUT.exists() else {}
    if OUT.exists():
        shutil.copy(OUT, PREV)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["channel", "format", "title", "views", "channel_median",
                                          "ratio", "duration_s", "url", "thumbnail"])
        w.writeheader()
        w.writerows(rows)

    new = [r for r in rows if r["url"] not in old]
    gone = [r for u, r in old.items() if u not in {x["url"] for x in rows}]
    print(f"{len(rows)} outliers from {len(chans)} channels -> {OUT}")
    if old:
        print(f"Changed since last run: {len(new)} new, {len(gone)} dropped")
        for r in new[:20]:
            print(f"  + {r['ratio']}x  {r['channel']}: {r['title']}")


if __name__ == "__main__":
    sys.exit(main())
