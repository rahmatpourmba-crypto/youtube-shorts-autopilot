import os
import sys
import json
import time
import re
import datetime
import urllib.request
from pathlib import Path

# Ensure UTF-8 output on all consoles
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "used_viral_reels.json"
OUTPUT_DIR = BASE_DIR / "output" / "viral_quran_reels"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

from instagram_publisher import get_instagram_client
from youtube_uploader import upload_short, CHANNELS

# =====================================================================
# ELITE VIRAL RECITERS POOL (Ultra-High Engagement on Instagram)
# =====================================================================
RECITERS_CONFIG = {
    "yasser": {
        "name_ar": "الشيخ ياسر الدوسري",
        "name_en": "Sheikh Yasser Al-Dosari",
        "tags": ["ياسر_الدوسري", "الشيخ_ياسر_الدوسري", "تلاوات_ياسر_الدوسري"],
        "keywords": ["دوسري", "الدوسري", "yasser", "yasseraldossary"],
        "default_title": "تلاوة خاشعة مبكية | الشيخ ياسر الدوسري 🕊️✨"
    },
    "youssef": {
        "name_ar": "القارئ يوسف صقير",
        "name_en": "Youssef Saghir",
        "tags": ["يوسف_صقير", "يوسف_الصقير", "تلاوات_يوسف_صقير"],
        "keywords": ["يوسف صقير", "صقير", "الصقير", "youssef"],
        "default_title": "تلاوة تأسر القلوب بصوت القارئ يوسف صقير 🕊️✨"
    },
    "luhaidan": {
        "name_ar": "الشيخ محمد اللحيدان",
        "name_en": "Muhammad Al-Luhaidan",
        "tags": ["محمد_اللحيدان", "الشيخ_محمد_اللحيدان", "تلاوات_محمد_اللحيدان"],
        "keywords": ["لحيدان", "اللحيدان", "luhaidan"],
        "default_title": "تلاوة خاشعة تهز القلوب | الشيخ محمد اللحيدان 🕊️✨"
    },
    "islam_sobhi": {
        "name_ar": "القارئ إسلام صبحي",
        "name_en": "Islam Sobhi",
        "tags": ["اسلام_صبحي", "إسلام_صبحي", "تلاوات_اسلام_صبحي"],
        "keywords": ["اسلام صبحي", "إسلام صبحي", "sobhi"],
        "default_title": "راحة نفسية لا توصف بصوت إسلام صبحي 🕊️✨"
    },
    "mossad": {
        "name_ar": "القارئ عبدالرحمن مسعد",
        "name_en": "Abdul Rahman Mossad",
        "tags": ["عبدالرحمن_مسعد", "عبد_الرحمن_مسعد", "تلاوات_عبدالرحمن_مسعد"],
        "keywords": ["عبدالرحمن مسعد", "مسعد", "mossad"],
        "default_title": "أرح سمعك وقلبك | القارئ عبدالرحمن مسعد 🕊️✨"
    },
    "raad": {
        "name_ar": "القارئ رعد الكردي",
        "name_en": "Raad Al-Kurdi",
        "tags": ["رعد_الكردي", "رعد_محمد_الكردي", "تلاوات_رعد_الكردي"],
        "keywords": ["رعد الكردي", "الكردي", "raad"],
        "default_title": "تلاوة هادئة مريحة للأعصاب | رعد الكردي 🕊️✨"
    }
}

# 6-SLOT DAILY ROTATION: Exactly 3 Yasser Al-Dosari + 3 Other Elite Reciters
def get_reciter_key_for_current_slot() -> str:
    """
    Determines which reciter to target based on current Tehran Hour:
    - 06:00 IRST (Slot 1): Yasser Al-Dosari (Fajr / Morning Peace)
    - 10:00 IRST (Slot 2): Youssef Saghir (Mid-Morning Uplift)
    - 14:00 IRST (Slot 3): Yasser Al-Dosari (Afternoon Focus)
    - 18:00 IRST (Slot 4): Muhammad Al-Luhaidan / Islam Sobhi (Sunset / Maghrib)
    - 22:00 IRST (Slot 5): Yasser Al-Dosari (Night Calm / Bedtime)
    - 02:00 IRST (Slot 6): Abdul Rahman Mossad / Raad Al-Kurdi (Tahajjud / Global)
    """
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    tehran_now = utc_now + datetime.timedelta(hours=3, minutes=30)
    hour = tehran_now.hour

    if 4 <= hour < 8:
        return "yasser"
    elif 8 <= hour < 12:
        return "youssef"
    elif 12 <= hour < 16:
        return "yasser"
    elif 16 <= hour < 20:
        return "luhaidan"
    elif 20 <= hour < 24:
        return "yasser"
    else: # 0 <= hour < 4
        return "mossad"

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def clean_arabic_title(caption: str, reciter_info: dict) -> str:
    """
    Extracts a clean, high-CTR YouTube Short title from the original Instagram caption.
    """
    if not caption:
        return f"{reciter_info['default_title']} #Quran #Shorts"
    
    # Remove excessive hashtags from title
    lines = [l.strip() for l in caption.splitlines() if l.strip()]
    first_line = lines[0] if lines else ""
    cleaned = re.sub(r'#\S+', '', first_line).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    if len(cleaned) < 15:
        cleaned = reciter_info["default_title"]
    
    full_title = f"{cleaned} | {reciter_info['name_ar']} #Shorts #Quran"
    return full_title[:100]

def find_and_download_viral_reel(min_views: int = 100000, max_duration: float = 49.9, target_reciter_key: str = None):
    """
    Finds top Instagram reels for the targeted reciter with views > 100k,
    duration < 50 seconds, downloads the exact original video file without modification.
    """
    if not target_reciter_key or target_reciter_key not in RECITERS_CONFIG:
        target_reciter_key = get_reciter_key_for_current_slot()

    reciter = RECITERS_CONFIG[target_reciter_key]
    used_codes = set(load_history())
    cl = get_instagram_client("quran")
    
    candidate_reels = []
    hashtags_to_search = reciter["tags"] + ["تلاوة_خاشعة", "قران_كريم"]

    print("\n" + "=" * 65)
    print(f"=== SEARCHING VIRAL REELS: {reciter['name_ar']} ({reciter['name_en']}) ===")
    print(f"Target Metric: > {min_views:,} views | Duration < 50s | 100% Original Video")
    print("=" * 65)

    for tag in hashtags_to_search:
        print(f"\n[Instagram Query] Searching top viral reels in #{tag}...")
        try:
            medias = cl.hashtag_medias_top(tag, amount=25)
            print(f"  -> Found {len(medias)} candidate top posts.")
            
            for m in medias:
                # Must be a video / reel
                if m.media_type != 2:
                    continue
                if m.code in used_codes:
                    continue

                caption = m.caption_text or ""
                # Ensure it matches reciter's identity
                matched_kw = any(kw.lower() in caption.lower() for kw in reciter["keywords"])
                if not matched_kw:
                    # If searched by generic tag, skip if reciter not mentioned
                    if tag in ["تلاوة_خاشعة", "قران_كريم"]:
                        continue

                # Check duration: STRICTLY LESS THAN 50 SECONDS
                duration = getattr(m, "video_duration", 0)
                if duration and duration >= max_duration:
                    continue

                views = getattr(m, "view_count", 0) or 0
                plays = getattr(m, "play_count", 0) or 0
                likes = m.like_count or 0
                
                # Check metrics: views/plays > 100k, or likes > 4k (correlates to 100k+ plays)
                effective_score = max(views, plays, likes * 25)
                
                print(f"  [Reel {m.code}] Plays: {plays:,} | Views: {views:,} | Likes: {likes:,} | Dur: {duration}s | Score: {effective_score:,}")
                
                if effective_score >= min_views or likes >= 4000:
                    candidate_reels.append({
                        "code": m.code,
                        "pk": m.pk,
                        "video_url": str(m.video_url),
                        "caption": caption,
                        "plays": plays,
                        "views": views,
                        "likes": likes,
                        "duration": duration,
                        "score": effective_score,
                        "reciter": reciter
                    })
                    print(f"  🔥 MATCH FOUND: Reel {m.code} meets >100k threshold & <50s duration!")

        except Exception as e:
            print(f"  [Warning] Tag #{tag} query error: {e}")
            time.sleep(2)

    # Sort candidates by score descending (highest views first)
    candidate_reels.sort(key=lambda x: x["score"], reverse=True)

    # Fallback to general pool if specific reciter had no unplayed match under 50s
    if not candidate_reels:
        print(f"\n[Notice] Checking top ranked reels for {reciter['name_ar']} under 50s...")
        for tag in reciter["tags"]:
            try:
                top_m = cl.hashtag_medias_top(tag, amount=15)
                for m in top_m:
                    if m.media_type == 2 and m.code not in used_codes:
                        dur = getattr(m, "video_duration", 0)
                        if dur and dur >= max_duration:
                            continue
                        candidate_reels.append({
                            "code": m.code,
                            "pk": m.pk,
                            "video_url": str(m.video_url),
                            "caption": m.caption_text or "",
                            "plays": getattr(m, "play_count", 0),
                            "views": getattr(m, "view_count", 0),
                            "likes": m.like_count or 0,
                            "duration": dur,
                            "score": m.like_count or 0,
                            "reciter": reciter
                        })
                candidate_reels.sort(key=lambda x: x["score"], reverse=True)
            except Exception:
                pass

    if not candidate_reels:
        print(f"[Fallback] Trying Yasser Al-Dosari master catalog...")
        if target_reciter_key != "yasser":
            return find_and_download_viral_reel(min_views=min_views, max_duration=max_duration, target_reciter_key="yasser")
        print("[Error] No new viral reels found matching criteria (<50s, >100k views).")
        return None

    chosen = candidate_reels[0]
    rec = chosen["reciter"]
    print("\n" + "=" * 65)
    print(f"★ SELECTED VIRAL REEL: {chosen['code']} | Reciter: {rec['name_ar']}")
    print(f"Estimated Impact: {chosen['score']:,} engagements | Likes: {chosen['likes']:,}")
    print("=" * 65)

    target_video_file = OUTPUT_DIR / f"quran_{chosen['code']}.mp4"
    print(f"Downloading original video from Instagram CDN...")
    req = urllib.request.Request(
        chosen["video_url"],
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req, timeout=30) as resp, open(target_video_file, 'wb') as f_out:
        f_out.write(resp.read())

    print(f"✓ Original Reel downloaded: {target_video_file.name} ({target_video_file.stat().st_size // 1024} KB)")

    title = clean_arabic_title(chosen["caption"], rec)
    description = (
        f"{title}\n\n"
        f"تلاوة خاشعة مباركة بصوت {rec['name_ar']} حفظه الله.\n\n"
        f"اللهم اجعل القرآن الكريم ربيع قلوبنا ونور صدورنا وجلاء أحزاننا وذهاب همومنا.\n\n"
        f"• الأصل من تلاوات منصات التواصل الأكثر انتشاراً وتأثيراً (High Viral Reach).\n\n"
        f"#{rec['name_ar'].replace(' ', '_')} #القرآن_الكريم #تلاوة_خاشعة #قرآن #Shorts #Islam #Quran"
    )
    tags = [
        rec["name_ar"],
        "القرآن الكريم",
        "تلاوة خاشعة",
        "قران",
        rec["name_en"].lower(),
        "quran",
        "quran recitation",
        "shorts",
        "islam"
    ]

    return {
        "video": str(target_video_file),
        "code": chosen["code"],
        "title": title,
        "description": description,
        "tags": tags,
        "reciter": rec["name_ar"]
    }

def main():
    print("=================================================================")
    print("=== MULTI-RECITER VIRAL REEL DISPATCHER (EVERY 4 HOURS) ===")
    print("3x Sheikh Yasser Al-Dosari + 3x Other Elite Reciters Daily")
    print("High View Count > 100,000 | Duration < 50s | Direct 100% Unmodified")
    print("=================================================================")

    reel_data = find_and_download_viral_reel(min_views=100000, max_duration=49.9)
    if not reel_data:
        print("[Abort] Could not fetch eligible viral reel.")
        sys.exit(1)

    print(f"\n[YouTube Upload] Uploading directly to {CHANNELS['quran']['name']}...")
    upload_res = upload_short(
        channel_key="quran",
        video_path=reel_data["video"],
        title=reel_data["title"],
        description=reel_data["description"],
        tags=reel_data["tags"],
        category_id="22"
    )

    if upload_res:
        history = load_history()
        history.append(reel_data["code"])
        save_history(history)
        vid_id = upload_res.get("video_id") or upload_res.get("id", "")
        print(f"\n🎉 SUCCESS: Viral Reel {reel_data['code']} uploaded to YouTube Quran Channel!")
        print(f"URL: https://youtube.com/shorts/{vid_id}")
    else:
        print("[Upload Notice] YouTube upload did not return an ID.")

if __name__ == "__main__":
    main()
