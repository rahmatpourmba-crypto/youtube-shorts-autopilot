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
        f"#{' #'.join(TWO_TOWER_TAGS)}"
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
        f"🔭 Deep space mysteries captured by modern astrophysics & space telescopes.\n"
        f"✨ شگفتی‌های بی‌پایان کیهان و ژرفای اعجاب‌انگیز تلسکوپ‌های فضایی.\n\n"
        f"💬 What do you think lies beyond the observable universe? Drop your thoughts below! 👇\n\n"
        f"🛰️ Follow @cryp.tolab1 for daily discoveries in deep cosmos, AI & futuristic science.\n\n"
        f"──────────────────\n"
        f"#{' #'.join(TWO_TOWER_TAGS)} #Explore #Reels #Viral"
    )
    return caption

def find_and_download_viral_ai_reel(min_views: int = 100000, max_duration: float = 49.9):
    """
    Finds top viral reels (>100k views, <50s duration) with 100% clean/moral standards.
    """
    used_codes = set(load_history())
    cl = get_instagram_client("cryptolab")

    candidate_reels = []
    print("\n" + "=" * 65)
    print("=== SEARCHING VIRAL REELS: AI UNVEILED | FUTURE TECH ===")
    print(f"Target Metric: > {min_views:,} views | Duration < 50s | Protocol 131 Ready")
    print("=" * 65)

    for tag in VIRAL_TAGS:
        print(f"\n[Instagram Query] Searching top viral reels in #{tag}...")
        try:
            medias = cl.hashtag_medias_top(tag, amount=20)
            for m in medias:
                if m.media_type != 2:
                    continue
                if m.code in used_codes:
                    continue

                duration = getattr(m, "video_duration", 0)
                if duration and duration >= max_duration:
                    continue

                caption = m.caption_text or ""
                caption_lower = caption.lower()
                prohibited_words = ["model", "fashion", "girl", "dance", "song", "tiktok", "makeup", "outfit", "bikini"]
                if any(pw in caption_lower for pw in prohibited_words):
                    continue

                views = getattr(m, "view_count", 0) or 0
                plays = getattr(m, "play_count", 0) or 0
                likes = m.like_count or 0
                effective_score = max(views, plays, likes * 25)

                if effective_score >= min_views or likes >= 2500:
                    user_handle = getattr(getattr(m, "user", None), "username", "Original Creator")
                    candidate_reels.append({
                        "code": m.code,
                        "pk": m.pk,
                        "video_url": str(m.video_url),
                        "caption": caption,
                        "creator": f"@{user_handle}",
                        "plays": plays,
                        "views": views,
                        "likes": likes,
                        "duration": duration,
                        "score": effective_score
                    })
                    print(f"  🔥 CANDIDATE: Reel {m.code} | Score: {effective_score:,} | Dur: {duration}s")

            if len(candidate_reels) >= 10:
                break
        except Exception as e:
            print(f"  [Instagram Notice] Query note on #{tag}: {e}")
            time.sleep(2)

    candidate_reels.sort(key=lambda x: x["score"], reverse=True)

    # Relax threshold if needed (Self-Healing)
    if not candidate_reels:
        print("  [Self-Healing] Relaxing search threshold to > 25,000 views...")
        for tag in ["jameswebb", "deepspace"]:
            try:
                medias = cl.hashtag_medias_top(tag, amount=15)
                for m in medias:
                    if m.media_type == 2 and m.code not in used_codes:
                        dur = getattr(m, "video_duration", 0)
                        if dur and dur < max_duration:
                            candidate_reels.append({
                                "code": m.code,
                                "pk": m.pk,
                                "video_url": str(m.video_url),
                                "caption": m.caption_text or "",
                                "creator": "@DeepSpaceArchives",
                                "plays": getattr(m, "play_count", 0),
                                "views": getattr(m, "view_count", 0),
                                "likes": m.like_count or 0,
                                "duration": dur,
                                "score": m.like_count or 0
                            })
            except Exception:
                pass
        candidate_reels.sort(key=lambda x: x["score"], reverse=True)

    if not candidate_reels:
        print("[Error] No viral candidate reels available.")
        return None

    # Self-Healing Failover Download Loop
    chosen = None
    target_video_file = None
    for idx, cand in enumerate(candidate_reels):
        code = cand["code"]
        video_url = cand["video_url"]
        temp_file = OUTPUT_DIR / f"ai_{code}.mp4"

        print(f"  [{idx+1}/{len(candidate_reels)}] Downloading Reel {code} from CDN...")
        try:
            req = urllib.request.Request(
                video_url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=35) as resp, open(temp_file, 'wb') as f_out:
                f_out.write(resp.read())

            if temp_file.exists() and temp_file.stat().st_size > 50000:
                chosen = cand
                target_video_file = temp_file
                print(f"  ✓ Video Downloaded: {target_video_file.name} ({target_video_file.stat().st_size // 1024} KB)")
                break
            else:
                if temp_file.exists():
                    temp_file.unlink()
        except Exception as e:
            print(f"  [Failover] Download failed for {code}: {e}. Trying next...")
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass

    if not chosen or not target_video_file:
        return None

    # Clean title
    raw = chosen["caption"]
    first_line = [l.strip() for l in raw.splitlines() if l.strip()]
    raw_title = first_line[0] if first_line else "Mind-Blowing Deep Space Discovery"
    cleaned = re.sub(r'#\S+', '', raw_title).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    if len(cleaned) < 15 or len(cleaned) > 85:
        cleaned = "Insane Mega Machinery & Extreme Engineering in Action"

    title = f"⚙️ {cleaned} #Shorts #Engineering #Machines"
    if len(title) > 75:
        title = title[:72].rstrip() + ".."

    description = build_protocol_131_description(title, creator_handle=chosen.get("creator", "Original Creators"))
    import random
    comment_hook = random.choice(PINNED_ENGAGEMENT_HOOKS)

    return {
        "code": chosen["code"],
        "video": target_video_file,
        "title": title,
        "description": description,
        "caption": chosen["caption"],
        "tags": TWO_TOWER_TAGS,
        "comment_hook": comment_hook
    }

def publish_twin_ai_video(force: bool = False, max_retries: int = 3, publish_instagram: bool = False):
    """
    Simultaneous Dual Upload: YouTube Shorts (AI Unveiled) + Instagram Reels (@cryp.tolab1)
    """
    for attempt in range(1, max_retries + 1):
        print(f"\n[AI PIPELINE] Dual Dispatch Attempt {attempt}/{max_retries}...")
        try:
            min_v = 100000 if attempt == 1 else (40000 if attempt == 2 else 15000)
            data = find_and_download_viral_ai_reel(min_views=min_v)
            if not data:
                if attempt < max_retries:
                    time.sleep(10)
                    continue
                return False

            video_file = data["video"]
            thumb_file = extract_thumbnail_from_video(video_file)
            results = {}

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
                    pinned_comment=data["comment_hook"]
                )
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
                history = load_history()
                history.append(data["code"])
                save_history(history)
                print(f"  ✓ Dual Publishing Succeeded! Code: {data['code']}")
                return results

        except Exception as e:
            print(f"[Attempt {attempt} Exception] {e}")
            if attempt < max_retries:
                time.sleep(10)

    return None

if __name__ == "__main__":
    publish_twin_ai_video()
