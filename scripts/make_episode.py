"""Step 5: edit the daily best-clips episode (16:9).

No intro: the first row of the clips CSV opens the video. Every clip gets a one-line
label and the streamer's handle as a lower third. Writes the episode, plus a
description with chapters and a credit link for every streamer.

clips CSV columns: file,label,handle,site,source_url[,start,end]
  python3 scripts/make_episode.py --clips data/episode_2026-11-22.csv \
      --title "GTA 6's Best Clips Today" --out out/episode_2026-11-22.mp4
"""
import argparse
import csv
import subprocess
import tempfile
from pathlib import Path

W, H, FPS = 1920, 1080, 30
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def credit(site, handle):
    return {"twitch": f"https://www.twitch.tv/{handle}", "kick": f"https://kick.com/{handle}",
            "tiktok": f"https://www.tiktok.com/@{handle}"}.get(site, handle)


def norm(row, i, tmp):
    """Scale/pad to 1080p30, even loudness, burn the label + handle lower third."""
    label, handle = tmp / f"l{i}.txt", tmp / f"h{i}.txt"
    label.write_text(row["label"])
    handle.write_text({"twitch": "twitch.tv/", "kick": "kick.com/"}.get(row["site"], "@") + row["handle"])
    seek = ["-ss", row["start"]] if row.get("start") else []
    until = ["-to", row["end"]] if row.get("end") else []
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},"
          f"drawbox=x=0:y=ih-190:w=iw:h=190:color=black@0.55:t=fill:enable='lt(t,4)',"
          f"drawtext=fontfile={FONT}:textfile={label}:fontsize=64:fontcolor=white:x=60:y=h-170:enable='lt(t,4)',"
          f"drawtext=fontfile={FONT}:textfile={handle}:fontsize=40:fontcolor=0xFFDE00:x=60:y=h-86")
    out = tmp / f"c{i}.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", *seek, *until, "-i", row["file"], "-vf", vf,
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000", "-ac", "2",
         "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", str(out)])
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--clips", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    rows = list(csv.DictReader(open(a.clips)))
    tmp = Path(tempfile.mkdtemp())
    parts = [norm(r, i, tmp) for i, r in enumerate(rows)]
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", "-movflags", "+faststart", a.out])

    t, chapters, credits = 0.0, [], []
    for r, part in zip(rows, parts):
        chapters.append(f"{int(t // 60)}:{int(t % 60):02d} {r['label']} ({r['handle']})")
        link = credit(r["site"], r["handle"])
        if link not in credits:
            credits.append(link)
        t += dur(str(part))
    desc = (f"{a.title}\n\nEvery clip belongs to the streamer who made it. Go follow them:\n"
            + "\n".join(credits) + "\n\nChapters:\n" + "\n".join(chapters)
            + "\n\nOriginal clips:\n" + "\n".join(r["source_url"] for r in rows) + "\n")
    Path(a.out).with_suffix(".description.txt").write_text(desc)
    print(f"{a.out} ({t / 60:.1f} min, {len(rows)} clips)")


if __name__ == "__main__":
    main()
