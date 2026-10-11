import os
import sys
import json
import time
from pathlib import Path
from instagrapi import Client

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent

ACCOUNTS = {
    "quran": {
        "username": "abdol_basit_rahmatpour",
        "password": os.environ.get("IG_PASSWORD_QURAN", "2899813366"),
        "session_file": BASE_DIR / "ig_session_quran.json",
        "display": "@abdol_basit_rahmatpour"
    },
    "cryptolab": {
        "username": "cryp.tolab1",
        "password": os.environ.get("IG_PASSWORD_CRYPTOLAB", "2899813366"),
        "session_file": BASE_DIR / "ig_session_cryptolab.json",
        "display": "@cryp.tolab1"
    }
}

def get_instagram_client(niche: str = "quran") -> Client:
    """
    Returns an authenticated instagrapi Client using saved persistent session settings.
    """
    acc = ACCOUNTS.get(niche, ACCOUNTS["quran"])
    cl = Client()
    cl.delay_range = [2, 5]

    session_path = acc["session_file"]
    logged_in = False

    if session_path.exists():
        try:
            print(f"  [Instagram-{niche.upper()}] Loading persistent session from {session_path.name}...")
            cl.load_settings(session_path)
            cl.login(acc["username"], acc["password"])
            logged_in = True
            print(f"  [Instagram-{niche.upper()}] Session verified for {acc['display']}.")
        except Exception as e:
            print(f"  [Instagram-{niche.upper()}] Session restore failed ({e}), re-authenticating...")

    if not logged_in:
        print(f"  [Instagram-{niche.upper()}] Fresh login for {acc['display']}...")
        cl.login(acc["username"], acc["password"])
        cl.dump_settings(session_path)
        print(f"  [Instagram-{niche.upper()}] Logged in & session saved to {session_path.name}.")

    return cl

def build_bilingual_quran_caption(base_title: str) -> str:
    """
    Builds a high-retention, high-engagement Persian & Kurdish (Sorani) bilingual caption
    optimized for Instagram Explore & Reels algorithms.
    """
    caption = (
        "🌿 تلاوت خاشعانه و آرامش‌بخش قرآن کریم 🕊️\n"
        "ئارامی دڵ و ڕووح بە دەنگی قورئانی پیرۆز ✨\n\n"
        "✨ قال الله تعالى: ﴿الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾\n\n"
        "🤍 برای آرامش دلت گوش کن و برای عزیزانت بفرست..\n"
        "🤍 بۆ ئارامی دڵ و ڕووحت گوێ بگرە و بۆ ئازیزانت بنێرە..\n\n"
        "🌿 صلوات بر پیامبر رحمت بفرستید | صەڵاوات لەسەر پێغەمبەر (د.خ) لێبدەن 🤍\n\n"
        "─── ⋆⋅☆⋅⋆ ───\n"
        "#قرآن #تلاوت #قورئان #ئارامی_دڵ #تلاوة_خاشعة #راحة_نفسية #کوردستان #مهاباد #سنندج #سلیمانی #اربیل #reels #explore #quran"
    )
    return caption

def publish_instagram_reel(video_path: str, caption: str, niche: str = "quran", thumbnail_path: str = None):
    """
    Uploads a vertical 9:16 video as an Instagram Reel completely FREE using direct instagrapi.
    """
    acc = ACCOUNTS.get(niche, ACCOUNTS["quran"])
    target_video = Path(video_path)

    if not target_video.exists():
        print(f"  [Instagram Error] Video file does not exist: {video_path}")
        return None

    try:
        print(f"  [Instagram-{niche.upper()}] Connecting to Instagram as {acc['display']}...")
        cl = get_instagram_client(niche=niche)

        print(f"  [Instagram-{niche.upper()}] Uploading Reel ({target_video.name})...")
        thumb = Path(thumbnail_path) if thumbnail_path and Path(thumbnail_path).exists() else None

        media = cl.clip_upload(
            path=target_video,
            caption=caption,
            thumbnail=thumb
        )

        media_pk = media.pk
        reel_code = media.code
        reel_url = f"https://www.instagram.com/reel/{reel_code}/"
        print(f"  [Instagram Success] Reel published to {acc['display']}! URL: {reel_url}")
        return {
            "status": "success",
            "media_pk": media_pk,
            "code": reel_code,
            "url": reel_url
        }
    except Exception as e:
        print(f"  [Instagram Error] Failed to publish reel to {acc['display']}: {e}")
        return None

if __name__ == "__main__":
    print("Testing Instagram Clients...")
    for n in ["quran", "cryptolab"]:
        try:
            cl = get_instagram_client(n)
            print(f"✓ {n}: Connected successfully as {cl.username}")
        except Exception as e:
            print(f"✗ {n}: {e}")
