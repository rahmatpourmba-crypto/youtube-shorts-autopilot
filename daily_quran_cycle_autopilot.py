import os
import sys
import time
import socket
import subprocess
from pathlib import Path
from datetime import datetime, time as dtime, timezone, timedelta
import imageio_ffmpeg

# Fix console encoding on Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Fast DNS cache to prevent local DNS timeouts
DNS_CACHE = {
    'youtube.googleapis.com': '172.217.112.4',
    'www.googleapis.com': '172.217.116.4',
    'oauth2.googleapis.com': '74.125.133.95',
}
_orig_getaddrinfo = socket.getaddrinfo
def fast_getaddrinfo(host, port, *args, **kwargs):
    if host in DNS_CACHE:
        return _orig_getaddrinfo(DNS_CACHE[host], port, *args, **kwargs)
    return _orig_getaddrinfo(host, port, *args, **kwargs)
socket.getaddrinfo = fast_getaddrinfo

os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

import youtube_uploader

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Authoritative Original 36s Master Video (124,635 views viral hit)
MASTER_VIDEO = BASE_DIR / "assets" / "videos" / "MASTER_YASSER_VIRAL_36S.mp4"
OUTPUT_BASE = BASE_DIR / "output" / "original_yasser_cycle_slots"
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

# 7 Publishing Slots: Every 2 Hours from 11:00 AM to 11:00 PM
TARGET_SLOTS = [
    (11, 0,  "اكتب شيء تؤجر عليه | الشيخ ياسر الدوسري #Shorts #Quran", 1.000, 1.000),
    (13, 0,  "اكتب شيء تؤجر عليه ✨ | الشيخ ياسر الدوسري #Shorts #Quran", 1.005, 1.010),
    (15, 0,  "تلاوة تهز القلوب 🤍 | اكتب شيء تؤجر عليه | الشيخ ياسر الدوسري #Shorts", 1.008, 1.015),
    (17, 0,  "اكتب شيء تؤجر عليه 🌿 | تلاوة خاشعة تريح القلب | الشيخ ياسر الدوسري #Shorts", 1.010, 1.012),
    (19, 0,  "راحة نفسية لا توصف 🕊️ | اكتب شيء تؤجر عليه | الشيخ ياسر الدوسري #Shorts", 1.006, 1.014),
    (21, 0,  "اكتب شيء تؤجر عليه | صوت يدخل القلب مباشرة 🤍 | الشيخ ياسر الدوسري #Quran", 1.012, 1.018),
    (23, 0,  "تلاوة خاشعة تسكن الروح ✨ | اكتب شيء تؤجر عليه | الشيخ ياسر الدوسري #Shorts", 1.007, 1.012)
]

DESCRIPTION = """اكتب شيء تؤجر عليه | الشيخ ياسر الدوسري #Shorts #Quran

تلاوة خاشعة مباركة تأسر القلوب والأسماع بصوت فضيلة الشيخ الدكتور ياسر الدوسري حفظه الله ورعاه من الحرم المكي الشريف.

قال الله تعالى: ﴿الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾

اللهم اجعل القرآن الكريم ربيع قلوبنا، ونور صدورنا، وجلاء أحزاننا، وذهاب همومنا وغمومنا.

• الأصل من تلاوات منصات التواصل الأكثر انتشاراً وتأثيراً (High Viral Reach).

#الشيخ_ياسر_الدوسري #القرآن_الكريم #تلاوة_خاشعة #قرآن #Shorts #Islam #Quran #سورة"""

TAGS = [
    "islam", "quran", "quran recitation", "sheikh yasser al-dosari", 
    "shorts", "الشيخ ياسر الدوسري", "القرآن الكريم", "تلاوة خاشعة", 
    "قران", "اكتب شيء تؤجر عليه", "ياسر الدوسري"
]

PINNED_COMMENT = "سبحان الله وبحمده، سبحان الله العظيم 🤍 اكتب شيء تؤجر عليه في التعليقات واكسب حسنة جارية ✨"


def prepare_variant(slot_idx: int, contrast: float, saturation: float) -> Path:
    out_file = OUTPUT_BASE / f"slot_{slot_idx+1}_original_yasser_36s.mp4"
    if out_file.exists() and out_file.stat().st_size > 1000:
        return out_file

    if contrast == 1.0 and saturation == 1.0:
        cmd = [
            FFMPEG_EXE, "-y",
            "-i", str(MASTER_VIDEO),
            "-c:v", "libx264",
            "-crf", "17",
            "-preset", "veryfast",
            "-c:a", "copy",
            "-metadata", f"comment=NourAlQuran_{slot_idx}_{int(time.time())}",
            str(out_file)
        ]
    else:
        cmd = [
            FFMPEG_EXE, "-y",
            "-i", str(MASTER_VIDEO),
            "-vf", f"eq=contrast={contrast}:saturation={saturation}",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "17",
            "-c:a", "copy",
            "-metadata", f"comment=NourAlQuran_{slot_idx}_{int(time.time())}",
            str(out_file)
        ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        return MASTER_VIDEO
    return out_file


def run_cycle():
    if not MASTER_VIDEO.exists():
        print(f"❌ Master video file not found at: {MASTER_VIDEO}")
        return

    now_local = datetime.now().astimezone()
    today = now_local.date()

    print("=" * 75)
    print("⭐ اتوماسیون انتشار اصل ویدیوی ۳۶ ثانیه‌ای: اكتب شيء تؤجر عليه - الشيخ ياسر الدوسري")
    print(f"⏰ ساعت محلی سیستم: {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("📅 چرخه: هر ۲ ساعت یکبار بین ساعت ۱۱:۰۰ صبح تا ۲۳:۰۰ شب (۷ نوبت در روز)")
    print("=" * 75)

    results = []

    for idx, (target_h, target_m, title, contrast, saturation) in enumerate(TARGET_SLOTS):
        slot_dt_local = datetime.combine(today, dtime(target_h, target_m), tzinfo=now_local.tzinfo)

        # If this slot has already passed today, schedule for tomorrow
        if slot_dt_local <= now_local:
            slot_dt_local += timedelta(days=1)

        slot_dt_utc = slot_dt_local.astimezone(timezone.utc)
        publish_at_iso = slot_dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        schedule_label = f"{slot_dt_local.strftime('%Y-%m-%d %I:%M %p')} local ({publish_at_iso} UTC)"

        print(f"\n[نوبت {idx+1}/7] آماده‌سازی برای زمانبندی: {schedule_label}")
        print(f"  عنوان: {title}")

        # Prepare variant of original 36s master video
        variant_file = prepare_variant(idx, contrast, saturation)

        uploaded = False
        for attempt in range(1, 3):
            try:
                up_res = youtube_uploader.upload_short(
                    channel_key="quran",
                    video_path=str(variant_file),
                    title=title,
                    description=DESCRIPTION,
                    tags=TAGS,
                    pinned_comment=PINNED_COMMENT,
                    publish_at=publish_at_iso
                )
                if up_res and (up_res.get("video_id") or up_res.get("id")):
                    vid_id = up_res.get("video_id") or up_res.get("id")
                    url = up_res.get("url", f"https://youtube.com/shorts/{vid_id}")
                    print(f"  ✓ نوبت {idx+1} با موفقیت در یوتیوب زمانبندی شد: {url}")
                    results.append((idx+1, title, url, slot_dt_local.strftime('%I:%M %p')))
                    uploaded = True
                    break
                else:
                    print(f"  ⚠️ تلاش {attempt}: محدودیت سهمیه روزانه یا پاسخ نامعتبر.")
            except Exception as e:
                print(f"  ⚠️ خطا در تلاش {attempt}: {e}")
            time.sleep(3)

        if not uploaded:
            print(f"  ⚠️ سقف روزانه آپلود یوتیوب (Daily Upload Limit) برای امروز پر است. این نوبت در چرخه بعدی با باز شدن سهمیه زمانبندی خواهد شد.")
            break

        time.sleep(3)

    print("\n" + "=" * 75)
    print("✨ گزارش وضعیت چرخه انتشار اصل ویدیو:")
    for num, t, url, timing in results:
        print(f"  نوبت {num} ({timing}): {url}")
    print("=" * 75)


if __name__ == "__main__":
    run_cycle()
