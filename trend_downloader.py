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
    Applies aggressive anti-copyright transformations:
    - Speed up by 1.04x (breaks acoustic & optical exact matches)
    - Audio pitch shift & resample (44100*1.02 -> 44100)
    - Color grading eq filter (contrast 1.06, saturation 1.08)
    - Scale & center crop to 1080x1920 (9:16 vertical)
    - Top hook banner overlay
    """
    out_dir = Path(output_video).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Video filters:
    # 1. PTS speedup (1.04x)
    # 2. Scale & crop to 1080x1920 vertical
    # 3. Subtle color grade / contrast boost
    vf = "setpts=PTS/1.04,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=contrast=1.06:brightness=0.01:saturation=1.09"
    
    # Audio filters:
    # 1. asetrate pitch shift
    # 2. aresample to standard 44100
    # 3. atempo to match speed
    af = "asetrate=44100*1.02,aresample=44100,atempo=1.04/1.02"

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", input_video,
        "-vf", vf,
        "-af", af,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-threads", "0",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        output_video
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Extract thumbnail frame at 2.5 seconds
    thumb_path = out_dir / "thumbnail.jpg"
    cmd_thumb = [
        FFMPEG_EXE, "-y",
        "-ss", "00:00:02.500",
        "-i", output_video,
        "-vframes", "1",
        "-q:v", "2",
        str(thumb_path)
    ]
    subprocess.run(cmd_thumb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Apply luxury high-CTR styling on thumbnail
    if thumb_path.exists():
        try:
            from metadata_optimizer import generate_luxury_thumbnail
            generate_luxury_thumbnail(str(thumb_path), str(thumb_path), niche=niche, custom_text=hook_banner)
        except Exception as e:
            print(f"  [Thumbnail warning]: {e}")

    return {
        "video": output_video,
        "thumbnail": str(thumb_path)
    }
