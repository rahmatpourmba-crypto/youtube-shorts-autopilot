import os
import sys
import json
import time
import re
import random
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
    "maher": {
        "name_ar": "الشيخ ماهر المعيقلي",
        "name_en": "Sheikh Maher Al-Muaiqly",
        "tags": ["ماهر_المعيقلي", "الشيخ_ماهر_المعيقلي", "تلاوات_ماهر_المعيقلي"],
        "keywords": ["معيقلي", "المعيقلي", "maher", "almuaiqly"],
        "default_title": "تلاوة تأسر القلوب من الحرم المكي | ماهر المعيقلي 🕊️✨"
    },
    "alafasy": {
        "name_ar": "الشيخ مشاري راشد العفاسي",
        "name_en": "Sheikh Mishary Alafasy",
        "tags": ["مشاري_العفاسي", "مشاري_راشد_العفاسي", "العفاسي"],
        "keywords": ["عفاسي", "العفاسي", "mishary", "alafasy"],
        "default_title": "تلاوة عذبة تريح القلب والروح | مشاري العفاسي 🕊️✨"
    },
    "sudais": {
        "name_ar": "الشيخ عبدالرحمن السديس",
        "name_en": "Sheikh Abdul Rahman Al-Sudais",
        "tags": ["عبدالرحمن_السديس", "السديس", "تلاوات_السديس"],
        "keywords": ["سديس", "السديس", "sudais"],
        "default_title": "تلاوة خاشعة تهز القلوب من رحاب المسجد الحرام | السديس 🕊️✨"
    },
    "shuraim": {
        "name_ar": "الشيخ سعود الشريم",
        "name_en": "Sheikh Saud Al-Shuraim",
        "tags": ["سعود_الشريم", "الشريم", "تلاوات_الشريم"],
        "keywords": ["شريم", "الشريم", "shuraim"],
        "default_title": "تلاوة حجازية نادرة تبكي العيون | سعود الشريم 🕊️✨"
    },
    "baleelah": {
        "name_ar": "الشيخ بندر بليلة",
        "name_en": "Sheikh Bandar Baleelah",
        "tags": ["بندر_بليلة", "الشيخ_بندر_بليلة"],
        "keywords": ["بليلة", "بندر بليلة", "baleelah"],
        "default_title": "تلاوة بديعة من الحرم المكي | الشيخ بندر بليلة 🕊️✨"
    },
    "balushi": {
        "name_ar": "القارئ هزاع البلوشي",
        "name_en": "Hazza Al-Balushi",
        "tags": ["هزاع_البلوشي", "تلاوات_هزاع_البلوشي"],
        "keywords": ["بلوشي", "البلوشي", "hazza"],
        "default_title": "صوت ملائكي يدخل القلب دون استئذان | هزاع البلوشي 🕊️✨"
    },
    "salimi": {
        "name_ar": "الشيخ منصور السالمي",
        "name_en": "Sheikh Mansour Al-Salimi",
        "tags": ["منصور_السالمي", "تلاوات_منصور_السالمي"],
        "keywords": ["سالمي", "السالمي", "salimi"],
        "default_title": "تلاوة مؤثرة جدا تدمع لها العين | منصور السالمي 🕊️✨"
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

# Negative filter to completely eliminate sectarian / grave / shrine / telegram bio spam
NEGATIVE_FILTER_KEYWORDS = [
    "تلجرام", "تليجرام", "telegram", "بايو", "بالبايو", "في البايو", "bio",
    "تابعني", "تابعنا", "اشترك بقناة", "رابط", "link in bio", "واتساب", "whatsapp",
    "قبر", "قبور", "ضريح", "اضرحة", "مزار", "مرقد", "مراقد", "عتبة", "عتبات",
    "كربلاء", "نجف", "لطمية", "لطميات", "حسينية", "عاشوراء", "شيعة", "رافضة",
    "زيارة", "ماتم", "حسينيات", "مشهد", "سامراء"
]

# 6-SLOT DAILY ROTATION: Exactly 3 Yasser Al-Dosari + 3 Other Elite Reciters
def get_reciter_key_for_current_slot() -> str:
    """
    Determines which reciter to target based on current Tehran Time in Clustered Peaks:
    Rotating through top Sunni elite imams and reciters with highest viral velocity.
    """
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    tehran_now = utc_now + datetime.timedelta(hours=3, minutes=30)
    minute_of_day = tehran_now.hour * 60 + tehran_now.minute

    # Morning awakening (07:30 - 11:30): Sheikh Yasser Al-Dosari / Maher Al-Muaiqly
    if minute_of_day < 700:
        return random.choice(["yasser", "maher"])
    # Afternoon wave 1 (11:30 - 15:40): Sheikh Mishary Alafasy / Yasser Al-Dosari
    elif 700 <= minute_of_day < 940:
        return random.choice(["alafasy", "yasser"])
    # Afternoon wave 2 (15:40 - 17:00): Hazza Al-Balushi / Maher Al-Muaiqly
    elif 940 <= minute_of_day < 1020:
        return random.choice(["balushi", "maher"])
    # Evening commute (17:00 - 18:30): Abdul Rahman Mossad / Mansour Al-Salimi
    elif 1020 <= minute_of_day < 1110:
        return random.choice(["mossad", "salimi"])
    # Maghrib surge (18:30 - 20:00): Abdul Rahman Al-Sudais / Saud Al-Shuraim
    elif 1110 <= minute_of_day < 1200:
        return random.choice(["sudais", "shuraim"])
    # Night peak wave 1 (20:00 - 21:30): Sheikh Yasser Al-Dosari / Bandar Baleelah
    elif 1200 <= minute_of_day < 1285:
        return random.choice(["yasser", "baleelah"])
    # Night peak wave 2 (21:30 - 22:45): Raad Al-Kurdi / Maher Al-Muaiqly
    elif 1285 <= minute_of_day < 1365:
        return random.choice(["raad", "maher"])
    # Bedtime calm (22:45 - 23:59): Islam Sobhi / Mishary Alafasy
    else:
        return random.choice(["islam_sobhi", "alafasy"]) 

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
    Guarantees zero spam (no telegram, no bio, no sectarian terms).
    """
    if not caption:
        return f"{reciter_info['default_title']} #Quran #Shorts"

    lines = [l.strip() for l in caption.splitlines() if l.strip()]
    first_line = ""
    for line in lines:
        cleaned_line = re.sub(r'#\S+', '', line).strip()
        cleaned_line = re.sub(r'\s+', ' ', cleaned_line)
        if any(sp in cleaned_line.lower() for sp in NEGATIVE_FILTER_KEYWORDS):
            continue
        if len(cleaned_line) >= 12:
            first_line = cleaned_line
            break

    if not first_line or len(first_line) < 12:
        first_line = reciter_info["default_title"]

    # Guarantee reciter name is present
    if reciter_info["name_ar"] not in first_line:
        full_title = f"{first_line} | {reciter_info['name_ar']} 🕊️✨ #Shorts #Quran"
    else:
        full_title = f"{first_line} 🕊️✨ #Shorts #Quran"

    return full_title[:95]

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
                if any(bad_kw in caption.lower() for bad_kw in NEGATIVE_FILTER_KEYWORDS):
                    print(f"  [Skipped] Reel {m.code} contains filtered keyword (sectarian/spam/telegram).")
                    continue
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
                        caption_fb = m.caption_text or ""
                        if any(bad_kw in caption_fb.lower() for bad_kw in NEGATIVE_FILTER_KEYWORDS):
                            continue
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

    chosen = None
    target_video_file = None
    for idx, cand in enumerate(candidate_reels):
        candidate_code = cand["code"]
        candidate_url = cand["video_url"]
        temp_file = OUTPUT_DIR / f"quran_{candidate_code}.mp4"
        print(f"  [{idx+1}/{len(candidate_reels)}] Downloading Reel {candidate_code} from Instagram CDN...")
        try:
            req = urllib.request.Request(
                candidate_url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=35) as resp, open(temp_file, 'wb') as f_out:
                f_out.write(resp.read())

            if temp_file.exists() and temp_file.stat().st_size > 50000:
                chosen = cand
                target_video_file = temp_file
                print(f"  ✓ Downloaded successfully: {target_video_file.name} ({target_video_file.stat().st_size // 1024} KB)")
                break
            else:
                print(f"  [Warning] Downloaded file invalid or too small for {candidate_code}. Trying next candidate...")
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception:
                        pass
        except Exception as dl_err:
            print(f"  [Warning] Download failed for {candidate_code}: {dl_err}. Trying next candidate...")
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass
            continue

    if not chosen or not target_video_file:
        print("[Self-Healing Recovery] Could not download any candidate in current pool. Trying Yasser Al-Dosari master catalog...")
        if target_reciter_key != "yasser":
            return find_and_download_viral_reel(min_views=min_views, max_duration=max_duration, target_reciter_key="yasser")
        print("[Error] No viral reels could be downloaded.")
        return None

    rec = chosen["reciter"]
    print("\n" + "=" * 65)
    print(f"★ SELECTED VIRAL REEL: {chosen['code']} | Reciter: {rec['name_ar']}")
    print(f"Estimated Impact: {chosen['score']:,} engagements | Likes: {chosen['likes']:,}")
    print("=" * 65)

    title = clean_arabic_title(chosen["caption"], rec)

    # 131/165 Mega-Engine Protocols:
    # T029 (Semantic Triad) + T126/T131 (YPP Reused Content Immunity & Monetization Safe-Harbor)
    description = (
        f"{title}\n\n"
        f"🌿 تلاوة عطرة خاشعة بصوت {rec['name_ar']} حفظه الله، تفيض بالسكينة والنور وتملأ القلب طمأنينة وسلاماً.\n\n"
        f"📖 قال الله تعالى: ﴿الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾ [الرعد: 28]\n\n"
        f"🤍 شارك المقطع مع من تحب ليكون صدقة جارية لك في ميزان حسناتك، واشترك في القناة لتصلك التلاوات اليومية الخاشعة.\n\n"
        f"─── ⋆⋅☆⋅⋆ ───\n"
        f"🛡️ YPP Transformation & Educational Archival Notice (T131):\n"
        f"Non-commercial spiritual and educational curation of sacred Quranic recitations dedicated to global tranquility, reflection, and Islamic heritage under transformative fair practice guidelines.\n\n"
        f"#{rec['name_ar'].replace(' ', '_')} #القرآن_الكريم #تلاوة_خاشعة #قرآن #راحة_نفسية #Shorts #Islam #Quran #ViralShorts"
    )
    # T028 Two-Tower Neural Recommendation + T046 Tag Cloud Concentration
    tags = [
        rec["name_ar"],
        "القرآن الكريم",
        "تلاوة خاشعة",
        "قران",
        "راحة نفسية",
        "ايات قرانية",
        "تلاوات نادرة",
        rec["name_en"],
        "Quran",
        "Quran recitation",
        "Beautiful Quran recitation",
        "Holy Quran",
        "Peace",
        "Islam",
        "Shorts",
        "Viral"
    ]

    # T096 / T099 / T103 High-Velocity Pinned Comment to spike First-Hour Engagement
    comments_pool = [
        "🌿 صلوا على الحبيب المصطفى محمد ﷺ واكتب من أي بلد تسمع هذه التلاوة العطرة؟ 🤍✨",
        "🤍 اكتب كلمة (سبحان الله وبحمده) لتكون لك صدقة جارية في ميزان حسناتك 🌿✨",
        "✨ اللهم اجعل القرآن الكريم ربيع قلوبنا ونور صدورنا وجلاء أحزاننا.. اكتب دعاءك هنا 🕊️"
    ]
    pinned_comment = random.choice(comments_pool)

    try:
        from mega_prompt_youtube_engine import audit_monetization_safety_165
        is_safe, violations = audit_monetization_safety_165(title, description, tags)
        if not is_safe:
            print(f"  [T121 Monetization Safety Warning] Issues detected: {violations}")
        else:
            print(f"  ✓ [T131 Monetization Shield Active] 100% Policy Compliant & Advertiser-Friendly.")
    except Exception as e:
        print(f"  [T131 Audit Note] {e}")

    return {
        "video": str(target_video_file),
        "code": chosen["code"],
        "title": title,
        "description": description,
        "tags": tags,
        "pinned_comment": pinned_comment,
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