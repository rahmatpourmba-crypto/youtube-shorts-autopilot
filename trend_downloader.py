import subprocess
import json
import re
from pathlib import Path
import shutil
import imageio_ffmpeg
from PIL import Image, ImageDraw

FFMPEG_EXE = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()

def search_and_download_viral_short(search_query: str, download_dir: str):
    """
    Searches YouTube for real viral Shorts under 60 seconds, downloads the highest-viewed one,
    and returns its file path and metadata.
    """
    out_dir = Path(download_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Use Ultra-Smart Velocity Scanner
    from smart_trend_scanner import find_highest_velocity_viral_short
    best_entry = find_highest_velocity_viral_short(search_query, max_candidates=10)

    if not best_entry:
        raise RuntimeError(f"Could not find any suitable viral Shorts for '{search_query}'")

    video_url = best_entry.get("webpage_url") or f"https://www.youtube.com/watch?v={best_entry.get('id')}"
    raw_video_path = out_dir / "raw_download.mp4"
    
    # 2. Download the video with high quality & datacenter bypass
    clients = ["android", "ios", "mweb", "android_creator"]
    download_success = False
    
    for client in clients:
        cmd_dl = [
            "yt-dlp",
            "--ffmpeg-location", FFMPEG_EXE,
            "--extractor-args", f"youtube:player_client={client}",
            "--geo-bypass",
            "-f", "best[ext=mp4]/best",
            "-o", str(raw_video_path),
            video_url
        ]
        try:
            subprocess.run(cmd_dl, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            download_success = True
            break
        except subprocess.CalledProcessError as err:
            err_msg = err.stderr.decode('utf-8', errors='ignore') if err.stderr else ""
            print(f"  [yt-dlp note] Client '{client}' failed, trying next client: {err_msg[:120]}")
            continue

    if not download_success:
        # Ultimate fallback
        cmd_fallback = [
            "yt-dlp",
            "--ffmpeg-location", FFMPEG_EXE,
            "--geo-bypass",
            "-o", str(raw_video_path),
            video_url
        ]
        subprocess.run(cmd_fallback, check=True)

    
    return {
        "raw_video": str(raw_video_path),
        "title": best_entry.get("title", "Viral Trending Short"),
        "tags": best_entry.get("tags", []),
        "description": best_entry.get("description", "")
    }

def apply_anti_copyright_edits(input_video: str, output_video: str, hook_banner: str = None, niche: str = "animals"):
    """
    Applies the 300M-View Viral Editing Strategy:
    - Strict 1080x1920 (9:16) vertical format (no awkward squares).
    - Contrast/vibrancy remastering exceeding original video quality.
    - Pacing boost (1.05x) and audio normalization for >100% retention.
    - High-CTR luxury cover extraction and styling.
    """
    from video_editor_pro import render_300m_viral_short
    return render_300m_viral_short(
        input_video=input_video,
        output_video=output_video,
        hook_banner=hook_banner,
        niche=niche
    )
