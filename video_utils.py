import subprocess
import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def get_ffmpeg():
    return FFMPEG_EXE

def apply_anti_copyright_transformations(input_video: str, output_video: str, speed: float = 1.04):
    """
    Applies anti-copyright filters:
    1. Slight speedup (1.04x)
    2. Audio pitch shifting & resampling (bypasses Content ID sound wave match)
    3. Visual color grading / subtle contrast & saturation boost
    4. 1080x1920 9:16 vertical crop/scaling
    """
    atempo = speed
    setpts = f"PTS/{speed}"
    
    # ffmpeg video filter: scale to vertical 1080:1920, slight color grading
    vf = f"setpts={setpts},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=contrast=1.06:brightness=0.02:saturation=1.08"
    # audio filter: pitch slightly shifted and tempo adjusted
    af = f"asetrate=44100*1.02,aresample=44100,atempo={atempo/1.02}"

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", input_video,
        "-vf", vf,
        "-af", af,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        output_video
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_video

def create_short_from_audio_and_slides(slides: list, audio_path: str, output_video: str, duration: float = None):
    """
    Creates a dynamic 1080x1920 vertical video from slide images and an audio track.
    """
    Path(output_video).parent.mkdir(parents=True, exist_ok=True)
    
    # Calculate duration if not provided
    if duration is None:
        cmd_dur = [
            FFMPEG_EXE, "-i", audio_path,
            "-show_entries", "format=duration",
            "-v", "quiet", "-of", "csv=p=0"
        ]
        # fallback simple check
        duration = 15.0 # default fallback
        try:
            res = subprocess.run([FFMPEG_EXE, "-i", audio_path], stderr=subprocess.PIPE, text=True)
            for line in res.stderr.splitlines():
                if "Duration:" in line:
                    t_str = line.split("Duration:")[1].split(",")[0].strip()
                    h, m, s = t_str.split(":")
                    duration = float(h)*3600 + float(m)*60 + float(s)
                    break
        except Exception:
            pass

    slide_duration = max(2.5, duration / max(len(slides), 1))
    
    # Build concat file
    concat_file = Path(output_video).parent / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for slide in slides:
            f.write(f"file '{Path(slide).as_posix()}'\n")
            f.write(f"duration {slide_duration:.2f}\n")
        if slides:
            f.write(f"file '{Path(slides[-1]).as_posix()}'\n")

    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-i", audio_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "21",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_video
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if concat_file.exists():
        concat_file.unlink()
    return output_video

def generate_eye_catching_thumbnail(title: str, subtitle: str, badge: str, output_path: str, bg_color1=(24, 18, 43), bg_color2=(99, 44, 219)):
    """
    Generates a high-CTR, vibrant 1080x1920 thumbnail.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), bg_color1)
    draw = ImageDraw.Draw(img)

    # Vertical gradient
    for y in range(height):
        ratio = y / height
        r = int(bg_color1[0] * (1 - ratio) + bg_color2[0] * ratio)
        g = int(bg_color1[1] * (1 - ratio) + bg_color2[1] * ratio)
        b = int(bg_color1[2] * (1 - ratio) + bg_color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Decorative geometric accents (glow cards)
    card_rect = [60, 400, 1020, 1500]
    draw.rounded_rectangle(card_rect, radius=40, fill=(15, 15, 25, 220), outline=(255, 215, 0), width=4)

    # Badge Pill (e.g. "HOT", "NEW", "100% FREE", "QUICK TUTORIAL")
    badge_rect = [120, 460, 960, 560]
    draw.rounded_rectangle(badge_rect, radius=25, fill=(255, 69, 0))
    draw.text((width // 2, 510), badge, fill=(255, 255, 255), anchor="mm")

    # Title & Subtitle text
    draw.text((width // 2, 750), title, fill=(255, 255, 255), anchor="mm")
    draw.text((width // 2, 950), subtitle, fill=(255, 215, 0), anchor="mm")
    
    # Call to action footer
    cta_rect = [120, 1300, 960, 1420]
    draw.rounded_rectangle(cta_rect, radius=30, fill=(0, 200, 83))
    draw.text((width // 2, 1360), "WATCH NOW ▶", fill=(0, 0, 0), anchor="mm")

    img.save(output_path, "JPEG", quality=95)
    return output_path
