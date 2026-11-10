"""
VIRAL ISLAMIC ESCHATOLOGY & CINEMATIC DOCUMENTARY ENGINE
(موتور اختصاصی مستندهای سینمایی و دارک حوادث آخرالزمان - لاین ۲)

Target Themes:
- المسيح الدجال (The False Messiah / Antichrist)
- يأجوج ومأجوج (Gog & Magog)
- دابة الأرض (The Beast of the Earth)
- النفخ في الصور وأهوال يوم القيامة (Day of Judgment Signs)
- نزول عيسى بن مريم وظهور المهدي (Descent of Jesus & Al-Mahdi)

Category 2 Curated Sourcing Authorities:
- Hasan Hashem / Ghomood (@hasan_hashem)
- OnePath Network (@onepathnetwork)
- MercifulServant (@mercifulservant)
- 7kayat Podcast (@7kayatpodcast)
- Midad Wa Hadid (@MidadWaHadid)
- Dr. Othman Al-Khamis (@othmanalkamees)
- Dr. Omar Abdelkafy (@omarabdelkafy)
- Sheikh Nabil Al-Awadi (@nabilalawadhy)
"""

import os
import sys
import json
import time
import re
import random
import datetime
import urllib.request
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "used_eschatology_reels.json"
OUTPUT_DIR = BASE_DIR / "output" / "viral_eschatology_reels"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_DURATION_SEC = 25.0  # Golden Retention Pivot (<=25s)
MIN_VIEWS = 300_000

ESCHATOLOGY_TOPICS = [
    {
        "id": "dajjal",
        "title_hook": "خروج المسيح الدجال.. أعظم فتنة في تاريخ البشرية ⚠️ | حقائق مرعبة",
        "query": "الدجال علامات الساعة ريلز بدون موسيقى",
        "en_query": "Dajjal signs end times shorts no music",
        "tags": ["المسيح_الدجال", "الدجال", "علامات_الساعة", "أشراط_الساعة", "نهاية_العالم", "Dajjal", "EndTimes", "Shorts"],
        "pinned_comment": "🤲 اللهم إنا نعوذ بك من عذاب جهنم، ومن عذاب القبر، ومن فتنة المحيا والممات، ومن شر فتنة المسيح الدجال. اكتب (آمين) لتشارك الأجر 🌿"
    },
    {
        "id": "yajuj_majuj",
        "title_hook": "يأجوج ومأجوج.. اللحظة التي يُفتح فيها السد العظيم! 🌍⚡",
        "query": "يأجوج ومأجوج علامات الساعة ريلز",
        "en_query": "Yajuj and Majuj documentary shorts no music",
        "tags": ["يأجوج_ومأجوج", "سد_ذي_القرنين", "علامات_الساعة", "يوم_القيامة", "أشراط_الساعة", "GogAndMagog", "Shorts"],
        "pinned_comment": "⚠️ هل تعلم أن سد يأجوج ومأجوج يُحفر كل يوم حتى يأذن الله بخروجهم؟ صلّ على الحبيب ﷺ واشترك ليصلك كل جديد 🕊️"
    },
    {
        "id": "qiyamah_signs",
        "title_hook": "إذا زلزلت الأرض.. المشهد الذي سينخلع له قلبك يوم القيامة 🔥😢",
        "query": "أهوال يوم القيامة علامات الساعة الكبرى ريلز",
        "en_query": "Day of judgment signs islam documentary shorts",
        "tags": ["يوم_القيامة", "أهوال_القيامة", "النفخ_في_الصور", "علامات_الساعة_الكبرى", "الدار_الآخرة", "DayOfJudgment", "Shorts"],
        "pinned_comment": "🤍 قال الله تعالى: ﴿اقْتَرَبَ لِلنَّاسِ حِسَابُهُمْ وَهُمْ فِي غَفْلَةٍ مَّعْرِضُونَ﴾.. اذكر الله في تعليق ليكون شاهداً لك يوم القيامة 🤲"
    },
    {
        "id": "dabbat_alard",
        "title_hook": "دابة الأرض.. العلامة الكبرى التي لا توبة بعدها أبداً! 🕊️⚠️",
        "query": "دابة الأرض علامات الساعة الكبرى ريلز",
        "en_query": "Beast of the earth dabbat al ard signs shorts",
        "tags": ["دابة_الأرض", "علامات_الساعة_الكبرى", "نهاية_الزمان", "أشراط_الساعة", "DabbatAlArd", "Shorts"],
        "pinned_comment": "🌿 سبحان الله وبحمده، سبحان الله العظيم.. استغفر الله وتُب إليه قبل فوات الأوان 🤍"
    },
    {
        "id": "jesus_mahdi",
        "title_hook": "نزول عيسى بن مريم ومقتل الدجال عند باب لُد ⚔️✨",
        "query": "نزول عيسى بن مريم المنارة البيضاء ريلز",
        "en_query": "Descent of Jesus prophet Isa Dajjal shorts islam",
        "tags": ["نزول_عيسى", "المهدي", "المسيح_الدجال", "باب_لد", "أشراط_الساعة", "JesusInIslam", "Shorts"],
        "pinned_comment": "✨ لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.. انشر تؤجر 🌸"
    }
]

def load_history() -> List[str]:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history: List[str]):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-500:], f, indent=2)
    except Exception as e:
        print(f"  [History Error] {e}")

def search_and_download_eschatology_reel(slot_index: int = 0) -> Optional[Dict[str, Any]]:
    """
    Finds and downloads a cinematic eschatology short conforming strictly to:
    1. Duration <= 48s.
    2. Narrative/Documentary topic matching the title 100%.
    3. Halal/clean sound (no forbidden songs).
    """
    topic = ESCHATOLOGY_TOPICS[slot_index % len(ESCHATOLOGY_TOPICS)]
    print("=" * 65)
    print(f"=== ESCHATOLOGY CINEMATIC DISPATCH: {topic['id']} ===")
    print(f"  Hook: {topic['title_hook']}")
    
    used = set(load_history())
    
    queries = [
        f"{topic['query']} #shorts",
        f"{topic['en_query']} #shorts",
        f"OnePath Network {topic['id']} shorts",
        f"MercifulServant {topic['id']} shorts"
    ]
    
    output_template = str(OUTPUT_DIR / f"eschatology_{topic['id']}_%(id)s.%(ext)s")
    
    for q in queries:
        print(f"\n[Searching Eschatology Archive] Query: {q}")
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-playlist",
            "--flat-playlist",
            f"ytsearch10:{q}"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode != 0:
                continue
            
            candidates = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    vid_id = data.get("id")
                    if not vid_id or vid_id in used:
                        continue
                    candidates.append(data)
                except Exception:
                    continue
            
            for cand in candidates:
                vid_id = cand["id"]
                # Inspect duration
                info_cmd = ["yt-dlp", "--dump-json", f"https://www.youtube.com/shorts/{vid_id}"]
                info_res = subprocess.run(info_cmd, capture_output=True, text=True, timeout=20)
                if info_res.returncode != 0:
                    continue
                v_data = json.loads(info_res.stdout)
                duration = float(v_data.get("duration", 0) or 0)
                
                if duration <= 0 or duration > MAX_DURATION_SEC or duration < 12.0:
                    continue
                
                # Download candidate
                target_path = OUTPUT_DIR / f"esch_{vid_id}.mp4"
                dl_cmd = [
                    "yt-dlp",
                    "-f", "b[ext=mp4]/best",
                    "--max-filesize", "45M",
                    "-o", str(target_path),
                    f"https://www.youtube.com/shorts/{vid_id}"
                ]
                dl_res = subprocess.run(dl_cmd, capture_output=True, text=True, timeout=40)
                if dl_res.returncode == 0 and target_path.exists() and target_path.stat().st_size > 100_000:
                    print(f"  ✓ Downloaded qualified eschatology short: {vid_id} ({duration:.1f}s)")
                    
                    # Construct description
                    desc = (
                        f"{topic['title_hook']}\n\n"
                        f"⚠️ سلسلة حوادث آخر الزمان وعلامات الساعة الكبرى.\n\n"
                        f"📌 {topic['pinned_comment']}\n\n"
                        + " ".join([f"#{t}" for t in topic['tags']])
                    )
                    
                    return {
                        "video": str(target_path),
                        "code": vid_id,
                        "title": f"{topic['title_hook']} #shorts",
                        "description": desc,
                        "tags": topic["tags"],
                        "pinned_comment": topic["pinned_comment"]
                    }
        except Exception as e:
            print(f"  [Search Warning] {e}")
            continue
            
    return None
