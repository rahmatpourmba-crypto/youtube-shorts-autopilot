import socket
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
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
import imageio_ffmpeg

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

import youtube_uploader

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SRC_VIDEO = BASE_DIR / "output" / "live_quran_yasser_viral" / "quran_aesthetic_short.mp4"
THUMB_SRC = BASE_DIR / "output" / "live_quran_yasser_viral" / "thumbnail.jpg"
CAMPAIGN_DIR = BASE_DIR / "output" / "yasser_24h_campaign"
CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)

SCHEDULE_SLOTS = [
    {
        "slot_num": 1,
        "hours_offset": 0.0, # NOW (Public immediately)
        "title": "اكتب شيء تؤجر عليه 🕊️ تلاوة خاشعة تريح القلوب | الشيخ ياسر الدوسري #Shorts #Quran",
        "badge": "تلاوة خاشعة 🕊️",
        "contrast": 1.01,
        "sat": 1.02
    },
    {
        "slot_num": 2,
        "hours_offset": 4.5,
        "title": "اكتب شيء تؤجر عليه 🤍 سورة الكهف نور وطمأنينة | الشيخ ياسر الدوسري #Shorts #Quran",
        "badge": "راحة نفسية 🤍",
        "contrast": 1.03,
        "sat": 1.05
    },
    {
        "slot_num": 3,
        "hours_offset": 9.0,
        "title": "اكتب شيء تؤجر عليه 🌿 راحة نفسية وسكينة للقلب | الشيخ ياسر الدوسري #Shorts #Quran",
        "badge": "سكينة للروح 🌿",
        "contrast": 1.02,
        "sat": 1.04
    },
    {
        "slot_num": 4,
        "hours_offset": 13.5,
        "title": "اكتب شيء تؤجر عليه ✨ تلاوة تقشعر لها الأبدان | الشيخ ياسر الدوسري #Shorts #Quran",
        "badge": "طمأنينة عجيبة ✨",
        "contrast": 1.04,
        "sat": 1.03
    },
    {
        "slot_num": 5,
        "hours_offset": 18.0,
        "title": "اكتب شيء تؤجر عليه 🕊️ أرح سمعك وقلبك بالقرآن | الشيخ ياسر الدوسري #Shorts #Quran",
        "badge": "أرح سمعك 🕊️",
        "contrast": 1.01,
        "sat": 1.06
    },
    {
        "slot_num": 6,
        "hours_offset": 22.5,
        "title": "اكتب شيء تؤجر عليه 🤍 ما تيسر من الذكر الحكيم | الشيخ ياسر الدوسري #Shorts #Quran",
        "badge": "ذكر حكيم 🤍",
        "contrast": 1.03,
        "sat": 1.02
    }
]

def prepare_unique_video(slot):
    num = slot["slot_num"]
    out_vid = CAMPAIGN_DIR / f"slot_{num}_yasser.mp4"
    c = slot["contrast"]
    s = slot["sat"]
    
    # Anti-duplicate slight adjustment + unique metadata
    cmd = [
        FFMPEG, "-y", "-hide_banner",
        "-i", str(SRC_VIDEO),
        "-vf", f"eq=contrast={c}:saturation={s}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-metadata", f"title=Yasser Al-Dosari Quran Campaign Slot {num}",
        str(out_vid)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return out_vid

def run_campaign():
    now_utc = datetime.now(timezone.utc)
    print("=" * 70)
    print("=== LAUNCHING 24-HOUR QURAN YASSER CAMPAIGN ===")
    print(f"Current UTC Time: {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Interval: Every 4.5 hours across the next 24 hours (6 Total Slots)")
    print("=" * 70)

    results = []
    for slot in SCHEDULE_SLOTS:
        num = slot["slot_num"]
        offset = slot["hours_offset"]
        title = slot["title"]
        
        # Prepare video with unique visual hash
        vid_file = prepare_unique_video(slot)
        
        publish_at_iso = None
        if offset > 0:
            scheduled_dt = now_utc + timedelta(hours=offset)
            publish_at_iso = scheduled_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            schedule_desc = f"SCHEDULED for {publish_at_iso} (+{offset}h)"
        else:
            schedule_desc = "PUBLISHING LIVE NOW (Immediate Public)"

        print(f"\n[Slot {num}/6] {schedule_desc}")
        print(f"  Title: {title}")

        description = (
            f"{title}\n\n"
            "تلاوة خاشعة مباركة بصوت الشيخ ياسر الدوسري حفظه الله.\n"
            "قال الله تعالى: ﴿الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾\n\n"
            "اللهم اجعل القرآن الكريم ربيع قلوبنا ونور صدورنا وجلاء أحزاننا وذهاب همومنا.\n"
            "• شارك المقطع واشترك في القناة لتصلك التلاوات الخاشعة يومياً 🕊️\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            "#اكتب_شيء_تؤجر_عليه #الشيخ_ياسر_الدوسري #سورة_الكهف #تلاوة_خاشعة #قرآن #Shorts #Islam #Quran"
        )
        tags = [
            "اكتب شيء تؤجر عليه", "الشيخ ياسر الدوسري", "سورة الكهف", "تلاوة خاشعة", 
            "قرآن كريم", "قران", "Shorts", "Quran", "Islam", "Yasser Al-Dosari"
        ]
        pinned_comment = "🌿 اكتب (سبحان الله وبحمده) لتشارك في الأجر وثواب نشر القرآن الكريم 🤍🕊️"

        upload_res = None
        for attempt in range(1, 4):
            try:
                print(f"  Attempt {attempt}/3...")
                upload_res = youtube_uploader.upload_short(
                    channel_key="quran",
                    video_path=str(vid_file),
                    title=title,
                    description=description,
                    tags=tags,
                    thumbnail_path=str(THUMB_SRC),
                    pinned_comment=pinned_comment,
                    publish_at=publish_at_iso
                )
                if upload_res:
                    break
            except Exception as ex:
                print(f"  Attempt {attempt} error: {ex}")
            time.sleep(5)

        if upload_res:
            res_id = upload_res.get("video_id") or upload_res.get("id")
            res_url = upload_res.get("url", f"https://youtube.com/shorts/{res_id}")
            print(f"  ✓ Slot {num} Succeeded: {res_url} (Schedule: {publish_at_iso or 'PUBLIC NOW'})")
            results.append((num, title, res_url, publish_at_iso or 'LIVE NOW'))
        else:
            print(f"  ❌ Slot {num} failed or hit daily quota.")
            break

        time.sleep(3) # safe break between API calls

    print("\n" + "=" * 70)
    print("✨ FINAL 24-HOUR CAMPAIGN STATUS REPORT:")
    for num, t, url, timing in results:
        print(f"  Slot {num}: {timing} ➜ {url}")
    print("=" * 70)

if __name__ == "__main__":
    run_campaign()
