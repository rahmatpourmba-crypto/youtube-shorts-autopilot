import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
import imageio_ffmpeg

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
FFMPEG_DIR = str(Path(FFMPEG_EXE).parent)
if FFMPEG_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

BASE_DIR = Path(r"C:\Users\Admin\.copilot\repos\youtube-shorts-autopilot")
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output" / "produced_shorts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL_OUTPUT = OUTPUT_DIR / "viral_short_dajjal_22s.mp4"
AUDIO_FILE = OUTPUT_DIR / "dajjal_audio.mp3"
AMBIENT_AUDIO = OUTPUT_DIR / "dajjal_ambient.mp3"
MIXED_AUDIO = OUTPUT_DIR / "dajjal_mixed_audio.mp3"
ASS_SUBTITLES = OUTPUT_DIR / "dajjal_subs.ass"

VOICE_TEXT = (
    "أعظم فتنة خُلقت منذ خلق الله آدم إلى قيام الساعة، هي فتنة المسيح الدجال! "
    "رجلٌ يطوف الأرض في أربعين يوما، ومعه جنة ونار، فجنته نار وناره جنة! "
    "اللهم إنا نعوذ بك من شر فتنة المسيح الدجال."
)

async def generate_voice():
    import edge_tts
    print("[1/5] Generating deep cinematic Arabic narration with edge-tts...")
    communicate = edge_tts.Communicate(VOICE_TEXT, "ar-SA-HamedNeural", rate="-4%")
    await communicate.save(str(AUDIO_FILE))
    print(f"  ✓ Voice saved to: {AUDIO_FILE}")

def get_audio_duration(file_path):
    cmd = [
        FFMPEG_EXE, "-hide_banner", "-i", str(file_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            dur_str = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = dur_str.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 21.5

def generate_ambient_track(duration):
    print("[2/5] Synthesizing atmospheric deep rumble...")
    # Low frequency wind rumble (halal atmospheric sound)
    cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-f", "lavfi", "-i", f"anoisesrc=c=pink:r=44100:a=0.08,lowpass=f=180,volume=1.8",
        "-t", f"{duration:.2f}",
        str(AMBIENT_AUDIO)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    
    # Mix narration and ambient
    mix_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(AUDIO_FILE),
        "-i", str(AMBIENT_AUDIO),
        "-filter_complex", "[0:a]volume=1.2[v];[1:a]volume=0.35[a];[v][a]amix=inputs=2:duration=first[out]",
        "-map", "[out]",
        str(MIXED_AUDIO)
    ]
    subprocess.run(mix_cmd, capture_output=True, check=True)
    print("  ✓ Audio mixed successfully")

def generate_ass_subtitles(total_duration):
    print("[3/5] Generating styled Arabic ASS subtitle file...")
    # Arabic text lines with timestamps
    # 0.0 - 7.2: أعظم فتنة خُلقت منذ خلق الله آدم إلى قيام الساعة، هي فتنة المسيح الدجال!
    # 7.2 - 14.8: رجلٌ يطوف الأرض في أربعين يوماً، ومعه جنة ونار.. فجنته نار وناره جنة!
    # 14.8 - total_dur: اللهم إنا نعوذ بك من شر فتنة المسيح الدجال 🤲
    
    font_path = BASE_DIR / "Vazirmatn-Bold.ttf"
    
    ass_content = f"""[Script Info]
Title: Dajjal Viral Short
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopHook,Vazirmatn,52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,8,40,40,240,1
Style: Subtitles,Vazirmatn,58,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,380,1
Style: Dua,Vazirmatn,56,&H0050FF50,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.50,TopHook,,0,0,0,,{{\\b1\\c&H00D4FF&}}⚠️ خروج المسيح الدجال{{\\r}}\\N{{\\fs42\\c&HFFFFFF&}}أعظم فتنة في تاريخ البشرية
Dialogue: 0,0:00:00.20,0:00:07.10,Subtitles,,0,0,0,,أعظم فتنة خُلقت منذ خلق الله آدم إلى قيام الساعة\\N{{\\c&H00FFFF&}}هي فتنة المسيح الدجال!{{\\r}}
Dialogue: 0,0:00:07.10,0:00:14.50,Subtitles,,0,0,0,,رجلٌ يطوف الأرض في أربعين يوماً\\Nومعه جنةٌ ونار.. {{\\c&H3030FF&}}فجنته نار{{\\r}} {{\\c&H30FF30&}}وناره جنة!{{\\r}}
Dialogue: 0,0:00:14.50,{format_time(total_duration)},Dua,,0,0,0,,🤲 اللهم إنا نعوذ بك من شر فتنة المسيح الدجال\\N{{\\fs44\\c&HFFFFFF&}}اكتب (آمين) في التعليقات لتشارك الأجر🌿
"""
    with open(ASS_SUBTITLES, "w", encoding="utf-8") as f:
        f.write(ass_content)
    print(f"  ✓ Subtitles written to: {ASS_SUBTITLES}")

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def render_final_video(img1, img2, img3, duration):
    print("[4/5] Rendering 1080x1920 60fps vertical short with Ken Burns camera movement...")
    
    # We create 3 clips with zoompan and concatenate them
    # img1: 0 - 7s
    # img2: 7 - 14s
    # img3: 14 - duration
    
    d1 = 7.2
    d2 = 7.2
    d3 = max(6.0, duration - 14.4 + 0.3)
    
    v1 = OUTPUT_DIR / "v1.mp4"
    v2 = OUTPUT_DIR / "v2.mp4"
    v3 = OUTPUT_DIR / "v3.mp4"
    v_concat = OUTPUT_DIR / "v_concat.mp4"
    
    # 60 fps 1080x1920 zoompan
    # Clip 1: Zoom In 1.0 -> 1.15
    f1 = int(d1 * 30)
    cmd1 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img1),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0015,1.15)':d={f1}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d1:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v1)
    ]
    subprocess.run(cmd1, capture_output=True, check=True)
    
    # Clip 2: Pan & Subtle Zoom 1.15 -> 1.02
    f2 = int(d2 * 30)
    cmd2 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img2),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='max(1.15-0.0015*on,1.02)':d={f2}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d2:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v2)
    ]
    subprocess.run(cmd2, capture_output=True, check=True)
    
    # Clip 3: Zoom In 1.0 -> 1.12
    f3 = int(d3 * 30)
    cmd3 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img3),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0012,1.12)':d={f3}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d3:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v3)
    ]
    subprocess.run(cmd3, capture_output=True, check=True)
    
    # Concat clips
    concat_list = OUTPUT_DIR / "concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{v1.name}'\nfile '{v2.name}'\nfile '{v3.name}'\n")
        
    cmd_concat = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy",
        str(v_concat)
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)
    
    # Burn ASS subtitles + audio muxing
    # On Windows ffmpeg, escape backslashes in subtitle path
    ass_escaped = str(ASS_SUBTITLES).replace("\\", "/").replace(":", "\\:")
    fonts_dir = str(BASE_DIR).replace("\\", "/").replace(":", "\\:")
    
    final_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(v_concat),
        "-i", str(MIXED_AUDIO),
        "-vf", f"subtitles='{ass_escaped}':fontsdir='{fonts_dir}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{duration:.2f}",
        "-movflags", "+faststart",
        str(FINAL_OUTPUT)
    ]
    res = subprocess.run(final_cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        print("Final ffmpeg error:", res.stderr)
        raise RuntimeError("FFmpeg subtitle burn failed")
        
    print(f"  ✓ Video successfully rendered: {FINAL_OUTPUT}")
    print(f"  ✓ Final size: {FINAL_OUTPUT.stat().st_size:,} bytes | Duration: {duration:.2f}s")
    return FINAL_OUTPUT

def upload_to_youtube(video_path):
    print("[5/5] Uploading directly to YouTube Shorts...")
    os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'
    
    import youtube_uploader
    
    title = "خروج المسيح الدجال.. أعظم فتنة في تاريخ البشرية ⚠️ | وثائقي مرعب #shorts"
    description = (
        "خروج المسيح الدجال.. أعظم فتنة في تاريخ البشرية ⚠️ | علامات الساعة الكبرى.\n\n"
        "قال رسول الله ﷺ: «ما بين خلق آدم إلى قيام الساعة خلق أكبر من الدجال» (صحيح مسلم).\n\n"
        "🤲 اللهم إنا نعوذ بك من عذاب جهنم، ومن عذاب القبر، ومن فتنة المحيا والممات، ومن شر فتنة المسيح الدجال.\n\n"
        "📌 اكتب (آمين) لتشارك الأجر واشترك في القناة ليصلك كل جديد 🕊️\n\n"
        "#المسيح_الدجال #الدجال #علامات_الساعة #أشراط_الساعة #نهاية_العالم #Dajjal #EndTimes #Shorts #Islam"
    )
    tags = ["المسيح_الدجال", "الدجال", "علامات_الساعة", "أشراط_الساعة", "نهاية_العالم", "Dajjal", "EndTimes", "وثائقي", "قصص_الأنبياء", "Shorts"]
    pinned_comment = "🤲 اللهم إنا نعوذ بك من عذاب جهنم، ومن عذاب القبر، ومن فتنة المحيا والممات، ومن شر فتنة المسيح الدجال. اكتب (آمين) لتشارك الأجر 🌿"
    
    result = youtube_uploader.upload_short(
        channel_key="quran",
        video_path=str(video_path),
        title=title,
        description=description,
        tags=tags,
        pinned_comment=pinned_comment
    )
    return result

async def main():
    await generate_voice()
    duration = get_audio_duration(AUDIO_FILE)
    print(f"Narration duration: {duration:.2f}s")
    
    generate_ambient_track(duration)
    generate_ass_subtitles(duration)
    
    img1 = ASSETS_DIR / "dajjal_scene1_island.png"
    img2 = ASSETS_DIR / "dajjal_scene2_gates.png"
    img3 = ASSETS_DIR / "dajjal_scene3_apocalypse.png"
    
    if not (img1.exists() and img2.exists() and img3.exists()):
        print(f"Waiting for images... Checked: {img1.exists()}, {img2.exists()}, {img3.exists()}")
        return
        
    out_vid = render_final_video(img1, img2, img3, duration)
    up_res = upload_to_youtube(out_vid)
    print("\n" + "=" * 60)
    print("=== LIVE UPLOAD RESULT ===")
    print(json.dumps(up_res, indent=2, ensure_ascii=False))
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
