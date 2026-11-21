"""Free thumbnail maker (replaces gpt-image / nano banana pro). Rules: THUMBNAILS.md.

Background is a frame from our own footage (or any image). Adds 1-4 big words with a
thick stroke, an optional red arrow or circle, and a saturation/contrast boost.

Examples:
  python3 scripts/make_thumbnail.py --video in.mp4 --text "EVERY SECRET" --out out/t1.jpg
  python3 scripts/make_thumbnail.py --video in.mp4 --at 42.5 --text "NO WAY" \
      --circle 900,400,120 --out out/t2.jpg
  python3 scripts/make_thumbnail.py --image a.png --image b.png --vs --out out/t3.jpg
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets" / "fonts" / "Anton.woff"
W, H = 1280, 720
YELLOW, WHITE, RED, BLACK = (255, 222, 0), (255, 255, 255), (230, 20, 20), (0, 0, 0)


def frame_at(video, t):
    out = Path(tempfile.mkdtemp()) / "f.png"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(t), "-i", video, "-frames:v", "1", str(out)],
                   check=True)
    return Image.open(out).convert("RGB")


def duration(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def score(im):
    """Prefer sharp, bright, colorful frames (what the outliers use)."""
    small = im.resize((320, 180))
    sharp = ImageStat.Stat(small.convert("L").filter(ImageFilter.FIND_EDGES)).mean[0]
    sat = ImageStat.Stat(small.convert("HSV")).mean[1]
    bright = ImageStat.Stat(small.convert("L")).mean[0]
    return sharp * 2 + sat + (60 if 70 < bright < 200 else 0)


def best_frame(video, samples=24):
    d = duration(video)
    frames = [frame_at(video, d * (i + 0.5) / samples) for i in range(samples)]
    return max(frames, key=score)


def cover(im):
    r = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def grade(im):
    im = ImageEnhance.Color(im).enhance(1.35)
    im = ImageEnhance.Contrast(im).enhance(1.15)
    return ImageEnhance.Sharpness(im).enhance(1.3)


def big_text(im, text, color, pos):
    d = ImageDraw.Draw(im)
    lines = text.upper().split("|")
    size = 230 if len(lines) == 1 and len(text) <= 8 else 170 if len(lines) == 1 else 140
    font = ImageFont.truetype(str(FONT), size)
    while max(d.textlength(l, font=font) for l in lines) > W * 0.9:
        size -= 8
        font = ImageFont.truetype(str(FONT), size)
    stroke = max(8, size // 14)
    line_h = int(size * 1.08)
    total = line_h * len(lines)
    y = {"bottom": H - total - 40, "top": 30, "middle": (H - total) // 2}[pos]
    for l in lines:
        x = (W - d.textlength(l, font=font)) // 2
        d.text((x + 10, y + 12), l, font=font, fill=(0, 0, 0, 180), stroke_width=stroke, stroke_fill=BLACK)
        d.text((x, y), l, font=font, fill=color, stroke_width=stroke, stroke_fill=BLACK)
        y += line_h


def circle(im, x, y, r):
    d = ImageDraw.Draw(im)
    for w, c in ((22, BLACK), (14, RED)):
        d.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)


def arrow(im, x1, y1, x2, y2):
    import math
    d = ImageDraw.Draw(im)
    a = math.atan2(y2 - y1, x2 - x1)
    head = [(x2, y2), (x2 - 70 * math.cos(a - 0.5), y2 - 70 * math.sin(a - 0.5)),
            (x2 - 70 * math.cos(a + 0.5), y2 - 70 * math.sin(a + 0.5))]
    bx, by = x2 - 55 * math.cos(a), y2 - 55 * math.sin(a)
    d.line([(x1, y1), (bx, by)], fill=BLACK, width=40)
    d.polygon(head, fill=BLACK)
    d.line([(x1, y1), (bx, by)], fill=RED, width=26)
    d.polygon([(x2 - 8 * math.cos(a), y2 - 8 * math.sin(a))] + head[1:], fill=RED)


def vs_split(a, b):
    left, right = cover(a).crop((W // 4, 0, W // 4 + W // 2, H)), cover(b).crop((W // 4, 0, W // 4 + W // 2, H))
    im = Image.new("RGB", (W, H))
    im.paste(left, (0, 0))
    im.paste(right, (W // 2, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([W // 2 - 4, 0, W // 2 + 4, H], fill=WHITE)
    font = ImageFont.truetype(str(FONT), 200)
    tw = d.textlength("VS", font=font)
    d.text(((W - tw) / 2, H - 290), "VS", font=font, fill=RED, stroke_width=14, stroke_fill=WHITE)
    return im


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--video")
    p.add_argument("--at", type=float, help="seconds; default: auto-pick the best frame")
    p.add_argument("--image", action="append", default=[])
    p.add_argument("--vs", action="store_true", help="split-screen of two --image/--at frames")
    p.add_argument("--text", default="", help="1-4 words; '|' for a line break")
    p.add_argument("--color", choices=["yellow", "white"], default="yellow")
    p.add_argument("--pos", choices=["bottom", "top", "middle"], default="bottom")
    p.add_argument("--circle", help="x,y,r")
    p.add_argument("--arrow", help="x1,y1,x2,y2")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    if a.vs:
        im = vs_split(*[Image.open(i).convert("RGB") for i in a.image[:2]])
    elif a.image:
        im = cover(Image.open(a.image[0]).convert("RGB"))
    else:
        im = cover(frame_at(a.video, a.at) if a.at is not None else best_frame(a.video))
    im = grade(im)
    if a.circle:
        circle(im, *map(int, a.circle.split(",")))
    if a.arrow:
        arrow(im, *map(int, a.arrow.split(",")))
    if a.text:
        big_text(im, a.text, YELLOW if a.color == "yellow" else WHITE, a.pos)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    im.save(a.out, quality=92)
    im.resize((168, 94), Image.LANCZOS).save(Path(a.out).with_suffix(".phone.png"))
    print(a.out)


if __name__ == "__main__":
    main()
