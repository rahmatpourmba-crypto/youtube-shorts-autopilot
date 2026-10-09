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
    
    # 2. Download the video with high quality
    cmd_dl = [
        "yt-dlp",
        "--ffmpeg-location", FFMPEG_EXE,
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", str(raw_video_path),
        video_url
    ]
    subprocess.run(cmd_dl, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return {
        "raw_video": str(raw_video_path),
        "title": best_entry.get("title", "Viral Trending Short"),
        "tags": best_entry.get("tags", []),
        "description": best_entry.get("description", "")
    }

def apply_anti_copyright_edits(input_video: str, output_video: str, hook_banner: str = None):
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
    
    # Add high-CTR hook overlay on thumbnail if banner provided
    if thumb_path.exists() and hook_banner:
        try:
            img = Image.open(thumb_path)
            draw = ImageDraw.Draw(img)
            w, h = img.size
            # Top banner
            draw.rectangle([0, 150, w, 320], fill=(0, 0, 0, 180))
            draw.rounded_rectangle([60, 170, w - 60, 300], radius=25, fill=(255, 69, 0))
            draw.text((w // 2, 235), hook_banner, fill=(255, 255, 255), anchor="mm")
            img.save(thumb_path, "JPEG", quality=95)
        except Exception:
            pass

    return {
        "video": output_video,
        "thumbnail": str(thumb_path)
    }
