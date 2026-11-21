"""Step 8: package a cut or thumbnail for a fresh judge agent (RULES.md rule 2).

Makes gauntlet/<name>/ with:
  frames.jpg      - first frame large + 11 evenly spaced frames (videos), or the image itself
  phone.png       - thumbnails only: the image at 168x94, phone search size
  reference.jpg   - 6 outlier thumbnails from data/thumbs for comparison
  info.txt        - duration, size, platform target
The judge gets only this folder plus gauntlet/JUDGE.md, never our notes.

  python3 scripts/gauntlet_pack.py out/v1.mp4 --platform tiktok
"""
import argparse
import glob
import random
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height",
                        "-of", "default=nw=1", f], capture_output=True, text=True, check=True)
    return r.stdout


def frames(video, n=12):
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                              video], capture_output=True, text=True, check=True).stdout)
    tmp = Path(tempfile.mkdtemp())
    out = []
    for i, t in enumerate([0.05] + [d * k / n for k in range(1, n)]):
        f = tmp / f"{i}.png"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", str(f)],
                       check=True)
        out.append(Image.open(f).convert("RGB"))
    return out


def grid(ims, cols, cell_w):
    cell_h = round(cell_w * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    g = Image.new("RGB", (cols * cell_w, rows * cell_h), "black")
    for i, im in enumerate(ims):
        g.paste(im.resize((cell_w, cell_h)), ((i % cols) * cell_w, (i // cols) * cell_h))
    return g


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--platform", required=True, help="youtube | youtube-shorts | tiktok | instagram")
    a = p.parse_args()
    src = Path(a.file)
    dst = ROOT / "gauntlet" / src.stem
    dst.mkdir(parents=True, exist_ok=True)

    if src.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
        im = Image.open(src).convert("RGB")
        im.save(dst / "frames.jpg", quality=90)
        im.resize((168, 94), Image.LANCZOS).save(dst / "phone.png")
        info = f"thumbnail {im.width}x{im.height}"
    else:
        fr = frames(str(src))
        first = fr[0].resize((fr[0].width // 2, fr[0].height // 2))
        rest = grid(fr[1:], 6 if fr[0].height > fr[0].width else 4, 300)
        sheet = Image.new("RGB", (max(first.width, rest.width), first.height + rest.height), "black")
        sheet.paste(first, (0, 0))
        sheet.paste(rest, (0, first.height))
        sheet.save(dst / "frames.jpg", quality=88)
        info = probe(str(src))

    thumbs = sorted(glob.glob(str(ROOT / "data" / "thumbs" / "*.jpg")))
    if thumbs:
        random.seed(src.stem)
        grid([Image.open(t).convert("RGB") for t in random.sample(thumbs, min(6, len(thumbs)))], 3, 400) \
            .save(dst / "reference.jpg", quality=85)
    (dst / "info.txt").write_text(f"file: {src.name}\nplatform: {a.platform}\n{info}")
    print(dst)


if __name__ == "__main__":
    main()
