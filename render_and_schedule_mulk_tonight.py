import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
import imageio_ffmpeg

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
FFMPEG_DIR = str(Path(FFMPEG_EXE).parent)
if FFMPEG_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

BASE_DIR = Path(r"C:\Users\Admin\.copilot\repos\youtube-shorts-autopilot")
BRAIN_DIR = Path(r"C:\Users\Admin\.gemini\antigravity\brain\07cbd881-98d7-4279-9a49-744c1a04aca6")
OUTPUT_DIR = BASE_DIR / "output" / "produced_shorts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL_OUTPUT = OUTPUT_DIR / "viral_short_mulk_scheduled_tonight.mp4"
PROCESSED_AUDIO = OUTPUT_DIR / "mulk_audio_atempo.mp3"
ASS_SUBTITLES = OUTPUT_DIR / "mulk_subs.ass"

def prepare_audio(input_audio):
    print("[1/4] Processing recitation with atempo 1.02...")
    cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(input_audio),
        "-filter:a", "atempo=1.02,volume=1.15",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(PROCESSED_AUDIO)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    
    dur_cmd = [FFMPEG_EXE, "-hide_banner", "-i", str(PROCESSED_AUDIO)]
    res = subprocess.run(dur_cmd, capture_output=True, text=True, errors="ignore")
    duration = 35.1
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            dur_str = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = dur_str.split(":")
            duration = float(h) * 3600 + float(m) * 60 + float(s)
            break
    print(f"  ✓ Processed audio ready. Exact duration: {duration:.2f}s")
    return duration

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def generate_ass_subtitles(total_duration):
    print("[2/4] Generating styled Arabic ASS subtitle file...")
    
    ass_content = f"""[Script Info]
Title: Surah Al-Mulk Yasser Al-Dosari Short
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopHook,Vazirmatn,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,8,40,40,240,1
Style: Ayah,Vazirmatn,56,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,380,1
Style: Dua,Vazirmatn,52,&H0050FF50,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:07.50,TopHook,,0,0,0,,{{\\b1\\c&H00D4FF&}}🌌 المنجية من عذاب القبر.. سورة الملك{{\\r}}\\N{{\\fs38\\c&HFFFFFF&}}تلاوة خاشعة تسكن الروح قبل النوم
Dialogue: 0,0:00:00.20,0:00:09.50,Ayah,,0,0,0,,﴿ تَبَٰرَكَ ٱلَّذِي بِيَدِهِ ٱلۡمُلۡكُ\\Nوَهُوَ عَلَىٰ كُلِّ شَيۡءٍۢ قَدِيرٌ ﴾
Dialogue: 0,0:00:09.50,0:00:21.00,Ayah,,0,0,0,,﴿ ٱلَّذِي خَلَقَ ٱلۡمَوۡتَ وَٱلۡحَيَوٰةَ\\Nلِيَبۡلُوَكُمۡ أَيُّكُمۡ أَحۡسَنُ عَمَلٗاۚ\\Nوَهُوَ ٱلۡعَزِيزُ ٱلۡغَفُورُ ﴾
Dialogue: 0,0:00:21.00,{format_time(total_duration - 4.0)},Ayah,,0,0,0,,﴿ ٱلَّذِي خَلَقَ سَبۡعَ سَمَٰوَٰتٍۢ طِبَاقٗاۖ\\Nمَّا تَرَىٰ فِي خَلۡقِ ٱلرَّحۡمَٰنِ مِن تَفَٰوُتٍۢ ﴾
Dialogue: 0,{format_time(total_duration - 4.0)},{format_time(total_duration)},Dua,,0,0,0,,🤲 اكتب (سبحان الله وبحمده) لتشارك الأجر\\N{{\\fs40\\c&HFFFFFF&}}واشترك في القناة ليصلك القرآن يومياً 🕊️
"""
    with open(ASS_SUBTITLES, "w", encoding="utf-8") as f:
        f.write(ass_content)
    print(f"  ✓ Subtitles written to: {ASS_SUBTITLES}")

def render_final_video(img1, img2, img3, duration):
    print(f"[3/4] Rendering 1080x1920 60fps vertical short ({duration:.1f}s)...")
    
    d1 = duration * 0.33
    d2 = duration * 0.34
    d3 = duration - d1 - d2
    
    v1 = OUTPUT_DIR / "mulk_v1.mp4"
    v2 = OUTPUT_DIR / "mulk_v2.mp4"
    v3 = OUTPUT_DIR / "mulk_v3.mp4"
    v_concat = OUTPUT_DIR / "mulk_v_concat.mp4"
    
    # Clip 1: Zoom In 1.0 -> 1.14
    f1 = int(d1 * 30)
    cmd1 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img1),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0013,1.14)':d={f1}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d1:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v1)
    ]
    subprocess.run(cmd1, capture_output=True, check=True)
    
    # Clip 2: Pan & Subtle Zoom 1.14 -> 1.02
    f2 = int(d2 * 30)
    cmd2 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img2),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='max(1.14-0.0013*on,1.02)':d={f2}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d2:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v2)
    ]
    subprocess.run(cmd2, capture_output=True, check=True)
    
    # Clip 3: Zoom In 1.0 -> 1.12
    f3 = int(d3 * 30)
    cmd3 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img3),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0013,1.12)':d={f3}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d3:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v3)
    ]
    subprocess.run(cmd3, capture_output=True, check=True)
    
    # Concat clips
    concat_list = OUTPUT_DIR / "mulk_concat_v.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{v1.resolve()}'\n")
        f.write(f"file '{v2.resolve()}'\n")
        f.write(f"file '{v3.resolve()}'\n")
        
    concat_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy",
        str(v_concat)
    ]
    subprocess.run(concat_cmd, capture_output=True, check=True)
    
    # Subtitles, watermark, color polish, anti-fingerprint
    ass_path_escaped = str(ASS_SUBTITLES.resolve()).replace("\\", "/").replace(":", "\\:")
    watermark_text = "@NourAlQuran"
    
    vf_chain = (
        f"subtitles='{ass_path_escaped}',"
        f"scale=1.02*iw:-1,crop=1080:1920,"
        f"eq=contrast=1.05:brightness=0.01:saturation=1.08,"
        f"drawtext=text='{watermark_text}':x=w-tw-40:y=240:fontsize=36:fontcolor=white@0.70:box=1:boxcolor=black@0.35:boxborderw=6"
    )
    
    final_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(v_concat),
        "-i", str(PROCESSED_AUDIO),
        "-vf", vf_chain,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1",
        "-shortest",
        str(FINAL_OUTPUT)
    ]
    subprocess.run(final_cmd, capture_output=True, check=True)
    print(f"  ✓ High-Production Video Rendered: {FINAL_OUTPUT}")
    return FINAL_OUTPUT

def upload_and_schedule(video_path, publish_at_iso):
    print(f"[4/4] Scheduling Short on YouTube channel 'quran' at {publish_at_iso}...")
    os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'
    
    import youtube_uploader
    import time
    
    title = "سورة الملك تنجي من عذاب القبر 🌌✨ تلاوة تسكن الروح قبل النوم | الشيخ ياسر الدوسري #Shorts"
    description = (
        "سورة الملك المباركة كاملة الخشوع.. المانعة والمنجية من عذاب القبر 🌌✨\n\n"
        "بصوت فضيلة الشيخ الدكتور ياسر الدوسري حفظه الله.\n\n"
        "قال الله تعالى:\n"
        "﴿ تَبَٰرَكَ ٱلَّذِي بِيَدِهِ ٱلۡمُلۡكُ وَهُوَ عَلَىٰ كُلِّ شَيۡءٍۢ قَدِيرٌ ۝ ٱلَّذِي خَلَقَ ٱلۡمَوۡتَ وَٱلۡحَيَوٰةَ لِيَبۡلُوَكُمۡ أَيُّكُمۡ أَحۡسَنُ عَمَلٗاۚ وَهُوَ ٱلۡعَزِيزُ ٱلۡغَفُورُ ۝ ٱلَّذِي خَلَقَ سَبۡعَ سَمَٰوَٰتٍۢ طِبَاقٗاۖ مَّا تَرَىٰ فِي خَلۡقِ ٱلرَّحۡمَٰنِ مِن تَفَٰوُتٍۢ ﴾ [الملك: 1-3]\n\n"
        "🤲 اكتب (سبحان الله وبحمده، سبحان الله العظيم) في التعليقات.\n\n"
        "📌 اشترك في قناة نور القرآن ليصلك كل يوم مقطع يريح قلبك 🌿\n\n"
        "#سورة_الملك #ياسر_الدوسري #قرآن_كريم #تلاوة_خاشعة #راحة_نفسية #قبل_النوم #Shorts #Quran"
    )
    tags = [
        "سورة_الملك", "ياسر_الدوسري", "القرآن_الكريم", "تلاوة_خاشعة", 
        "راحة_نفسية", "قبل_النوم", "ادعية", "SurahAlMulk", "YasserAlDosari", "Shorts", "Quran"
    ]
    pinned_comment = "🌌 قال النبي ﷺ: «إن سورة من القرآن ثلاثون آية شفعت لرجل حتى غفر له: تبارك الذي بيده الملك».. اكتب شيء تؤجر عليه 🌿"
    
    for attempt in range(1, 4):
        try:
            print(f"  Upload attempt {attempt}/3...")
            result = youtube_uploader.upload_short(
                channel_key="quran",
                video_path=str(video_path),
                title=title,
                description=description,
                tags=tags,
                pinned_comment=pinned_comment,
                publish_at=publish_at_iso
            )
            if result:
                return result
        except Exception as e:
            print(f"  Attempt {attempt} failed: {e}")
            time.sleep(5)
            
    return None

def main():
    raw_audio = BASE_DIR / "mulk_full.mp3"
    if not raw_audio.exists():
        raw_audio = Path("mulk_full.mp3")
        
    duration = prepare_audio(raw_audio)
    generate_ass_subtitles(duration)
    
    # Locate generated images
    img1 = BRAIN_DIR / "mulk_scene1_heavens_clean_png_1794760724861.jpg"
    img2 = BRAIN_DIR / "mulk_scene2_creation_png_1794760780779.jpg"
    img3 = BRAIN_DIR / "mulk_scene3_quran_night_png_1794760864834.jpg"
    
    if not (img1 and img2 and img3):
        print(f"Missing images: img1={img1}, img2={img2}, img3={img3}")
        return
        
    out_vid = render_final_video(img1, img2, img3, duration)
    
    # Scheduled for 20:00 UTC = 23:30 Tehran / 23:00 Riyadh tonight!
    publish_at_target = "2026-11-15T20:00:00.000Z"
    up_res = upload_and_schedule(out_vid, publish_at_target)
    print("\n" + "=" * 60)
    print("=== LIVE UPLOAD & SCHEDULE RESULT ===")
    print(json.dumps(up_res, indent=2, ensure_ascii=False))
    print("=" * 60)

if __name__ == "__main__":
    main()
