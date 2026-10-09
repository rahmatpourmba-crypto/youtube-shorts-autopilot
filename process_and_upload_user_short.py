import os
import sys
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from youtube_uploader import upload_short, CHANNELS

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def main():
    video_url = "https://youtube.com/shorts/Wt2J2i18Qeo"
    out_dir = Path(__file__).resolve().parent / "output" / "user_lion_hyenas_short"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    raw_video = out_dir / "raw_lion.mp4"
    edited_video = out_dir / "lion_vs_hyenas_modified.mp4"
    thumbnail_path = out_dir / "thumbnail.jpg"

    print("=" * 60, flush=True)
    print("Processing Real Viral Short: Lion Vs Hyenas Fight", flush=True)
    print("Destination: Funy animal Channel (@funyanimal27)", flush=True)
    print("=" * 60, flush=True)

    # 1. Download
    print("\n[1/3] Downloading original viral video with yt-dlp...", flush=True)
    cmd_dl = [
        "yt-dlp",
        "--ffmpeg-location", FFMPEG_EXE,
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", str(raw_video),
        video_url
    ]
    subprocess.run(cmd_dl, check=True)
    print(f"  Downloaded: {raw_video}", flush=True)

    # 2. Anti-copyright Transformations
    print("\n[2/3] Applying anti-copyright modifications (Speedup 1.04x, Pitch Shift, Color Grade)...", flush=True)
    vf = "setpts=PTS/1.04,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=contrast=1.06:brightness=0.01:saturation=1.09"
    af = "asetrate=44100*1.02,aresample=44100,atempo=1.04/1.02"

    cmd_edit = [
        FFMPEG_EXE, "-y",
        "-i", str(raw_video),
        "-vf", vf,
        "-af", af,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        str(edited_video)
    ]
    subprocess.run(cmd_edit, check=True)

    # Extract dynamic thumbnail
    cmd_thumb = [
        FFMPEG_EXE, "-y",
        "-ss", "00:00:03.000",
        "-i", str(edited_video),
        "-vframes", "1",
        "-q:v", "2",
        str(thumbnail_path)
    ]
    subprocess.run(cmd_thumb)

    # Add hook banner on thumbnail
    try:
        img = Image.open(thumbnail_path)
        draw = ImageDraw.Draw(img)
        w, h = img.size
        # Glowing top badge
        draw.rounded_rectangle([60, 160, w - 60, 310], radius=30, fill=(220, 20, 60))
        draw.text((w // 2, 235), "UNBELIEVABLE RESCUE! 🦁👑", fill=(255, 255, 255), anchor="mm")
        img.save(thumbnail_path, "JPEG", quality=95)
    except Exception as e:
        print(f"Thumbnail hook warning: {e}", flush=True)

    # 3. Upload to YouTube
    print("\n[3/3] Uploading modified Short to Funy animal Channel...", flush=True)
    title = "Lion Vs Hyenas Fight | Brother Lion Comes To The Rescue! 🦁👑 #Shorts #Wildlife"
    desc = (
        "Watch this incredible moment when a lion gets surrounded by a pack of hyenas, "
        "and another lion rushes in to save his brother! Nature is truly wild and amazing.\n\n"
        "🔔 Subscribe to @funyanimal27 for daily crazy animal & wildlife shorts!\n\n"
        "#Shorts #Lion #Wildlife #Animals #Hyenas #Nature #ViralShorts"
    )
    tags = ["Lion", "Hyenas", "Wildlife", "Animals", "Nature", "Shorts", "Viral", "BigCats", "LionFight"]

    upload_res = upload_short(
        channel_key="animals",
        video_path=str(edited_video),
        title=title,
        description=desc,
        tags=tags,
        category_id="15",
        thumbnail_path=str(thumbnail_path)
    )

    if upload_res:
        print("\n" + "=" * 60, flush=True)
        print("SUCCESSFULLY PUBLISHED TO YOUTUBE!", flush=True)
        print(f"Direct Short Link: {upload_res['url']}", flush=True)
        print("=" * 60, flush=True)

if __name__ == "__main__":
    main()
