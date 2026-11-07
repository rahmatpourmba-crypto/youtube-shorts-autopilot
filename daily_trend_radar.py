"""
DAILY DYNAMIC TREND RADAR & CHRONO-PSYCHOLOGICAL ENGINE
(موتور ترندیابی پویای روزانه و موج‌سواری بر عواطف زمانی مخاطبان)

Algorithmic Core:
1. Friday Wave (جمعه‌ها): 100% focused on Surah Al-Kahf (global Friday surge).
2. Night Serenity Wave (شب‌ها و ساعات پایانی): Surah Al-Mulk, Ayatul Kursi, and deep calming sleep recitation.
3. Morning Barakah Wave (صبح‌ها و ظهر): Surah Al-Waqiah (sustenance/barakah) and Surah Ar-Rahman.
4. Afternoon Relief Wave (عصر و غروب): Surah Yusuf, Surah Maryam, Surah Taha (comfort & overcoming grief).
5. 24-Hour Velocity Tracking: Feeds real-time trending search queries into video sourcing.
"""

import os
import sys
import json
import random
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

TEHRAN_TZ = datetime.timezone(datetime.timedelta(hours=3, minutes=30))

DAYPART_PROFILES = {
    "friday_kahf": {
        "key": "friday_kahf",
        "name_fa": "نور جمعه (سوره مبارکه کهف)",
        "target_surah": "الكهف",
        "surah_en": "Al-Kahf",
        "primary_queries": [
            "سورة الكهف تلاوة خاشعة",
            "نور ما بين الجمعتين سورة الكهف",
            "Surah Al-Kahf friday shorts"
        ],
        "hooks": [
            "نور ما بين الجمعتين ✨ | سورة الكهف",
            "تلاوة خاشعة تملأ يومك بالبركة 🕊️ | سورة الكهف",
            "أجمل ما تستمع إليه في يوم الجمعة 🌿 | سورة الكهف",
            "سورة الكهف كاملة بصوت يريح القلب 🤍",
        ],
        "tags": [
            "سورة الكهف", "الكهف", "يوم الجمعة", "الجمعة", "تلاوة الجمعة",
            "نور ما بين الجمعتين", "Surah Al-Kahf", "Surah Kahf", "Friday Quran"
        ],
        "description_intro": (
            "✨ قال النبي ﷺ: «من قرأ سورةَ الكهفِ في يومِ الجمعةِ أضاء له من النورِ ما بين الجمُعَتَين».\n"
            "🌿 تلاوة عطرة خاشعة من سورة الكهف تملأ قلبك سكينة ونوراً."
        )
    },
    "night_serenity": {
        "key": "night_serenity",
        "name_fa": "آرامش شبانگاهی و خواب آسوده (سوره ملک و آية الکرسی)",
        "target_surah": "الملك",
        "surah_en": "Al-Mulk",
        "primary_queries": [
            "سورة الملك قبل النوم",
            "آية الكرسي للنوم والسكينة",
            "تلاوة هادئة لراحة البال والنوم",
            "Surah Al-Mulk sleep"
        ],
        "hooks": [
            "راحة نفسية لا توصف قبل النوم 🌙✨",
            "سورة تنجي من عذاب القبر.. استمع قبل نومك 🕊️",
            "تلاوة هادئة تسكن الروح وتزيل هموم اليوم 🤍",
            "آية الكرسي مكررة للحفظ والسكينة التامة 🎧",
            "استمع بقلبك ونم في أمان الله وسكينته 🌙",
        ],
        "tags": [
            "سورة الملك", "الملك", "آية الكرسي", "تلاوة قبل النوم", "راحة نفسية",
            "تلاوة هادئة", "هدوء الأعصاب", "المنجية من عذاب القبر", "Surah Al-Mulk",
            "Surah Mulk", "Relaxing Quran for Sleep", "Peaceful Quran"
        ],
        "description_intro": (
            "🌙 قال النبي ﷺ عن سورة الملك: «إن سورة من القرآن ثلاثون آية شفعت لرجل حتى غفر له».\n"
            "🕊️ استمع بهدوء قبل نومك لتغمر قلبك السكينة والطمأنينة وتنام في حفظ الله ورعايته."
        )
    },
    "morning_barakah": {
        "key": "morning_barakah",
        "name_fa": "برکت روز، گشایش کار و رزق (سوره واقعه و رحمن)",
        "target_surah": "الواقعة",
        "surah_en": "Al-Waqiah",
        "primary_queries": [
            "سورة الواقعة لجلب الرزق والبركة",
            "سورة الرحمن تلاوة خاشعة",
            "سورة يس تلاوة الصباح",
            "Surah Al-Waqiah barakah"
        ],
        "hooks": [
            "سورة مباركة لجلب الرزق وتفريج الهموم 🌿✨",
            "ابدأ يومك بنور القرآن وراحة البال 🕊️",
            "تلاوة تفيض بالسكينة والبركة في يومك 🤍",
            "عروس القرآن.. صوت يهز القلوب ويشرح الصدر ✨",
            "سورة تفتح أبواب الخير والبركة في رزقك 🤲",
        ],
        "tags": [
            "سورة الواقعة", "سورة الرحمن", "الواقعة", "الرحمن", "جلب الرزق",
            "بركة الصباح", "تلاوة الصباح", "سعة الرزق", "Surah Al-Waqiah",
            "Surah Ar-Rahman", "Morning Quran", "Barakah"
        ],
        "description_intro": (
            "🌿 ابدأ يومك مع آيات الذكر الحکیم المبارکة لجلب الرزق والسکینة والبرکة فی حیاتک.\n"
            "✨ قال الله تعالى: ﴿وَمَن يَتَّقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا وَيَرْزُقْهُ مِنْ حَيْثُ لَا يَحْتَسِبُ﴾."
        )
    },
    "afternoon_relief": {
        "key": "afternoon_relief",
        "name_fa": "رفع دلتنگی و تفریج غم و اندوه (سوره یوسف و مریم)",
        "target_surah": "يوسف",
        "surah_en": "Yusuf",
        "primary_queries": [
            "سورة يوسف تفريج الهموم",
            "سورة مريم تلاوة خاشعة",
            "تلاوة مبكية مؤثرة",
            "Surah Yusuf emotional recitation"
        ],
        "hooks": [
            "آيات تذهب الهم والحزن عن قلبك 🕊️💔",
            "الفرج بعد الشدة.. استمع بقلبك وانسَ همومك 🌿",
            "صوت تقشعر له الأبدان من خشية الله 🤍",
            "تلاوة ندية تمس شغاف القلب وتبكي العين ✨",
            "لا تحزن إن الله معنا.. تلاوة تفيض بالأمل 🕊️",
        ],
        "tags": [
            "سورة يوسف", "سورة مريم", "يوسف", "مريم", "تفريج الهموم",
            "زوال الحزن", "تلاوة مبكية", "تلاوة مؤثرة", "Surah Yusuf",
            "Surah Maryam", "Emotional Quran"
        ],
        "description_intro": (
            "🤍 تلاوة خاشعة تبث الأمل فی روحک وتذکرک بأن مع العسر یسراً وأن فرج الله قریب.\n"
            "✨ قال الله تعالى: ﴿إِنَّمَا أَشْكُو بَثِّي وَحُزْنِي إِلَى اللَّهِ﴾."
        )
    }
}


def get_current_trend_profile(utc_now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """
    Evaluates current wall-clock Tehran time and returns the winning
    daily/hourly psychological wave profile.
    """
    utc_now = utc_now or datetime.datetime.now(datetime.timezone.utc)
    tehran_dt = utc_now.astimezone(TEHRAN_TZ)

    hour = tehran_dt.hour
    weekday = tehran_dt.weekday()  # 0=Monday, 4=Friday, 6=Sunday

    # 1. Friday Worldwide Wave: Friday between 04:00 AM and 23:59 PM Tehran
    if weekday == 4 and 4 <= hour <= 23:
        return DAYPART_PROFILES["friday_kahf"]

    # 2. Night Serenity Wave: 20:00 (8 PM) through 04:59 AM Tehran
    if hour >= 20 or hour < 5:
        return DAYPART_PROFILES["night_serenity"]

    # 3. Morning Barakah Wave: 05:00 AM through 13:59 PM Tehran
    if 5 <= hour < 14:
        return DAYPART_PROFILES["morning_barakah"]

    # 4. Afternoon Relief Wave: 14:00 (2 PM) through 19:59 PM Tehran
    return DAYPART_PROFILES["afternoon_relief"]


def get_recommended_search_query(target_reciter_ar: str, utc_now: Optional[datetime.datetime] = None) -> str:
    """
    Returns high-velocity search query tailored for the active daily/hourly trend.
    """
    profile = get_current_trend_profile(utc_now)
    surah = profile["target_surah"]
    return f"{target_reciter_ar} سورة {surah} تلاوة خاشعة #shorts"


def enrich_metadata_for_current_trend(
    base_title: str,
    caption: str,
    reciter_ar: str,
    reciter_tag: str,
    reciter_en: str = "",
    detected_surah: Optional[str] = None,
    utc_now: Optional[datetime.datetime] = None,
    rng=None
) -> Dict[str, Any]:
    """
    Constructs high-CTR title, description, and tags aligned with the active trend wave.
    """
    rng = rng or random
    profile = get_current_trend_profile(utc_now)
    surah = detected_surah or profile["target_surah"]
    
    # Pick a high-converting hook tailored for this wave
    hook = rng.choice(profile["hooks"])
    
    # Build Title (ensure clean, zero-spam structure)
    if surah in hook:
        body = f"{hook} | {reciter_ar}"
    else:
        surah_label = surah if surah.startswith("آية") else f"سورة {surah}"
        body = f"{hook} | {surah_label} | {reciter_ar}"
        
    from metadata_optimizer import build_title_with_suffix
    title = build_title_with_suffix(body, f"#{reciter_tag} #قرآن #shorts")
    
    # Merge wave tags with core YouTube SEO tags
    trend_tags = profile["tags"][:5]
    core_tags = [
        reciter_ar,
        reciter_tag.replace("_", " "),
        reciter_en,
        f"سورة {surah}" if not surah.startswith("آية") else surah,
        "قرآن",
        "تلاوة خاشعة",
        "القرآن الكريم",
        "راحة نفسية",
        "Quran",
        "Quran recitation",
        "Holy Quran",
        "Shorts"
    ]
    
    combined_tags = []
    seen = set()
    for t in (trend_tags + core_tags):
        if t and t not in seen:
            seen.add(t)
            combined_tags.append(t)
            
    # YouTube tag budget ~480 chars
    final_tags, total_chars = [], 0
    for t in combined_tags:
        if total_chars + len(t) + 1 > 480:
            break
        final_tags.append(t)
        total_chars += len(t) + 1
        
    hashtags = [f"#{reciter_tag}", "#قرآن", "#shorts", "#تلاوة_خاشعة", "#راحة_نفسية"]
    if surah and not surah.startswith("آية"):
        hashtags.insert(1, f"#سورة_{surah.replace(' ', '_')}")
        
    description = (
        f"{title}\n\n"
        f"🎙️ بصوت {reciter_ar}\n"
        f"📖 سورة {surah}\n\n"
        f"{profile['description_intro']}\n\n"
        "🤍 صلّوا على الحبيب المصطفى ﷺ واكتب من أي بلد تستمع لهذه التلاوة المباركة 🌍\n"
        "📌 شارك المقطع ليكون صدقة جارية لك، واشترك في القناة ليصلك جديد التلاوات اليومية الخاشعة.\n\n"
        + " ".join(hashtags)
    )
    
    return {
        "title": title,
        "description": description,
        "tags": final_tags,
        "surah": surah,
        "trend_profile": profile["key"],
        "trend_name": profile["name_fa"]
    }
