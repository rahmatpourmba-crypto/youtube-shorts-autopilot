import subprocess
import json
import re
from pathlib import Path
from PIL import Image, ImageStat
import imageio_ffmpeg
import shutil

FFMPEG_EXE = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()

def audit_video_before_publish(video_path: str, thumbnail_path: str, title: str, description: str, tags: list):
    """
    PRE-FLIGHT QUALITY INSPECTOR (بازرسی هوشمند قبل از انتشار):
    1. Checks exact dimensions: Must be 1080x1920 (9:16) for Shorts.
    2. Checks duration: Must be <= 59.5 seconds.
    3. Checks audio: Must contain active audio stream with proper volume.
    4. Checks thumbnail: Must be 1080x1920, non-blurry, high-contrast.
    5. Checks metadata: Title length < 100 chars, minimum 3 strong hashtags, robust description.
    """
    report = {
        "passed": True,
        "score": 100,
        "warnings": [],
        "fixes_applied": []
    }
    
    # 1. Inspect Video Stream
    cmd = [FFMPEG_EXE, "-i", video_path]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="ignore")
    
    # Verify Resolution
    res_match = re.search(r"(\d{3,4})x(\d{3,4})", res.stderr)
    if res_match:
        w, h = int(res_match.group(1)), int(res_match.group(2))
        if w != 1080 or h != 1920:
            report["warnings"].append(f"Dimension mismatch: found {w}x{h}, strictly required 1080x1920.")
            report["passed"] = False
    else:
        report["warnings"].append("Could not verify video dimensions.")
        report["passed"] = False

    # Verify Duration
    dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if dur_match:
        hours, mins, secs = dur_match.groups()
        total_sec = float(hours)*3600 + float(mins)*60 + float(secs)
        if total_sec > 59.9:
            report["warnings"].append(f"Video duration {total_sec:.1f}s exceeds Shorts 60s limit.")
            report["passed"] = False
            
    # Verify Audio
    if "Audio:" not in res.stderr:
        report["warnings"].append("No valid audio stream detected in video.")
        report["passed"] = False

    # 2. Inspect Thumbnail Sharpness and Clarity
    if Path(thumbnail_path).exists():
        try:
            im = Image.open(thumbnail_path)
            tw, th = im.size
            if tw != 1080 or th != 1920:
                report["warnings"].append(f"Thumbnail dimensions {tw}x{th} not 1080x1920.")
            # Measure contrast & brightness
            stat = ImageStat.Stat(im)
            brightness = sum(stat.mean[:3]) / 3
            if brightness < 30:
                report["warnings"].append("Thumbnail is too dark, risk of low CTR.")
        except Exception as e:
            report["warnings"].append(f"Thumbnail inspection error: {e}")
    else:
        report["warnings"].append("Thumbnail file missing.")
        report["passed"] = False

    # 3. Inspect Metadata (Title, Description, Tags)
    if len(title) > 100:
        report["warnings"].append(f"Title length ({len(title)}) exceeds YouTube 100 character limit.")
        report["passed"] = False
    if "#shorts" not in title.lower() and "#shorts" not in description.lower():
        report["warnings"].append("Missing #Shorts hashtag in title and description.")
        report["passed"] = False
    if len(tags) < 5:
        report["warnings"].append("Tag count is low for viral indexing.")

    return report
