"""Brand + subtitle Quran reels before upload (Quran channel).

Pipeline (see brand_reel):
  1. Transcribe the reel audio with faster-whisper (Arabic, CPU).
  2. Fuzzy-match the diacritics-stripped transcript against the *bundled, verbatim* Tanzil Quran
     text (data/quran/), narrowed by surah names found in the caption.
  3. Only when the match is high-confidence, burn timed ayah subtitles: Arabic (Tanzil simple text)
     + translation (fa.ansarian / en.sahih). Otherwise subtitles are skipped and logged - we never
     show a possibly-wrong verse. Text is never generated.
  4. Always add channel branding (logo watermark + reciter lower-third) and re-encode to
     1080x1920 H.264/AAC, < 45s, audio preserved.

Dedupe hashes are computed on the *source* download by dedupe_guard before this runs.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "quran"
BRAND_DIR = BASE_DIR / "assets" / "branding"
LOGO_PATH = BRAND_DIR / "logo_noor_alquran.png"
FONT_PATH = BASE_DIR / "Vazirmatn-Bold.ttf"
FONT_FAMILY = "Vazirmatn"
CHANNEL_NAME_AR = "نور القرآن"
CHANNEL_NAME_EN = "The Holy Light"
MAX_OUT_SEC = 44.5
W, H = 1080, 1920

WHISPER_MODEL = os.environ.get("QURAN_WHISPER_MODEL", "small")
WHISPER_CACHE = os.environ.get("WHISPER_CACHE", str(Path.home() / ".cache" / "faster-whisper"))
SUB_LANG = os.environ.get("QURAN_SUB_LANG", "fa")  # fa | en
MIN_SCORE = float(os.environ.get("QURAN_MATCH_MIN_SCORE", "82"))
MIN_MARGIN = 6.0
MIN_CHARS = 18

RLM = "\u200f"  # force RTL paragraph direction in libass
TRANSLATIONS = {"fa": "fa.ansarian.txt", "en": "en.sahih.txt"}


# --------------------------------------------------------------------------- text data
def _load_tanzil(name):
    out = {}
    with open(DATA_DIR / name, encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            s, a, t = line.rstrip("\n").split("|", 2)
            out[(int(s), int(a))] = t.strip()
    return out


@lru_cache(maxsize=None)
def quran_text():
    return _load_tanzil("quran-simple.txt")


@lru_cache(maxsize=None)
def translation(lang):
    return _load_tanzil(TRANSLATIONS[lang])


@lru_cache(maxsize=None)
def surahs():
    return json.loads((DATA_DIR / "surah-names.json").read_text(encoding="utf-8"))


_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]")
_MAP = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي",
                      "ء": "", "ک": "ك", "ی": "ي"})


def normalize_ar(text: str) -> str:
    t = _DIACRITICS.sub("", text or "").translate(_MAP)
    t = re.sub(r"[^\u0621-\u064A\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


@lru_cache(maxsize=None)
def surah_index():
    """{surah: (normalized_text, [(char_start, char_end, ayah)])}"""
    q = quran_text()
    idx = {}
    for s in range(1, 115):
        parts, spans, pos, a = [], [], 0, 1
        while (s, a) in q:
            n = normalize_ar(q[(s, a)])
            parts.append(n)
            spans.append((pos, pos + len(n), a))
            pos += len(n) + 1
            a += 1
        idx[s] = (" ".join(parts), spans)
    return idx


def surah_hints(caption: str):
    """Surah numbers named in the caption (e.g. 'سورة الملك', '#سورة_يوسف', 'Surah Al-Mulk')."""
    cap = normalize_ar((caption or "").replace("_", " "))
    low = (caption or "").lower().replace("-", "").replace("_", " ")
    hits = []
    for s in surahs():
        name = normalize_ar(s["name"])
        bare = re.sub(r"^ال", "", name)
        if re.search(r"(?:سوره|سورة)\s+(?:ال)?" + re.escape(bare) + r"(?:\s|$)", cap) or \
                re.search(r"(?:surah|sura|surat)\s*" + re.escape(s["tname"].lower().replace("-", "")), low):
            hits.append(s["index"])
    return hits


# --------------------------------------------------------------------------- ASR
def transcribe(audio_path):
    from faster_whisper import WhisperModel
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8", download_root=WHISPER_CACHE,
                         cpu_threads=os.cpu_count() or 2)
    import numpy as np
    # decode with system ffmpeg (avoids PyAV version incompatibilities)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio_path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True, timeout=300).stdout
    pcm = np.frombuffer(raw, dtype=np.float32)
    segs, _ = model.transcribe(pcm, language="ar", beam_size=5, word_timestamps=True,
                               vad_filter=False, condition_on_previous_text=False)
    words = []
    for seg in segs:
        for w in seg.words or []:
            n = normalize_ar(w.word)
            if n:
                words.append((n, float(w.start), float(w.end)))
    return words


# --------------------------------------------------------------------------- matching
def match_ayahs(words, caption="", log=print):
    """Return {'surah', 'ayahs': [(ayah, start, end)], 'score'} or None when not confident."""
    from rapidfuzz import fuzz
    transcript = " ".join(w for w, _, _ in words)
    if len(transcript.replace(" ", "")) < MIN_CHARS:
        log(f"  [AyahSubs] transcript too short ({transcript!r}); skipping subtitles")
        return None
    idx = surah_index()
    hints = surah_hints(caption)
    results = []
    for s, (text, spans) in idx.items():
        al = fuzz.partial_ratio_alignment(transcript, text)
        if al:
            results.append((al.score, s, al.dest_start, al.dest_end))
    results.sort(reverse=True)
    best = results[0]
    second = next((r for r in results[1:] if r[1] != best[1]), (0,))
    hinted = [r for r in results if r[1] in hints]
    log(f"  [AyahSubs] transcript={transcript[:120]!r}")
    log(f"  [AyahSubs] best surah {best[1]} score={best[0]:.1f}, 2nd={second[0]:.1f}, hints={hints}")
    if hinted and hinted[0][1] != best[1]:
        # caption names a surah - trust it only if its own match is also strong
        if hinted[0][0] >= MIN_SCORE and best[0] - hinted[0][0] < MIN_MARGIN:
            best = hinted[0]
        else:
            log("  [AyahSubs] caption surah hint disagrees with audio match; skipping subtitles")
            return None
    margin_ok = (best[0] - second[0] >= MIN_MARGIN) or (best[1] in hints and best[0] >= MIN_SCORE)
    if best[0] < MIN_SCORE or not margin_ok:
        log("  [AyahSubs] low-confidence match; skipping subtitles (never show possibly-wrong ayahs)")
        return None
    score, s, d0, d1 = best
    text, spans = idx[s]
    covered = [(a, max(st, d0), min(en, d1), st, en) for st, en, a in spans if en > d0 and st < d1]
    # drop ayahs only grazed by the alignment window (< 4 chars and < 25% of the ayah)
    covered = [c for c in covered if (c[2] - c[1]) >= 4 or (c[2] - c[1]) >= 0.25 * (c[4] - c[3])]
    if not covered or len(covered) > 12:
        return None
    timed = _time_ayahs(words, s, [c[0] for c in covered])
    if not timed:
        log("  [AyahSubs] could not time ayahs; skipping subtitles")
        return None
    return {"surah": s, "ayahs": timed, "score": score}


def _time_ayahs(words, surah, ayahs):
    """Monotonic fuzzy word alignment -> first/last time each ayah's words are heard."""
    from rapidfuzz import fuzz
    q = quran_text()
    ref = []
    for a in ayahs:
        for w in normalize_ar(q[(surah, a)]).split():
            ref.append((w, a))
    first, last = {}, {}
    p = 0
    for w, t0, t1 in words:
        best, bi = 0, None
        for j in range(max(0, p - 6), min(len(ref), p + 10)):  # small backtrack: reciters repeat
            sc = fuzz.ratio(w, ref[j][0])
            if sc > best:
                best, bi = sc, j
        if bi is not None and best >= 70:
            a = ref[bi][1]
            first.setdefault(a, t0)
            last[a] = t1
            p = bi + 1
    if not first:
        return []
    order = sorted(first, key=lambda a: first[a])
    out = []
    for i, a in enumerate(order):
        st = 0.0 if i == 0 else first[a]
        en = first[order[i + 1]] if i + 1 < len(order) else None
        out.append((a, st, en))
    return out


# --------------------------------------------------------------------------- rendering
def ensure_logo(path=LOGO_PATH):
    if path.exists():
        return path
    from PIL import Image, ImageDraw, ImageFont
    import arabic_reshaper
    from bidi.algorithm import get_display
    path.parent.mkdir(parents=True, exist_ok=True)
    S = 4  # supersample
    w, h = 300 * S, 300 * S
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    gold, cream = (212, 175, 55, 255), (255, 250, 235, 255)
    d.ellipse((6 * S, 6 * S, w - 6 * S, h - 6 * S), fill=(10, 50, 40, 215), outline=gold, width=5 * S)
    d.ellipse((22 * S, 22 * S, w - 22 * S, h - 22 * S), outline=(212, 175, 55, 140), width=2 * S)
    # 8-point star (Rub el Hizb) as emblem
    import math
    cx, cy, r = w / 2, 105 * S, 38 * S
    for rot in (0, 45):
        pts = [(cx + r * math.cos(math.radians(rot + k * 90 + 45)), cy + r * math.sin(math.radians(rot + k * 90 + 45)))
               for k in range(4)]
        d.polygon(pts, fill=gold)
    d.ellipse((cx - 13 * S, cy - 13 * S, cx + 13 * S, cy + 13 * S), fill=(10, 50, 40, 255))
    f_ar = ImageFont.truetype(str(FONT_PATH), 50 * S)
    f_en = ImageFont.truetype(str(FONT_PATH), 25 * S)
    from PIL import features
    if features.check("raqm"):  # Pillow shapes Arabic itself
        d.text((cx, 185 * S), CHANNEL_NAME_AR, font=f_ar, fill=cream, anchor="mm", direction="rtl")
    else:
        ar = get_display(arabic_reshaper.reshape(CHANNEL_NAME_AR))
        d.text((cx, 185 * S), ar, font=f_ar, fill=cream, anchor="mm")
    d.text((cx, 237 * S), CHANNEL_NAME_EN, font=f_en, fill=gold, anchor="mm")
    img.resize((300, 300), Image.LANCZOS).save(path)
    return path


def _ass_escape(t):
    return t.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")


def _ts(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def _ar_digits(n):
    return str(n).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def build_ass(duration, reciter_ar, match=None, lang=SUB_LANG):
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Ayah,{FONT_FAMILY},{{AYAH_SIZE}},&H00FFFFFF,&H00FFFFFF,&H00202020,&H96000000,0,0,0,0,100,100,0,0,1,3,2,2,70,70,560,1
Style: Trans,{FONT_FAMILY},{{TR_SIZE}},&H0037D4F0,&H0037D4F0,&H00202020,&H96000000,0,0,0,0,100,100,0,0,1,2.5,1,8,110,110,1440,1
Style: Reciter,{FONT_FAMILY},40,&H00FFFFFF,&H00FFFFFF,&H64000000,&H8C1E3214,0,0,0,0,100,100,0,0,3,14,0,3,60,60,170,1
Style: Source,{FONT_FAMILY},22,&H80FFFFFF,&H80FFFFFF,&H80000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,2,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    end_all = _ts(duration)
    ev.append(f"Dialogue: 1,0:00:00.00,{end_all},Reciter,,0,0,0,,{{\\fad(400,0)}}{RLM}{_ass_escape(reciter_ar)}{RLM}")
    ayah_size, tr_size = 54, 34
    if match:
        q, tr = quran_text(), translation(lang)
        s = match["surah"]
        longest = max(len(q[(s, a)]) for a, _, _ in match["ayahs"])
        if longest > 220:
            ayah_size, tr_size = 42, 28
        elif longest > 140:
            ayah_size, tr_size = 48, 31
        src = "Tanzil.net · " + ("Ansarian" if lang == "fa" else "Saheeh International")
        sname = next(x["name"] for x in surahs() if x["index"] == s)
        for a, st, en in match["ayahs"]:
            en = duration if en is None else min(en, duration)
            if en - st < 0.3:
                continue
            ar = RLM + _ass_escape(q[(s, a)]) + RLM
            trl = (RLM if lang == "fa" else "") + _ass_escape(tr[(s, a)]) + (RLM if lang == "fa" else "")
            ref = f"{RLM}سورة {sname} · {_ar_digits(a)}{RLM}  |  {src}"
            ev.append(f"Dialogue: 2,{_ts(st)},{_ts(en)},Ayah,,0,0,0,,{{\\fad(250,200)}}{ar}")
            ev.append(f"Dialogue: 2,{_ts(st)},{_ts(en)},Trans,,0,0,0,,{{\\fad(250,200)}}{trl}")
            ev.append(f"Dialogue: 1,{_ts(st)},{_ts(en)},Source,,0,0,0,,{ref}")
    return hdr.replace("{AYAH_SIZE}", str(ayah_size)).replace("{TR_SIZE}", str(tr_size)) + "\n".join(ev) + "\n"


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return bool(out.stdout.strip())


def render(src, out, ass_text, audio=None):
    """Compose src video (+ optional separate audio) -> branded 1080x1920 mp4."""
    logo = ensure_logo()
    tmp = Path(tempfile.mkdtemp(prefix="qbrand_"))
    try:
        fonts = tmp / "fonts"
        fonts.mkdir()
        shutil.copy(FONT_PATH, fonts / FONT_PATH.name)
        (tmp / "subs.ass").write_text(ass_text, encoding="utf-8")
        dur = min(probe_duration(audio or src) or MAX_OUT_SEC, MAX_OUT_SEC)
        vf = (f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,"
              f"eq=brightness=-0.08[bg];[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];"
              f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[base];"
              f"[1:v]scale=190:-1,format=rgba,colorchannelmixer=aa=0.85[logo];"
              f"[base][logo]overlay=W-w-40:150,drawbox=x=0:y=1150:w=iw:h=560:color=black@0.28:t=fill[lg];"
              f"[lg]subtitles=subs.ass:fontsdir=fonts,format=yuv420p[v]")
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
        cmd += (["-stream_loop", "-1"] if audio else []) + ["-i", str(Path(src).resolve())]
        cmd += ["-loop", "1", "-i", str(logo)]
        if audio:
            cmd += ["-i", str(Path(audio).resolve())]
        cmd += ["-filter_complex", vf, "-map", "[v]"]
        amap = "2:a" if audio else ("0:a" if has_audio(src) else None)
        if amap:
            cmd += ["-map", amap, "-c:a", "aac", "-b:a", "160k", "-ar", "44100"]
        cmd += ["-t", f"{dur:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(Path(out).resolve())]
        subprocess.run(cmd, check=True, cwd=tmp, timeout=900)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return Path(out)


def extract_audio(src, dst):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vn", "-ac", "1",
                    "-ar", "16000", "-t", str(MAX_OUT_SEC), str(dst)], check=True, timeout=300)
    return dst


def detect_ayahs(media, caption="", log=print):
    """Transcribe + match; never raises (returns None on any failure)."""
    try:
        with tempfile.TemporaryDirectory() as td:
            wav = extract_audio(media, Path(td) / "a.wav")
            words = transcribe(wav)
        return match_ayahs(words, caption, log=log)
    except Exception as e:  # ASR/matching problems must never block branding
        log(f"  [AyahSubs] detection failed ({e}); skipping subtitles")
        return None


def brand_reel(src, caption="", reciter_ar="الشيخ ياسر الدوسري", out=None, audio=None, log=print):
    """Return path of the branded reel. Raises if rendering fails (caller must not upload the original)."""
    src = Path(src)
    out = Path(out) if out else src.with_name(src.stem + "_branded.mp4")
    if not has_audio(audio or src):
        raise RuntimeError("reel has no audio track")
    match = detect_ayahs(audio or src, caption, log=log)
    dur = min(probe_duration(audio or src) or MAX_OUT_SEC, MAX_OUT_SEC)
    if match:
        log(f"  [AyahSubs] ✓ surah {match['surah']} ayahs {[a for a, _, _ in match['ayahs']]} "
            f"(score {match['score']:.1f})")
    try:
        render(src, out, build_ass(dur, reciter_ar, match), audio=audio)
    except Exception as e:
        if not match:
            raise
        log(f"  [Branding] render with subtitles failed ({e}); retrying branding-only")
        match = None
        render(src, out, build_ass(dur, reciter_ar, None), audio=audio)
    if not out.exists() or out.stat().st_size < 50_000 or probe_duration(out) < 1:
        raise RuntimeError("branded output invalid")
    log(f"  [Branding] ✓ {out.name} ({probe_duration(out):.1f}s, subtitles={'yes' if match else 'no'})")
    return out, match


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--audio")
    ap.add_argument("--caption", default="")
    ap.add_argument("--reciter", default="الشيخ ياسر الدوسري")
    ap.add_argument("--out")
    a = ap.parse_args()
    p, m = brand_reel(a.video, a.caption, a.reciter, a.out, a.audio)
    print(json.dumps({"out": str(p), "match": m}, ensure_ascii=False))
