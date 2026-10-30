"""
ORIGINAL SHORTS GENERATOR (monetization-safe)
Renders fully original 1080x1920 vertical Shorts (<60s) for the Quran and AI channels.
No third-party reels are downloaded or re-uploaded.

- Quran: owned recitation clips in assets/audio + bundled ayah text/translations
  (data/quran_ayahs.json), animated Arabic text with Persian & English captions over
  the ambient background in assets/videos (or a generated gradient).
- AI: script from mega_prompt_engine_21 (fallback: channel_ai templates), TTS via
  voice_generator.generate_speech, kinetic word-group captions over generated motion
  graphics (ffmpeg lavfi gradients). Nothing is downloaded.
"""
import json
import random
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

import imageio_ffmpeg

BASE_DIR = Path(__file__).resolve().parent
FFMPEG_EXE = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1920
MAX_SECONDS = 58.0
FONT_FA = BASE_DIR / "Vazirmatn-Bold.ttf"
FONT_AR = BASE_DIR / "assets" / "fonts" / "droid_arabic_bold.ttf"
FONT_EN = BASE_DIR / "assets" / "fonts" / "tahoma_bold.ttf"
AYAH_DATA = BASE_DIR / "data" / "quran_ayahs.json"
AUDIO_DIR = BASE_DIR / "assets" / "audio"
QURAN_BG = BASE_DIR / "assets" / "videos" / "quran_ambient_vertical.mp4"
HAS_RAQM = features.check("raqm")


# ---------------------------------------------------------------- helpers
def _font(path: Path, size: int):
    for p in (path, FONT_FA, FONT_EN):
        try:
            if p.exists():
                return ImageFont.truetype(str(p), size,
                                          layout_engine=ImageFont.Layout.RAQM if HAS_RAQM else ImageFont.Layout.BASIC)
        except Exception:
            continue
    return ImageFont.load_default(size=size)


def _rtl(text: str) -> str:
    """Shape RTL text when libraqm is not available (Pillow BASIC layout)."""
    if HAS_RAQM:
        return text
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(_rtl(trial), font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _text_png(out: Path, text: str, font_path: Path, size: int, color, rtl=False, max_w=940,
              box=True, stroke=3, line_gap=1.35):
    """Transparent full-width PNG with centered wrapped text; returns (path, height)."""
    tmp = Image.new("RGBA", (W, 10))
    d = ImageDraw.Draw(tmp)
    font = _font(font_path, size)
    lines = _wrap(d, text, font, max_w)
    while len(lines) > 6 and size > 30:
        size -= 6
        font = _font(font_path, size)
        lines = _wrap(d, text, font, max_w)
    lh = int(size * line_gap)
    h = lh * len(lines) + 60
    img = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if box:
        widest = max(d.textlength(_rtl(l) if rtl else l, font=font) for l in lines)
        x0 = max(20, int((W - widest) / 2) - 40)
        d.rounded_rectangle([x0, 5, W - x0, h - 5], radius=32, fill=(0, 0, 0, 120))
    y = 30 + lh // 2
    for l in lines:
        s = _rtl(l) if rtl else l
        kw = {"direction": "rtl"} if (rtl and HAS_RAQM) else {}
        d.text((W // 2, y), s, font=font, fill=color, anchor="mm", stroke_width=stroke,
               stroke_fill=(0, 0, 0, 230), **kw)
        y += lh
    img.save(out)
    return out, h


def _duration(path) -> float:
    r = subprocess.run([FFMPEG_EXE, "-i", str(path)], stderr=subprocess.PIPE, text=True)
    for line in r.stderr.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 0.0


def _run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg failed:\n" + r.stderr[-3000:])


def _render(bg_args, overlays, audio_args, audio_filter, total, out: Path, bg_filter, caption_concat=None, caption_y=1000):
    """overlays: list of (png, y, start, end, slide_px)."""
    cmd = [FFMPEG_EXE, "-y"] + bg_args + audio_args
    n_pre = 2
    for png, *_ in overlays:
        cmd += ["-loop", "1", "-t", f"{total:.2f}", "-i", str(png)]
    fc = [f"[0:v]{bg_filter},trim=duration={total:.2f},setpts=PTS-STARTPTS[v0]"]
    last = "v0"
    for i, (png, y, st, en, slide) in enumerate(overlays):
        idx = i + n_pre
        fd = min(0.35, max(0.1, (en - st) / 4))
        fc.append(f"[{idx}:v]format=rgba,fade=t=in:st={st:.2f}:d={fd:.2f}:alpha=1,"
                  f"fade=t=out:st={max(st, en - fd):.2f}:d={fd:.2f}:alpha=1[o{i}]")
        yexpr = f"{y}+{slide}*max(0\\,1-(t-{st:.2f})/0.35)" if slide else str(y)
        fc.append(f"[{last}][o{i}]overlay=x=0:y='{yexpr}':enable='between(t,{st:.2f},{en:.2f})'[v{i + 1}]")
        last = f"v{i + 1}"
    if caption_concat:
        cidx = n_pre + len(overlays)
        cmd += ["-f", "concat", "-safe", "0", "-i", str(caption_concat)]
        fc.append(f"[{cidx}:v]format=rgba,setpts=PTS-STARTPTS[cap]")
        fc.append(f"[{last}][cap]overlay=x=0:y={caption_y}:eof_action=pass[vc]")
        last = "vc"
    fc.append(f"[1:a]{audio_filter}[aout]")
    cmd += ["-filter_complex", ";".join(fc), "-map", f"[{last}]", "-map", "[aout]",
            "-t", f"{total:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
    _run(cmd)
    return out


def _thumb(video: Path, out: Path, at: float):
    subprocess.run([FFMPEG_EXE, "-y", "-ss", f"{at:.2f}", "-i", str(video), "-vframes", "1", "-q:v", "2", str(out)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


# ---------------------------------------------------------------- QURAN
def load_ayahs():
    with open(AYAH_DATA, encoding="utf-8") as f:
        return json.load(f)["clips"]


def render_quran_original(output_dir, run_count: int = 1, clip_name: str = None) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ayahs = load_ayahs()
    names = sorted(n for n in ayahs if (AUDIO_DIR / n).exists())
    if not names:
        raise FileNotFoundError("No recitation clips with matching ayah data in assets/audio")
    name = clip_name or names[(run_count - 1) % len(names)]
    a = ayahs[name]
    audio = AUDIO_DIR / name
    rec = min(_duration(audio) or 8.0, MAX_SECONDS - 6)
    intro = 1.5
    # Hold the ayah on screen after recitation so short clips still read well; min 12s total.
    total = min(MAX_SECONDS, max(12.0, intro + rec + 4.0))
    end_ayah = total - 0.2

    title_png, _ = _text_png(out / "q_title.png", f"{a['surah_ar']} - {a['ref']}", FONT_FA, 60,
                             (255, 215, 120, 255), rtl=True)
    ar_png, ar_h = _text_png(out / "q_ar.png", a["arabic"], FONT_AR, 86, (255, 255, 255, 255), rtl=True, stroke=4)
    fa_png, fa_h = _text_png(out / "q_fa.png", a["fa"], FONT_FA, 50, (190, 240, 210, 255), rtl=True, stroke=2)
    en_png, en_h = _text_png(out / "q_en.png", a["en"], FONT_EN, 44, (235, 235, 235, 255), stroke=2)
    foot_png, _ = _text_png(out / "q_foot.png", "Recitation: Sheikh Yasser Al-Dosari", FONT_EN, 34,
                            (220, 220, 220, 230), box=False, stroke=2)

    ar_y = 560
    fa_y = ar_y + ar_h + 30
    en_y = fa_y + fa_h + 20
    overlays = [
        (title_png, 300, 0.2, end_ayah, 40),
        (ar_png, ar_y, intro, end_ayah, 60),
        (fa_png, fa_y, intro + min(1.5, rec / 3), end_ayah, 40),
        (en_png, en_y, intro + min(2.5, rec / 2), end_ayah, 40),
        (foot_png, 1720, 0.5, end_ayah, 0),
    ]
    if QURAN_BG.exists():
        bg_args = ["-stream_loop", "-1", "-i", str(QURAN_BG)]
        bg_filter = ("scale=1188:2112,crop=1080:1920:x='(in_w-out_w)/2+40*sin(t/4)':y='(in_h-out_h)/2',"
                     "eq=brightness=-0.08:saturation=1.1")
    else:
        bg_args = ["-f", "lavfi", "-i", "gradients=s=1080x1920:c0=0x06281e:c1=0x0b4d3a:c2=0x1a1a3a:speed=0.008:r=30"]
        bg_filter = "null"
    audio_args = ["-i", str(audio)]
    afilter = f"adelay={int(intro * 1000)}|{int(intro * 1000)},apad,afade=t=out:st={total - 1:.2f}:d=1"
    video = out / "quran_original_short.mp4"
    _render(bg_args, overlays, audio_args, afilter, total, video, bg_filter)
    thumb = _thumb(video, out / "thumbnail.jpg", min(total - 1, intro + rec))

    return {
        "video": str(video), "thumbnail": str(thumb), "clip": name, "ayah": a,
        "raw_title": f"{a['surah_ar']} {a['ref']} | {a['surah_en']}",
        "description_extra": (f"{a['surah_ar']} ({a['surah_en']} {a['ref']})\n\n{a['arabic']}\n\n"
                              f"FA: {a['fa']}\nEN: {a['en']}\n\nRecitation: Sheikh Yasser Al-Dosari."),
        "duration": total,
    }


# ---------------------------------------------------------------- AI
def _ai_script(run_count: int) -> dict:
    try:
        from mega_prompt_engine_21 import get_mega_prompt_script
        s = get_mega_prompt_script("ai", run_count)
        if s.get("body"):
            return s
    except Exception as e:
        print(f"  [Original AI] mega prompt engine unavailable ({e}); using channel_ai templates")
    from channel_ai import AI_TOPICS
    t = AI_TOPICS["en"][(run_count - 1) % len(AI_TOPICS["en"])]
    return {"hook": t["hook"], "body": [t["script"]], "title": t["title"],
            "tags": [x.lstrip("#") for x in t["tags"]]}


def _fit_audio_text(body: list, audio_path: Path, out: Path, language: str):
    """Trim sentences until the voiceover fits under the Shorts limit."""
    from voice_generator import generate_speech
    sentences = list(body)
    while True:
        text = " ".join(sentences)
        generate_speech(text, language, str(audio_path))
        d = _duration(audio_path)
        if d <= MAX_SECONDS - 2 or len(sentences) <= 1:
            return text, d
        sentences = sentences[:-1]


def render_ai_original(output_dir, run_count: int = 1, language: str = "en") -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    s = _ai_script(run_count)
    body = [s["hook"]] + [b for b in s["body"] if b.strip() != s["hook"].strip()]
    audio = out / "voice.mp3"
    text, dur = _fit_audio_text(body, audio, out, language)
    total = min(MAX_SECONDS, dur + 0.8)

    # Kinetic karaoke captions: 3-word groups, active word highlighted, timed by characters spoken.
    # Rendered as ONE alpha image-sequence track (concat demuxer) so ffmpeg stays fast.
    words = text.split()
    weights = [len(w) + 2 for w in words]
    tw = sum(weights)
    cap_dir = out / "captions"
    cap_dir.mkdir(exist_ok=True)
    font = _font(FONT_EN, 92)
    concat_lines, t_acc = [], 0.0
    for gi in range(0, len(words), 3):
        group = words[gi:gi + 3]
        for wi in range(len(group)):
            d = dur * weights[gi + wi] / tw
            img = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
            dr = ImageDraw.Draw(img)
            parts = [w.upper() for w in group]
            widths = [dr.textlength(p_ + " ", font=font) for p_ in parts]
            scale_font = font
            if sum(widths) > 1000:
                scale_font = _font(FONT_EN, int(92 * 1000 / sum(widths)))
                widths = [dr.textlength(p_ + " ", font=scale_font) for p_ in parts]
            x = (W - sum(widths)) / 2
            for k, (p_, w_) in enumerate(zip(parts, widths)):
                active = k == wi
                if active:
                    tw_ = dr.textlength(p_, font=scale_font)
                    dr.rounded_rectangle([x - 12, 145, x + tw_ + 12, 275], radius=22, fill=(124, 58, 237, 235))
                dr.text((x, 210), p_, font=scale_font, anchor="lm",
                        fill=(255, 225, 0, 255) if active else (255, 255, 255, 255),
                        stroke_width=8, stroke_fill=(0, 0, 0, 255))
                x += w_
            fp = cap_dir / f"c_{gi + wi:04d}.png"
            img.save(fp)
            concat_lines.append(f"file '{fp.as_posix()}'\nduration {d:.3f}")
            t_acc += d
    concat_lines.append(f"file '{(cap_dir / f'c_{len(words) - 1:04d}.png').as_posix()}'")
    concat = out / "captions.txt"
    concat.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")

    overlays = []
    hook_png, _ = _text_png(out / "ai_hook.png", s["hook"].upper(), FONT_EN, 58, (0, 240, 255, 255), stroke=3)
    overlays.append((hook_png, 260, 0.0, min(total, 3.5), 50))
    brand, _ = _text_png(out / "ai_brand.png", "AI UNVEILED", FONT_EN, 40, (255, 255, 255, 200), box=False)
    overlays.append((brand, 1700, 0.0, total, 0))

    rnd = random.Random(run_count)
    cols = rnd.choice([("0x0f0524", "0x00507a", "0x3a0ca3", "0x00b4d8"),
                       ("0x050a1f", "0x7209b7", "0x0b3d91", "0x4cc9f0"),
                       ("0x0a0a12", "0x1b998b", "0x2d0a4e", "0xf72585")])
    bg_args = ["-f", "lavfi", "-i",
               f"gradients=s=1080x1920:c0={cols[0]}:c1={cols[1]}:c2={cols[2]}:c3={cols[3]}:n=4:speed=0.015:r=30"]
    bg_filter = "noise=alls=6:allf=t,vignette=PI/5"
    video = out / "ai_original_short.mp4"
    _render(bg_args, overlays, ["-i", str(audio)], f"apad,atrim=0:{total:.2f}", total, video, bg_filter,
            caption_concat=concat, caption_y=1000)
    thumb = _thumb(video, out / "thumbnail.jpg", 1.0)
    return {"video": str(video), "thumbnail": str(thumb), "title": s["title"], "hook": s["hook"],
            "script": text, "tags": s.get("tags", []), "pinned_comment": s.get("pinned_comment"),
            "duration": total}


if __name__ == "__main__":
    import sys
    dest = Path(sys.argv[1] if len(sys.argv) > 1 else BASE_DIR / "output" / "original_samples")
    q = render_quran_original(dest / "quran", run_count=2)
    print("Quran:", q["video"], q["duration"])
    a = render_ai_original(dest / "ai", run_count=1)
    print("AI:", a["video"], a["duration"])
