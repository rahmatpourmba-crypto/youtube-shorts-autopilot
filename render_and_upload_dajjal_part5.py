import os
import sys
import json
import subprocess
from pathlib import Path
import imageio_ffmpeg
import numpy as np
import scipy.io.wavfile as wavfile
from scipy.signal import butter, lfilter

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
FFMPEG_DIR = str(Path(FFMPEG_EXE).parent)
if FFMPEG_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

BASE_DIR = Path(r"C:\Users\Admin\.copilot\repos\youtube-shorts-autopilot")
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output" / "produced_shorts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FINAL_OUTPUT = OUTPUT_DIR / "viral_short_dajjal_p5_nabil_24s.mp4"
HUMAN_VOICE = OUTPUT_DIR / "p5_voice_24s.mp3"

MUSIC_FILE = OUTPUT_DIR / "dajjal_p5_music.wav"
MIXED_AUDIO = OUTPUT_DIR / "dajjal_p5_mixed.mp3"
ASS_SUBTITLES = OUTPUT_DIR / "dajjal_p5_subs.ass"

DURATION = 24.0

def generate_cinematic_music(duration=DURATION):
    print("[1/4] Generating dark atmospheric cinematic music...")
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    f_D1 = 36.71
    f_D2 = 73.42
    f_F2 = 87.31
    f_A2 = 110.00
    
    sub = 0.35 * np.sin(2 * np.pi * f_D1 * t)
    drone1 = 0.25 * np.sin(2 * np.pi * f_D2 * t)
    drone2 = 0.20 * np.sin(2 * np.pi * (f_D2 * 1.003) * t)
    pad = 0.16 * np.sin(2 * np.pi * f_F2 * t) + 0.12 * np.sin(2 * np.pi * f_A2 * t)
    
    # Tension pulse
    pulse = np.zeros_like(t)
    bpm = 60
    spb = 60.0 / bpm
    for beat in range(int(duration / spb)):
        t_start = int(beat * spb * sr)
        pulse_len = int(0.20 * sr)
        if t_start + pulse_len < len(pulse):
            pt = np.linspace(0, 0.20, pulse_len, endpoint=False)
            freq_decay = np.linspace(60, 28, pulse_len)
            hit = np.sin(2 * np.pi * freq_decay * pt) * np.exp(-pt * 18)
            pulse[t_start:t_start + pulse_len] += 0.45 * hit
            
    b, a = butter(4, 500 / (sr / 2), btype='low')
    mix = sub + drone1 + drone2 + pad + pulse
    filtered = lfilter(b, a, mix)
    
    fade_in = np.minimum(t / 1.5, 1.0)
    fade_out = np.minimum((duration - t) / 1.8, 1.0)
    final_music = filtered * fade_in * fade_out
    
    max_val = np.max(np.abs(final_music))
    if max_val > 0:
        final_music = (final_music / max_val) * 0.85
        
    wavfile.write(str(MUSIC_FILE), sr, (final_music * 32767).astype(np.int16))
    
    # Mix human voice + music
    mix_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(HUMAN_VOICE),
        "-i", str(MUSIC_FILE),
        "-filter_complex", "[0:a]volume=1.40[v];[1:a]volume=0.28[m];[v][m]amix=inputs=2:duration=first[out]",
        "-map", "[out]",
        str(MIXED_AUDIO)
    ]
    subprocess.run(mix_cmd, capture_output=True, check=True)
    print("  ✓ Mixed human voice & cinematic music successfully!")

def generate_ass_subtitles():
    print("[2/4] Generating styled Arabic ASS subtitle file...")
    ass_content = f"""[Script Info]
Title: Dajjal Part 5 Master Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HookBadge,Vazirmatn,54,&H0000D7FF,&H000000FF,&H00000000,&HE6100814,-1,0,0,0,100,100,0,0,1,5,0,8,40,40,160,1
Style: SubNarrative,Vazirmatn,62,&H00FFFFFF,&H000000FF,&H00000000,&HB4000000,-1,0,0,0,100,100,0,0,1,6,3,2,60,60,340,1
Style: SubEmphasis,Vazirmatn,68,&H0000FFFF,&H000000FF,&H0000008B,&HC8000000,-1,0,0,0,105,105,0,0,1,7,4,2,60,60,340,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.00,0:00:24.00,HookBadge,,0,0,0,,{{\\an8\\bord4\\fscx102\\fscy102\\c&H0030FF&}}⚠️ خروج الدجال من بلاد خراسان | الشيخ نبيل العوضي (الجزء 5) ⚠️
Dialogue: 0,0:00:00.00,0:00:07.50,SubNarrative,,0,0,0,,يخرج الدجال من قبل المشرق من بلاد يقال لها خراسان
Dialogue: 0,0:00:07.50,0:00:15.50,SubEmphasis,,0,0,0,,يتبعه أقوام كأن وجوههم المجان المطرقة!
Dialogue: 0,0:00:15.50,0:00:24.00,SubNarrative,,0,0,0,,أعظم فتنة تمر على وجه الأرض.. فاستعيذوا بالله من فتنته!
"""
    with open(ASS_SUBTITLES, "w", encoding="utf-8") as f:
        f.write(ass_content)
    print("  ✓ ASS subtitles generated.")

def render_final_video(img1, img2, img3, duration=DURATION):
    print("[3/4] Rendering video with Ken Burns and subtitles...")
    d1 = 8.0
    d2 = 8.0
    d3 = 8.0
    
    v1 = OUTPUT_DIR / "p5_v1.mp4"
    v2 = OUTPUT_DIR / "p5_v2.mp4"
    v3 = OUTPUT_DIR / "p5_v3.mp4"
    v_concat = OUTPUT_DIR / "p5_v_concat.mp4"
    
    # Clip 1: Zoom In 1.0 -> 1.15
    f1 = int(d1 * 30)
    cmd1 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img1),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0018,1.15)':d={f1}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d1:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v1)
    ]
    subprocess.run(cmd1, capture_output=True, check=True)
    
    # Clip 2: Pan & Zoom Out 1.15 -> 1.02
    f2 = int(d2 * 30)
    cmd2 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img2),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='max(1.15-0.0015*on,1.02)':d={f2}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d2:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v2)
    ]
    subprocess.run(cmd2, capture_output=True, check=True)
    
    # Clip 3: Majestic Zoom In 1.0 -> 1.14
    f3 = int(d3 * 30)
    cmd3 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img3),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0016,1.14)':d={f3}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d3:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v3)
    ]
    subprocess.run(cmd3, capture_output=True, check=True)
    
    # Concat
    concat_list = OUTPUT_DIR / "p5_concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{v1.name}'\nfile '{v2.name}'\nfile '{v3.name}'\n")
        
    cmd_concat = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy",
        str(v_concat)
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)
    
    # Burn ASS subtitles + mix
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
        
    print(f"  ✓ Video Part 5 rendered: {FINAL_OUTPUT}")
    print(f"  ✓ Size: {FINAL_OUTPUT.stat().st_size:,} bytes | Duration: {duration:.2f}s")
    return FINAL_OUTPUT

def upload_to_youtube(video_path):
    print("[4/4] Uploading Part 5 directly to YouTube Shorts...")
    os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'
    
    import youtube_uploader
    
    title = "خروج الدجال من خراسان وأتباعه! | الشيخ نبيل العوضي ⚠️ (الجزء 5) #shorts"
    description = (
        "خروج المسيح الدجال من بلاد خراسان وأول من يتبعه.. بصوت الشيخ نبيل العوضي حفظه الله ⚠️ | الجزء الخامس.\n\n"
        "قال رسول الله ﷺ: «يخرج الدجال من أرض بالمشرق يقال لها خراسان، يتبعه أقوام كأن وجوههم المجان المطرقة» (رواه الترمذي وصححه الألباني).\n\n"
        "اللهم إنا نعوذ بك من عذاب القبر ومن فتنة المسيح الدجال 🤲\n\n"
        "📌 شارك المقطع واشترك في القناة لتعم الفائدة 🕊️\n\n"
        "#المسيح_الدجال #خراسان #الشيخ_نبيل_العوضي #علامات_الساعة #الجزء_الخامس #نهاية_العالم #Dajjal #Shorts #Islam"
    )
    tags = ["خروج_الدجال", "خراسان", "المسيح_الدجال", "نبيل_العوضي", "علامات_الساعة", "نهاية_العالم", "Dajjal", "Shorts", "Islam"]
    pinned_comment = "🤲 اللهم إنا نعوذ بك من فتنة المسيح الدجال.. اكتب (يا الله) لتثبيت الشهادة واشترك في القناة 🌿"
    
    result = youtube_uploader.upload_short(
        channel_key="quran",
        video_path=str(video_path),
        title=title,
        description=description,
        tags=tags,
        pinned_comment=pinned_comment
    )
    return result

def main():
    generate_cinematic_music()
    generate_ass_subtitles()
    
    img1 = ASSETS_DIR / "dajjal_scene3_apocalypse.png"
    img2 = ASSETS_DIR / "dajjal_p3_scene2.png"
    img3 = ASSETS_DIR / "dajjal_p4_scene1.png"
    
    if not (img1.exists() and img2.exists() and img3.exists()):
        print(f"Missing images!")
        return
        
    out_vid = render_final_video(img1, img2, img3, DURATION)
    up_res = upload_to_youtube(out_vid)
    print("\n" + "=" * 60)
    print("LIVE UPLOAD RESULT:", up_res)
    print("=" * 60)

if __name__ == "__main__":
    main()
