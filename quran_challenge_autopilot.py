#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
👑 ARABIC VIRAL QURAN CHALLENGE SHORTS ENGINE ("نور القرآن | The Holy Light")
Channel: @islamrazekhoshabkhte
Target Geo: Iraq, Algeria, Egypt, Saudi Arabia
Engineered for: >120% APV (Average Percentage Viewed) & High Comment Engagement
=============================================================================
"""

import os
import sys
import time
import json
import re
import random
import hashlib
import shutil
import subprocess
import urllib.request
import argparse
import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Ensure UTF-8 console output on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Directories & Constants
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
DEBUG_FRAMES_DIR = OUTPUT_DIR / "debug_frames"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)
BACKGROUNDS_DIR.mkdir(parents=True, exist_ok=True)
DEBUG_FRAMES_DIR.mkdir(parents=True, exist_ok=True)

STATE_FILE = OUTPUT_DIR / "quran_challenge_state.json"
REGISTRY_FILE = BASE_DIR / "upload_registry.json"

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
]

# Reciter mappings for EveryAyah
RECITERS = {
    "dosari": {
        "name": "القارئ ياسر الدوسري",
        "folder": "Yasser_Ad-Dussary_128kbps",
    },
    "minshawi": {
        "name": "القارئ محمد صديق المنشاوي",
        "folder": "Minshawy_Murattal_128kbps",
    },
    "abdulbasit": {
        "name": "القارئ عبدالباسط عبدالصمد",
        "folder": "Abdul_Basit_Murattal_192kbps",
    },
    "alafasy": {
        "name": "القارئ مشاري العفاسي",
        "folder": "Alafasy_128kbps",
    },
}

# 18 Verified Challenges (Complete Next & Guess Surah)
CHALLENGE_BANK = [
    {
        "id": "duha_4_5",
        "type": "complete_next",
        "reciter": "dosari",
        "difficulty": "متوسط",
        "prompt": (93, 4),
        "answer": (93, 5),
        "distractors": [(93, 6), (93, 8)],
        "friday_priority": False,
    },
    {
        "id": "raad_28",
        "type": "guess_surah",
        "reciter": "dosari",
        "difficulty": "سهل",
        "prompt": (13, 28),
        "options": ["سورة الرعد", "سورة البقرة", "سورة يونس"],
        "correct": 0,
        "friday_priority": False,
    },
    {
        "id": "fajr_27_28",
        "type": "complete_next",
        "reciter": "dosari",
        "difficulty": "سهل",
        "prompt": (89, 27),
        "answer": (89, 28),
        "distractors": [(89, 29), (89, 30)],
        "friday_priority": False,
    },
    {
        "id": "zumar_53",
        "type": "guess_surah",
        "reciter": "minshawi",
        "difficulty": "متوسط",
        "prompt": (39, 53),
        "options": ["سورة غافر", "سورة الزمر", "سورة يوسف"],
        "correct": 1,
        "friday_priority": False,
    },
    {
        "id": "sharh_4_5",
        "type": "complete_next",
        "reciter": "dosari",
        "difficulty": "سهل",
        "prompt": (94, 4),
        "answer": (94, 5),
        "distractors": [(94, 2), (94, 7)],
        "friday_priority": False,
    },
    {
        "id": "taha_46",
        "type": "guess_surah",
        "reciter": "dosari",
        "difficulty": "صعب",
        "prompt": (20, 46),
        "options": ["سورة القصص", "سورة طه", "سورة الشعراء"],
        "correct": 1,
        "friday_priority": False,
    },
    {
        "id": "kahf_10_11",
        "type": "complete_next",
        "reciter": "dosari",
        "difficulty": "صعب",
        "prompt": (18, 10),
        "answer": (18, 11),
        "distractors": [(18, 12), (18, 14)],
        "friday_priority": True,
    },
    {
        "id": "yunus_92",
        "type": "guess_surah",
        "reciter": "dosari",
        "difficulty": "صعب",
        "prompt": (10, 92),
        "options": ["سورة يونس", "سورة الأعراف", "سورة طه"],
        "correct": 0,
        "friday_priority": False,
    },
    {
        "id": "kawthar_1_2",
        "type": "complete_next",
        "reciter": "alafasy",
        "difficulty": "سهل",
        "prompt": (108, 1),
        "answer": (108, 2),
        "distractors": [(108, 3), (103, 2)],
        "friday_priority": False,
    },
    {
        "id": "yusuf_86",
        "type": "guess_surah",
        "reciter": "abdulbasit",
        "difficulty": "سهل",
        "prompt": (12, 86),
        "options": ["سورة الأنبياء", "سورة يوسف", "سورة مريم"],
        "correct": 1,
        "friday_priority": False,
    },
    {
        "id": "mulk_1_2",
        "type": "complete_next",
        "reciter": "alafasy",
        "difficulty": "متوسط",
        "prompt": (67, 1),
        "answer": (67, 2),
        "distractors": [(67, 3), (67, 5)],
        "friday_priority": False,
    },
    {
        "id": "ghafir_44",
        "type": "guess_surah",
        "reciter": "alafasy",
        "difficulty": "صعب جدا",
        "prompt": (40, 44),
        "options": ["سورة غافر", "سورة الشورى", "سورة فصلت"],
        "correct": 0,
        "friday_priority": False,
    },
    {
        "id": "balad_11_12",
        "type": "complete_next",
        "reciter": "minshawi",
        "difficulty": "صعب",
        "prompt": (90, 11),
        "answer": (90, 12),
        "distractors": [(90, 13), (90, 17)],
        "friday_priority": False,
    },
    {
        "id": "baqarah_186",
        "type": "guess_surah",
        "reciter": "dosari",
        "difficulty": "متوسط",
        "prompt": (2, 186),
        "options": ["سورة آل عمران", "سورة البقرة", "سورة النساء"],
        "correct": 1,
        "friday_priority": False,
    },
    {
        "id": "asr_1_2",
        "type": "complete_next",
        "reciter": "abdulbasit",
        "difficulty": "سهل",
        "prompt": (103, 1),
        "answer": (103, 2),
        "distractors": [(102, 1), (104, 1)],
        "friday_priority": False,
    },
    {
        "id": "anbiya_87",
        "type": "guess_surah",
        "reciter": "dosari",
        "difficulty": "متوسط",
        "prompt": (21, 87),
        "options": ["سورة الصافات", "سورة يونس", "سورة الأنبياء"],
        "correct": 2,
        "friday_priority": False,
    },
    {
        "id": "rahman_12_13",
        "type": "complete_next",
        "reciter": "minshawi",
        "difficulty": "متوسط",
        "prompt": (55, 12),
        "answer": (55, 13),
        "distractors": [(55, 14), (55, 10)],
        "friday_priority": False,
    },
    {
        "id": "kahf_46",
        "type": "guess_surah",
        "reciter": "dosari",
        "difficulty": "متوسط",
        "prompt": (18, 46),
        "options": ["سورة الكهف", "سورة لقمان", "سورة الحديد"],
        "correct": 0,
        "friday_priority": True,
    },
]

# ---------------------------------------------------------------------------
# Resolve FFmpeg and FFprobe
# ---------------------------------------------------------------------------
def get_ffmpeg_exe() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise RuntimeError("FFmpeg executable not found! Please install FFmpeg or imageio-ffmpeg.")

def get_ffprobe_exe() -> str:
    exe = shutil.which("ffprobe")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        ff = Path(imageio_ffmpeg.get_ffmpeg_exe())
        probe = ff.parent / ("ffprobe.exe" if sys.platform.startswith("win") else "ffprobe")
        if probe.exists():
            return str(probe)
    except Exception:
        pass
    # Fallback to ffmpeg for media info probe
    return get_ffmpeg_exe()

FFMPEG_BIN = get_ffmpeg_exe()

# ---------------------------------------------------------------------------
# Font Management (Auto-Download)
# ---------------------------------------------------------------------------
AMIRI_FONT_PATH = FONTS_DIR / "Amiri-Bold.ttf"
CAIRO_FONT_PATH = FONTS_DIR / "Cairo-Bold.ttf"
SCHEHERAZADE_FONT_PATH = FONTS_DIR / "ScheherazadeNew-Bold.ttf"

def ensure_fonts():
    """Ensures Amiri-Bold, Cairo-Bold, and ScheherazadeNew-Bold fonts are present in assets/fonts/."""
    urls = {
        AMIRI_FONT_PATH: "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Bold.ttf",
        CAIRO_FONT_PATH: "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf",
        SCHEHERAZADE_FONT_PATH: "https://github.com/google/fonts/raw/main/ofl/scheherazadenew/ScheherazadeNew-Bold.ttf"
    }
    for path, url in urls.items():
        if not path.exists() or path.stat().st_size < 1000:
            print(f"[Fonts] Downloading {path.name}...")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as resp, open(path, "wb") as f:
                    f.write(resp.read())
                print(f"[Fonts] Downloaded {path.name} successfully ({path.stat().st_size} bytes).")
            except Exception as e:
                print(f"[Fonts Warning] Failed to download {path.name}: {e}")
                # Fallback to bundled font if available
                bundled_vazir = BASE_DIR / "Vazirmatn-Bold.ttf"
                if bundled_vazir.exists():
                    shutil.copy(bundled_vazir, path)
                    print(f"[Fonts] Fallback: copied Vazirmatn-Bold to {path.name}")

# ---------------------------------------------------------------------------
# Module A: Headless & Local YouTube OAuth
# ---------------------------------------------------------------------------
def get_youtube_service(client_secrets_path: str = "client_secrets.json"):
    """
    Initializes and returns the authenticated Google YouTube API v3 service.
    1. Restores credentials from environment variables if present (CLIENT_SECRETS_JSON, TOKEN_QURAN_BASE64).
    2. Checks direct env vars (YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN).
    3. Checks token_quran.pickle (Production token for @islamrazekhoshabkhte in GitHub Secrets).
    4. Fallback to local token.json.
    5. Raises clear instructions if missing.
    """
    import base64
    import pickle
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    # 0. Check and restore credentials from base64 env vars (GitHub Secrets integration)
    env_cs_json = os.getenv("CLIENT_SECRETS_JSON")
    if env_cs_json:
        cs_dest = BASE_DIR / client_secrets_path
        if not cs_dest.exists():
            try:
                with open(cs_dest, "w", encoding="utf-8") as f:
                    f.write(env_cs_json)
                print(f"[OAuth] Restored {cs_dest.name} from CLIENT_SECRETS_JSON.")
            except Exception as e:
                print(f"[OAuth Warning] Could not write CLIENT_SECRETS_JSON: {e}")

    env_b64 = os.getenv("TOKEN_QURAN_B64") or os.getenv("TOKEN_QURAN_BASE64")
    token_pickle = BASE_DIR / "token_quran.pickle"
    if env_b64 and not token_pickle.exists():
        try:
            with open(token_pickle, "wb") as pf:
                pf.write(base64.b64decode(env_b64.strip()))
            print(f"[OAuth] Restored {token_pickle.name} from TOKEN_QURAN_BASE64.")
        except Exception as e:
            print(f"[OAuth Warning] Could not write token_quran.pickle from base64: {e}")

    # 1. Environment variables (direct ID / Secret / Refresh Token)
    env_cid = os.getenv("YOUTUBE_CLIENT_ID")
    env_csec = os.getenv("YOUTUBE_CLIENT_SECRET")
    env_reftok = os.getenv("YOUTUBE_REFRESH_TOKEN")

    if env_cid and env_csec and env_reftok:
        print("[OAuth] Using credentials from environment variables (GitHub Actions mode).")
        creds = Credentials(
            token=None,
            refresh_token=env_reftok,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=env_cid,
            client_secret=env_csec,
            scopes=YOUTUBE_SCOPES
        )
        creds.refresh(Request())
        return build("youtube", "v3", credentials=creds)

    # 2. Check token_quran.pickle (Production token for @islamrazekhoshabkhte)
    if token_pickle.exists():
        print(f"[OAuth] Checking credentials from {token_pickle}...")
        try:
            with open(token_pickle, "rb") as pf:
                creds = pickle.load(pf)
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    print("[OAuth] Refreshing token_quran.pickle credentials...")
                    creds.refresh(Request())
                    with open(token_pickle, "wb") as pf:
                        pickle.dump(creds, pf)
            if creds and creds.valid:
                print("[OAuth] Successfully authenticated via token_quran.pickle!")
                return build("youtube", "v3", credentials=creds)
        except Exception as e:
            print(f"[OAuth Warning] Failed to refresh token_quran.pickle: {e}")

    # 3. Fallback to local token.json
    token_file = BASE_DIR / "token.json"
    if token_file.exists():
        print(f"[OAuth] Loading credentials from {token_file}...")
        try:
            with open(token_file, "r", encoding="utf-8") as f:
                token_data = json.load(f)
            creds = Credentials.from_authorized_user_info(token_data, YOUTUBE_SCOPES)
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    print("[OAuth] Refreshing expired credentials...")
                    creds.refresh(Request())
                    with open(token_file, "w", encoding="utf-8") as f:
                        f.write(creds.to_json())
            return build("youtube", "v3", credentials=creds)
        except Exception as e:
            print(f"[OAuth Warning] Failed to load token.json: {e}")

    # Neither exists
    cs_file = Path(client_secrets_path)
    if not cs_file.is_absolute():
        cs_file = BASE_DIR / client_secrets_path

    msg = (
        "\n" + "=" * 70 + "\n"
        "❌ [خطای احراز هویت یوتیوب / YouTube OAuth Required]\n"
        "فایل توکن احراز هویت یافت نشد یا منقضی شده است.\n"
        "برای اتصال خودکار کانال و دریافت توکن، دستور زیر را در خط فرمان اجرا کنید:\n\n"
        f"    python quran_challenge_autopilot.py --mode auth --client-secrets {cs_file.name}\n\n"
        "سپس لینک باز شده را در مرورگر تأیید کنید تا فایل token.json ذخیره گردد.\n"
        "=" * 70 + "\n"
    )
    raise RuntimeError(msg)

def run_auth_flow(client_secrets_path: str = "client_secrets.json"):
    """
    Executes interactive local OAuth flow, creates token.json,
    prints credentials for GitHub Actions, and auto-configures GitHub secrets if gh is present.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow

    cs_file = Path(client_secrets_path)
    if not cs_file.is_absolute():
        cs_file = BASE_DIR / client_secrets_path

    if not cs_file.exists():
        raise FileNotFoundError(f"Client secrets file not found: {cs_file}")

    print(f"[OAuth Auth] Starting OAuth flow with {cs_file}...")
    flow = InstalledAppFlow.from_client_secrets_file(str(cs_file), YOUTUBE_SCOPES)
    creds = flow.run_local_server(port=0)

    token_file = BASE_DIR / "token.json"
    with open(token_file, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    print(f"\n✓ Token saved successfully to: {token_file}")

    with open(cs_file, "r", encoding="utf-8") as f:
        cs_data = json.load(f)
    key = "installed" if "installed" in cs_data else "web"
    client_id = cs_data[key].get("client_id", "")
    client_secret = cs_data[key].get("client_secret", "")
    refresh_token = creds.refresh_token or ""

    print("\n" + "=" * 70)
    print("📋 [GITHUB ACTIONS SECRETS - مقادیر برای ثبت در گیت‌هاب]")
    print("=" * 70)
    print(f"YOUTUBE_CLIENT_ID     : {client_id}")
    print(f"YOUTUBE_CLIENT_SECRET : {client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN : {refresh_token}")
    print("=" * 70 + "\n")

    # Check if gh CLI is available to push secrets automatically
    gh_exe = shutil.which("gh")
    if gh_exe:
        try:
            print("[OAuth] Attempting to set GitHub Secrets via gh CLI...")
            for name, val in [
                ("YOUTUBE_CLIENT_ID", client_id),
                ("YOUTUBE_CLIENT_SECRET", client_secret),
                ("YOUTUBE_REFRESH_TOKEN", refresh_token)
            ]:
                p = subprocess.run([gh_exe, "secret", "set", name, "--body", val], capture_output=True, text=True)
                if p.returncode == 0:
                    print(f"  ✓ Secret {name} set successfully on GitHub.")
                else:
                    print(f"  ⚠️ Could not set secret {name}: {p.stderr.strip()}")
        except Exception as e:
            print(f"  ⚠️ gh secret error: {e}")

# ---------------------------------------------------------------------------
# Module B: One-Time Channel Cleanup & Arabic SEO Rewrite (--mode fix-channel)
# ---------------------------------------------------------------------------
def fix_channel_videos(youtube_service):
    """
    Cleans up algorithm-damaging videos on @islamrazekhoshabkhte:
    1. Sets private: ssimq8jM1lk, hCJd-AtdIm0
    2. Sets unlisted: Iagl53fZ2m4
    3. Rewrites Arabic SEO snippet for: XPPEteGj4WM, CS6zDaLLePQ, pwYSkR9drZs, cmuY2w0srm8
    """
    print("\n" + "=" * 70)
    print("🧹 [CHANNEL CLEANUP & ALGORITHM RESTORATION] پاکسازی ویدیوهای مخل الگوریتم...")
    print("=" * 70)

    # 1. Set private
    for vid_id in ["ssimq8jM1lk", "hCJd-AtdIm0"]:
        try:
            print(f"  • Setting video {vid_id} to private...")
            youtube_service.videos().update(
                part="status",
                body={"id": vid_id, "status": {"privacyStatus": "private"}}
            ).execute()
            print(f"    ✓ Video {vid_id} is now PRIVATE.")
        except Exception as e:
            print(f"    ⚠️ Notice ({vid_id}): {e}")

    # 2. Set unlisted
    try:
        vid_id = "Iagl53fZ2m4"
        print(f"  • Setting duplicate video {vid_id} to unlisted...")
        youtube_service.videos().update(
            part="status",
            body={"id": vid_id, "status": {"privacyStatus": "unlisted"}}
        ).execute()
        print(f"    ✓ Video {vid_id} is now UNLISTED.")
    except Exception as e:
        print(f"    ⚠️ Notice ({vid_id}): {e}")

    # 3. Rewrite Snippets
    updates = {
        "XPPEteGj4WM": {
            "title": "ألا بذكر الله تطمئن القلوب 🤍 تلاوة تريح النفس | ياسر الدوسري #قرآن #shorts",
            "description": (
                "﴿الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾\n"
                "تلاوة خاشعة عطرة بصوت الشيخ ياسر الدوسري تريح القلوب وتزيل الهموم.\n\n"
                "اشترك في قناة نور القرآن 🕊️ ليصلك كل يوم مقطع يريح قلبك.\n\n"
                "#قرآن_كريم #ياسر_الدوسري #تلاوة_خاشعة #راحة_نفسية #العراق #الجزائر #مصر #shorts"
            )
        },
        "CS6zDaLLePQ": {
            "title": "يا أيتها النفس المطمئنة 🤍 تلاوة مبكية بصوت ياسر الدوسري #قرآن #shorts",
            "description": (
                "﴿يَا أَيَّتُهَا النَّفْسُ الْمُطْمَئِنَّةُ ۝ ارْجِعِي إِلَىٰ رَبِّكِ رَاضِيَةً مَّرْضِيَّةً﴾\n"
                "تلاوة تهز المشاعر وتلامس الوجدان من سورة الفجر بصوت الشيخ ياسر الدوسري.\n\n"
                "قناة نور القرآن 🕊️ @islamrazekhoshabkhte\n\n"
                "#قرآن_كريم #ياسر_الدوسري #سورة_الفجر #تلاوة_خاشعة #راحة_نفسية #العراق #الجزائر #مصر #shorts"
            )
        },
        "pwYSkR9drZs": {
            "title": "آية الرزق وتفريج الهم 🤍 ومن يتق الله يجعل له مخرجاً | ياسر الدوسري #shorts",
            "description": (
                "﴿وَمَن يَتَّقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا ۝ وَيَرْزُقْهُ مِنْ حَيْثُ لَا يَحْتَسِبُ﴾\n"
                "آية عظيمة لفتح أبواب الرزق والفرج وتيسير الأمور بصوت الشيخ ياسر الدوسري.\n\n"
                "اشترك في قناة نور القرآن 🕊️ لتعطير يومك بآيات كتاب الله.\n\n"
                "#قرآن_كريم #ياسر_الدوسري #آية_الرزق #تلاوة_خاشعة #راحة_نفسية #العراق #الجزائر #مصر #shorts"
            )
        },
        "cmuY2w0srm8": {
            "title": "فإن مع العسر يسرا 🤍 رسالة أمل لكل مهموم | ياسر الدوسري #قرآن #shorts",
            "description": (
                "﴿فَإِنَّ مَعَ الْعُسْرِ يُسْرًا ۝ إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾\n"
                "بشارة إلهية بالفرج واليسر بعد كل ضيق وعسر بصوت خاشع ومؤثر للشيخ ياسر الدوسري.\n\n"
                "قناة نور القرآن 🕊️\n\n"
                "#قرآن_كريم #ياسر_الدوسري #سورة_الشرح #تلاوة_خاشعة #راحة_نفسية #العراق #الجزائر #مصر #shorts"
            )
        }
    }

    tags = ["قرآن كريم", "ياسر الدوسري", "تلاوة خاشعة", "راحة نفسية", "العراق", "الجزائر", "مصر", "shorts"]

    for vid_id, data in updates.items():
        try:
            print(f"  • Updating SEO & Arabic metadata for {vid_id}...")
            youtube_service.videos().update(
                part="snippet",
                body={
                    "id": vid_id,
                    "snippet": {
                        "title": data["title"],
                        "description": data["description"],
                        "tags": tags,
                        "categoryId": "22",
                        "defaultLanguage": "ar",
                        "defaultAudioLanguage": "ar"
                    }
                }
            ).execute()
            print(f"    ✓ Video {vid_id} metadata rewritten with High-CTR Arabic SEO.")
        except Exception as e:
            print(f"    ⚠️ Notice ({vid_id}): {e}")

    print("=" * 70)
    print("✓ Channel cleanup and metadata update completed successfully!\n")

# ---------------------------------------------------------------------------
# Module C: Quranic Text & Audio Fetching
# ---------------------------------------------------------------------------
def fetch_verse_text(surah: int, ayah: int) -> str:
    """
    Fetches official Uthmani Quranic text from api.alquran.cloud.
    Strips leading Bismillah only when surah != 1 and ayah == 1.
    """
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/quran-uthmani"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["data"]["text"]

        # Strip Bismillah if not Surah Al-Fatihah
        if surah != 1 and ayah == 1:
            for bism in ["بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ", "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ", "﻿بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ "]:
                if raw.startswith(bism):
                    raw = raw[len(bism):].strip()
        return raw.strip()
    except Exception as e:
        print(f"[Quran Cloud API Warning] ({surah}:{ayah}): {e}; checking local fallback...")
        # Local Tanzil fallback
        local_quran = BASE_DIR / "data" / "quran" / "quran-simple.txt"
        if local_quran.exists():
            with open(local_quran, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 3 and int(parts[0]) == surah and int(parts[1]) == ayah:
                        return parts[2]
        raise RuntimeError(f"Could not fetch text for Surah {surah}, Ayah {ayah}")

def download_audio_ayah(reciter_key: str, surah: int, ayah: int) -> Path:
    """
    Downloads EveryAyah audio recitation for given reciter and verse.
    Trims leading/trailing silence and loudness-normalizes to -14 LUFS.
    """
    rec_cfg = RECITERS.get(reciter_key, RECITERS["dosari"])
    url = f"https://everyayah.com/data/{rec_cfg['folder']}/{surah:03d}{ayah:03d}.mp3"
    
    raw_mp3 = OUTPUT_DIR / f"raw_audio_{rec_cfg['folder']}_{surah:03d}{ayah:03d}.mp3"
    clean_wav = OUTPUT_DIR / f"norm_audio_{rec_cfg['folder']}_{surah:03d}{ayah:03d}.wav"

    if clean_wav.exists() and clean_wav.stat().st_size > 10000:
        return clean_wav

    print(f"  [Audio Downloader] Fetching {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as resp, open(raw_mp3, "wb") as f_out:
        f_out.write(resp.read())

    # FFmpeg silence trim + loudnorm normalization (-14 LUFS)
    # silenceremove + loudnorm filter
    af = "silenceremove=start_periods=1:start_duration=0.05:start_threshold=-45dB:stop_periods=1:stop_duration=0.3:stop_threshold=-45dB,loudnorm=I=-14:TP=-1.5:LRA=11"
    cmd = [
        FFMPEG_BIN, "-y", "-hide_banner",
        "-i", str(raw_mp3),
        "-af", af,
        "-c:a", "pcm_s16le",
        str(clean_wav)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return clean_wav

def get_audio_duration(file_path: Path) -> float:
    """Probes exact duration of audio/video file using FFmpeg."""
    cmd = [FFMPEG_BIN, "-hide_banner", "-i", str(file_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", res.stderr)
    if m:
        h, mn, s = m.groups()
        return float(h) * 3600 + float(mn) * 60 + float(s)
    return 5.0

# ---------------------------------------------------------------------------
# Module D: High-End Motion-Designer UI Rendering (Pillow)
# ---------------------------------------------------------------------------
def reshape_arabic(text: str) -> str:
    """Reshapes and applies BiDi algorithm to Arabic strings for Pillow rendering."""
    if not text:
        return ""
    import arabic_reshaper
    from bidi.algorithm import get_display
    config = {
        'delete_harakat': False,
        'support_ligatures': True,
        'OFL': True
    }
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def wrap_arabic_lines(text: str, font, max_width: int) -> list[str]:
    """Wraps Arabic text into lines fitting within max_width pixels."""
    import arabic_reshaper
    from bidi.algorithm import get_display

    words = text.split()
    lines = []
    curr = []
    for w in words:
        test_line = " ".join(curr + [w])
        b = font.getbbox(get_display(arabic_reshaper.reshape(test_line)))
        if (b[2] - b[0]) <= max_width:
            curr.append(w)
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))
    return lines

def draw_luxury_box(draw, x, y, w, h, radius, fill_color, border_color, border_w=3):
    """Draws a 3D glassmorphic luxury card with soft drop shadow and inner top bevel."""
    shadow_offset = 6
    draw.rounded_rectangle([x + 2, y + shadow_offset, x + w + 2, y + h + shadow_offset], radius=radius, fill=(0, 0, 0, 160))
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill_color, outline=border_color, width=border_w)
    # 3D top bevel
    draw.line([x + radius, y + 4, x + w - radius, y + 4], fill=(255, 255, 255, 45), width=2)

def render_quiz_frame(
    badge_title: str,
    reciter_display: str,
    question_text: str,
    options: list[str],
    state: str = "prompt",          # "prompt", "countdown", "reveal"
    countdown_number: int = 3,
    countdown_ratio: float = 1.0,   # 1.0 down to 0.0 for progress bar
    correct_idx: int = -1,
    sub_note: str = ""
) -> Image.Image:
    """
    Renders a pixel-perfect 1080x1920 luxury RGBA frame.
    ZERO EMOJI BUG RULE: Uses clean geometric shapes, borders, and pure Arabic text.
    Respects Shorts UI safe zones (clears bottom 420px and right 130px).
    """
    from PIL import Image, ImageDraw, ImageFont

    ensure_fonts()
    quran_font_to_use = AMIRI_FONT_PATH
    
    font_badge = ImageFont.truetype(str(CAIRO_FONT_PATH), 36)
    font_verse = ImageFont.truetype(str(quran_font_to_use), 56)

    canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # 1. Top Badges (y = 110..245)
    # Channel Mini Handle
    handle_txt = reshape_arabic("@islamrazekhoshabkhte  |  نور القرآن")
    font_handle = ImageFont.truetype(str(CAIRO_FONT_PATH), 24)
    b_h = font_handle.getbbox(handle_txt)
    draw.text(((1080 - (b_h[2] - b_h[0])) // 2, 110), handle_txt, font=font_handle, fill=(203, 213, 225, 220))

    # Top Challenge Badge (Luxury Gold Pill)
    badge_w, badge_h = 800, 85
    bx = (1080 - badge_w) // 2
    by = 155
    draw_luxury_box(draw, bx, by, badge_w, badge_h, radius=42, fill_color=(10, 25, 24, 240), border_color=(234, 179, 8, 255), border_w=3)
    b_txt = reshape_arabic(badge_title)
    bb = font_badge.getbbox(b_txt)
    draw.text((bx + (badge_w - (bb[2] - bb[0])) // 2, by + 18), b_txt, font=font_badge, fill=(254, 240, 138, 255))

    # 2. Upper-Middle Sacred Quran Card (y = 270..780)
    card_w, card_h = 980, 490
    cx = (1080 - card_w) // 2
    cy = 270
    draw_luxury_box(draw, cx, cy, card_w, card_h, radius=36, fill_color=(4, 22, 18, 245), border_color=(212, 175, 55, 255), border_w=3)
    # Inner gold border
    draw.rounded_rectangle([cx + 12, cy + 12, cx + card_w - 12, cy + card_h - 12], radius=28, outline=(234, 179, 8, 80), width=1)

    # Reciter Pill Tag
    rec_w, rec_h = 440, 52
    rx = (1080 - rec_w) // 2
    ry = cy + 20
    draw.rounded_rectangle([rx, ry, rx + rec_w, ry + rec_h], radius=26, fill=(15, 35, 30, 210), outline=(212, 175, 55, 140), width=1)
    font_rec = ImageFont.truetype(str(CAIRO_FONT_PATH), 26)
    r_txt = reshape_arabic(f"🎙️ {reciter_display}")
    br = font_rec.getbbox(r_txt)
    draw.text((rx + (rec_w - (br[2] - br[0])) // 2, ry + 10), r_txt, font=font_rec, fill=(253, 224, 71, 255))

    # Quranic Verse Calligraphy
    verse_lines = wrap_arabic_lines(question_text, font_verse, card_w - 90)
    if len(verse_lines) > 3:
        font_verse = ImageFont.truetype(str(quran_font_to_use), 46)
        verse_lines = wrap_arabic_lines(question_text, font_verse, card_w - 90)

    line_spacing = 74 if len(verse_lines) <= 3 else 62
    total_text_h = len(verse_lines) * line_spacing
    vy = cy + 95 + (350 - total_text_h) // 2

    for line in verse_lines:
        line_bidi = reshape_arabic(line)
        bl = font_verse.getbbox(line_bidi)
        lx = (1080 - (bl[2] - bl[0])) // 2
        # Deep dark drop-shadow for 100% legibility
        draw.text((lx + 3, vy + 4), line_bidi, font=font_verse, fill=(0, 0, 0, 255))
        draw.text((lx + 1, vy + 2), line_bidi, font=font_verse, fill=(0, 0, 0, 200))
        # Crisp lettering
        draw.text((lx, vy), line_bidi, font=font_verse, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(2, 15, 12, 230))
        vy += line_spacing

    # 3. Middle Countdown / Reveal Section (y = 795..990)
    mid_y = 795
    if state == "countdown":
        # Luxury Glowing Gold Progress Bar
        bar_w, bar_h = 880, 20
        bar_x = (1080 - bar_w) // 2
        draw.rounded_rectangle([bar_x, mid_y, bar_x + bar_w, mid_y + bar_h], radius=10, fill=(15, 30, 26, 220), outline=(71, 85, 105, 200), width=1)
        fill_w = int(bar_w * max(0.0, min(1.0, countdown_ratio)))
        if fill_w > 0:
            draw.rounded_rectangle([bar_x, mid_y, bar_x + fill_w, mid_y + bar_h], radius=10, fill=(234, 179, 8, 255))

        # Circular Countdown Timer Badge
        dial_dia = 96
        dx = (1080 - dial_dia) // 2
        dy = mid_y + 36
        draw.ellipse([dx - 4, dy - 4, dx + dial_dia + 4, dy + dial_dia + 4], fill=(234, 179, 8, 120))
        draw.ellipse([dx, dy, dx + dial_dia, dy + dial_dia], fill=(185, 28, 28, 255), outline=(255, 255, 255, 255), width=3)
        font_dial = ImageFont.truetype(str(CAIRO_FONT_PATH), 54)
        d_txt = str(countdown_number)
        db = font_dial.getbbox(d_txt)
        draw.text((dx + (dial_dia - (db[2] - db[0])) // 2, dy + 14), d_txt, font=font_dial, fill=(255, 255, 255, 255))

        # Urgent Prompt Banner
        p_txt = reshape_arabic("⚡ اكتب إجابتك في التعليقات قبل انتهاء الوقت! ⚡")
        font_p = ImageFont.truetype(str(CAIRO_FONT_PATH), 28)
        pb = font_p.getbbox(p_txt)
        draw.text(((1080 - (pb[2] - pb[0])) // 2 + 2, dy + dial_dia + 18), p_txt, font=font_p, fill=(0, 0, 0, 200))
        draw.text(((1080 - (pb[2] - pb[0])) // 2, dy + dial_dia + 16), p_txt, font=font_p, fill=(253, 224, 71, 255))

    elif state == "reveal":
        # Majestic Glowing Emerald Banner
        r_box_w, r_box_h = 760, 86
        rx = (1080 - r_box_w) // 2
        ry = mid_y + 35
        draw_luxury_box(draw, rx, ry, r_box_w, r_box_h, radius=43, fill_color=(13, 148, 100, 255), border_color=(74, 222, 128, 255), border_w=3)
        font_rev = ImageFont.truetype(str(CAIRO_FONT_PATH), 38)
        rev_txt = reshape_arabic(f"✓ الإجابة الصحيحة  ({sub_note})")
        rvb = font_rev.getbbox(rev_txt)
        draw.text((rx + (r_box_w - (rvb[2] - rvb[0])) // 2, ry + 18), rev_txt, font=font_rev, fill=(255, 255, 255, 255))

    else:  # prompt state
        # Prompt Guidance Badge
        g_w, g_h = 720, 68
        gx = (1080 - g_w) // 2
        gy = mid_y + 45
        draw.rounded_rectangle([gx, gy, gx + g_w, gy + g_h], radius=34, fill=(10, 28, 24, 210), outline=(212, 175, 55, 180), width=2)
        font_g = ImageFont.truetype(str(CAIRO_FONT_PATH), 28)
        g_txt = reshape_arabic("🎧 استمع جيداً واختر الإجابة الصحيحة")
        gb = font_g.getbbox(g_txt)
        draw.text((gx + (g_w - (gb[2] - gb[0])) // 2, gy + 14), g_txt, font=font_g, fill=(253, 224, 71, 255))

    # 4. Multiple Choice Option Cards (y = 1010..1520)
    opt_w, opt_h = 960, 124
    opt_x = (1080 - opt_w) // 2
    opt_y = 1010
    opt_gap = 26
    letters = ["أ", "ب", "ج"]
    font_opt = ImageFont.truetype(str(AMIRI_FONT_PATH), 40)
    font_let = ImageFont.truetype(str(CAIRO_FONT_PATH), 36)

    for i, opt_text in enumerate(options):
        oy = opt_y + i * (opt_h + opt_gap)
        is_correct = (state == "reveal" and i == correct_idx)
        is_faded = (state == "reveal" and i != correct_idx)

        if is_correct:
            card_fill = (15, 130, 80, 255)
            card_border = (74, 222, 128, 255)
            border_w = 4
            let_bg = (74, 222, 128, 255)
            let_fg = (4, 40, 24, 255)
            text_color = (255, 255, 255, 255)
        elif is_faded:
            card_fill = (10, 18, 22, 130)
            card_border = (50, 70, 75, 120)
            border_w = 1
            let_bg = (30, 45, 50, 140)
            let_fg = (148, 163, 184, 180)
            text_color = (148, 163, 184, 180)
        else:
            card_fill = (6, 24, 22, 245)
            card_border = (212, 175, 55, 255)
            border_w = 2
            let_bg = (234, 179, 8, 255)
            let_fg = (15, 23, 42, 255)
            text_color = (255, 255, 255, 255)

        draw_luxury_box(draw, opt_x, oy, opt_w, opt_h, radius=28, fill_color=card_fill, border_color=card_border, border_w=border_w)

        # 3D Letter Medallion on the RIGHT (RTL layout)
        med_dia = 68
        mx = opt_x + opt_w - med_dia - 24
        my = oy + (opt_h - med_dia) // 2
        draw.ellipse([mx, my, mx + med_dia, my + med_dia], fill=let_bg, outline=(255, 255, 255, 200), width=2)
        
        let_txt = reshape_arabic(letters[i])
        lb = font_let.getbbox(let_txt)
        draw.text((mx + (med_dia - (lb[2] - lb[0])) // 2, my + 10), let_txt, font=font_let, fill=let_fg)

        # Verse Option Text
        ot_lines = wrap_arabic_lines(opt_text, font_opt, opt_w - med_dia - 70)
        if len(ot_lines) > 1:
            font_opt_small = ImageFont.truetype(str(AMIRI_FONT_PATH), 34)
            ot_lines = wrap_arabic_lines(opt_text, font_opt_small, opt_w - med_dia - 70)
            use_font = font_opt_small
            ot_spacing = 44
        else:
            use_font = font_opt
            ot_spacing = 50

        total_ot_h = len(ot_lines) * ot_spacing
        oty = oy + (opt_h - total_ot_h) // 2

        for o_line in ot_lines:
            obidi = reshape_arabic(o_line)
            ob = use_font.getbbox(obidi)
            olx = mx - 20 - (ob[2] - ob[0])
            draw.text((olx + 2, oty + 2), obidi, font=use_font, fill=(0, 0, 0, 220))
            draw.text((olx, oty), obidi, font=use_font, fill=text_color, stroke_width=1, stroke_fill=(0, 0, 0, 160))
            oty += ot_spacing

    return canvas

# Module E: Zero-Music Halal Audio & Background Engine (FFmpeg)
# ---------------------------------------------------------------------------
def generate_clock_tick_sfx(output_path: Path, duration: float = 3.0):
    """Generates crisp clock tick SFX procedurally via FFmpeg."""
    cmd = [
        FFMPEG_BIN, "-y", "-hide_banner",
        "-f", "lavfi",
        "-i", "sine=f=1200:d=0.03,afade=t=out:st=0.01:d=0.02,volume=0.9",
        "-f", "lavfi",
        "-i", "sine=f=800:d=0.03,afade=t=out:st=0.01:d=0.02,volume=0.9",
        "-filter_complex",
        "[0:a]adelay=0|0[t1];"
        "[1:a]adelay=1000|1000[t2];"
        "[0:a]adelay=2000|2000[t3];"
        "[t1][t2][t3]amix=inputs=3:dropout_transition=0:normalize=0,apad=pad_dur=0.5[aout]",
        "-map", "[aout]",
        "-t", f"{duration:.2f}",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)

def generate_chime_sfx(output_path: Path):
    """Generates clean bell chime SFX procedurally via FFmpeg."""
    cmd = [
        FFMPEG_BIN, "-y", "-hide_banner",
        "-f", "lavfi",
        "-i", "sine=f=1046.5:d=0.6",
        "-t", "0.6",
        "-af", "volume=0.8,afade=t=out:st=0.1:d=0.5",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)

synthesize_clock_tick_sfx = generate_clock_tick_sfx
synthesize_reveal_chime_sfx = generate_chime_sfx
synthesize_chime_sfx = generate_chime_sfx

def get_or_generate_background_video(total_duration: float, output_path: Path):
    """
    Synthesizes a Breathtaking Luxury Royal Islamic Motion Background:
    Rich royal emerald & midnight navy animated gradient with golden divine bloom,
    delicate celestial stardust motes and cinematic vignette.
    """
    print(f"  [Background Engine] Synthesizing Luxury Royal Islamic Motion Background ({total_duration:.1f}s)...")
    
    # Check if a custom curated luxury video is in assets/backgrounds/ (excluding legacy plain video)
    custom_bgs = [p for p in BACKGROUNDS_DIR.glob("*.mp4") if "ambient" not in p.name.lower()]
    if custom_bgs:
        chosen = random.choice(custom_bgs)
        print(f"  [Background Engine] Using custom luxury video asset: {chosen.name}")
        cmd = [
            FFMPEG_BIN, "-y", "-hide_banner",
            "-stream_loop", "-1", "-i", str(chosen),
            "-t", f"{total_duration:.2f}",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,vignette=PI/3.2,setsar=1",
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path

    # Synthesize breathtaking procedural luxury emerald-gold gradient with celestial particles
    lavfi_src = (
        f"gradients=s=1080x1920:c0=0x021612:c1=0x093b2e:x0=540:y0=1920:x1=540:y1=0:d={total_duration+1}:r=30"
    )
    vf = "noise=alls=7:allf=t+u,vignette=PI/3.2,eq=contrast=1.15:brightness=0.01:saturation=1.3"
    cmd = [
        FFMPEG_BIN, "-y", "-hide_banner",
        "-f", "lavfi", "-i", lavfi_src,
        "-vf", vf,
        "-t", f"{total_duration:.2f}",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


def assemble_challenge_short(challenge: dict, output_file: Path) -> Path:
    """
    Composites the full 1080x1920 video for a challenge:
    - Fetches texts & audios
    - Renders visual frames
    - Synchronizes timing
    - Encodes final MP4
    """
    cid = challenge["id"]
    ctype = challenge["type"]
    rec_cfg = RECITERS[challenge["reciter"]]
    rec_name = rec_cfg["name"]

    print("\n" + "=" * 65)
    print(f"🎬 [ENGINE PIPELINE] Building Quran Challenge: {cid} ({ctype})")
    print(f"  • Reciter: {rec_name}")
    print(f"  • Difficulty: {challenge.get('difficulty', 'متوسط')}")
    print("=" * 65)

    temp_dir = OUTPUT_DIR / f"temp_{cid}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch Verses & Prepare Options
    p_surah, p_ayah = challenge["prompt"]
    prompt_text = fetch_verse_text(p_surah, p_ayah)
    prompt_audio = download_audio_ayah(challenge["reciter"], p_surah, p_ayah)
    p_dur = get_audio_duration(prompt_audio)

    # Deterministic Option Preparation
    if ctype == "complete_next":
        ans_surah, ans_ayah = challenge["answer"]
        ans_text = fetch_verse_text(ans_surah, ans_ayah)
        ans_audio = download_audio_ayah(challenge["reciter"], ans_surah, ans_ayah)
        ans_dur = get_audio_duration(ans_audio)

        dist1_text = fetch_verse_text(*challenge["distractors"][0])
        dist2_text = fetch_verse_text(*challenge["distractors"][1])

        # Deterministic shuffle across A, B, C via sha256
        target_idx = hashlib.sha256(cid.encode()).digest()[0] % 3
        if target_idx == 0:
            options = [ans_text, dist1_text, dist2_text]
            correct_idx = 0
        elif target_idx == 1:
            options = [dist1_text, ans_text, dist2_text]
            correct_idx = 1
        else:
            options = [dist1_text, dist2_text, ans_text]
            correct_idx = 2

        badge_title = f"تحدي أكمل الآية  |  المستوى: {challenge.get('difficulty', 'متوسط')}"
        reveal_note = f"الآية {ans_ayah}"
    else:  # guess_surah
        options = challenge["options"]
        correct_idx = challenge["correct"]
        badge_title = f"من أي سورة هذه الآية؟  |  المستوى: {challenge.get('difficulty', 'متوسط')}"
        reveal_note = options[correct_idx]
        ans_audio = None
        ans_dur = 0.0

    # 2. Timing Map
    if ctype == "complete_next":
        # Prompt recitation -> 3.0s countdown -> Reveal & Answer recitation
        countdown_start = p_dur
        countdown_dur = 3.0
        reveal_start = countdown_start + countdown_dur
        reveal_dur = max(ans_dur, 3.5)
        total_duration = reveal_start + reveal_dur
    else:  # guess_surah
        # If recitation >= 5s, countdown during final 3s
        if p_dur >= 5.0:
            countdown_start = max(1.0, p_dur - 3.0)
            countdown_dur = 3.0
            reveal_start = p_dur
            reveal_dur = 2.4
            total_duration = reveal_start + reveal_dur
        else:
            countdown_start = p_dur
            countdown_dur = 2.5
            reveal_start = countdown_start + countdown_dur
            reveal_dur = 2.4
            total_duration = reveal_start + reveal_dur

    print(f"  • Timing Map: Audio={p_dur:.1f}s | Countdown={countdown_dur:.1f}s | Reveal={reveal_dur:.1f}s | Total={total_duration:.1f}s")

    # 3. Render Image Frames
    f_prompt = temp_dir / "frame_prompt.png"
    f_cd3 = temp_dir / "frame_cd3.png"
    f_cd2 = temp_dir / "frame_cd2.png"
    f_cd1 = temp_dir / "frame_cd1.png"
    f_reveal = temp_dir / "frame_reveal.png"

    # Frame: Prompt State
    render_quiz_frame(badge_title, rec_name, f"﴿ {prompt_text} ﴾", options, state="prompt").save(f_prompt)
    # Countdown Frames (3, 2, 1)
    render_quiz_frame(badge_title, rec_name, f"﴿ {prompt_text} ﴾", options, state="countdown", countdown_number=3, countdown_ratio=1.0).save(f_cd3)
    render_quiz_frame(badge_title, rec_name, f"﴿ {prompt_text} ﴾", options, state="countdown", countdown_number=2, countdown_ratio=0.66).save(f_cd2)
    render_quiz_frame(badge_title, rec_name, f"﴿ {prompt_text} ﴾", options, state="countdown", countdown_number=1, countdown_ratio=0.33).save(f_cd1)
    # Reveal Frame
    reveal_question = f"﴿ {prompt_text} ﴾" if ctype == "guess_surah" else f"﴿ {prompt_text} {ans_text} ﴾"
    render_quiz_frame(badge_title, rec_name, reveal_question, options, state="reveal", correct_idx=correct_idx, sub_note=reveal_note).save(f_reveal)

    # Copy debug frames for verification
    if cid in ["duha_4_5", "raad_28"]:
        shutil.copy(f_prompt, DEBUG_FRAMES_DIR / f"{cid}_prompt.png")
        shutil.copy(f_cd2, DEBUG_FRAMES_DIR / f"{cid}_countdown.png")
        shutil.copy(f_reveal, DEBUG_FRAMES_DIR / f"{cid}_reveal.png")

    # 4. Prepare Audio Components
    tick_sfx = temp_dir / "clock_tick_3s.wav"
    chime_sfx = temp_dir / "reveal_chime.wav"
    synthesize_clock_tick_sfx(tick_sfx)
    synthesize_reveal_chime_sfx(chime_sfx)

    # 5. Background Video
    bg_video = temp_dir / "bg_video.mp4"
    get_or_generate_background_video(total_duration, bg_video)

    # 6. Composite Everything with FFmpeg
    # Video overlays:
    # 0 -> countdown_start: f_prompt
    # countdown_start -> countdown_start+1: f_cd3
    # countdown_start+1 -> countdown_start+2: f_cd2
    # countdown_start+2 -> reveal_start: f_cd1
    # reveal_start -> end: f_reveal
    t_cd = countdown_start
    t_rev = reveal_start

    filter_complex = (
        f"[0:v]scale=1080:1920,setsar=1[bg];"
        f"[bg][1:v]overlay=0:0:enable='between(t,0,{t_cd:.2f})'[v1];"
        f"[v1][2:v]overlay=0:0:enable='between(t,{t_cd:.2f},{t_cd+1.0:.2f})'[v2];"
        f"[v2][3:v]overlay=0:0:enable='between(t,{t_cd+1.0:.2f},{t_cd+2.0:.2f})'[v3];"
        f"[v3][4:v]overlay=0:0:enable='between(t,{t_cd+2.0:.2f},{t_rev:.2f})'[v4];"
        f"[v4][5:v]overlay=0:0:enable='gte(t,{t_rev:.2f})',fade=t=out:st={total_duration-0.35:.2f}:d=0.35[vout];"
    )

    # Audio filter complex
    # Input 6: prompt_audio
    # Input 7: tick_sfx
    # Input 8: chime_sfx
    # (Optional Input 9: ans_audio)
    tick_delay_ms = int(t_cd * 1000)
    chime_delay_ms = int(t_rev * 1000)

    if ctype == "complete_next":
        ans_delay_ms = int(t_rev * 1000)
        audio_filter = (
            f"[6:a]volume=1.0[a_p];"
            f"[7:a]adelay={tick_delay_ms}|{tick_delay_ms},volume=0.9[a_t];"
            f"[8:a]adelay={chime_delay_ms}|{chime_delay_ms},volume=0.85[a_ch];"
            f"[9:a]adelay={ans_delay_ms}|{ans_delay_ms},volume=1.0[a_ans];"
            f"[a_p][a_t][a_ch][a_ans]amix=inputs=4:dropout_transition=0:normalize=0,afade=t=out:st={total_duration-0.35:.2f}:d=0.35[aout]"
        )
    else:
        audio_filter = (
            f"[6:a]volume=1.0[a_p];"
            f"[7:a]adelay={tick_delay_ms}|{tick_delay_ms},volume=0.9[a_t];"
            f"[8:a]adelay={chime_delay_ms}|{chime_delay_ms},volume=0.85[a_ch];"
            f"[a_p][a_t][a_ch]amix=inputs=3:dropout_transition=0:normalize=0,afade=t=out:st={total_duration-0.35:.2f}:d=0.35[aout]"
        )

    cmd = [
        FFMPEG_BIN, "-y", "-hide_banner",
        "-i", str(bg_video),        # 0
        "-i", str(f_prompt),        # 1
        "-i", str(f_cd3),           # 2
        "-i", str(f_cd2),           # 3
        "-i", str(f_cd1),           # 4
        "-i", str(f_reveal),        # 5
        "-i", str(prompt_audio),    # 6
        "-i", str(tick_sfx),        # 7
        "-i", str(chime_sfx),       # 8
    ]
    if ctype == "complete_next":
        cmd.extend(["-i", str(ans_audio)])  # 9

    cmd.extend([
        "-filter_complex", filter_complex + audio_filter,
        "-map", "[vout]",
        "-map", "[aout]",
        "-t", f"{total_duration:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_file)
    ])

    print("  [FFmpeg] Compositing challenge short...")
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"  ✓ Output file rendered: {output_file.name} ({output_file.stat().st_size:,} bytes)")

    # Clean up temp directory
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

    return output_file

# ---------------------------------------------------------------------------
# Module F: Upload, Auto-Comment Bait & State Persistence
# ---------------------------------------------------------------------------
def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"posted_ids": [], "last_run": None}

def save_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def select_next_challenge(force_id: str = None) -> dict:
    """Selects next challenge prioritizing Friday Al-Kahf challenges on Thu eve/Fri."""
    if force_id:
        for c in CHALLENGE_BANK:
            if c["id"] == force_id:
                return c
        raise ValueError(f"Challenge ID '{force_id}' not found in bank.")

    state = load_state()
    posted = set(state.get("posted_ids", []))

    # Friday Intelligence: Check Iraq / Mecca time (UTC+3)
    now_iraq = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
    is_friday_window = (now_iraq.weekday() == 3 and now_iraq.hour >= 17) or (now_iraq.weekday() == 4)

    if is_friday_window:
        print("[Friday Intelligence] Thursday evening / Friday window detected; checking Surah Al-Kahf...")
        for c in CHALLENGE_BANK:
            if c.get("friday_priority") and c["id"] not in posted:
                print(f"  ✓ Selected Friday Priority Challenge: {c['id']}")
                return c

    # General rotation: pick first unposted challenge
    for c in CHALLENGE_BANK:
        if c["id"] not in posted:
            return c

    # If all posted, cycle back
    print("[State] All 18 challenges have been posted! Resetting cycle...")
    state["posted_ids"] = []
    save_state(state)
    return CHALLENGE_BANK[0]

def upload_challenge_short(youtube, video_path: Path, challenge: dict) -> dict:
    """Uploads the challenge short to YouTube with Arabic engagement metadata."""
    from googleapiclient.http import MediaFileUpload

    rec_name = RECITERS[challenge["reciter"]]["name"]
    ctype = challenge["type"]

    if ctype == "complete_next":
        title = f"تحدي أكمل الآية في 3 ثوانٍ 🔥 هل تعرفها؟ | {rec_name} #قرآن #shorts"
    else:
        title = f"من أي سورة هذه الآية؟ ⏳ اختبار سريع للمسلمين | {rec_name} #قرآن #shorts"

    description = (
        f"{title}\n\n"
        f"تحدي قرآني مبارك لأهل القرآن ومحبي كتاب الله 📖 بصوت {rec_name}.\n"
        "هل عرفت الإجابة قبل انتهاء الـ 3 ثوانٍ؟ اكتب إجابتك في التعليقات 🤍👇\n\n"
        "اشترك في قناة نور القرآن ليصلك تحدي جديد كل يوم 🕊️ @islamrazekhoshabkhte\n\n"
        "#قرآن_كريم #تحدي_قرآني #تلاوة_خاشعة #العراق #الجزائر #مصر #Shorts"
    )

    tags = [
        "تحدي القرآن", "تحدي أكمل الآية", "من أي سورة", "اختبار القرآن",
        "قرآن كريم", rec_name, "تلاوة خاشعة", "راحة نفسية",
        "العراق", "الجزائر", "مصر", "السعودية", "shorts"
    ]

    body = {
        "snippet": {
            "title": title[:95],
            "description": description,
            "tags": tags,
            "categoryId": "22",
            "defaultLanguage": "ar",
            "defaultAudioLanguage": "ar"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    print(f"\n[YouTube Upload] Uploading {video_path.name} to @islamrazekhoshabkhte...")
    media = MediaFileUpload(str(video_path), chunksize=5*1024*1024, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  [Progress] Uploaded {int(status.progress() * 100)}%")

    vid_id = response.get("id")
    video_url = f"https://youtube.com/shorts/{vid_id}"
    print(f"  ✓ Upload Successful! Video URL: {video_url}")

    # Auto-post engagement comment
    comment_text = "هل عرفت الإجابة قبل انتهاء الـ 3 ثوانٍ؟ 🔥 اكتب (نعم) أو (لا) ومن أي بلد تتابعنا (العراق، الجزائر، مصر)؟ 🤍👇"
    try:
        print("  [Auto-Comment] Posting pinned engagement comment...")
        c_body = {
            "snippet": {
                "videoId": vid_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text
                    }
                }
            }
        }
        youtube.commentThreads().insert(part="snippet", body=c_body).execute()
        print("  ✓ Engagement comment posted successfully.")
    except Exception as e:
        print(f"  ⚠️ Comment post notice: {e}")

    # Record state
    state = load_state()
    if challenge["id"] not in state["posted_ids"]:
        state["posted_ids"].append(challenge["id"])
    state["last_run"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_state(state)

    # Record in upload_registry.json
    try:
        reg_file = BASE_DIR / "upload_registry.json"
        reg = {}
        if reg_file.exists():
            with open(reg_file, "r", encoding="utf-8") as rf:
                reg = json.load(rf)
        reg.setdefault("quran", []).append({
            "code": f"quiz_{challenge['id']}",
            "video_id": vid_id,
            "title": title,
            "ts": int(time.time()),
            "type": "quran_challenge"
        })
        with open(reg_file, "w", encoding="utf-8") as rf:
            json.dump(reg, rf, indent=2, ensure_ascii=False)
    except Exception:
        pass

    return {"video_id": vid_id, "url": video_url}

# ---------------------------------------------------------------------------
# CLI Command Dispatcher
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Arabic Viral Quran Challenge YouTube Shorts Engine")
    parser.add_argument("--mode", choices=["auth", "fix-channel", "dry-run", "produce-upload"], default="dry-run", help="Execution mode")
    parser.add_argument("--client-secrets", default="client_secrets.json", help="Path to client_secrets.json")
    parser.add_argument("--challenge-id", default=None, help="Force specific challenge ID")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("👑 [نور القرآن | The Holy Light] Arabic Quran Challenge Shorts Engine")
    print(f"  Mode: {args.mode} | Challenge ID: {args.challenge_id or 'Auto-Select'}")
    print("=" * 70)

    if args.mode == "auth":
        run_auth_flow(args.client_secrets)
        return

    if args.mode == "fix-channel":
        yt = get_youtube_service(args.client_secrets)
        fix_channel_videos(yt)
        return

    # Select challenge
    challenge = select_next_challenge(args.challenge_id)
    out_video = OUTPUT_DIR / f"quran_challenge_{challenge['id']}.mp4"

    # Assemble video
    assemble_challenge_short(challenge, out_video)

    if args.mode == "dry-run":
        print("\n" + "🎉" * 30)
        print(f"✨ [DRY RUN COMPLETE] Test video generated successfully!")
        print(f"  • Video Path: {out_video}")
        print(f"  • File Size: {out_video.stat().st_size:,} bytes")
        print(f"  • Duration: {get_audio_duration(out_video):.2f}s")
        print("🎉" * 30 + "\n")
        return

    if args.mode == "produce-upload":
        yt = get_youtube_service(args.client_secrets)
        res = upload_challenge_short(yt, out_video, challenge)
        print(f"\n✓ Produced and published successfully: {res['url']}")

if __name__ == "__main__":
    main()
