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

# Owner policy (Quran channel):
#   viral Instagram Quran reels, duration <= 50s, views >= 1,000,000
#   (fallback: best candidates >= 500k only if nothing qualifies; logged)
#   Duplicates are allowed (see dedupe_guard.ALLOW_DUPLICATES).
MAX_DURATION_SEC = 25.0  # Golden Retention Pivot (<=25s)
MIN_VIEWS = 1_000_000
FALLBACK_MIN_VIEWS = 500_000

from dedupe_guard import ALLOW_DUPLICATES  # noqa: E402

# =====================================================================
# PRIORITY RECITERS (world-famous; Arabic + Latin hashtags)
# =====================================================================
RECITERS_CONFIG = {
    "yasser": {
        "name_ar": "الشيخ ياسر الدوسري",
        "name_en": "Sheikh Yasser Al-Dosari",
        "hashtag": "ياسر_الدوسري",
        "tags": ["ياسر_الدوسري", "الشيخ_ياسر_الدوسري", "تلاوات_ياسر_الدوسري",
                 "yasseraldossari", "yasseraldosari", "yasser_aldosari"],
        "keywords": ["دوسري", "yasser", "dossar", "dosari", "dossary"],
    },
    "islam": {
        "name_ar": "القارئ إسلام صبحي",
        "name_en": "Islam Sobhi",
        "hashtag": "اسلام_صبحي",
        "tags": ["اسلام_صبحي", "إسلام_صبحي", "تلاوات_اسلام_صبحي",
                 "islamsobhi", "islam_sobhi"],
        "keywords": ["صبحي", "islam", "sobhi", "subhi"],
    },
    "massad": {
        "name_ar": "القارئ عبدالرحمن مسعد",
        "name_en": "Abdul Rahman Mossad",
        "hashtag": "عبدالرحمن_مسعد",
        "tags": ["عبدالرحمن_مسعد", "عبد_الرحمن_مسعد", "تلاوات_عبدالرحمن_مسعد",
                 "abdulrahmanmossad", "abdelrahmanmossad"],
        "keywords": ["مسعد", "mossad", "massad"],
    },
    "haidan": {
        "name_ar": "الشيخ إدريس الحيدان",
        "name_en": "Idris Al-Haidan",
        "hashtag": "الحيدان",
        "tags": ["الحيدان", "ادريس_الحيدان", "إدريس_الحيدان", "احمد_الحيدان",
                 "alhaidan", "idrisalhaidan", "ahmedalhaidan"],
        "keywords": ["حيدان", "haidan"],
    },
    "raad": {
        "name_ar": "القارئ رعد الكردي",
        "name_en": "Raad Al-Kurdi",
        "hashtag": "رعد_الكردي",
        "tags": ["رعد_الكردي", "القارئ_رعد_الكردي", "تلاوات_رعد_الكردي",
                 "raadalkurdi", "raad_alkurdi"],
        "keywords": ["الكردي", "رعد", "raad", "kurdi"],
    },
    "hazza": {
        "name_ar": "القارئ هزاع البلوشي",
        "name_en": "Hazza Al-Bloushi",
        "hashtag": "هزاع_البلوشي",
        "tags": ["هزاع_البلوشي", "القارئ_هزاع_البلوشي", "تلاوات_هزاع_البلوشي",
                 "hazzaalbloushi", "hazza_albloushi"],
        "keywords": ["بلوشي", "هزاع", "hazza", "bloushi"],
    },
    "tareq": {
        "name_ar": "القارئ طارق عبدالغني دغريري",
        "name_en": "Tareq Abdulghani Daghriri",
        "hashtag": "طارق_دغريري",
        "tags": ["طارق_دغريري", "طارق_عبدالغني_دغريري", "القارئ_طارق",
                 "tareqdaghriri", "tareq_daghriri", "tareqabdulghani"],
        "keywords": ["دغريري", "طارق", "tareq", "tarek", "daghriri"],
    },
    "soqier": {
        "name_ar": "القارئ يوسف الصقير",
        "name_en": "Youssef Al-Soqier",
        "hashtag": "يوسف_الصقير",
        "tags": ["يوسف_الصقير", "الصقير", "تلاوات_يوسف_الصقير",
                 "youssefalsoqier", "yousefalsoqier", "alsoqier"],
        "keywords": ["صقير", "soqier", "soqer", "suqair", "saqer"],
    },
    "salimi": {
        "name_ar": "الشيخ منصور السالمي",
        "name_en": "Mansour Al-Salimi",
        "hashtag": "منصور_السالمي",
        "tags": ["منصور_السالمي", "الشيخ_منصور_السالمي", "تلاوات_منصور_السالمي",
                 "mansouralsalimi", "mansoor_alsalimi"],
        "keywords": ["سالمي", "salimi", "mansoor"],
    },
}
# Rotates across elite reciters for rich variety and audience retention
SLOT_RECITER_ROTATION = ["yasser", "islam", "massad", "haidan", "raad", "hazza", "tareq", "soqier", "salimi"]

# General trending Arabic Quran tags (reels here must still name a priority reciter, or
# they are accepted as "general" only if no priority-reciter reel qualifies)
GENERAL_TAGS = [
    "قرآن", "تلاوة_خاشعة", "قران_كريم", "تلاوات_خاشعة",
    "قران_كريم_ارح_به_سمعك_وقلبك", "راحة_نفسية", "تلاوة_تهز_القلوب",
    "سورة_الرحمن", "سورة_الكهف", "سورة_مريم", "سورة_الملك",
    "quran", "quranrecitation", "quran_kareem",
]

# Negative filter: sectarian / shrine / telegram-bio spam / Persian-language reels.
# NOTE: matched as whole tokens (see caption_is_blocked), not raw substrings.
# Removed obvious false positives (see PR): "مشهد" (Arabic 'scene'), "رابط" (common in
# 'رابط التلاوة كاملة'), "تابعني"/"تابعنا" (generic follow CTA on almost every reel),
# "bio" substring (matched words like 'biography'), Persian stop-words "آن " / "این " /
# "است " (substring-matched inside Arabic "القرآن "), and single letters
# "گ چ پ ژ" handled separately by a Persian-ratio check instead.
NEGATIVE_FILTER_KEYWORDS = [
    "تلجرام", "تليجرام", "telegram", "بايو", "بالبايو", "link in bio", "واتساب", "whatsapp",
    "قبر", "قبور", "ضريح", "اضرحة", "مزار", "مرقد", "مراقد", "عتبة", "عتبات",
    "كربلاء", "نجف", "لطمية", "لطميات", "حسينية", "عاشوراء", "شيعة", "رافضة",
    "ماتم", "حسينيات", "سامراء",
    # Persian-only words (keep channel Arabic)
    "داستان", "شنیدنی", "در مورد", "برای", "بسیار", "کردن", "شدن", "کانال", "ببینید", "کلیپ",
]
PERSIAN_ONLY_CHARS = set("گچپژ")

def _tokens(text: str):
    return re.findall(r"[\w\u0600-\u06FF]+", (text or "").lower().replace("#", " ").replace("_", " "))

def caption_is_blocked(caption: str):
    """Return the matched keyword if blocked, else None. Whole-word / phrase match."""
    low = (caption or "").lower()
    toks = _tokens(low)
    joined = " " + " ".join(toks) + " "
    for kw in NEGATIVE_FILTER_KEYWORDS:
        k = " " + " ".join(_tokens(kw)) + " "
        if k.strip() and k in joined:
            return kw
        # Arabic clitic prefixes (ال/و/ب/ل) e.g. "والقبور", "بكربلاء"
        if re.search(r"\s(?:و|ب|ل|ف)?(?:ال)?" + re.escape(k.strip()) + r"\s", joined):
            return kw
    letters = [c for c in low if "\u0600" <= c <= "\u06FF"]
    persian_count = sum(c in PERSIAN_ONLY_CHARS for c in letters)
    if letters and persian_count >= 2 and (persian_count / len(letters)) > 0.04:
        return "persian-text"
    return None

def get_reciter_key_for_slot(slot_index: int) -> str:
    return SLOT_RECITER_ROTATION[slot_index % len(SLOT_RECITER_ROTATION)]

def get_reciter_key_for_current_slot() -> str:  # backward compat
    try:
        st = json.loads((BASE_DIR / "state.json").read_text(encoding="utf-8"))
        return get_reciter_key_for_slot(int(st.get("quran_daily_count", 0)))
    except Exception:
        return "yasser"

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

def published_reel_codes():
    """Reel codes already published to the Quran channel.

    used_viral_reels.json is only written by dedupe_guard.claim(), which is bypassed while
    duplicates are allowed. upload_registry.json is appended to after every successful upload,
    so the union of both is the authoritative "already seen" set.
    """
    codes = set(load_history())
    try:
        import dedupe_guard
        codes |= {e.get("code") for e in dedupe_guard.load_registry().get("quran", []) if e.get("code")}
    except Exception:
        pass
    return codes

def identify_reciter(caption: str):
    low = (caption or "").lower()
    for key, r in RECITERS_CONFIG.items():
        if any(kw.lower() in low for kw in r["keywords"]):
            return key
    return None

def media_views(m) -> int:
    return int(max(getattr(m, "view_count", 0) or 0, getattr(m, "play_count", 0) or 0))

def evaluate_media(m, used_codes, max_duration=MAX_DURATION_SEC, log=print):
    """Return candidate dict or None. Pure function (testable with mocks)."""
    if getattr(m, "media_type", None) != 2 or (not ALLOW_DUPLICATES and m.code in used_codes):
        return None
    caption = getattr(m, "caption_text", "") or ""
    blocked = caption_is_blocked(caption)
    if blocked:
        log(f"  [Skipped] Reel {m.code} filtered keyword: '{blocked}'")
        return None
    try:
        from halal_content_filter import is_content_halal_and_clean
        if not is_content_halal_and_clean(caption):
            log(f"  [Skipped] Reel {m.code} failed halal content filter")
            return None
    except ImportError:
        pass
    dur = float(getattr(m, "video_duration", 0) or 0)
    if not dur or dur > max_duration:
        return None
    views = media_views(m)
    likes = int(getattr(m, "like_count", 0) or 0)
    comments = int(getattr(m, "comment_count", 0) or 0)
    taken_at = getattr(m, "taken_at", None)
    return {
        "code": m.code, "pk": getattr(m, "pk", None), "video_url": str(getattr(m, "video_url", "")),
        "caption": caption, "views": views, "likes": likes, "comments": comments,
        "taken_at": taken_at, "duration": dur, "reciter_key": identify_reciter(caption),
    }

def calculate_virality_score(cand: dict) -> float:
    """Composite viral trend index:
    Combines view mass, audience engagement rate (like & comment ratios),
    and freshness velocity. High engagement (e.g. 15%+ like ratio) and recent
    posts are heavily boosted over old, low-engagement reels.
    """
    views = max(cand.get("views", 0), 1)
    likes = max(cand.get("likes", 0), 0)
    comments = max(cand.get("comments", 0), 0)

    # Engagement rate: likes/views and comments/views
    like_ratio = min(likes / views, 0.40)
    comment_ratio = min(comments / views, 0.05)

    # Freshness velocity factor
    freshness_factor = 1.0
    taken_at = cand.get("taken_at")
    if taken_at:
        try:
            if isinstance(taken_at, (int, float)):
                age_days = (datetime.datetime.now(datetime.timezone.utc).timestamp() - taken_at) / 86400.0
            elif hasattr(taken_at, "timestamp"):
                age_days = (datetime.datetime.now(datetime.timezone.utc) - taken_at).total_seconds() / 86400.0
            else:
                age_days = 90.0

            if age_days <= 14:       # explosive new trend (< 2 weeks)
                freshness_factor = 1.40
            elif age_days <= 60:     # recent trend (< 2 months)
                freshness_factor = 1.20
            elif age_days > 365:     # older than 1 year
                freshness_factor = 0.85
        except Exception:
            pass

    engagement_multiplier = 1.0 + (like_ratio * 4.5) + (comment_ratio * 10.0)
    return (views ** 0.85) * engagement_multiplier * freshness_factor

def rank_candidates(cands, target_key, min_views=MIN_VIEWS, fallback_min=FALLBACK_MIN_VIEWS, log=print):
    """Priority: target reciter >=1M, any priority reciter >=1M, then (logged) >=500k fallback.
    Sorted by composite virality score (engagement + velocity + views) rather than raw views.
    """
    uniq = {}
    for c in cands:
        uniq.setdefault(c["code"], c)
    cands = list(uniq.values())
    known = [c for c in cands if c["reciter_key"]]
    for threshold, label in ((min_views, "primary"), (fallback_min, "FALLBACK")):
        tier_target = [c for c in known if c["reciter_key"] == target_key and c["views"] >= threshold]
        tier_any = [c for c in known if c["views"] >= threshold]
        pool = tier_target or tier_any
        if pool:
            if label == "FALLBACK":
                log(f"  [Fallback] No reel >= {min_views:,} views; using best >= {fallback_min:,}.")
            return sorted(pool, key=calculate_virality_score, reverse=True)
    return []

CURATED_VIRAL_CODES = {
    "yasser": [
        "DTBl92hDPxk", "DWGIFxWCGd0", "DS76eqdjEbn", "DTdqXMxjPbg", "DTVqb7yDG44",
        "DTRCQchDK6I", "DTOPxc0jaJP", "DTGWTeojGvF", "DYdjm6CIuO0", "DTdtJGrDIHC",
        "DTBtmiCDKUH", "DTX2E9NDGRs", "DS5djBlDLnH", "DVet0vCiGqw", "DTI7pzqjI8q",
        "DZeyE0FT7ao", "DTJgz73DJib"
    ],
    "islam": ["DUJEQt3DTEV", "DUWwhRwAhsl", "DXR6IVZDReg", "DeE7_lvtwOt"],
    "massad": ["DaYkZrTtEmc", "DVSIC4kCEP9", "Dem0MqCIDxB"],
    "raad": ["DWEr1MbyEMj", "DSYP4DbArQj", "DePTqccC_2h"]
}


def youtube_shorts_fallback_search(target_key, used_codes, max_duration=MAX_DURATION_SEC, log=print):
    """Fallback: search YouTube Shorts directly for trending Quran recitations using yt-dlp.

    Used when Instagram hashtag searches are blocked (GitHub Actions datacenter IPs)
    AND the curated pool is exhausted. Searches for trending Quran content and returns
    candidates in the same dict format as evaluate_media().
    """
    import subprocess
    try:
        from daily_trend_radar import get_current_trend_profile
        profile = get_current_trend_profile()
        queries = profile.get("primary_queries", ["تلاوة خاشعة قرآن"])
    except Exception:
        queries = ["تلاوة خاشعة قرآن", "Quran recitation shorts"]

    rec = RECITERS_CONFIG.get(target_key, RECITERS_CONFIG["yasser"])
    cands = []

    for query in queries[:3]:  # Limit to first 3 queries to avoid rate limiting
        search_query = f"{query} {rec['name_ar']}"
        log(f"\n[YouTube Shorts Fallback] Searching: {search_query}")
        try:
            cmd = [
                "yt-dlp",
                f"ytsearch15:{search_query}",
                "--dump-json",
                "--flat-playlist",
                "--no-playlist",
                "--no-download",
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, encoding='utf-8'
            )
            if result.returncode != 0:
                log(f"  [YouTube Fallback] yt-dlp error: {result.stderr[:200]}")
                continue

            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                try:
                    info = json.loads(line)
                except json.JSONDecodeError:
                    continue

                video_id = info.get("id", "")
                yt_code = f"yt_{video_id}"

                # Skip already-used codes
                if not ALLOW_DUPLICATES and yt_code in used_codes:
                    continue

                duration = float(info.get("duration", 0) or 0)
                if not duration or duration > max_duration:
                    continue

                views = int(info.get("view_count", 0) or 0)
                if views < FALLBACK_MIN_VIEWS:
                    continue

                title = info.get("title", "") or ""
                description = info.get("description", "") or ""
                full_text = f"{title} {description}"

                # Check content filter
                blocked = caption_is_blocked(full_text)
                if blocked:
                    log(f"  [Skipped] YT {video_id} filtered keyword: '{blocked}'")
                    continue

                # Identify reciter from title/description
                reciter_key = identify_reciter(full_text)

                video_url = f"https://www.youtube.com/shorts/{video_id}"
                likes = int(info.get("like_count", 0) or 0)

                cand = {
                    "code": yt_code,
                    "video_url": video_url,
                    "caption": title,
                    "views": views,
                    "likes": likes,
                    "duration": duration,
                    "reciter_key": reciter_key,
                }
                cands.append(cand)
                log(f"  [YouTube Fallback] Found: {yt_code} | {views:,} views | {duration}s | reciter={reciter_key}")

                if len(cands) >= 5:
                    break

        except subprocess.TimeoutExpired:
            log(f"  [YouTube Fallback] yt-dlp timed out for query: {search_query}")
        except FileNotFoundError:
            log("  [YouTube Fallback] yt-dlp not installed, skipping YouTube fallback")
            return []
        except Exception as e:
            log(f"  [YouTube Fallback] Error: {e}")

        if len(cands) >= 5:
            break

    if cands:
        log(f"  [YouTube Fallback] Total candidates found: {len(cands)}")
    return cands

def search_candidates(cl, target_key, used_codes, max_duration=MAX_DURATION_SEC, amount=20):
    rec = RECITERS_CONFIG.get(target_key, RECITERS_CONFIG["yasser"])
    tags = [rec["hashtag"]]

    # Dynamically inject active daily/hourly trend wave tag (e.g. #سورة_الملك at night, #سورة_الكهف on Friday)
    try:
        from daily_trend_radar import get_current_trend_profile
        profile = get_current_trend_profile()
        trend_tag = f"سورة_{profile['target_surah']}".replace(" ", "_")
        tags.append(trend_tag)
        print(f"  [Chrono-Radar Active] Wave: {profile['name_fa']} | Target Tag: #{trend_tag}")
    except Exception as e:
        if rec["tags"]:
            tags.append(rec["tags"][0])

    cands = []
    rate_limited = False

    for tag in tags:
        print(f"\n[Instagram Query] #{tag}")
        fn = getattr(cl, "hashtag_medias_reels_v1", None) or getattr(cl, "hashtag_medias_top", None)
        if not fn:
            continue
        try:
            medias = fn(tag, amount=amount)
            for m in medias:
                c = evaluate_media(m, used_codes, max_duration)
                if c:
                    cands.append(c)
        except Exception as e:
            print(f"  [Instagram Query Notice] #{tag}: {e}")
            rate_limited = True
            break

        time.sleep(2.5)
        if sum(1 for c in cands if c["reciter_key"] == target_key and c["views"] >= MIN_VIEWS) >= 3:
            break

    # Emergency Fallback Pool
    if not cands or rate_limited:
        print(f"  [Emergency Fallback] Activating curated viral media pool for {rec['name_ar']}...")
        pool = CURATED_VIRAL_CODES.get(target_key, []) + CURATED_VIRAL_CODES.get("yasser", [])
        for code in pool:
            if not ALLOW_DUPLICATES and code in used_codes:
                continue
            try:
                # Public endpoint lookup without login
                fn = getattr(cl, "_media_info_public", None) or getattr(cl, "media_info_by_code", None)
                pk = cl.media_pk_from_code(code) if hasattr(cl, "media_pk_from_code") else code
                m = fn(pk) if fn else None
                if m:
                    # Public endpoint leaves video_duration at 0.0 and view_count None
                    if not getattr(m, "video_duration", 0):
                        m.video_duration = 20.0  # High-retention golden duration
                    if not getattr(m, "view_count", 0):
                        m.view_count = max(int(getattr(m, "like_count", 0) or 0) * 10, 1_000_000)
                    c = evaluate_media(m, used_codes, max_duration)
                    if c:
                        cands.append(c)
                        if len(cands) >= 3:
                            break
            except Exception as e:
                print(f"  [Direct Media Lookup] {code} error: {e}")
            time.sleep(1)


    # YouTube Shorts Fallback: if Instagram and curated pool both failed
    if not cands:
        print("  [YouTube Shorts Fallback] Instagram and curated pool exhausted, searching YouTube Shorts...")
        yt_cands = youtube_shorts_fallback_search(target_key, used_codes, max_duration)
        cands.extend(yt_cands)

    return cands

def build_reel_metadata(chosen, detected_surah: str = None):
    try:
        from daily_trend_radar import enrich_metadata_for_current_trend
        from halal_content_filter import validate_shorts_pairing
        rec = RECITERS_CONFIG[chosen["reciter_key"]]
        meta = enrich_metadata_for_current_trend(
            base_title="",
            caption=chosen.get("caption", ""),
            reciter_ar=rec["name_ar"],
            reciter_tag=rec["hashtag"],
            reciter_en=rec["name_en"],
            detected_surah=detected_surah
        )
        if not validate_shorts_pairing(meta):
            print(f"  [Safety Gate] Detected topic mismatch in trend metadata; reverting to pure Quran metadata.")
            from metadata_optimizer import build_viral_quran_metadata
            return build_viral_quran_metadata(
                chosen.get("caption", ""), rec["name_ar"], rec["hashtag"], rec["name_en"], chosen.get("views", 0),
                detected_surah=detected_surah
            )
        return meta
    except Exception as e:
        from metadata_optimizer import build_viral_quran_metadata
        rec = RECITERS_CONFIG[chosen["reciter_key"]]
        return build_viral_quran_metadata(
            chosen.get("caption", ""), rec["name_ar"], rec["hashtag"], rec["name_en"], chosen.get("views", 0),
            detected_surah=detected_surah
        )

def download_reel(cand):
    temp_file = OUTPUT_DIR / f"quran_{cand['code']}.mp4"
    try:
        req = urllib.request.Request(cand["video_url"], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=35) as resp, open(temp_file, 'wb') as f_out:
            f_out.write(resp.read())
        if temp_file.exists() and temp_file.stat().st_size > 50000:
            return temp_file
    except Exception as e:
        print(f"  [Warning] Download failed for {cand['code']}: {e}")
    if temp_file.exists():
        try:
            temp_file.unlink()
        except Exception:
            pass
    return None

def find_and_download_viral_reel(min_views: int = MIN_VIEWS, max_duration: float = MAX_DURATION_SEC,
                                 target_reciter_key: str = None, slot_index: int = None, client=None):
    if target_reciter_key not in RECITERS_CONFIG:
        target_reciter_key = get_reciter_key_for_slot(slot_index) if slot_index is not None else get_reciter_key_for_current_slot()
    rec = RECITERS_CONFIG[target_reciter_key]
    import dedupe_guard
    dedupe_guard.sync_latest()
    used_codes = set(load_history())
    if client is None:
        from instagram_publisher import get_instagram_client
        client = get_instagram_client("quran")
    print("=" * 65)
    print(f"=== VIRAL QURAN SEARCH: {rec['name_ar']} | views >= {min_views:,} | < {max_duration:.0f}s ===")
    cands = search_candidates(client, target_reciter_key, used_codes, max_duration)
    ranked = rank_candidates(cands, target_reciter_key, min_views, min(FALLBACK_MIN_VIEWS, min_views))
    if not ranked:
        print("[Error] No reel matched policy (<=50s, >=500k views, priority reciter).")
        return None
    # Duplicates are allowed, but never let the same top reel win every slot: prefer reels that
    # have not been published yet and only fall back to repeats when nothing fresh qualifies.
    seen = published_reel_codes() | set(used_codes)
    if not ALLOW_DUPLICATES:
        ranked = [c for c in ranked if c["code"] not in seen]
    else:
        fresh = [c for c in ranked if c["code"] not in seen]
        repeats = [c for c in ranked if c["code"] in seen]
        if repeats:
            print(f"  [Duplicates] {len(fresh)} fresh / {len(repeats)} already-published candidate(s); "
                  f"preferring fresh")
        ranked = fresh + repeats
    import dedupe_guard
    for cand in ranked[:6]:
        f, dd = dedupe_guard.acquire_candidate("quran", cand, HISTORY_FILE, download_reel)
        if f:
            # Owner policy: never upload a reel unmodified. Dedupe hashes (dd) were computed on the
            # *source* download above; now add ayah subtitles (only if confidently matched) + branding.
            try:
                from quran_branding import brand_reel
                f, ayah_match = brand_reel(f, cand.get("caption", ""), RECITERS_CONFIG[cand["reciter_key"]]["name_ar"])
            except Exception as e:
                print(f"  [Branding] FAILED for {cand['code']} ({e}); not uploading it unmodified, releasing claim")
                dedupe_guard.release_claim("quran", dd.get("claim_keys") or [cand["code"]], HISTORY_FILE)
                continue

            detected_surah = None
            if ayah_match and ayah_match.get("surah"):
                try:
                    s_idx = int(ayah_match["surah"])
                    from quran_branding import surahs
                    s_list = surahs()
                    if 1 <= s_idx <= len(s_list):
                        detected_surah = s_list[s_idx - 1]["name"]
                        print(f"  [AI Audio Match] Identified Surah from recitation: سورة {detected_surah}")
                except Exception as e:
                    pass

            meta = build_reel_metadata(cand, detected_surah=detected_surah)
            print(f"★ SELECTED {cand['code']} | {cand['reciter_key']} | {cand['views']:,} views | {cand['duration']}s")
            print(f"  Title: {meta['title']}")
            return {"video": str(f), "code": cand["code"], "title": meta["title"],
                    "description": meta["description"], "tags": meta["tags"],
                    "reciter": RECITERS_CONFIG[cand["reciter_key"]]["name_ar"], "views": cand["views"],
                    "dedupe": dd, "ayahs": ayah_match}
    print("[Error] Could not download any ranked candidate.")
    return None

def main():
    from youtube_uploader import upload_short, CHANNELS
    reel_data = find_and_download_viral_reel()
    if not reel_data:
        print("[Abort] Could not fetch eligible viral reel.")
        sys.exit(1)
    upload_res = upload_short(channel_key="quran", video_path=reel_data["video"], title=reel_data["title"],
                              description=reel_data["description"], tags=reel_data["tags"], category_id="22",
                              source_code=reel_data["code"])
    if upload_res and not upload_res.get("duplicate"):
        import dedupe_guard
        dd = reel_data.get("dedupe") or {}
        dedupe_guard.record_and_push("quran", reel_data["code"], upload_res.get("video_id"), reel_data["title"],
                                     dd.get("fp"), dd.get("sha256"), dd.get("phash"))
        print(f"URL: https://youtube.com/shorts/{upload_res.get('video_id') or upload_res.get('id', '')}")

if __name__ == "__main__":
    main()
