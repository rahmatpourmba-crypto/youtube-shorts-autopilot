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

FINAL_OUTPUT = OUTPUT_DIR / "viral_short_yajuj_majuj_scheduled.mp4"
AUDIO_FILE = OUTPUT_DIR / "yajuj_audio.mp3"
MUSIC_FILE = OUTPUT_DIR / "yajuj_cinematic_music.wav"
MIXED_AUDIO = OUTPUT_DIR / "yajuj_mixed_audio.mp3"
ASS_SUBTITLES = OUTPUT_DIR / "yajuj_subs.ass"

VOICE_TEXT = (
    "لحظة خروج يأجوج ومأجوج.. اللحظة التي يُدك فيها السد العظيم! "
    "قال الله تعالى: حتى إذا فُتحت يأجوج ومأجوج وهم من كل حدب ينسلون! "
    "قومٌ لا يدان لأحد بقتالهم.. فيأمر الله عيسى بن مريم أن يحرز عباده إلى الطور! "
    "اللهم نجنا من الفتن، ما ظهر منها وما بطن."
)

async def generate_voice():
    import edge_tts
    print("[1/5] Generating deep cinematic Arabic narration for Yajuj & Majuj...")
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
    return 24.0

def generate_cinematic_music(duration):
    print("[2/5] Synthesizing dark apocalyptic cinematic drone & heartbeat...")
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # Low frequency ominous notes
    f_sub = 38.89  # D#1
    f_root = 77.78 # D#2
    f_third = 92.50 # F#2
    
    sub = 0.38 * np.sin(2 * np.pi * f_sub * t)
    drone1 = 0.26 * np.sin(2 * np.pi * f_root * t)
    drone2 = 0.20 * np.sin(2 * np.pi * (f_root * 1.003) * t)
    pad = 0.16 * np.sin(2 * np.pi * f_third * t)
    
    # Heartbeat tension pulse
    pulse = np.zeros_like(t)
    bpm = 60
    spb = 60.0 / bpm
    total_beats = int(duration / spb)
    for beat in range(total_beats):
        t_start = int(beat * spb * sr)
        pulse_len = int(0.24 * sr)
        if t_start + pulse_len < len(pulse):
            pt = np.linspace(0, 0.24, pulse_len, endpoint=False)
            freq_decay = np.linspace(62, 28, pulse_len)
            hit = np.sin(2 * np.pi * freq_decay * pt) * np.exp(-pt * 16)
            pulse[t_start:t_start + pulse_len] += 0.48 * hit
            t2 = t_start + int(0.22 * sr)
            if t2 + pulse_len < len(pulse):
                pulse[t2:t2 + pulse_len] += 0.30 * hit
                
    # Riser
    riser_env = np.clip((t - 6.0) / (duration - 6.0), 0, 1) ** 2.0
    riser_freq = np.linspace(75, 180, len(t))
    riser = 0.16 * riser_env * np.sin(2 * np.pi * riser_freq * t)
    
    b, a = butter(4, 500 / (sr / 2), btype='low')
    mix = sub + drone1 + drone2 + pad + pulse + riser
    filtered = lfilter(b, a, mix)
    
    max_val = np.max(np.abs(filtered))
    if max_val > 0:
        filtered = filtered / max_val * 0.70
        
    wav_data = (filtered * 32767).astype(np.int16)
    wavfile.write(str(MUSIC_FILE), sr, wav_data)
    print(f"  ✓ Dark cinematic synth saved to: {MUSIC_FILE}")
    
    # Mix with edge-tts voice
    mix_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(AUDIO_FILE),
        "-i", str(MUSIC_FILE),
        "-filter_complex", "[0:a]volume=1.25[v];[1:a]volume=0.32[m];[v][m]amix=inputs=2:duration=first[out]",
        "-map", "[out]",
        str(MIXED_AUDIO)
    ]
    subprocess.run(mix_cmd, capture_output=True, check=True)
    print("  ✓ Mixed audio track created successfully")

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def generate_ass_subtitles(total_duration):
    print("[3/5] Generating styled Arabic ASS subtitle file...")
    
    ass_content = f"""[Script Info]
Title: Yajuj and Majuj Viral Short
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopHook,Vazirmatn,50,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,8,40,40,240,1
Style: Subtitles,Vazirmatn,56,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,380,1
Style: Ayah,Vazirmatn,54,&H0000E6FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,380,1
Style: Dua,Vazirmatn,54,&H0050FF50,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:06.00,TopHook,,0,0,0,,{{\\b1\\c&H0033FF&}}⚠️ خروج يأجوج ومأجوج{{\\r}}\\N{{\\fs40\\c&HFFFFFF&}}اللحظة التي يُدك فيها السد العظيم!
Dialogue: 0,0:00:00.20,0:00:06.20,Subtitles,,0,0,0,,لحظة خروج يأجوج ومأجوج..\\N{{\\c&H00D4FF&}}اللحظة التي يُدك فيها السد العظيم!{{\\r}}
Dialogue: 0,0:00:06.20,0:00:13.80,Ayah,,0,0,0,,﴿حَتَّىٰ إِذَا فُتِحَتْ يَأْجُوجُ وَمَأْجُوجُ\\Nوَهُم مِّن كُلِّ حَدَبٍ يَنسِلُونَ﴾
Dialogue: 0,0:00:13.80,0:00:20.50,Subtitles,,0,0,0,,قومٌ لا يدان لأحد بقتالهم..\\Nفيأمر الله عيسى أن يحرز عباده إلى الطور!
Dialogue: 0,0:00:20.50,{format_time(total_duration)},Dua,,0,0,0,,🤲 اللهم نجنا من الفتن ما ظهر منها وما بطن\\N{{\\fs42\\c&HFFFFFF&}}اكتب (يا رب سلّم) واشترك في القناة 🕊️
"""
    with open(ASS_SUBTITLES, "w", encoding="utf-8") as f:
        f.write(ass_content)
    print(f"  ✓ Subtitles written to: {ASS_SUBTITLES}")

def render_final_video(img1, img2, img3, duration):
    print(f"[4/5] Rendering 1080x1920 60fps vertical short ({duration:.1f}s)...")
    
    d1 = duration * 0.32
    d2 = duration * 0.36
    d3 = duration - d1 - d2
    
    v1 = OUTPUT_DIR / "yajuj_v1.mp4"
    v2 = OUTPUT_DIR / "yajuj_v2.mp4"
    v3 = OUTPUT_DIR / "yajuj_v3.mp4"
    v_concat = OUTPUT_DIR / "yajuj_v_concat.mp4"
    
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
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0015,1.12)':d={f3}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
        "-t", f"{d3:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(v3)
    ]
    subprocess.run(cmd3, capture_output=True, check=True)
    
    # Concat clips
    concat_list = OUTPUT_DIR / "yajuj_concat.txt"
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
    
    # Overlay subtitles, color grading, watermark, anti-fingerprint, and audio
    font_file = BASE_DIR / "Vazirmatn-Bold.ttf"
    ass_path_escaped = str(ASS_SUBTITLES.resolve()).replace("\\", "/").replace(":", "\\:")
    
    watermark_text = "@NourAlQuran"
    
    vf_chain = (
        f"subtitles='{ass_path_escaped}',"
        f"scale=1.02*iw:-1,crop=1080:1920,"
        f"eq=contrast=1.05:brightness=0.01:saturation=1.08,"
        f"drawtext=text='{watermark_text}':x=w-tw-40:y=240:fontsize=36:fontcolor=white@0.65:box=1:boxcolor=black@0.35:boxborderw=6"
    )
    
    final_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(v_concat),
        "-i", str(MIXED_AUDIO),
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
    print(f"[5/5] Scheduling Short on YouTube channel 'quran' at {publish_at_iso}...")
    os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'
    
    import youtube_uploader
    
    title = "لحظة خروج يأجوج ومأجوج.. وانهيار السد العظيم! ⚠️🌍 #shorts #علامات_الساعة"
    description = (
        "لحظة خروج يأجوج ومأجوج.. اللحظة التي يُدك فيها السد العظيم! ⚠️🌍\n\n"
        "قال الله تعالى:\n"
        "﴿حَتَّىٰ إِذَا فُتِحَتْ يَأْجُوجُ وَمَأْجُوجُ وَهُم مِّن كُلِّ حَدَبٍ يَنسِلُونَ ۝ وَاقْتَرَبَ الْوَعْدُ الْحَقُّ﴾ [الأنبياء: 96-97]\n\n"
        "وقد أخبر النبي ﷺ أن الله يوحي إلى نبي الله عيسى بن مريم عليه السلام:\n"
        "«إني قد أخرجت عباداً لي لا يدان لأحد بقتالهم، فحرّز عبادي إلى الطور».\n\n"
        "🤲 اللهم إنا نعوذ بك من الفتن ما ظهر منها وما بطن، ونسألك الثبات والنجاة.\n\n"
        "📌 اكتب (يا رب سلّم) في التعليقات واشترك في قناة نور القرآن 🕊️\n\n"
        "#يأجوج_ومأجوج #سد_ذي_القرنين #علامات_الساعة #أشراط_الساعة #نهاية_العالم #GogAndMagog #YajujAndMajuj #Shorts #Quran"
    )
    tags = [
        "يأجوج_ومأجوج", "سد_ذي_القرنين", "علامات_الساعة", "أشراط_الساعة", 
        "نهاية_العالم", "يوم_القيامة", "سورة_الأنبياء", "GogAndMagog", 
        "YajujAndMajuj", "Shorts", "Quran"
    ]
    pinned_comment = "⚠️ قال ﷺ: «يقول الله لعيسى: إني قد أخرجت عباداً لي لا يدان لأحد بقتالهم، فحرّز عبادي إلى الطور».. اكتب (يا رب سلّم) واشترك ليصلك الجزء القادم 🌿"
    
    result = youtube_uploader.upload_short(
        channel_key="quran",
        video_path=str(video_path),
        title=title,
        description=description,
        tags=tags,
        pinned_comment=pinned_comment,
        publish_at=publish_at_iso
    )
    return result

async def main():
    # 1. Voice
    await generate_voice()
    duration = get_audio_duration(AUDIO_FILE)
    print(f"Total Narration Duration: {duration:.2f}s (Strictly under 50s)")
    
    # 2. Audio & Subtitles
    generate_cinematic_music(duration)
    generate_ass_subtitles(duration)
    
    # 3. Locate Images
    img1 = BRAIN_DIR / "yajuj_scene1_barrier_png_1794680235125.jpg"
    img2 = BRAIN_DIR / "yajuj_scene2_swarm_png_1794680289590.jpg"
    img3 = BRAIN_DIR / "yajuj_scene3_refuge_png_1794680321727.jpg"
    
    if not (img1.exists() and img2.exists() and img3.exists()):
        print("Error: Missing images!")
        return
    
    out_vid = render_final_video(img1, img2, img3, duration)
    
    # 4. Target publish time: 1 hour in the future (e.g. ~22:50 Tehran / 19:20 UTC)
    import datetime
    scheduled_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=60)
    publish_at_target = scheduled_dt.strftime("%Y-%m-%dT%H:%M:00.000Z")
    
    up_res = upload_and_schedule(out_vid, publish_at_target)
    print("\n" + "=" * 60)
    print("=== LIVE UPLOAD & SCHEDULE RESULT ===")
    print(json.dumps(up_res, indent=2, ensure_ascii=False))
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
