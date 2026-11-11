import os
import sys
import shutil
import time
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import imageio_ffmpeg
import arabic_reshaper
from bidi.algorithm import get_display

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure API authorization
os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

import youtube_uploader
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
FONT_PATH = BASE_DIR / "Vazirmatn-Bold.ttf"

DROP_DIR = Path(os.path.expanduser("~/Desktop/ویدیوهای گوگل ویدز"))
ARCHIVE_DIR = DROP_DIR / "_منتشر_شده"

DEFAULT_VIRAL_TITLES = [
    ("حقيقة مرعبة لم تكن تعرفها! ⚠️ ما الذي ينتظر البشرية؟ #shorts #islam", "حقيقة مرعبة ستصدمك! ⚠️"),
    ("سر عظيم من أسرار القرآن الكريم يغير حياتك 🌿✨ #shorts #quran", "سر قرآني عظيم 🌿✨"),
    ("علامات الساعة الكبرى التي ظهرت بالفعل أمام أعيننا ⚡ #shorts #علامات_الساعة", "علامات الساعة الكبرى ⚠️"),
    ("تلاوة خاشعة تدمع لها العيون وتبكي القلوب 🕊️🤍 #shorts #راحة_نفسية", "تلاوة خاشعة تريح القلب 🕊️"),
    ("هل اقترب خروج المسيح الدجال؟ الدلائل النبوية الحاسمة ⚠️ #shorts #دجال", "هل اقترب خروج الدجال؟ ⚠️"),
    ("ماذا يحدث للروح بعد الموت مباشرة؟ تفاصيل تقشعر لها الأبدان ⚡ #shorts", "ماذا يحدث للروح بعد الموت؟ ⚡"),
    ("أعظم ابتلاء في تاريخ الأرض.. كيف تنجو منه؟ 🛡️ #shorts #نصيحة", "أعظم فتنة في تاريخ الأرض 🛡️")
]

def format_rtl(text):
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text

def get_video_info(video_path):
    cmd = [
        FFMPEG_EXE, "-i", str(video_path)
    ]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="replace")
    output = res.stderr
    
    duration = 30.0
    width = 1080
    height = 1920
    
    import re
    # Extract duration
    dur_m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", output)
    if dur_m:
        h_val, m_val, s_val = dur_m.groups()
        duration = int(h_val) * 3600 + int(m_val) * 60 + float(s_val)
        
    # Extract resolution
    res_m = re.search(r"Stream.*Video:.*,\s*(\d{3,4})x(\d{3,4})", output)
    if res_m:
        width = int(res_m.group(1))
        height = int(res_m.group(2))
        
    return duration, width, height

def create_master_thumbnail(video_path, thumbnail_path, title_text, is_vertical=True):
    duration, width, height = get_video_info(video_path)
    seek_time = min(max(duration * 0.25, 1.5), duration - 0.5) if duration > 3 else 1.0
    
    # Extract raw frame
    raw_frame = thumbnail_path.parent / f"raw_frame_{int(time.time())}.jpg"
    cmd = [
        FFMPEG_EXE, "-y",
        "-ss", f"{seek_time:.2f}",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(raw_frame)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if not raw_frame.exists():
        # Fallback to solid image
        img = Image.new("RGB", (1080, 1920) if is_vertical else (1280, 720), (15, 15, 20))
    else:
        img = Image.open(raw_frame).convert("RGB")
        try:
            raw_frame.unlink()
        except Exception:
            pass

    # Color grading
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.15)
    sat = ImageEnhance.Color(img)
    img = sat.enhance(1.20)

    # Size adjustment
    target_size = (1080, 1920) if is_vertical else (1280, 720)
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    w, h = target_size

    # Load Font
    font_size = 56 if is_vertical else 52
    try:
        font = ImageFont.truetype(str(FONT_PATH), font_size)
    except Exception:
        font = ImageFont.load_default()

    rtl_text = format_rtl(title_text)

    if is_vertical:
        # Top banner for 9:16 Shorts
        box_y1 = int(h * 0.10)
        box_y2 = box_y1 + 140
        # Dark vignette behind badge
        draw.rounded_rectangle([40, box_y1, w - 40, box_y2], radius=24, fill=(10, 10, 15, 230), outline=(212, 175, 55), width=4)
        draw.text((w // 2, (box_y1 + box_y2) // 2), rtl_text, font=font, fill=(255, 255, 255), anchor="mm")
    else:
        # Bottom/Top banner for 16:9 Landscape
        box_y1 = int(h * 0.76)
        box_y2 = box_y1 + 120
        draw.rounded_rectangle([60, box_y1, w - 60, box_y2], radius=20, fill=(10, 10, 15, 235), outline=(220, 20, 60), width=4)
        draw.text((w // 2, (box_y1 + box_y2) // 2), rtl_text, font=font, fill=(255, 255, 255), anchor="mm")

    img.save(thumbnail_path, "JPEG", quality=95)
    return thumbnail_path

def set_youtube_thumbnail(video_id, thumbnail_path):
    try:
        token_path = BASE_DIR / "token_quran.pickle"
        with open(token_path, "rb") as f:
            creds = pickle.load(f)
        youtube = build("youtube", "v3", credentials=creds)
        req = youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
        )
        res = req.execute()
        print(f"  ✓ Thumbnail applied directly to YouTube ({res.get('kind', 'OK')})")
        return True
    except Exception as e:
        print(f"  ⚠️ Warning setting thumbnail: {e}")
        return False

def process_video_file(video_path: Path):
    print("=" * 70)
    print(f"🎬 Processing Video: {video_path.name}")
    print("=" * 70)

    duration, width, height = get_video_info(video_path)
    is_vertical = height >= width or duration <= 60
    print(f"  Duration: {duration:.1f}s | Resolution: {width}x{height} | Vertical/Shorts: {is_vertical}")

    # Clean filename
    stem = video_path.stem.replace("_", " ").replace("-", " ").strip()
    
    # Check if custom name provided or fallback to viral titles
    if len(stem) > 6 and not any(w in stem.lower() for w in ["video", "vid", "untitled", "google", "output", "render"]):
        base_title = stem
        hook_badge = base_title[:35]
        full_title = f"{base_title} ⚠️ | وثائقي مؤثر #shorts" if is_vertical else f"{base_title} | وثائقي رسمي"
    else:
        import random
        full_title, hook_badge = random.choice(DEFAULT_VIRAL_TITLES)

    print(f"  Title: {full_title}")
    print(f"  Hook Badge: {hook_badge}")

    # Check if user provided their own custom thumbnail (from Gemini or elsewhere)
    user_thumb = None
    possible_thumbs = [
        video_path.with_suffix('.jpg'),
        video_path.with_suffix('.png'),
        video_path.parent / f"{video_path.stem}_thumb.jpg",
        video_path.parent / f"{video_path.stem}_thumb.png",
        video_path.parent / "thumbnail.jpg",
        video_path.parent / "thumbnail.png",
        video_path.parent / "thumb.jpg",
        video_path.parent / "thumb.png",
        video_path.parent / "cover.jpg",
        video_path.parent / "cover.png",
    ]
    for pt in possible_thumbs:
        if pt.exists() and pt.is_file():
            user_thumb = pt
            break

    # If no exact match, look for any standalone jpg/png in DROP_DIR
    if not user_thumb:
        for p in video_path.parent.iterdir():
            if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png"] and not p.name.startswith("_") and not p.name.startswith("thumb_"):
                user_thumb = p
                break

    if user_thumb:
        thumb_path = user_thumb
        print(f"  🎨 Using User's Custom Gemini Thumbnail: {thumb_path.name}")
    else:
        # Generate master thumbnail from frame
        thumb_path = video_path.parent / f"thumb_{video_path.stem}.jpg"
        create_master_thumbnail(video_path, thumb_path, hook_badge, is_vertical=is_vertical)
        print(f"  ✓ Generated Master Thumbnail: {thumb_path.name}")

    # SEO Description
    description = (
        f"🌿 {full_title}\n\n"
        "✨ تلاوة وعبر ومواعظ إيمانية تهز القلوب وتوقظ الغافلين. إن في ذلك لذكرى لمن كان له قلب أو ألقى السمع وهو شهيد.\n\n"
        "🔔 اشترك في قناة «نور القرآن | The Holy Light» وفعل زر التنبيهات ليصلك كل جديد يومياً.\n"
        "🤍 لا تنس مشاركة الفيديو مع أهلك وأصدقائك ليكون صدقة جارية لك ولهم.\n\n"
        "─── ⋆⋅☆⋅⋆ ───\n"
        "#Shorts #القرآن #اسلاميات #تلاوة_خاشعة #موعظة #حقيقة #دجال #قصص_الأنبياء #Islamic #Quran"
    )

    tags = [
        "قرآن كريم", "تلاوة خاشعة", "موعظة", "قصص اسلامية", "المسيح الدجال",
        "علامات الساعة", "Shorts", "Viral", "Quran", "Islam", "Faith", "Eschatology"
    ]

    # Upload via youtube_uploader
    print("\n  [Uploading] Transmitting to YouTube channel 'نور القرآن | The Holy Light'...")
    upload_res = youtube_uploader.upload_short(
        channel_key="quran",
        video_path=str(video_path),
        title=full_title,
        description=description,
        tags=tags
    )

    video_id = upload_res.get("video_id") or upload_res.get("id")
    video_url = upload_res.get("url", f"https://youtu.be/{video_id}")

    if video_id:
        print(f"  🎉 Published Successfully: {video_url}")
        # Apply custom thumbnail
        set_youtube_thumbnail(video_id, thumb_path)

        # Move to archive folder
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        dest_video = ARCHIVE_DIR / video_path.name
        dest_thumb = ARCHIVE_DIR / thumb_path.name
        
        # If destination already exists, add timestamp
        if dest_video.exists():
            dest_video = ARCHIVE_DIR / f"{video_path.stem}_{int(time.time())}{video_path.suffix}"
        
        shutil.move(str(video_path), str(dest_video))
        if thumb_path.exists():
            shutil.move(str(thumb_path), str(dest_thumb))
            
        print(f"  📦 Moved to Archive: {dest_video.name}")
        return True, video_url
    else:
        print("  ❌ Upload failed or returned no video ID.")
        return False, None

def scan_and_publish():
    DROP_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    valid_extensions = {".mp4", ".mov", ".mkv", ".webm"}
    videos = [
        p for p in DROP_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in valid_extensions and not p.name.startswith("_") and not p.name.startswith(".")
    ]

    if not videos:
        print(f"\n📂 هیچ ویدیوی جدیدی در پوشه دسکتاپ پیدا نشد:")
        print(f"   مسیر: {DROP_DIR}")
        print("   هر زمان ویدیویی در این پوشه بیندازید، این اسکریپت آن را با تامبنیل و تنظیمات کامل در یوتیوب منتشر می‌کند.\n")
        return []

    print(f"\n🚀 {len(videos)} ویدیوی جدید در پوشه پیدا شد. آغاز فرآیند انتشار خودکار...\n")
    results = []
    for v in videos:
        success, url = process_video_file(v)
        if success:
            results.append((v.name, url))
        time.sleep(3) # Small safety break between multiple uploads

    print("\n" + "=" * 70)
    print("✨ گزارش نهایی آپلود اتوپایلوت:")
    for name, url in results:
        print(f"  • {name} ➜ {url}")
    print("=" * 70 + "\n")
    return results

if __name__ == "__main__":
    scan_and_publish()
