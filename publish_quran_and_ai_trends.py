import os
import sys
import subprocess
import json
import datetime
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from trend_downloader import search_and_download_viral_short, apply_anti_copyright_edits
from youtube_uploader import upload_short, CHANNELS

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def process_and_upload(channel_key: str, search_query: str, hook_banner: str, category_id: str):
    ch_info = CHANNELS[channel_key]
    out_dir = Path(__file__).resolve().parent / "output" / f"real_trend_{channel_key}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60, flush=True)
    print(f"[{ch_info['name']}] Processing Real Trending Short", flush=True)
    print(f"Target Account: {ch_info['email']}", flush=True)
    print("=" * 60, flush=True)
    
    # 1. Search and Download Real Trend
    print(f"\n[1/3] Searching & Downloading real viral Short for '{search_query}'...", flush=True)
    downloaded = search_and_download_viral_short(search_query, str(out_dir))
    print(f"  Downloaded: {downloaded['raw_video']}", flush=True)
    print(f"  Original Title: {downloaded['title']}", flush=True)
    
    # 2. Anti-copyright Modifications
    print("\n[2/3] Applying anti-copyright video editing (Speedup 1.04x, Pitch Shift, Color Grade)...", flush=True)
    edited_path = str(out_dir / f"final_{channel_key}_short.mp4")
    res = apply_anti_copyright_edits(
        input_video=downloaded["raw_video"],
        output_video=edited_path,
        hook_banner=hook_banner
    )
    print(f"  Edited Video: {res['video']}", flush=True)
    print(f"  Custom Thumbnail: {res['thumbnail']}", flush=True)
    
    # Title & Metadata
    clean_title = downloaded["title"]
    if "#shorts" not in clean_title.lower():
        clean_title = f"{clean_title[:80]} #Shorts"
        
    tags = downloaded.get("tags") or ["Shorts", "Viral"]
    desc = f"{downloaded.get('title')}\n\nSubscribe for daily viral Shorts!\n\n#Shorts #Viral"
    
    # 3. Upload to YouTube
    print(f"\n[3/3] Uploading modified Short to {ch_info['name']}...", flush=True)
    upload_res = upload_short(
        channel_key=channel_key,
        video_path=res["video"],
        title=clean_title,
        description=desc,
        tags=tags,
        category_id=category_id,
        thumbnail_path=res["thumbnail"]
    )
    
    if upload_res:
        print(f"\n[SUCCESS] Published to {ch_info['name']}! URL: {upload_res['url']}", flush=True)
        return upload_res["url"]
    else:
        print(f"\n[ERROR] Upload failed for {channel_key}.", flush=True)
        return None

def main():
    results = {}
    
    # 1. Quran Channel
    quran_url = process_and_upload(
        channel_key="quran",
        search_query="تلاوة خاشعة تريح القلب سورة quran recitation",
        hook_banner="تلاوة خاشعة تريح القلب 🕊️✨",
        category_id="22"
    )
    results["quran"] = quran_url

    # 2. AI Tools Channel
    ai_url = process_and_upload(
        channel_key="ai",
        search_query="insane new AI tools productivity",
        hook_banner="INSANE NEW AI TOOLS! 🤖⚡",
        category_id="28"
    )
    results["ai"] = ai_url

    print("\n" + "=" * 60, flush=True)
    print("ALL REAL TREND SHORTS PROCESSED AND PUBLISHED!", flush=True)
    for ch, link in results.items():
        print(f"  - {ch.upper()}: {link}", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    main()
