import os
import sys
import time
import socket
from pathlib import Path
from datetime import datetime, timezone, timedelta

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

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

import quran_pinterest_aesthetic_engine as qe
import youtube_uploader

DAILY_CYCLES = [
    # Day A (Core Yasser Favorites)
    [
        (0, "سورة يوسف", "اكتب شيء تؤجر عليه 🕊️ سورة يوسف | الشيخ ياسر الدوسري #Shorts #Quran", "🌿 اكتب (سبحان الله) لتشارك في الأجر 🤍"),
        (3, "سورة مريم", "اكتب شيء تؤجر عليه 🤍 سورة مريم تفيض بالسكينة | الشيخ ياسر الدوسري #Shorts #Quran", "🕊️ اكتب (لا إله إلا الله) لتملأ قلبك طمأنينة ✨"),
        (5, "سورة الرحمن", "اكتب شيء تؤجر عليه 🌸 سورة الرحمن عروس القرآن | الشيخ ياسر الدوسري #Shorts #Quran", "🌸 اكتب (الحمدلله رب العالمين) اعترافاً بفضل الله 🤍"),
        (2, "سورة الملك", "اكتب شيء تؤجر عليه 🌌 سورة الملك المنجية من عذاب القبر | الشيخ ياسر الدوسري #Shorts #Quran", "🌌 اكتب (أستغفر الله العظيم) لعلها تكون منجية 🕊️"),
        (1, "سورة الكهف", "اكتب شيء تؤجر عليه 🌿 سورة الكهف نور وطمأنينة | الشيخ ياسر الدوسري #Shorts #Quran", "🌿 اكتب (اللهم صل وسلم على نبينا محمد) 🤍")
    ],
    # Day B (Spiritual Reflection & Peace)
    [
        (4, "سورة إبراهيم", "اكتب شيء تؤجر عليه 🕋 دعاء الخليل إبراهيم عليه السلام | الشيخ ياسر الدوسري #Shorts #Quran", "🕋 اكتب (رب اجعل هذا البلد آمناً) 🤲"),
        (0, "سورة يوسف", "اكتب شيء تؤجر عليه 🕊️ أحسن القصص ما تيسر من سورة يوسف | الشيخ ياسر الدوسري #Shorts #Quran", "🤍 اكتب (سبحان الله وبحمده) لتشارك الأجر 🌿"),
        (2, "سورة الملك", "اكتب شيء تؤجر عليه 🌌 أرح سمعك وقلبك بسورة الملك | الشيخ ياسر الدوسري #Shorts #Quran", "🌌 اكتب (تبارك الله أحسن الخالقين) 🕊️"),
        (5, "سورة الرحمن", "اكتب شيء تؤجر عليه 🌸 تلاوة خاشعة تهز القلوب لسورة الرحمن | الشيخ ياسر الدوسري #Shorts #Quran", "🌸 اكتب (الحمدلله) حمداً كثيراً طيباً 🤍"),
        (3, "سورة مريم", "اكتب شيء تؤجر عليه 🕊️ راحة نفسية تفوق الوصف.. سورة مريم | الشيخ ياسر الدوسري #Shorts #Quran", "🕊️ اكتب (يا رب) في تعليق 🌿")
    ]
]

def run_daily_cycle(cycle_id=0):
    now_utc = datetime.now(timezone.utc)
    items = DAILY_CYCLES[cycle_id % len(DAILY_CYCLES)]
    
    print("=" * 75)
    print(f"=== RUNNING AUTONOMOUS 24-HOUR QURAN CYCLE (Batch {cycle_id}) ===")
    print(f"Base UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("Cadence: 5 Slots spaced every 4.5 hours across 24h")
    print("=" * 75)

    out_base = BASE_DIR / "output" / f"cycle_batch_{int(time.time())}"
    out_base.mkdir(parents=True, exist_ok=True)

    results = []
    offsets = [0.0, 4.5, 9.0, 13.5, 18.0]

    for idx, (story_idx, surah, title, pinned) in enumerate(items):
        offset = offsets[idx]
        slot_dir = out_base / f"slot_{idx+1}_{surah.replace(' ', '_')}"
        slot_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n[Slot {idx+1}/5] Preparing {surah} (Offset: +{offset}h)...")
        rendered = qe.render_quran_aesthetic_short(story_idx, slot_dir)
        vid_path = rendered["video"]
        thumb_path = rendered["thumbnail"]

        publish_at_iso = None
        if offset > 0:
            target_dt = now_utc + timedelta(hours=offset)
            publish_at_iso = target_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            schedule_label = f"SCHEDULED for {publish_at_iso} (+{offset}h)"
        else:
            schedule_label = "PUBLISHING LIVE PUBLIC NOW"

        print(f"  Timing: {schedule_label}")
        print(f"  Title: {title}")

        description = (
            f"{title}\n\n"
            f"تلاوة خاشعة عطرة مباركة من {surah} بصوت الشيخ ياسر الدوسري حفظه الله.\n"
            "قال الله تعالى: ﴿الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾\n\n"
            "اللهم اجعل القرآن الكريم ربيع قلوبنا ونور صدورنا وجلاء أحزاننا وذهاب همومنا.\n"
            "• شارك المقطع مع من تحب واشترك في القناة لتصلك التلاوات الخاشعة يومياً 🤍\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            f"#اكتب_شيء_تؤجر_عليه #الشيخ_ياسر_الدوسري #{surah.replace(' ', '_')} #تلاوة_خاشعة #قرآن #Shorts #Islam #Quran"
        )
        tags = [
            "اكتب شيء تؤجر عليه", "الشيخ ياسر الدوسري", surah, "تلاوة خاشعة", 
            "قرآن كريم", "قران", "Shorts", "Quran", "Islam", "Yasser Al-Dosari"
        ]

        uploaded = False
        for attempt in range(1, 4):
            try:
                print(f"  Uploading (Attempt {attempt}/3)...")
                up_res = youtube_uploader.upload_short(
                    channel_key="quran",
                    video_path=str(vid_path),
                    title=title,
                    description=description,
                    tags=tags,
                    thumbnail_path=str(thumb_path),
                    pinned_comment=pinned,
                    publish_at=publish_at_iso
                )
                if up_res:
                    res_id = up_res.get("video_id") or up_res.get("id")
                    url = up_res.get("url", f"https://youtube.com/shorts/{res_id}")
                    print(f"  ✓ Slot {idx+1} Published/Scheduled: {url}")
                    results.append((idx+1, surah, url, schedule_label))
                    uploaded = True
                    break
            except Exception as e:
                print(f"  ⚠️ Attempt {attempt} notice: {e}")
            time.sleep(4)

        if not uploaded:
            print(f"  ❌ Failed Slot {idx+1}")
            break

        time.sleep(3)

    print("\n" + "=" * 75)
    print("✨ DAILY 24-HOUR BATCH COMPLETE:")
    for slot_num, surah_name, url_str, timing_str in results:
        print(f"  Slot {slot_num} ({surah_name}): {timing_str} ➜ {url_str}")
    print("=" * 75)
    return results

if __name__ == "__main__":
    run_daily_cycle(0)
