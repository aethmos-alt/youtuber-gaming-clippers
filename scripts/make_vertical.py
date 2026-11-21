"""Step 6: cut a clip into a 1080x1920 vertical.

Layout: facecam on top (if --facecam given), gameplay below. The first frames are the
payoff (--hook), then the clip plays from --start. Word-by-word captions from
faster-whisper sit at ~52% height: clear of TikTok/Reels/Shorts buttons (right edge,
bottom ~20%). The streamer's handle is tagged on screen.

  python3 scripts/make_vertical.py --in clip.mp4 --start 3 --end 38 --hook 31.5 \
      --facecam 1440,780,480,300 --handle xqc --site twitch --out out/v1.mp4
"""
import argparse
import os
import subprocess
import tempfile
from pathlib import Path

W, H = 1080, 1920
CAM_H = 640
HOOK_LEN = 1.2
CAPTION_Y = 1000          # centre line of captions, px from top
FONT = "Inter Black"      # installed system font (libass looks it up by name)


def run(cmd):
    subprocess.run(cmd, check=True)


def trim(src, start, end, hook, dst):
    """Hook segment (payoff) + main segment, concatenated."""
    end_opt = [f"end={end}"] if end else []
    parts, labels = [], []
    if hook is not None:
        parts.append(f"[0:v]trim=start={hook}:end={hook + HOOK_LEN},setpts=PTS-STARTPTS[hv];"
                     f"[0:a]atrim=start={hook}:end={hook + HOOK_LEN},asetpts=PTS-STARTPTS[ha];")
        labels.append("[hv][ha]")
    t = ":".join([f"start={start}"] + end_opt)
    parts.append(f"[0:v]trim={t},setpts=PTS-STARTPTS[mv];[0:a]atrim={t},asetpts=PTS-STARTPTS[ma];")
    labels.append("[mv][ma]")
    fc = "".join(parts) + "".join(labels) + f"concat=n={len(labels)}:v=1:a=1[v][a]"
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-c:a", "aac", dst])


def ts(t):
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f"{h}:{m:02d}:{t % 60:05.2f}"


def captions(src, dst):
    from faster_whisper import WhisperModel
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
    segs, _ = model.transcribe(audio, word_timestamps=True, vad_filter=True)
    words = [w for s in segs for w in (s.words or [])]
    ev = []
    for i, w in enumerate(words):
        end = words[i + 1].start if i + 1 < len(words) and words[i + 1].start - w.end < 0.6 else w.end + 0.15
        txt = w.word.strip().upper().replace("{", "").replace("}", "")
        if txt:
            ev.append(f"Dialogue: 0,{ts(w.start)},{ts(max(end, w.start + 0.12))},W,,0,0,0,,"
                      f"{{\\pos(520,{CAPTION_Y})}}{txt}")
    Path(dst).write_text(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: W,{FONT},104,&H0000DEFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,9,4,5,140,160,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n")
    return len(ev)


def compose(src, ass, facecam, handle, site, dst):
    tag = {"twitch": "twitch.tv/", "kick": "kick.com/"}.get(site, "@") + handle
    tagfile = Path(tempfile.mkdtemp()) / "tag.txt"
    tagfile.write_text(tag)
    if facecam:
        x, y, w, h = facecam
        v = (f"[0:v]crop={w}:{h}:{x}:{y},scale={W}:{CAM_H}:force_original_aspect_ratio=increase,"
             f"crop={W}:{CAM_H}[cam];"
             f"[0:v]scale=-2:{H - CAM_H},crop={W}:{H - CAM_H}[gp];[cam][gp]vstack[base];")
        tag_y = CAM_H + 24
    else:
        v = (f"[0:v]scale=-2:{H},crop={W}:{H},boxblur=30:5,eq=brightness=-0.15[bg];"
             f"[0:v]scale={W}:-2[fg];[bg][fg]overlay=0:(H-h)/2[base];")
        tag_y = 560
    v += (f"[base]subtitles={ass},"
          f"drawtext=fontfile=/usr/share/fonts/opentype/inter/Inter-Black.otf:textfile={tagfile}:"
          f"fontsize=58:fontcolor=white:borderw=6:bordercolor=black:x=40:y={tag_y},fps=30[v]")
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-filter_complex", v, "-map", "[v]", "-map", "0:a",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", dst])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="src", required=True)
    p.add_argument("--start", type=float, default=0)
    p.add_argument("--end", type=float)
    p.add_argument("--hook", type=float, help="payoff time (s) shown first for 1.2s")
    p.add_argument("--facecam", help="x,y,w,h of the facecam in source pixels")
    p.add_argument("--handle", required=True)
    p.add_argument("--site", default="twitch", help="twitch | kick | tiktok")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    tmp = Path(tempfile.mkdtemp())
    trim(a.src, a.start, a.end, a.hook, str(tmp / "cut.mp4"))
    n = captions(str(tmp / "cut.mp4"), str(tmp / "c.ass"))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    compose(str(tmp / "cut.mp4"), str(tmp / "c.ass"),
            tuple(map(int, a.facecam.split(","))) if a.facecam else None, a.handle, a.site, a.out)
    print(f"{a.out} ({n} caption words)")


if __name__ == "__main__":
    main()
