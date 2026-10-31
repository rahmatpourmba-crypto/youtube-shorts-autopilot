import os
import sys
import json
import time
import re
import urllib.request
import subprocess
from pathlib import Path

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "used_ai_viral_reels.json"
OUTPUT_DIR = BASE_DIR / "output" / "viral_ai_reels"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

from instagram_publisher import get_instagram_client, publish_instagram_reel
from youtube_uploader import upload_short, CHANNELS

VIRAL_TAGS = [
    "heavyequipment",
    "heavymachinery",
    "megaengineering",
    "megamachines",
    "excavator",
    "constructionequipment",
    "satisfyingmachines",
    "miningequipment",
    "hydraulicpress",
    "industrialmachines"
]

TWO_TOWER_TAGS = [
    "Shorts", "HeavyMachinery", "MegaEngineering", "HeavyEquipment", "Construction",
    "Mining", "Satisfying", "Machines", "Industrial", "Engineering",
    "Excavator", "FutureTech", "Technology", "Viral", "Trending"
]

PINNED_ENGAGEMENT_HOOKS = [
    "🚜 Would you dare to operate this 400-ton monster machine? Yes or No? Drop your answer below! 👇⚡",
    "⚙️ Rate the sheer power of this engineering feat from 1 to 10! 👇🔥",
    "🏗️ Did you know this machine generates over 4,000 horsepower? What's your dream machine to drive? 👇🚜",
    "💥 React with 🚜 if you love heavy equipment, or ⚙️ if you appreciate mega engineering!",
    "🌊 What's more terrifying: Operating this machine on a cliff edge or on an offshore oil rig? Drop below! 👇"
]

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

def extract_thumbnail_from_video(video_path: Path) -> Path:
    """
    Extracts high-res authentic frame using FFmpeg as cover thumbnail.
    """
    thumb_path = video_path.with_suffix(".jpg")
    try:
        cmd = [
            "ffmpeg", "-y",
            "-ss", "00:00:01.500",
            "-i", str(video_path),
            "-vframes", "1",
            "-q:v", "2",
            str(thumb_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if thumb_path.exists() and thumb_path.stat().st_size > 1000:
            return thumb_path
    except Exception:
        pass
    return None

def build_protocol_131_description(title: str, creator_handle: str = "Respective Creators") -> str:
    """
    PROTOCOL 131: TRANSFORMATIONAL CURATION & EDUCATIONAL ARCHIVAL NOTICE
    Strictly complies with Section 107 of US Copyright Act (Fair Use)
    to guarantee 100% Monetization approval and immunity against Reused Content.
    """
    description = (
        f"⚙️ {title}\n\n"
        f"🚜 Engineering & Technical Breakdown:\n"
        f"Witness the pinnacle of modern mechanical engineering, heavy machinery, and industrial mega-projects. "
        f"These engineering wonders harness thousands of metric horsepower and advanced hydraulic pressures to achieve the impossible.\n\n"
        f"💬 Would you dare to operate this machine? Share your thoughts below!\n"
        f"✨ Subscribe to @AIUnveiledFutureTech for daily journeys across heavy engineering and futuristic machinery!\n\n"
        f"─── ⋆⋅☆⋅⋆ ───\n"
        f"⚖️ Copyright & Fair Use Archival Notice:\n"
        f"This video is curated and transformed for educational, research, and scientific commentary purposes "
        f"under the Fair Use doctrine (Section 107 of the US Copyright Act of 1976).\n"
        f"• Attribution: Visuals curated from public engineering archives and original creators ({creator_handle}).\n"
        f"• All rights remain with respective original copyright holders.\n"
        f"• For inquiries, credit attribution, or removal requests, please contact: workonlin63@gmail.com\n\n"
        f"─── ⋆⋅☆⋅⋆ ───\n"
        f"#AI #tech #shorts #technology #engineering #future #viral #science"
    )
    return description

def build_instagram_bilingual_caption(title: str) -> str:
    """
    Bilingual Instagram Explore Reel caption for @cryp.tolab1.
    """
    caption = (
        f"⚙️ {title}\n\n"
        f"🚜 Witness the raw power of modern heavy machinery and mega engineering projects.\n"
        f"✨ غول‌های صنعت و ابرپروژه‌های مهندسی شگفت‌انگیز جهان.\n\n"
        f"💬 Would you dare to operate this monster machine? Drop your thoughts below! 👇\n\n"
        f"⚡ Follow @cryp.tolab1 for daily discoveries in heavy machines, future engineering & technology.\n\n"
        f"──────────────────\n"
        f"#{' #'.join(TWO_TOWER_TAGS)} #Explore #Reels #Viral"
    )
    return caption

# =====================================================================
# Owner policy (AI / Cosmos / Mega Machines channel), mirrors Quran PR #3:
#   viral Instagram reels, duration < 45s, REAL views >= 1,000,000
#   (fallback >= 500k only if nothing qualifies; logged as [Fallback]).
#   No likes-based score: only view_count / play_count are trusted.
# =====================================================================
MAX_DURATION_SEC = 45.0
MIN_VIEWS = 1_000_000
FALLBACK_MIN_VIEWS = 500_000

# Extra AI / cosmos hashtags searched after the machine tags
EXTRA_TAGS = ["artificialintelligence", "robotics", "futuretech", "space", "jameswebb", "deepspace"]

# Whole-word / phrase matched (see caption_is_blocked). The old raw-substring check
# dropped legit tech reels: "model" hit "AI model" / "3D model" / "remodel", "song" hit
# "Samsong"-style brand typos, "dance" hit "guidance"/"abundance", "girl" hit "girlder".
# "model" is narrowed to fashion phrases so "AI model" / "scale model" pass.
PROHIBITED_KEYWORDS = ["fashion model", "female model", "fashion", "girl", "girls", "dance", "dancing",
                       "song", "tiktok", "makeup", "outfit", "bikini"]

# Shared halal/moral blacklist still applies (whole-word), except a few words that are
# ordinary engineering/tech vocabulary for this channel and caused false positives:
# "AI model", "rock drilling/crusher", "steel bar", "trans(mission)", "beat the record",
# "pop(s) up", "stake" (survey stakes). Quran channel's filter is untouched.
AI_TECH_SAFE_TERMS = {"model", "rock", "bar", "beat", "pop", "stake", "trans"}

def _tokens(text: str):
    return re.findall(r"[\w\u0600-\u06FF]+", (text or "").lower().replace("#", " ").replace("_", " "))

def caption_is_blocked(caption: str):
    """Return matched keyword if blocked, else None. Whole-word / phrase match (no substrings)."""
    joined = " " + " ".join(_tokens(caption)) + " "
    for kw in PROHIBITED_KEYWORDS:
        k = " " + " ".join(_tokens(kw)) + " "
        if k.strip() and k in joined:
            return kw
    try:
        from halal_content_filter import FORBIDDEN_KEYWORDS
    except ImportError:
        FORBIDDEN_KEYWORDS = []
    low = (caption or "").lower()
    for word in FORBIDDEN_KEYWORDS:
        if word.lower() in AI_TECH_SAFE_TERMS:
            continue
        if re.search(r"\b" + re.escape(word.lower()) + r"\b", low):
            return f"halal:{word}"
    return None

def media_views(m) -> int:
    """Real views only (view_count / play_count). Likes are NOT converted to views."""
    return int(max(getattr(m, "view_count", 0) or 0, getattr(m, "play_count", 0) or 0))

def evaluate_media(m, used_codes, max_duration=MAX_DURATION_SEC, log=print):
    if getattr(m, "media_type", None) != 2 or m.code in used_codes:
        return None
    caption = getattr(m, "caption_text", "") or ""
    blocked = caption_is_blocked(caption)
    if blocked:
        log(f"  [Skipped] Reel {m.code} filtered keyword: '{blocked}'")
        return None
    dur = float(getattr(m, "video_duration", 0) or 0)
    if not dur or dur >= max_duration:
        return None
    user_handle = getattr(getattr(m, "user", None), "username", None) or "Original Creator"
    return {"code": m.code, "pk": getattr(m, "pk", None), "video_url": str(getattr(m, "video_url", "")),
            "caption": caption, "creator": f"@{user_handle}", "views": media_views(m),
            "likes": getattr(m, "like_count", 0) or 0, "duration": dur}

def rank_candidates(cands, min_views=MIN_VIEWS, fallback_min=FALLBACK_MIN_VIEWS, log=print):
    uniq = {}
    for c in cands:
        uniq.setdefault(c["code"], c)
    cands = list(uniq.values())
    for threshold, label in ((min_views, "primary"), (fallback_min, "FALLBACK")):
        pool = [c for c in cands if c["views"] >= threshold]
        if pool:
            if label == "FALLBACK":
                log(f"  [Fallback] No reel >= {min_views:,} views; using best >= {fallback_min:,}.")
            return sorted(pool, key=lambda c: c["views"], reverse=True)
    return []

def search_candidates(cl, used_codes, max_duration=MAX_DURATION_SEC, amount=30):
    cands = []
    for tag in VIRAL_TAGS + EXTRA_TAGS:
        print(f"\n[Instagram Query] #{tag}")
        for fetch in ("hashtag_medias_top", "hashtag_medias_reels_v1"):
            fn = getattr(cl, fetch, None)
            if not fn:
                continue
            try:
                medias = fn(tag, amount=amount)
            except Exception as e:
                print(f"  [Instagram Notice] {fetch}(#{tag}): {e}")
                time.sleep(2)
                continue
            for m in medias:
                c = evaluate_media(m, used_codes, max_duration)
                if c:
                    cands.append(c)
        if sum(1 for c in cands if c["views"] >= MIN_VIEWS) >= 5:
            break
    return cands

def download_reel(cand):
    temp_file = OUTPUT_DIR / f"ai_{cand['code']}.mp4"
    try:
        req = urllib.request.Request(cand["video_url"], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=35) as resp, open(temp_file, 'wb') as f_out:
            f_out.write(resp.read())
        if temp_file.exists() and temp_file.stat().st_size > 50000:
            return temp_file
    except Exception as e:
        print(f"  [Failover] Download failed for {cand['code']}: {e}")
    if temp_file.exists():
        try:
            temp_file.unlink()
        except Exception:
            pass
    return None

def find_and_download_viral_ai_reel(min_views: int = MIN_VIEWS, max_duration: float = MAX_DURATION_SEC, client=None):
    import dedupe_guard
    dedupe_guard.sync_latest()
    used_codes = set(load_history())
    if client is None:
        client = get_instagram_client("cryptolab")
    print("=" * 65)
    print(f"=== VIRAL AI/TECH SEARCH | views >= {min_views:,} | < {max_duration:.0f}s ===")
    cands = search_candidates(client, used_codes, max_duration)
    ranked = rank_candidates(cands, min_views, min(FALLBACK_MIN_VIEWS, min_views))
    if not ranked:
        print("[Error] No reel matched policy (<45s, >=500k real views).")
        return None
    from metadata_optimizer import build_viral_ai_metadata
    for cand in ranked[:6]:
        f, dd = dedupe_guard.acquire_candidate("ai", cand, HISTORY_FILE, download_reel)
        if f:
            meta = build_viral_ai_metadata(cand["caption"], views=cand["views"])
            description = build_protocol_131_description(meta["title"], creator_handle=cand["creator"])
            import random
            print(f"★ SELECTED {cand['code']} | {cand['views']:,} views | {cand['duration']}s")
            print(f"  Title: {meta['title']}")
            return {"code": cand["code"], "video": f, "title": meta["title"], "description": description,
                    "caption": cand["caption"], "tags": meta["tags"], "views": cand["views"],
                    "comment_hook": random.choice(PINNED_ENGAGEMENT_HOOKS), "dedupe": dd}
    print("[Error] Could not download any ranked candidate.")
    return None

def publish_twin_ai_video(force: bool = False, max_retries: int = 2, publish_instagram: bool = False):
    """
    Simultaneous Dual Upload: YouTube Shorts (AI Unveiled) + Instagram Reels (@cryp.tolab1)
    """
    for attempt in range(1, max_retries + 1):
        print(f"\n[AI PIPELINE] Dual Dispatch Attempt {attempt}/{max_retries}...")
        try:
            # Same policy on every attempt (no threshold decay below the 500k fallback)
            data = find_and_download_viral_ai_reel()
            if not data:
                if attempt < max_retries:
                    time.sleep(10)
                    continue
                return False

            video_file = data["video"]
            thumb_file = extract_thumbnail_from_video(video_file)
            results = {}
            duplicate_on_youtube = False

            # 1. Upload to YouTube Shorts
            try:
                print(f"\n[YouTube-AI] Uploading to {CHANNELS['ai']['name']}...")
                yt_res = upload_short(
                    channel_key="ai",
                    video_path=str(video_file),
                    title=data["title"],
                    description=data["description"],
                    tags=data["tags"],
                    category_id="28",
                    thumbnail_path=str(thumb_file) if thumb_file else None,
                    pinned_comment=data["comment_hook"],
                    source_code=data["code"]
                )
                if yt_res and yt_res.get("duplicate"):
                    print(f"[YouTube-AI] {data['code']} already on channel ({yt_res.get('video_id')}) -> not re-uploaded")
                    yt_res = None
                    duplicate_on_youtube = True
                results["youtube"] = yt_res
            except Exception as e:
                print(f"[YouTube-AI Upload Error] {e}")

            # 2. Instagram Decoupled (Bypassed by default)
            if publish_instagram:
                try:
                    print(f"\n[Instagram-Reels] Uploading to @cryp.tolab1...")
                    ig_caption = build_instagram_bilingual_caption(data["title"])
                    ig_res = publish_instagram_reel(
                        video_path=str(video_file),
                        caption=ig_caption,
                        niche="cryptolab",
                        thumbnail_path=str(thumb_file) if thumb_file else None
                    )
                    results["instagram"] = ig_res
                except Exception as e:
                    print(f"[Instagram-Reels Upload Error] {e}")
            else:
                print("[Instagram Status] Decoupled: Reserved for dedicated Persian sponsorship pipeline.")

            if results.get("youtube") or results.get("instagram"):
                import dedupe_guard
                dd = data.get("dedupe") or {}
                vid = (results.get("youtube") or {}).get("video_id")
                dedupe_guard.record_and_push("ai", data["code"], vid, data["title"],
                                             dd.get("fp"), dd.get("sha256"), dd.get("phash"))
                print(f"  ✓ Dual Publishing Succeeded! Code: {data['code']}")
                return results

            # Nothing was published: release the claim so this reel is not burned forever.
            # Exception: if YouTube says the reel is already on the channel, the claim is correct.
            if not duplicate_on_youtube:
                import dedupe_guard
                dd = data.get("dedupe") or {}
                print(f"[AI Pipeline] Nothing published for {data['code']}; releasing claim for a later retry")
                dedupe_guard.release_claim("ai", dd.get("claim_keys") or [data["code"]], HISTORY_FILE)
                return None
            return None

        except Exception as e:
            print(f"[Attempt {attempt} Exception] {e}")
            if attempt < max_retries:
                time.sleep(10)

    return None

if __name__ == "__main__":
    publish_twin_ai_video()
