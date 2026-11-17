#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
🌙 LONG-FORM SLEEP & RELAXATION QURAN ENGINE (موتور لانگ‌فرم ۴۰۰۰ ساعت واچ‌تایم)
=============================================================================
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime, timezone

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import imageio_ffmpeg
FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_OUTPUT = BASE_DIR / "output" / "longform_quran"
WORKSPACE_OUTPUT.mkdir(parents=True, exist_ok=True)
ASSETS_DIR = BASE_DIR / "assets"
TOKEN_PICKLE_FILE = os.getenv("YOUTUBE_TOKEN_FILE", str(BASE_DIR / "token_quran.pickle"))
CHANNEL_WATERMARK = os.getenv("CHANNEL_WATERMARK", "@NourAlQuran")

LONGFORM_CHAPTERS = [
    {
        "name": "سورة الملك (المنجية من عذاب القبر)",
        "surah_num": 67,
        "ayah_count": 30,
        "prefix": "067"
    },
    {
        "name": "سورة السجدة (راحة وسكينة)",
        "surah_num": 32,
        "ayah_count": 30,
        "prefix": "032"
    },
    {
        "name": "سورة الرحمن (عروس القرآن)",
        "surah_num": 55,
        "ayah_count": 35,
        "prefix": "055"
    }
]

CDN_BASE = "https://everyayah.com/data/Yasser_Ad-Dussary_128kbps"

def authenticate_youtube():
    token_path = Path(TOKEN_PICKLE_FILE)
    creds = None
    if token_path.exists():
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "wb") as f:
                pickle.dump(creds, f)
        else:
            raise RuntimeError(f"YouTube credentials missing or invalid: {TOKEN_PICKLE_FILE}")

    return build("youtube", "v3", credentials=creds)

def download_surah_audio(chapter_info, out_dir):
    files = []
    prefix = chapter_info["prefix"]
    count = chapter_info["ayah_count"]
    print(f"\n[Audio Engine] دانلود صوت استودیویی {chapter_info['name']} ({count} آیه)...")
    
    for i in range(1, count + 1):
        code = f"{prefix}{i:03d}"
        dest = out_dir / f"{code}.mp3"
        if not (dest.exists() and dest.stat().st_size > 1000):
            url = f"{CDN_BASE}/{code}.mp3"
            for attempt in range(1, 4):
                try:
                    r = requests.get(url, timeout=20)
                    if r.status_code == 200:
                        with open(dest, "wb") as f:
                            f.write(r.content)
                        break
                except Exception:
                    time.sleep(1)
        if dest.exists() and dest.stat().st_size > 1000:
            files.append(dest)
        time.sleep(0.05)
    return files

def build_and_upload_longform():
    print("=" * 65)
    print("🌙 [LONG-FORM WATCH-TIME BOOSTER] شروع ساخت و آپلود ویدیوی آرامش‌بخش شبانه...")
    print("=" * 65)
    
    audio_dir = WORKSPACE_OUTPUT / "audio_source"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    all_audio_files = []
    chapter_timestamps = []
    current_time_sec = 0.0
    
    for ch in LONGFORM_CHAPTERS:
        mins = int(current_time_sec // 60)
        secs = int(current_time_sec % 60)
        chapter_timestamps.append(f"{mins:02d}:{secs:02d} - {ch['name']}")
        
        ch_files = download_surah_audio(ch, audio_dir)
        all_audio_files.extend(ch_files)
        current_time_sec += len(ch_files) * 6.5
        
    print(f"\n[Audio Master] در حال تجمیع {len(all_audio_files)} قطعه صوتی...")
    concat_list = WORKSPACE_OUTPUT / "concat_longform.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for fpath in all_audio_files:
            f.write(f"file '{fpath.resolve()}'\n")
            
    master_audio = WORKSPACE_OUTPUT / "master_longform_audio.mp3"
    subprocess.run([
        FFMPEG_BIN, "-y", "-hide_banner",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-filter:a", "volume=1.10,afade=t=in:ss=0:d=1.0",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(master_audio)
    ], check=True)
    
    # Measure audio duration
    dur_cmd = [FFMPEG_BIN, "-hide_banner", "-i", str(master_audio)]
    res = subprocess.run(dur_cmd, capture_output=True, text=True, errors="ignore")
    total_dur = 1800.0
    for l in res.stderr.splitlines():
        if "Duration:" in l:
            dur_str = l.split("Duration:")[1].split(",")[0].strip()
            h, m, s = dur_str.split(":")
            total_dur = float(h) * 3600 + float(m) * 60 + float(s)
            break
            
    print(f"  ✓ صوت تجمیع‌شده آماده شد: {total_dur/60:.1f} دقیقه")
    
    final_video = WORKSPACE_OUTPUT / f"relaxing_quran_sleep_{int(time.time())}.mp4"
    vf_chain = (
        "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        "eq=contrast=1.03:brightness=-0.02:saturation=1.05,"
        f"drawtext=text='{CHANNEL_WATERMARK}':x=w-tw-50:y=60:fontsize=32:fontcolor=white@0.75:shadowcolor=black@0.6:shadowx=2:shadowy=2,"
        "drawtext=text='تلاوة هادئة ومريحة للنوم والسكينة 🕊️ الشيخ ياسر الدوسري':x=(w-tw)/2:y=h-120:fontsize=42:fontcolor=white@0.90:shadowcolor=black@0.8:shadowx=2:shadowy=2"
    )
    
    bg_arg = ["-f", "lavfi", "-i", "color=c=0x070b19:s=1920x1080:d=60"]
    
    render_cmd = [
        FFMPEG_BIN, "-y", "-hide_banner",
        "-stream_loop", "-1",
        *bg_arg,
        "-i", str(master_audio),
        "-vf", vf_chain,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-c:a", "copy",
        "-shortest",
        str(final_video)
    ]
    
    print("  در حال رندر ویدیوی لانگ‌فرم 1920x1080...")
    subprocess.run(render_cmd, capture_output=True, check=True)
    print(f"  ✓ ویدیوی کامل لانگ‌فرم آماده شد: {final_video.name} ({final_video.stat().st_size:,} بایت)")
    
    title = "تلاوة هادئة ومريحة للنوم والراحة النفسية | سورة الملك والرحمن والسجدة | الشيخ ياسر الدوسري | Relaxing Quran"
    description = f"""تلاوة هادئة خاشعة تأسر القلوب وتسكن الأرواح بصوت الشيخ ياسر الدوسري حفظه الله.
استمع إليها قبل النوم، أثناء المذاكرة، أو لتهدئة النفس وطرد الهم والحزن.

قال تعالى: ﴿الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾

فهرس السور (Timestamps):
{chr(10).join(chapter_timestamps)}

🤲 اكتب شيئاً تؤجر عليه في التعليقات واذكر الله ليكون شاهداً لك يوم القيامة.
اشترك في قناة نور القرآن ليصلك القرآن الكريم يومياً 🕊️ {CHANNEL_WATERMARK}

#القرآن_الكريم #تلاوة_خاشعة #ياسر_الدوسري #سورة_الملك #سورة_الرحمن #النوم #راحة_نفسية #Quran #RelaxingQuran
"""
    tags = [
        "تلاوة هادئة", "قرآن للنوم", "راحة نفسية", "الشيخ ياسر الدوسري",
        "سورة الملك", "سورة الرحمن", "سورة السجدة", "القرآن الكريم",
        "relaxing quran", "quran for sleep", "quran recitation", "islam"
    ]
    
    # Upload via YouTube API
    try:
        yt = authenticate_youtube()
        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags,
                "categoryId": "22",
                "defaultLanguage": "ar",
                "defaultAudioLanguage": "ar"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        media = MediaFileUpload(str(final_video), chunksize=10*1024*1024, resumable=True, mimetype="video/*")
        request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
        
        print(f"  [Uploading Longform] در حال آپلود ویدیوی واچ‌تایم به یوتیوب...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  [Upload Progress] پیشرفت آپلود: {int(status.progress() * 100)}%")
                
        if response and response.get("id"):
            vid_id = response.get("id")
            url = f"https://www.youtube.com/watch?v={vid_id}"
            print(f"🎉 ویدیوی لانگ‌فرم واچ‌تایم با موفقیت منتشر شد: {url}")
            return {"status": "SUCCESS", "video_id": vid_id, "url": url}
    except Exception as e:
        print(f"⚠️ خطای آپلود لانگ‌فرم: {e}")
        
    return {"status": "ERROR"}

if __name__ == "__main__":
    build_and_upload_longform()
