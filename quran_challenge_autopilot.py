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

def ensure_fonts():
    """Ensures Amiri-Bold and Cairo-Bold fonts are present in assets/fonts/."""
    urls = {
        AMIRI_FONT_PATH: "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Bold.ttf",
        CAIRO_FONT_PATH: "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf"
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
    1. Checks environment variables (CI / GitHub Actions):
       YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN.
    2. Fallback to local token.json.
    3. Raises clear instructions if missing.
    """
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

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
    Renders a pixel-perfect 1080x1920 RGBA frame.
    ZERO EMOJI BUG RULE: Uses clean geometric shapes, borders, and pure Arabic text.
    Respects Shorts UI safe zones (clears bottom 330px and right 130px).
    """
    from PIL import Image, ImageDraw, ImageFont

    ensure_fonts()
    font_ui = ImageFont.truetype(str(CAIRO_FONT_PATH), 32)
    font_badge = ImageFont.truetype(str(CAIRO_FONT_PATH), 36)
    font_verse = ImageFont.truetype(str(AMIRI_FONT_PATH), 46)

    canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # 1. Top Badges (y = 120..240)
    # Channel Mini Handle
    handle_txt = reshape_arabic("@islamrazekhoshabkhte | نور القرآن")
    font_handle = ImageFont.truetype(str(CAIRO_FONT_PATH), 24)
    b_h = font_handle.getbbox(handle_txt)
    draw.text(((1080 - (b_h[2] - b_h[0])) // 2, 120), handle_txt, font=font_handle, fill=(203, 213, 225, 230))

    # Top Challenge Badge (Gold Pill)
    badge_w, badge_h = 760, 85
    bx = (1080 - badge_w) // 2
    by = 165
    draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=42, fill=(15, 23, 42, 230), outline=(212, 175, 55, 255), width=3)
    b_txt = reshape_arabic(badge_title)
    bb = font_badge.getbbox(b_txt)
    draw.text((bx + (badge_w - (bb[2] - bb[0])) // 2, by + 18), b_txt, font=font_badge, fill=(245, 208, 110, 255))

    # 2. Upper-Middle Question Card (y = 290..780)
    card_w, card_h = 960, 470
    cx = (1080 - card_w) // 2
    cy = 285
    draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=34, fill=(8, 16, 28, 215), outline=(212, 175, 55, 220), width=3)

    # Reciter label
    rec_txt = reshape_arabic(reciter_display)
    font_rec = ImageFont.truetype(str(CAIRO_FONT_PATH), 28)
    br = font_rec.getbbox(rec_txt)
    draw.text(((1080 - (br[2] - br[0])) // 2, cy + 28), rec_txt, font=font_rec, fill=(212, 175, 55, 240))

    # Quranic Verses (Amiri-Bold with auto-wrap)
    verse_lines = wrap_arabic_lines(question_text, font_verse, card_w - 90)
    if len(verse_lines) > 3:
        font_verse = ImageFont.truetype(str(AMIRI_FONT_PATH), 38)
        verse_lines = wrap_arabic_lines(question_text, font_verse, card_w - 90)

    line_spacing = 68
    total_text_h = len(verse_lines) * line_spacing
    vy = cy + 100 + (320 - total_text_h) // 2

    for line in verse_lines:
        line_bidi = reshape_arabic(line)
        bl = font_verse.getbbox(line_bidi)
        lx = (1080 - (bl[2] - bl[0])) // 2
        # Drop shadow
        draw.text((lx + 2, vy + 2), line_bidi, font=font_verse, fill=(0, 0, 0, 180))
        draw.text((lx, vy), line_bidi, font=font_verse, fill=(255, 255, 255, 255))
        vy += line_spacing

    # 3. Middle Countdown / Reveal Section (y = 790..980)
    mid_y = 795
    if state == "countdown":
        # Shrinking gold progress bar
        bar_w, bar_h = 880, 18
        bar_x = (1080 - bar_w) // 2
        draw.rounded_rectangle([bar_x, mid_y, bar_x + bar_w, mid_y + bar_h], radius=9, fill=(30, 41, 59, 200), outline=(71, 85, 105, 180), width=1)
        fill_w = int(bar_w * max(0.0, min(1.0, countdown_ratio)))
        if fill_w > 0:
            draw.rounded_rectangle([bar_x, mid_y, bar_x + fill_w, mid_y + bar_h], radius=9, fill=(212, 175, 55, 255))

        # Circular Countdown Digit Badge
        badge_dia = 90
        cdx = (1080 - badge_dia) // 2
        cdy = mid_y + 36
        draw.ellipse([cdx, cdy, cdx + badge_dia, cdy + badge_dia], fill=(220, 38, 38, 235), outline=(255, 255, 255, 240), width=3)
        font_digit = ImageFont.truetype(str(CAIRO_FONT_PATH), 52)
        d_txt = str(countdown_number)
        db = font_digit.getbbox(d_txt)
        draw.text((cdx + (badge_dia - (db[2] - db[0])) // 2, cdy + 12), d_txt, font=font_digit, fill=(255, 255, 255, 255))

        # Urgent Prompt Text
        p_txt = reshape_arabic("اكتب إجابتك في التعليقات قبل انتهاء الوقت")
        font_p = ImageFont.truetype(str(CAIRO_FONT_PATH), 26)
        pb = font_p.getbbox(p_txt)
        draw.text(((1080 - (pb[2] - pb[0])) // 2, cdy + badge_dia + 16), p_txt, font=font_p, fill=(250, 204, 21, 250))

    elif state == "reveal":
        # Glowing Emerald Green Answer Banner
        r_box_w, r_box_h = 740, 80
        rx = (1080 - r_box_w) // 2
        ry = mid_y + 35
        draw.rounded_rectangle([rx, ry, rx + r_box_w, ry + r_box_h], radius=40, fill=(15, 122, 73, 245), outline=(74, 222, 128, 255), width=3)
        rev_txt = reshape_arabic(f"الإجابة الصحيحة: {sub_note}")
        font_rev = ImageFont.truetype(str(CAIRO_FONT_PATH), 32)
        rb = font_rev.getbbox(rev_txt)
        draw.text((rx + (r_box_w - (rb[2] - rb[0])) // 2, ry + 18), rev_txt, font=font_rev, fill=(255, 255, 255, 255))
    else:
        # Prompt Idle State
        p_txt = reshape_arabic("اختر الإجابة الصحيحة من الخيارات التالية")
        font_p = ImageFont.truetype(str(CAIRO_FONT_PATH), 28)
        pb = font_p.getbbox(p_txt)
        draw.text(((1080 - (pb[2] - pb[0])) // 2, mid_y + 45), p_txt, font=font_p, fill=(203, 213, 225, 230))

    # 4. Lower-Middle Option Cards (y = 1010..1480)
    opt_y = 1010
    opt_w, opt_h = 940, 132
    opt_x = (1080 - opt_w) // 2
    letters = ["أ", "ب", "ج"]

    for i, opt in enumerate(options):
        curr_y = opt_y + i * (opt_h + 24)
        is_correct = (i == correct_idx)

        if state == "reveal" and is_correct:
            # Glowing Emerald Green Card
            fill_c = (15, 122, 73, 245)
            border_c = (74, 222, 128, 255)
            border_w = 4
            text_c = (255, 255, 255, 255)
            badge_bg = (34, 197, 94, 255)
        elif state == "reveal" and not is_correct:
            # Dimmed Out Option Card
            fill_c = (15, 23, 42, 140)
            border_c = (71, 85, 105, 120)
            border_w = 2
            text_c = (148, 163, 184, 180)
            badge_bg = (51, 65, 85, 180)
        else:
            # Normal State
            fill_c = (15, 23, 42, 225)
            border_c = (212, 175, 55, 185)
            border_w = 2
            text_c = (255, 255, 255, 255)
            badge_bg = (30, 41, 59, 240)

        draw.rounded_rectangle([opt_x, curr_y, opt_x + opt_w, curr_y + opt_h], radius=26, fill=fill_c, outline=border_c, width=border_w)

        # Right-aligned Letter Circle
        badge_dia = 78
        bx = opt_x + opt_w - badge_dia - 24
        by_opt = curr_y + (opt_h - badge_dia) // 2
        draw.ellipse([bx, by_opt, bx + badge_dia, by_opt + badge_dia], fill=badge_bg, outline=border_c, width=2)

        # Letter Text
        let_str = "✔" if (state == "reveal" and is_correct) else letters[i]
        font_let = ImageFont.truetype(str(CAIRO_FONT_PATH), 38)
        lb = font_let.getbbox(let_str)
        draw.text((bx + (badge_dia - (lb[2] - lb[0])) // 2, by_opt + 12), let_str, font=font_let, fill=(255, 255, 255, 255))

        # Option Text
        font_opt = ImageFont.truetype(str(AMIRI_FONT_PATH) if any("\u0600" <= c <= "\u06FF" for c in opt) else str(CAIRO_FONT_PATH), 38)
        opt_bidi = reshape_arabic(opt)
        ob = font_opt.getbbox(opt_bidi)
        ow = ob[2] - ob[0]
        if ow > (bx - opt_x - 50):
            # Auto-scale font down if needed
            font_opt = ImageFont.truetype(str(AMIRI_FONT_PATH), 30)
            ob = font_opt.getbbox(opt_bidi)
            ow = ob[2] - ob[0]

        draw.text((bx - ow - 35, curr_y + (opt_h - (ob[3] - ob[1])) // 2 - 4), opt_bidi, font=font_opt, fill=text_c)

    # 5. Bottom Call to Action (y = 1530)
    font_sub_cta = ImageFont.truetype(str(CAIRO_FONT_PATH), 26)
    if state == "reveal":
        cta_txt = reshape_arabic("صلِّ على النبي ﷺ واشترك ليصلك تحدي كل يوم")
    else:
        cta_txt = reshape_arabic("أهل القرآن يشاركون إجاباتهم بالتعليقات")
    cb = font_sub_cta.getbbox(cta_txt)
    draw.text(((1080 - (cb[2] - cb[0])) // 2, 1515), cta_txt, font=font_sub_cta, fill=(203, 213, 225, 220))

    return canvas

# ---------------------------------------------------------------------------
# Module E: Zero-Music Halal Audio & Background Engine (FFmpeg)
# ---------------------------------------------------------------------------
def synthesize_clock_tick_sfx(output_path: Path):
    """Synthesizes 3.0s wooden clock ticking SFX directly with FFmpeg (ZERO music)."""
    single_tick = OUTPUT_DIR / "single_tick.wav"
    cmd1 = [
        FFMPEG_BIN, "-y", "-hide_banner",
        "-f", "lavfi", "-i", "sine=frequency=900:duration=0.05",
        "-af", "volume=0.8",
        str(single_tick)
    ]
    subprocess.run(cmd1, capture_output=True, check=True)

    filter_complex = (
        "[0:a]asplit=3[t0][t1_pre][t2_pre];"
        "[t1_pre]adelay=1000|1000[t1];"
        "[t2_pre]adelay=2000|2000[t2];"
        "[t0][t1][t2]amix=inputs=3:dropout_transition=0:normalize=0,apad=whole_dur=3[aout]"
    )
    cmd2 = [
        FFMPEG_BIN, "-y", "-hide_banner",
        "-i", str(single_tick),
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", "3.0",
        str(output_path)
    ]
    subprocess.run(cmd2, capture_output=True, check=True)

def synthesize_reveal_chime_sfx(output_path: Path):
    """Synthesizes 0.6s soft single-note chime (1046Hz exponential decay) with FFmpeg."""
    cmd = [
        FFMPEG_BIN, "-y", "-hide_banner",
        "-f", "lavfi", "-i", "sine=frequency=1046:duration=0.6",
        "-af", "volume=0.8,afade=t=out:st=0.1:d=0.5",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)

def get_or_generate_background_video(total_duration: float, output_path: Path):
    """
    Priority 1: Random .mp4 in assets/backgrounds/ or assets/videos/
    Priority 2: Pexels API (if PEXELS_API_KEY set)
    Priority 3: Universal zero-key FFmpeg midnight atmospheric background
    """
    candidates = list(BACKGROUNDS_DIR.glob("*.mp4")) + list((ASSETS_DIR / "videos").glob("*.mp4"))
    if candidates:
        chosen = random.choice(candidates)
        print(f"  [Background Engine] Using video asset: {chosen.name}")
        # Loop to total_duration
        cmd = [
            FFMPEG_BIN, "-y", "-hide_banner",
            "-stream_loop", "-1", "-i", str(chosen),
            "-t", f"{total_duration:.2f}",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path

    # Check PEXELS_API_KEY
    pexels_key = os.getenv("PEXELS_API_KEY")
    if pexels_key:
        try:
            print("  [Background Engine] Querying Pexels API for vertical nature/mosque footage...")
            url = "https://api.pexels.com/videos/search?query=mosque+night+sky&orientation=portrait&per_page=5"
            req = urllib.request.Request(url, headers={"Authorization": pexels_key, "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for v in data.get("videos", []):
                    for vf in v.get("video_files", []):
                        if vf.get("width") == 1080 and vf.get("height") == 1920:
                            v_url = vf.get("link")
                            with urllib.request.urlopen(v_url, timeout=20) as v_resp, open(output_path, "wb") as f_out:
                                f_out.write(v_resp.read())
                            return output_path
        except Exception as e:
            print(f"  [Pexels Warning] {e}; switching to zero-key procedural fallback...")

    # Universal Zero-Key Fallback: Deep Midnight Atmospheric Background
    print(f"  [Background Engine] Generating zero-key procedural atmospheric background ({total_duration:.1f}s)...")
    vf = f"color=c=0x07131f:s=1080x1920:d={total_duration+1}:r=30,noise=alls=8:allf=t+u,vignette=PI/3"
    cmd = [
        FFMPEG_BIN, "-y", "-hide_banner",
        "-f", "lavfi", "-i", vf,
        "-t", f"{total_duration:.2f}",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path

# ---------------------------------------------------------------------------
# Video Assembly & Pipeline Execution
# ---------------------------------------------------------------------------
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
