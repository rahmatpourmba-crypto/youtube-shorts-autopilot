import os
import sys
import json
import asyncio
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

FINAL_OUTPUT = OUTPUT_DIR / "viral_short_dajjal_p2_21s.mp4"
AUDIO_FILE = OUTPUT_DIR / "dajjal_p2_audio.mp3"
MUSIC_FILE = OUTPUT_DIR / "dajjal_p2_cinematic_music.wav"
MIXED_AUDIO = OUTPUT_DIR / "dajjal_p2_mixed_audio.mp3"
ASS_SUBTITLES = OUTPUT_DIR / "dajjal_p2_subs.ass"

VOICE_TEXT = (
    "كيف يتحرك المسيح الدجال؟ وكيف يفتن الناس؟ "
    "يمر في الأرض كالغيث استدبرته الريح! ومعه جبال من طعام وأنهار تجري.. "
    "لكن يُحرم عليه دخول مكة والمدينة، فتحرسهما الملائكة! "
    "اللهم احفظنا من فتنته وثبت قلوبنا."
)

async def generate_voice():
    import edge_tts
    print("[1/5] Generating deep cinematic Arabic narration for Part 2...")
    communicate = edge_tts.Communicate(VOICE_TEXT, "ar-SA-HamedNeural", rate="-3%")
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
    return 21.0

def generate_cinematic_music(duration):
    print("[2/5] Synthesizing rich cinematic dark tension music...")
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # D minor dark frequencies
    f_D1 = 36.71
    f_D2 = 73.42
    f_F2 = 87.31
    f_A2 = 110.00
    
    # 1. Deep Sub bass drone
    sub = 0.40 * np.sin(2 * np.pi * f_D1 * t)
    drone1 = 0.28 * np.sin(2 * np.pi * f_D2 * t)
    drone2 = 0.22 * np.sin(2 * np.pi * (f_D2 * 1.004) * t)  # Chorus detune
    
    # 2. Ominous pad in minor third/fifth
    pad = 0.18 * np.sin(2 * np.pi * f_F2 * t) + 0.14 * np.sin(2 * np.pi * f_A2 * t)
    
    # 3. Heartbeat tension pulse (64 BPM)
    pulse = np.zeros_like(t)
    bpm = 64
    spb = 60.0 / bpm
    total_beats = int(duration / spb)
    for beat in range(total_beats):
        t_start = int(beat * spb * sr)
        pulse_len = int(0.22 * sr)
        if t_start + pulse_len < len(pulse):
            pt = np.linspace(0, 0.22, pulse_len, endpoint=False)
            freq_decay = np.linspace(65, 30, pulse_len)
            hit = np.sin(2 * np.pi * freq_decay * pt) * np.exp(-pt * 18)
            pulse[t_start:t_start + pulse_len] += 0.50 * hit
            # Double pulse (heartbeat lub-dub)
            t2 = t_start + int(0.20 * sr)
            if t2 + pulse_len < len(pulse):
                pulse[t2:t2 + pulse_len] += 0.32 * hit
                
    # 4. Tension swell / riser
    riser_env = np.clip((t - 7.0) / (duration - 7.0), 0, 1) ** 1.8
    riser_freq = np.linspace(80, 190, len(t))
    riser = 0.18 * riser_env * np.sin(2 * np.pi * riser_freq * t)
    
    # 5. Low-pass filter for dark cinema sound
    b, a = butter(4, 550 / (sr / 2), btype='low')
    mix = sub + drone1 + drone2 + pad + pulse + riser
    filtered = lfilter(b, a, mix)
    
    # Smooth envelopes
    fade_in = np.minimum(t / 1.2, 1.0)
    fade_out = np.minimum((duration - t) / 1.8, 1.0)
    final_music = filtered * fade_in * fade_out
    
    max_val = np.max(np.abs(final_music))
    if max_val > 0:
        final_music = (final_music / max_val) * 0.90
        
    wavfile.write(str(MUSIC_FILE), sr, (final_music * 32767).astype(np.int16))
    
    # Mix voice (1.25) and music (0.42) with ducking
    mix_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(AUDIO_FILE),
        "-i", str(MUSIC_FILE),
        "-filter_complex", "[0:a]volume=1.3[v];[1:a]volume=0.42[m];[v][m]amix=inputs=2:duration=first[out]",
        "-map", "[out]",
        str(MIXED_AUDIO)
    ]
    subprocess.run(mix_cmd, capture_output=True, check=True)
    print("  ✓ Cinematic music & voice mixed successfully!")

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def generate_ass_subtitles(total_duration):
    print("[3/5] Generating styled Arabic ASS subtitle file...")
    ass_content = f"""[Script Info]
Title: Dajjal Part 2 Viral Short
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
Style: GreenDua,Vazirmatn,56,&H0050FF50,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.50,TopHook,,0,0,0,,{{\\b1\\c&H00D4FF&}}⚠️ سرعة الدجال وعلاماته المرعبة!{{\\r}}\\N{{\\fs42\\c&HFFFFFF&}}الجزء الثاني | حقائق تقشعر لها الأبدان
Dialogue: 0,0:00:00.10,0:00:06.80,Subtitles,,0,0,0,,كيف يتحرك المسيح الدجال؟ وكيف يفتن الناس؟\\N{{\\c&H00D4FF&}}يمر في الأرض كالغيث استدبرته الريح!{{\\r}}
Dialogue: 0,0:00:06.80,0:00:14.20,Subtitles,,0,0,0,,معه جبالٌ من طعام وأنهار تجري..\\N{{\\c&H00FFFF&}}لكن يُحرم عليه دخول مكة والمدينة!{{\\r}}
Dialogue: 0,0:00:14.20,{format_time(total_duration)},GreenDua,,0,0,0,,تحرسهما الملائكة بسيوف من نور 🕊️\\N{{\\c&H50FF50&}}اللهم احفظنا من فتنته وثبت قلوبنا 🤲{{\\r}}
"""
    with open(ASS_SUBTITLES, "w", encoding="utf-8") as f:
        f.write(ass_content)
    print(f"  ✓ Subtitles written to: {ASS_SUBTITLES}")

def render_final_video(img1, img2, img3, duration):
    print("[4/5] Rendering 1080x1920 vertical short with Ken Burns camera movement...")
    
    d1 = 7.0
    d2 = 7.0
    d3 = max(6.0, duration - 14.0 + 0.3)
    
    v1 = OUTPUT_DIR / "p2_v1.mp4"
    v2 = OUTPUT_DIR / "p2_v2.mp4"
    v3 = OUTPUT_DIR / "p2_v3.mp4"
    v_concat = OUTPUT_DIR / "p2_v_concat.mp4"
    
    # Clip 1: Dramatic Zoom In 1.0 -> 1.15
    f1 = int(d1 * 30)
    cmd1 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img1),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0016,1.15)':d={f1}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d1:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v1)
    ]
    subprocess.run(cmd1, capture_output=True, check=True)
    
    # Clip 2: Pan & Zoom Out 1.14 -> 1.02
    f2 = int(d2 * 30)
    cmd2 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img2),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='max(1.14-0.0015*on,1.02)':d={f2}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d2:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v2)
    ]
    subprocess.run(cmd2, capture_output=True, check=True)
    
    # Clip 3: Cinematic Zoom In 1.0 -> 1.12
    f3 = int(d3 * 30)
    cmd3 = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-loop", "1", "-i", str(img3),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0014,1.12)':d={f3}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d3:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v3)
    ]
    subprocess.run(cmd3, capture_output=True, check=True)
    
    # Concat
    concat_list = OUTPUT_DIR / "p2_concat.txt"
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
        
    print(f"  ✓ Video Part 2 rendered: {FINAL_OUTPUT}")
    print(f"  ✓ Size: {FINAL_OUTPUT.stat().st_size:,} bytes | Duration: {duration:.2f}s")
    return FINAL_OUTPUT

def upload_to_youtube(video_path):
    print("[5/5] Uploading Part 2 directly to YouTube Shorts...")
    os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'
    
    import youtube_uploader
    
    title = "سرعة الدجال وعلاماته المرعبة! ⚠️ | الجزء الثاني #shorts"
    description = (
        "سرعة خروج المسيح الدجال وعلاماته المرعبة! ⚠️ | الجزء الثاني من سلسلة أحداث آخر الزمان.\n\n"
        "قال النبي ﷺ عن سرعة الدجال: «كالغيث استدبرته الريح» (صحيح مسلم).\n"
        "وقد بيّن النبي ﷺ أنه يطوف الأرض كلها إلا مكة والمدينة، فإن على كل نقب منها ملائكة يحرسونها.\n\n"
        "🤲 اللهم إنا نعوذ بك من فتنة المسيح الدجال، وثبت قلوبنا على الإيمان.\n\n"
        "📌 اكتب (آمين) لتشارك الأجر واشترك لمتابعة الجزء الثالث 🕊️\n\n"
        "#المسيح_الدجال #علامات_الساعة #الجزء_الثاني #نهاية_العالم #Dajjal #Shorts #Islam"
    )
    tags = ["المسيح_الدجال", "الدجال_الجزء_الثاني", "علامات_الساعة", "أشراط_الساعة", "نهاية_العالم", "Dajjal", "EndTimes", "وثائقي", "Shorts"]
    pinned_comment = "🤲 اللهم يا مقلب القلوب ثبت قلوبنا على دينك، وقنا شر فتنة المسيح الدجال. اكتب (آمين) لتشارك الأجر واشترك لمتابعة الجزء الثالث 🌿"
    
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
    print(f"Part 2 Narration duration: {duration:.2f}s")
    
    generate_cinematic_music(duration)
    generate_ass_subtitles(duration)
    
    img1 = ASSETS_DIR / "dajjal_p2_scene1.png"
    img2 = ASSETS_DIR / "dajjal_p2_scene2.png"
    img3 = ASSETS_DIR / "dajjal_p2_scene3.png"
    
    if not (img1.exists() and img2.exists() and img3.exists()):
        print(f"Waiting for images... Checked: {img1.exists()}, {img2.exists()}, {img3.exists()}")
        return
        
    out_vid = render_final_video(img1, img2, img3, duration)
    up_res = upload_to_youtube(out_vid)
    print("\n" + "=" * 60)
    print("=== LIVE UPLOAD RESULT (PART 2) ===")
    print(json.dumps(up_res, indent=2, ensure_ascii=False))
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
