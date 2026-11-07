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

# SAFETY POLICY:
# Personal accounts (like @abdol_basit_rahmatpour) are strictly decoupled and never
# logged into by automated cloud runners to guarantee 100% account security and privacy.
ACCOUNTS = {
    "quran": {
        "username": "",  # Unlinked for user account protection
        "password": "",
        "session_file": BASE_DIR / "ig_session_quran.json",
        "display": "Personal Account (Protected & Unlinked)"
    },
    "cryptolab": {
        "username": "cryp.tolab1",
        "password": os.environ.get("IG_PASSWORD_CRYPTOLAB", ""),
        "session_file": BASE_DIR / "ig_session_cryptolab.json",
        "display": "@cryp.tolab1"
    },
    "cars": {
        "username": "cryp.tolab1",
        "password": os.environ.get("IG_PASSWORD_CRYPTOLAB", ""),
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
    Returns an instagrapi Client with strict account safety guards.
    Owner personal accounts are permanently shielded from programmatic cloud logins.
    """
    cl = Client()
    cl.delay_range = [2, 5]

    acc = ACCOUNTS.get(niche, {})
    username = acc.get("username", "")

    # STRICT SAFETY SHIELD: Never attempt programmatic login with personal user accounts
    if not username or username == "abdol_basit_rahmatpour":
        print(f"  [Instagram Safety Shield] Cloud login disabled for '{niche}' to protect user account safety.")
        return cl

    session_path = acc.get("session_file")
    logged_in = False

    if session_path and session_path.exists():
        try:
            cl.load_settings(session_path)
            logged_in = True
        except Exception as e:
            print(f"  [Instagram-{niche.upper()}] Session notice: {e}")

    if not logged_in and acc.get("password"):
        try:
            cl.login(username, acc["password"])
            if session_path:
                cl.dump_settings(session_path)
        except Exception as e:
            print(f"  [Instagram-{niche.upper()}] Login notice: {e}")

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
    if not acc.get("username"):
        print(f"  [Instagram Notice] Upload skipped for '{niche}' (account unlinked for safety).")
        return None

    target_video = Path(video_path)
    if not target_video.exists():
        print(f"  [Instagram Error] Video file not found: {video_path}")
        return None

    cl = get_instagram_client(niche)
    return None
