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
#   viral Instagram Quran reels, duration < 45s, views >= 1,000,000
#   (fallback: best candidates >= 500k only if nothing qualifies; logged)
MAX_DURATION_SEC = 45.0
MIN_VIEWS = 1_000_000
FALLBACK_MIN_VIEWS = 500_000

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
    "haidan": {
        "name_ar": "الشيخ إدريس الحيدان",
        "name_en": "Idris Al-Haidan",
        "hashtag": "الحيدان",
        "tags": ["الحيدان", "ادريس_الحيدان", "إدريس_الحيدان", "احمد_الحيدان",
                 "alhaidan", "idrisalhaidan", "ahmedalhaidan"],
        "keywords": ["حيدان", "haidan"],
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
}
# Daily rotation of the 8 slots: Yasser gets 3, others get ~2 each
SLOT_RECITER_ROTATION = ["yasser", "haidan", "soqier", "tareq", "yasser", "haidan", "yasser", "soqier"]

# General trending Arabic Quran tags (reels here must still name a priority reciter, or
# they are accepted as "general" only if no priority-reciter reel qualifies)
GENERAL_TAGS = ["قرآن", "تلاوة_خاشعة", "قران_كريم", "تلاوات_خاشعة", "quran", "quranrecitation"]

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
    if letters and sum(c in PERSIAN_ONLY_CHARS for c in letters) / len(letters) > 0.02:
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
    if getattr(m, "media_type", None) != 2 or m.code in used_codes:
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
    if not dur or dur >= max_duration:
        return None
    views = media_views(m)
    return {
        "code": m.code, "pk": getattr(m, "pk", None), "video_url": str(getattr(m, "video_url", "")),
        "caption": caption, "views": views, "likes": getattr(m, "like_count", 0) or 0,
        "duration": dur, "reciter_key": identify_reciter(caption),
    }

def rank_candidates(cands, target_key, min_views=MIN_VIEWS, fallback_min=FALLBACK_MIN_VIEWS, log=print):
    """Priority: target reciter >=1M, any priority reciter >=1M, then (logged) >=500k fallback."""
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
            return sorted(pool, key=lambda c: c["views"], reverse=True)
    return []

def search_candidates(cl, target_key, used_codes, max_duration=MAX_DURATION_SEC, amount=30):
    tags = list(RECITERS_CONFIG[target_key]["tags"])
    for k, r in RECITERS_CONFIG.items():
        if k != target_key:
            tags += r["tags"][:2]
    tags += GENERAL_TAGS
    cands = []
    for tag in tags:
        print(f"\n[Instagram Query] #{tag}")
        for fetch in ("hashtag_medias_top", "hashtag_medias_reels_v1"):
            fn = getattr(cl, fetch, None)
            if not fn:
                continue
            try:
                medias = fn(tag, amount=amount)
            except Exception as e:
                print(f"  [Warning] {fetch}(#{tag}) error: {e}")
                time.sleep(2)
                continue
            for m in medias:
                c = evaluate_media(m, used_codes, max_duration)
                if c:
                    cands.append(c)
        # stop early once enough 1M+ reels for the target reciter are found
        if sum(1 for c in cands if c["reciter_key"] == target_key and c["views"] >= MIN_VIEWS) >= 3:
            break
    return cands

def build_reel_metadata(chosen):
    from metadata_optimizer import build_viral_quran_metadata
    rec = RECITERS_CONFIG[chosen["reciter_key"]]
    return build_viral_quran_metadata(chosen["caption"], rec["name_ar"], rec["hashtag"], rec["name_en"], chosen["views"])

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
        print("[Error] No reel matched policy (<45s, >=500k views, priority reciter).")
        return None
    import dedupe_guard
    for cand in ranked[:6]:
        f, dd = dedupe_guard.acquire_candidate("quran", cand, HISTORY_FILE, download_reel)
        if f:
            meta = build_reel_metadata(cand)
            print(f"★ SELECTED {cand['code']} | {cand['reciter_key']} | {cand['views']:,} views | {cand['duration']}s")
            print(f"  Title: {meta['title']}")
            return {"video": str(f), "code": cand["code"], "title": meta["title"],
                    "description": meta["description"], "tags": meta["tags"],
                    "reciter": RECITERS_CONFIG[cand["reciter_key"]]["name_ar"], "views": cand["views"],
                    "dedupe": dd}
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
