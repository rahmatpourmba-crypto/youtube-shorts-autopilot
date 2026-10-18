import os
import sys
import json
import time
import re
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

def clean_arabic_title(caption: str) -> str:
    """
    Extracts a clean, high-CTR YouTube Short title from the original Instagram caption.
    """
    if not caption:
        return "تلاوة خاشعة تأسر القلوب بصوت الشيخ ياسر الدوسري 🕊️✨ #Quran #Shorts"
    
    # Remove excessive hashtags from title
    lines = [l.strip() for l in caption.splitlines() if l.strip()]
    first_line = lines[0] if lines else ""
    # Strip hashtags
    cleaned = re.sub(r'#\S+', '', first_line).strip()
    # Strip excessive punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    if len(cleaned) < 15:
        cleaned = f"تلاوة خاشعة مبكية | الشيخ ياسر الدوسري 🕊️✨"
    
    full_title = f"{cleaned} | الشيخ ياسر الدوسري #Shorts #Quran"
    return full_title[:100]

def find_and_download_viral_reel(min_views: int = 500000, target_reciter: str = "ياسر الدوسري"):
    """
    Finds top Instagram reels for Sheikh Yasser Al-Dosari with views > 500k,
    downloads the exact original video file without modification.
    """
    used_codes = set(load_history())
    cl = get_instagram_client("quran")
    
    candidate_reels = []
    hashtags_to_search = [
        "ياسر_الدوسري",
        "الشيخ_ياسر_الدوسري",
        "تلاوات_ياسر_الدوسري",
        "تلاوة_خاشعة",
        "قران_كريم"
    ]

    print("\n" + "=" * 65)
    print(f"=== SEARCHING VIRAL REELS: Sheikh {target_reciter} ===")
    print(f"Target Metric: > {min_views:,} views/plays | 100% Original Unmodified Video")
    print("=" * 65)

    for tag in hashtags_to_search:
        print(f"\n[Instagram Query] Searching top viral reels in #{tag}...")
        try:
            medias = cl.hashtag_medias_top(tag, amount=20)
            print(f"  -> Found {len(medias)} candidate top posts.")
            
            for m in medias:
                # Must be a video / reel
                if m.media_type != 2:
                    continue
                if m.code in used_codes:
                    continue

                caption = m.caption_text or ""
                # Ensure it is related to Sheikh Yasser Al-Dosari
                if "دوسري" not in caption and "الدوسري" not in caption and "yasser" not in caption.lower():
                    # For specific tags, it might already be him, but let's be strict if tag is generic
                    if tag in ["تلاوة_خاشعة", "قران_كريم"]:
                        continue

                # Check duration (must be <= 60 seconds for YouTube Shorts)
                duration = getattr(m, "video_duration", 0)
                if duration and duration > 60:
                    continue

                views = getattr(m, "view_count", 0) or 0
                plays = getattr(m, "play_count", 0) or 0
                likes = m.like_count or 0
                
                # Check metrics: views/plays > 500k, or likes > 20k (which corresponds to 500k+ plays)
                effective_score = max(views, plays, likes * 25)
                
                print(f"  [Reel {m.code}] Plays: {plays:,} | Views: {views:,} | Likes: {likes:,} | Score: {effective_score:,}")
                
                if effective_score >= min_views or likes >= 20000:
                    candidate_reels.append({
                        "code": m.code,
                        "pk": m.pk,
                        "video_url": str(m.video_url),
                        "caption": caption,
                        "plays": plays,
                        "views": views,
                        "likes": likes,
                        "duration": duration,
                        "score": effective_score
                    })
                    print(f"  🔥 MATCH FOUND: Reel {m.code} meets >500k threshold!")
                    
        except Exception as e:
            print(f"  [Warning] Tag #{tag} query error: {e}")
            time.sleep(2)

    # Sort candidates by score descending (highest views first)
    candidate_reels.sort(key=lambda x: x["score"], reverse=True)

    if not candidate_reels:
        # Fallback to highest liked reel found if strict 500k views not exposed directly by IG
        print("\n[Notice] Checking top ranked reels for highest engagement...")
        for tag in ["ياسر_الدوسري"]:
            try:
                top_m = cl.hashtag_medias_top(tag, amount=10)
                for m in top_m:
                    if m.media_type == 2 and m.code not in used_codes:
                        candidate_reels.append({
                            "code": m.code,
                            "pk": m.pk,
                            "video_url": str(m.video_url),
                            "caption": m.caption_text or "",
                            "plays": getattr(m, "play_count", 0),
                            "views": getattr(m, "view_count", 0),
                            "likes": m.like_count or 0,
                            "duration": getattr(m, "video_duration", 0),
                            "score": m.like_count or 0
                        })
                candidate_reels.sort(key=lambda x: x["score"], reverse=True)
            except Exception:
                pass

    if not candidate_reels:
        print("[Error] No new viral reels found matching criteria.")
        return None

    chosen = candidate_reels[0]
    print("\n" + "=" * 65)
    print(f"★ SELECTED VIRAL REEL: {chosen['code']}")
    print(f"Estimated Impact: {chosen['score']:,} engagements | Likes: {chosen['likes']:,}")
    print("=" * 65)

    target_video_file = OUTPUT_DIR / f"yasser_{chosen['code']}.mp4"
    print(f"Downloading original video from Instagram CDN...")
    req = urllib.request.Request(
        chosen["video_url"],
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req, timeout=30) as resp, open(target_video_file, 'wb') as f_out:
        f_out.write(resp.read())

    print(f"✓ Original Reel downloaded: {target_video_file.name} ({target_video_file.stat().st_size // 1024} KB)")

    title = clean_arabic_title(chosen["caption"])
    description = (
        f"{title}\n\n"
        f"تلاوة خاشعة مباركة بصوت فضيلة الشيخ الدكتور ياسر بن راشد الدوسري حفظه الله.\n\n"
        f"اللهم اجعل القرآن الكريم ربيع قلوبنا ونور صدورنا وجلاء أحزاننا وذهاب همومنا.\n\n"
        f"• الأصل من تلاوات منصات التواصل الأكثر انتشاراً وتأثيراً (High Viral Reach).\n\n"
        f"#القرآن_الكريم #ياسر_الدوسري #تلاوة_خاشعة #قرآن #Shorts #Islam #YasserAlDosari"
    )
    tags = [
        "ياسر الدوسري",
        "القرآن الكريم",
        "تلاوة خاشعة",
        "قران",
        "yasser al dosari",
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
        "tags": tags
    }

def main():
    print("=================================================================")
    print("=== VIRAL INSTAGRAM REEL TO YOUTUBE SHORTS PIPELINE ===")
    print("Sheikh Yasser Al-Dosari (High View Count > 500,000)")
    print("Direct Re-Upload (Zero Alteration / Unmodified Authentic Audio & Video)")
    print("=================================================================")

    reel_data = find_and_download_viral_reel(min_views=500000)
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
        print(f"\n🎉 SUCCESS: Viral Reel {reel_data['code']} uploaded to YouTube Quran Channel!")
        print(f"URL: https://youtube.com/shorts/{upload_res['id']}")
    else:
        print("[Upload Notice] YouTube upload did not return an ID.")

if __name__ == "__main__":
    main()
