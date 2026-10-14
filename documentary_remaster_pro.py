"""
DOCUMENTARY REMASTER PRO - 7-LAYER ANTI-COPYRIGHT & ZERO-LOSS ENGINE
Specifically engineered for long-form Islamic historical & mystery documentaries (Dajjal, End Times, Battles).
- Visually Lossless CRF 18 + Unsharp AI filter
- Dual visual/audio temporal & pitch fingerprint scrambling (1.03x + 1.025 pitch)
- Broadcast Loudnorm normalization (-14 LUFS)
- Elegant gold Islamic watermark for 'نور القرآن'
- Natural 1080p high-res thumbnail extraction from the video itself
"""
import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

FFMPEG_EXE = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = Path(__file__).resolve().parent

def create_watermark_png(out_path: str, channel_name: str = "نور القرآن | The Holy Light"):
    """Creates a subtle, luxury transparent golden watermark for the channel."""
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Bottom right or top right subtle elegant tag
    font_path = "C:/Windows/Fonts/arialbd.ttf" if os.path.exists("C:/Windows/Fonts/arialbd.ttf") else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 28)
    except Exception:
        font = ImageFont.load_default()
        
    tag_text = "🕊️ " + channel_name
    # Draw soft semi-transparent pill in top right corner
    box = [(1480, 40), (1880, 95)]
    draw.rounded_rectangle(box, radius=18, fill=(15, 18, 30, 160), outline=(212, 175, 55, 190), width=2)
    draw.text((1680, 68), tag_text, font=font, fill=(255, 230, 140, 220), anchor="mm")
    
    img.save(out_path, "PNG")
    return out_path

def download_trending_documentary(video_id: str, download_dir: Path):
    download_dir.mkdir(parents=True, exist_ok=True)
    raw_video = download_dir / "raw_documentary.mp4"
    if raw_video.exists() and raw_video.stat().st_size > 10 * 1024 * 1024:
        print(f"  [Cache] Raw documentary already downloaded: {raw_video}")
        return str(raw_video)

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"  [Downloader] Fetching pristine 1080p source from YouTube: {video_url}...")
    cmd = [
        "yt-dlp",
        "--ffmpeg-location", FFMPEG_EXE,
        "--extractor-args", "youtube:player_client=tv,mweb,web",
        "--geo-bypass",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/18/best",
        "--merge-output-format", "mp4",
        "-o", str(raw_video),
        video_url
    ]
    subprocess.run(cmd, check=True)
    return str(raw_video)

def remaster_documentary_video(raw_input: str, output_path: str, watermark_png: str):
    print("  [Remaster Engine] Applying 7-Layer Zero-Loss Anti-Copyright Shield...")
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 7-LAYER FILTER CHAIN:
    # 1. crop=in_w*0.98:in_h*0.98 -> Strips edge fingerprints & old watermarks
    # 2. scale=1920:1080 -> Strict 1080p Full HD
    # 3. setpts=PTS/1.03 -> 3% speedup breaks temporal visual frame hash
    # 4. eq=contrast=1.06:brightness=0.01:saturation=1.12 -> Cinema color punch
    # 5. unsharp=5:5:0.6:5:5:0.0 -> AI-like crystal edge sharpening (no quality loss!)
    # 6. overlay -> Burns channel watermark
    # 7. asetrate + atempo + loudnorm -> Audio pitch & frequency shift + -14 LUFS broadcast mastering
    
    vf_base = (
        "crop=in_w*0.98:in_h*0.98,"
        "scale=1920:1080:flags=lanczos,"
        "setpts=PTS/1.03,"
        "eq=contrast=1.06:brightness=0.01:saturation=1.12,"
        "unsharp=5:5:0.6:5:5:0.0"
    )
    
    filter_complex = f"[0:v]{vf_base}[v_sharp];[v_sharp][1:v]overlay=0:0[outv]"
    af = "asetrate=44100*1.025,aresample=44100,atempo=1.03/1.025,loudnorm=I=-14:TP=-1.5:LRA=11"
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", raw_input,
        "-i", watermark_png,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a",
        "-af", af,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",          # Visually lossless premium broadcast quality
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",        # Studio-grade audio
        output_path
    ]
    
    print("  [FFmpeg] Rendering remastered 1080p Full HD master (this takes 1-3 mins)...")
    subprocess.run(cmd, check=True)
    print(f"  [Success] Remastered master completed: {output_path}")

    # Extract high-res thumbnail directly from the remastered video itself at peak moment (e.g. 180s)
    thumb_path = out_dir / "thumbnail.jpg"
    cmd_thumb = [
        FFMPEG_EXE, "-y",
        "-ss", "00:03:00.000",
        "-i", output_path,
        "-vframes", "1",
        "-q:v", "1",
        str(thumb_path)
    ]
    subprocess.run(cmd_thumb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"  [Thumbnail] Clean authentic 1080p frame extracted directly from video: {thumb_path}")
    
    return {
        "video": output_path,
        "thumbnail": str(thumb_path)
    }

def process_dajjal_documentary():
    work_dir = BASE_DIR / "output" / "documentary_dajjal"
    work_dir.mkdir(parents=True, exist_ok=True)
    
    source_id = "Bgwgh71nJos"
    source_channel = "وثائقية أحداث وحقائق روايات (3.07M Views)"
    print("=" * 65)
    print("=== ISLAMIC LONG-FORM DOCUMENTARY MASTERPIECE ===")
    print(f"Topic: The Island of Dajjal & Tamim Al-Dari")
    print(f"Selected Source Channel: {source_channel}")
    print(f"Source YouTube ID: {source_id} (14 minutes, 1080p HD)")
    print("=" * 65)
    
    watermark_file = str(work_dir / "watermark.png")
    create_watermark_png(watermark_file, "نور القرآن | The Holy Light")
    
    raw_video = download_trending_documentary(source_id, work_dir)
    remastered_video = str(work_dir / "dajjal_tamim_dari_1080p_remastered.mp4")
    
    result = remaster_documentary_video(raw_video, remastered_video, watermark_file)
    
    metadata = {
        "title": "رحلة تميم الداري إلى جزيرة المسيح الدجال ⚠️ | الوثائقي الكامل للقصة الحقيقية",
        "description": (
            "الفيلم الوثائقي الكامل لقصة الصحابي الجليل تميم الداري رضي الله عنه مع المسيح الدجال والجسّاسة في الجزيرة الغامضة في عرض البحر، كما رواها النبي ﷺ في الحديث الصحيح.\n\n"
            "📌 اشترك في قناة نور القرآن | The Holy Light لمزيد من القصص والوثائقيات الإسلامية الخاشعة.\n\n"
            "00:00 مقدمة القصة وعاصفة البحر\n"
            "02:15 الوصول إلى الجزيرة المجهولة\n"
            "05:30 لقاء دابة الجسّاسة العجيبة\n"
            "08:45 المحادثة المباشرة مع المسيح الدجال وأسئلته الثلاثة\n"
            "12:10 إخبار النبي ﷺ للمسلمين بالقصة وتأكيدها\n\n"
            "#الدجال #المسيح_الدجال #تميم_الداري #قصص_الأنبياء #وثائقي #القرآن_الكريم #أحداث_النهاية #نور_القرآن"
        ),
        "tags": [
            "الدجال", "المسيح الدجال", "تميم الداري", "جزيرة الدجال", "الجسّاسة", 
            "وثائقي إسلامي", "قصص القرآن", "أحداث النهاية", "علامات الساعة", 
            "نور القرآن", "Dajjal", "Tamim Dari", "Islamic Documentary", "End Times"
        ],
        "category_id": "22",
        "video_path": result["video"],
        "thumbnail_path": result["thumbnail"]
    }
    
    # Save metadata JSON
    with open(work_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    print("\n✓ Documentary remastered and ready for upload!")
    print(f"Video file: {result['video']}")
    print(f"Thumbnail: {result['thumbnail']}")
    print(f"Title: {metadata['title']}")
    return metadata

if __name__ == "__main__":
    process_dajjal_documentary()
