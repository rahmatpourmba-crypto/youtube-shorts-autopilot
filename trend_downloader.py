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
    
    # 1. Search for Shorts under 60s
    search_term = f"ytsearch8:{search_query} #shorts"
    cmd_search = [
        "yt-dlp",
        search_term,
        "--match-filter", "duration <= 60 & duration >= 10",
        "--dump-json",
        "--flat-playlist", "False",
        "--no-playlist"
    ]
    
    res = subprocess.run(cmd_search, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    lines = res.stdout.strip().split("\n")
    
    best_entry = None
    max_views = -1
    
    for line in lines:
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            views = data.get("view_count", 0) or 0
            dur = data.get("duration", 0) or 0
            if 10 <= dur <= 60:
                if views > max_views or best_entry is None:
                    max_views = views
                    best_entry = data
        except Exception:
            continue
            
    if not best_entry:
        # Fallback simple search without filter
        cmd_fallback = ["yt-dlp", f"ytsearch1:{search_query} #shorts", "--dump-json"]
        fb_res = subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        for line in fb_res.stdout.strip().split("\n"):
            try:
                best_entry = json.loads(line)
                break
            except Exception:
                pass

    if not best_entry:
        raise RuntimeError(f"Could not find any suitable viral Shorts for '{search_query}'")

    video_url = best_entry.get("webpage_url") or f"https://www.youtube.com/watch?v={best_entry.get('id')}"
    raw_video_path = out_dir / "raw_download.mp4"
    
    # 2. Download the video with high quality & datacenter bypass
    cmd_dl = [
        "yt-dlp",
        "--ffmpeg-location", FFMPEG_EXE,
        "--extractor-args", "youtube:player_client=android,ios",
        "--geo-bypass",
        "-f", "best[ext=mp4]/best",
        "-o", str(raw_video_path),
        video_url
    ]
    try:
        subprocess.run(cmd_dl, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as err:
        print(f"  [yt-dlp warning] Retrying with web client: {err.stderr.decode('utf-8', errors='ignore')[:200]}")
        cmd_dl_fallback = [
            "yt-dlp",
            "--ffmpeg-location", FFMPEG_EXE,
            "--extractor-args", "youtube:player_client=web,tv",
            "--geo-bypass",
            "-o", str(raw_video_path),
            video_url
        ]
        subprocess.run(cmd_dl_fallback, check=True)
    
    return {
        "raw_video": str(raw_video_path),
        "title": best_entry.get("title", "Viral Trending Short"),
        "tags": best_entry.get("tags", []),
        "description": best_entry.get("description", "")
    }

def apply_anti_copyright_edits(input_video: str, output_video: str, hook_banner: str = None, niche: str = "animals"):
    """
    Applies professional high-retention anti-copyright editing with smart framing,
    blurred backgrounds (if horizontal), audio remastering, and sharp luxury thumbnails.
    """
    from video_editor_pro import apply_professional_high_retention_edits
    return apply_professional_high_retention_edits(
        input_video=input_video,
        output_video=output_video,
        hook_banner=hook_banner,
        niche=niche
    )
