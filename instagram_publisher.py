import os
import sys
import json
import time
import subprocess
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

def publish_instagram_reel(video_path: str, caption: str, niche: str = "quran", thumbnail_path: str = None, initial_comment: str = None):
    """
    Uploads a vertical 9:16 video as an Instagram Reel.
    """
    acc = ACCOUNTS.get(niche, ACCOUNTS["quran"])
    target_video = Path(video_path)
    if not target_video.exists():
        print(f"  [Instagram Error] Video file not found: {video_path}")
        return None

    try:
        print(f"  [Instagram-{niche.upper()}] Connecting to Instagram as {acc['display']}...")
        cl = get_instagram_client(niche=niche)

        # Automatic thumbnail extraction via FFmpeg if missing
        if not thumbnail_path or not Path(thumbnail_path).exists():
            extracted_thumb = extract_thumbnail_from_video(target_video)
            thumbnail_path = str(extracted_thumb) if extracted_thumb else None

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

        # Update saved session
        cl.dump_settings(acc["session_file"])

        if initial_comment:
            try:
                cl.media_comment(media_pk, initial_comment)
                print(f"  [Instagram Success] Pinned initial comment posted to {acc['display']}!")
            except Exception as ce:
                print(f"  [Instagram Notice] Could not post initial comment: {ce}")

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
