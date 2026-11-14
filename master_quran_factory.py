#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
👑 MASTER QURAN FACTORY (کارخانه تمام‌خودکار ترندیابی و انتشار شورتس‌های قرآنی)
=============================================================================
Architecture & Pipeline (حالت الف: ترندیابی ۱۰۰٪ خالص و بدون ویدیوهای تکراری):
  1. 24h Viral Radar (رصد زنده شورتس‌های داغ قرآنی جهان عرب در ۲۴ تا ۴۸ ساعت اخیر)
  2. Strict Deduplication Engine (جلوگیری قطعی از تکرار هرگونه ویدیوی منتشرشده)
  3. Secure Downloader (دریافت خودکار فایل ویدیویی با کیفیت عمودی 1080x1920)
  4. FFmpeg Anti-Fingerprint Engine (زوم ۱۰۲٪ + سرعت ۱.۰۲x صوتی + سئو رنگی + واترمارک)
  5. Arabic SEO Generator with Gemini AI (تولید عنوان ویرال، شرح معنوی و هشتگ‌های داغ)
  6. Golden-Hour Scheduler (زمان‌بندی هوشمند در ساعات اوج مصرف اینترنت مکه و ریاض)

Author: Senior YouTube Automation & FFmpeg Engineer
Mode: 100% Pure Fresh Trend Discovery (Zero Repeats)
=============================================================================
"""

import os
import sys
import time
import json
import socket
import re
import math
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Fix console encoding on Windows platforms
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Fast DNS resolver cache to prevent network timeouts
DNS_CACHE = {
    'youtube.googleapis.com': '172.217.112.4',
    'www.googleapis.com': '172.217.116.4',
    'oauth2.googleapis.com': '74.125.133.95',
}
_orig_getaddrinfo = socket.getaddrinfo
def fast_getaddrinfo(host, port, *args, **kwargs):
    if host in DNS_CACHE:
        return _orig_getaddrinfo(DNS_CACHE[host], port, *args, **kwargs)
    return _orig_getaddrinfo(host, port, *args, **kwargs)
socket.getaddrinfo = fast_getaddrinfo

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests
import imageio_ffmpeg
FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_OUTPUT = BASE_DIR / "output" / "master_factory"
WORKSPACE_OUTPUT.mkdir(parents=True, exist_ok=True)
USED_RADAR_FILE = BASE_DIR / "used_radar_ids.json"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", str(BASE_DIR / "client_secrets.json"))
TOKEN_PICKLE_FILE = os.getenv("YOUTUBE_TOKEN_FILE", str(BASE_DIR / "token_quran.pickle"))
CHANNEL_WATERMARK = os.getenv("CHANNEL_WATERMARK", "@NourAlQuran")

MAX_SHORTS_DURATION = 45.0  # Seconds

# Expanded High-Trend Arabic Quran Queries
SEARCH_QUERIES = [
    "تلاوة خاشعة shorts",
    "القرآن الكريم shorts",
    "راحة نفسية shorts",
    "الشيخ ياسر الدوسري shorts",
    "القارئ اسلام صبحي shorts",
    "القارئ عبدالرحمن مسعد shorts",
    "القارئ هزاع البلوشي shorts",
    "سورة خاشعة shorts"
]

# Riyadh/Mecca Golden Publishing Windows (UTC+3)
RIYADH_TZ_OFFSET = timedelta(hours=3)
GOLDEN_HOURS_RIYADH = [
    (6, 0),   # After Fajr
    (17, 30), # Afternoon Leisure
    (22, 0)   # Night Sleep
]


def load_used_video_ids() -> set:
    used = set()
    if USED_RADAR_FILE.exists():
        try:
            with open(USED_RADAR_FILE, "r", encoding="utf-8") as f:
                used = set(json.load(f))
        except Exception:
            used = set()
    # Always include 7pP-c5_UtW0 and known past IDs so they NEVER repeat
    used.add("7pP-c5_UtW0")
    used.add("CaJyzFup3Os")
    used.add("aUX6Y8xT-0s")
    used.add("aRU4gzOdwzM")
    used.add("VKl2ScFu3H4")
    used.add("DYml5x1oPak")
    used.add("WTz9n9zworM")
    used.add("rcpqFkAW6B8")
    used.add("bgLMjaeTIRc")
    return used


def save_used_video_id(vid_id: str):
    used = load_used_video_ids()
    used.add(vid_id)
    with open(USED_RADAR_FILE, "w", encoding="utf-8") as f:
        json.dump(list(used), f, ensure_ascii=False, indent=2)


# ===========================================================================
# MODULE 1: 24h Viral Radar (رادار شکار ترندهای داغ ۲۴ ساعت اخیر - ۱۰۰٪ جدید)
# ===========================================================================
class ViralRadar:
    """Discovers top viral trending Quran shorts within last 24-48h sorted by viral velocity, strictly non-repeated."""

    def __init__(self, youtube_service):
        self.youtube = youtube_service

    def scan_top_short(self) -> dict:
        now_utc = datetime.now(timezone.utc)
        used_ids = load_used_video_ids()
        candidates = []

        print("\n" + "=" * 65)
        print("📡 [MODULE 1: 24h Viral Radar - حالت الف: ترندیابی ۱۰۰٪ جدید]")
        print(f"⏰ ساعت شروع پویش ترندها: {now_utc.strftime('%Y-%m-%d %H:%M:%SZ')}")
        print(f"🔒 تعداد ویدیوهای بلاک‌شده در پایگاه عدم‌تکرار: {len(used_ids)} ویدیو")
        print("=" * 65)

        # First pass: last 24h; if needed, expand to 48h
        for window_hours in [24, 48]:
            published_after = (now_utc - timedelta(hours=window_hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for query in SEARCH_QUERIES:
                print(f"  🔍 جستجو در ترندها: '{query}' (بازه {window_hours} ساعت گذشته)...")
                try:
                    search_res = self.youtube.search().list(
                        part="snippet",
                        q=query,
                        type="video",
                        videoDuration="short",
                        publishedAfter=published_after,
                        order="viewCount",
                        maxResults=20
                    ).execute()

                    video_ids = [
                        item["id"]["videoId"] for item in search_res.get("items", [])
                        if "videoId" in item.get("id", {}) and item["id"]["videoId"] not in used_ids
                    ]
                    if not video_ids:
                        continue

                    # Batch retrieve video metrics and duration
                    v_res = self.youtube.videos().list(
                        part="snippet,contentDetails,statistics",
                        id=",".join(video_ids[:30])
                    ).execute()

                    for vid in v_res.get("items", []):
                        vid_id = vid["id"]
                        if vid_id in used_ids:
                            continue

                        snippet = vid["snippet"]
                        content = vid["contentDetails"]
                        stats = vid["statistics"]

                        # Parse ISO 8601 duration
                        duration_sec = self._parse_iso_duration(content.get("duration", "PT0S"))
                        if duration_sec <= 0 or duration_sec > MAX_SHORTS_DURATION:
                            continue  # Enforce strictly <= 45s filter

                        views = int(stats.get("viewCount", 0) or 0)
                        likes = int(stats.get("likeCount", 0) or 0)
                        pub_time = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))

                        hours_elapsed = max((now_utc - pub_time).total_seconds() / 3600.0, 0.25)
                        # Viral velocity formula = views / hours_since_published
                        velocity = views / hours_elapsed

                        candidates.append({
                            "video_id": vid_id,
                            "url": f"https://youtube.com/shorts/{vid_id}",
                            "title": snippet.get("title", ""),
                            "description": snippet.get("description", ""),
                            "duration": duration_sec,
                            "views": views,
                            "likes": likes,
                            "velocity": velocity,
                            "hours_elapsed": hours_elapsed
                        })

                except Exception as e:
                    print(f"  ⚠️ خطای کوئری رادار برای '{query}': {e}")

            if candidates:
                break

        if not candidates:
            raise RuntimeError("هیچ ویدیوی واجد شرایط و جدیدی در ۲۴ تا ۴۸ ساعت اخیر یافت نشد.")

        # Deduplicate candidates by ID and sort by highest viral acceleration
        unique_cands = {c["video_id"]: c for c in candidates}
        sorted_cands = sorted(unique_cands.values(), key=lambda x: x["velocity"], reverse=True)
        winner = sorted_cands[0]

        print(f"\n🏆 [ویدیوی برنده رادار ترندهای داغ انتخاب شد]:")
        print(f"  • شناسه ویدیو (ID): {winner['video_id']}")
        print(f"  • عنوان اصلی: {winner['title']}")
        print(f"  • مدت زمان: {winner['duration']} ثانیه (فیلتر زیر ۴۵ ثانیه پاس شد)")
        print(f"  • شتاب بازدید: {winner['velocity']:.1f} بازدید در ساعت (مجموع بازدیدها: {winner.get('views', 0):,})")
        return winner

    @staticmethod
    def _parse_iso_duration(iso_dur: str) -> float:
        pattern = re.compile(r'PT(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(iso_dur)
        if not match:
            return 0.0
        minutes = int(match.group(1) or 0)
        seconds = int(match.group(2) or 0)
        return float(minutes * 60 + seconds)


# ===========================================================================
# MODULE 2: Secure Downloader (ماژول دانلود ایمن با بالاترین کیفیت)
# ===========================================================================
class SecureDownloader:
    """Downloads target short vertically in 1080x1920 using yt-dlp."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def download(self, target: dict) -> Path:
        print("\n" + "=" * 60)
        print("⬇️ [MODULE 2: Secure Downloader] دانلود فایل ویدیویی با کیفیت 1080x1920...")
        print("=" * 60)
        vid_id = target["video_id"]
        out_file = self.output_dir / f"trend_{vid_id}.mp4"

        if out_file.exists() and out_file.stat().st_size > 50000:
            return out_file

        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", str(out_file),
            target["url"]
        ]

        print(f"  در حال اجرای دانلود برای: {target['url']}...")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and out_file.exists() and out_file.stat().st_size > 50000:
            print(f"  ✓ دانلود با موفقیت تکمیل شد: {out_file.name} ({out_file.stat().st_size:,} بایت)")
            return out_file

        raise RuntimeError(f"دانلود ویدیو ناموفق بود: {res.stderr[:200]}")


# ===========================================================================
# MODULE 3: FFmpeg Anti-Fingerprint Engine (موتور ضدکپیرایت و تغییر ساختاری)
# ===========================================================================
class AntiFingerprintEngine:
    """
    Applies simultaneous FFmpeg transformations:
      - 102% subtle crop & zoom to break pixel hash
      - Color/contrast boost (contrast=1.03, saturation=1.04)
      - Audio speed alteration at 1.02x (atempo=1.02)
      - Strips all previous metadata (-map_metadata -1)
      - Constant 30fps re-encode with libx264 CRF=22
      - Adds channel watermark handle in corner
    """

    def __init__(self, watermark: str):
        self.watermark = watermark

    def process_video(self, input_video: Path, output_video: Path) -> Path:
        print("\n" + "=" * 60)
        print("🛡️ [MODULE 3: Anti-Fingerprint Engine] اجرای دگرگون‌سازی ضدکپیرایت در FFmpeg...")
        print("=" * 60)

        clean_watermark = re.sub(r'[^a-zA-Z0-9_@]', '', self.watermark)
        vf_filter = (
            "crop=iw*0.98:ih*0.98,"
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "eq=contrast=1.03:saturation=1.04,"
            f"drawtext=text='{clean_watermark}':x=w-tw-40:y=120:fontsize=36:fontcolor=white@0.85:shadowcolor=black@0.6:shadowx=2:shadowy=2"
        )
        af_filter = "atempo=1.02"

        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(input_video),
            "-vf", vf_filter,
            "-af", af_filter,
            "-r", "30",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-map_metadata", "-1",
            "-metadata", f"title=QuranRecitation_{int(time.time())}",
            str(output_video)
        ]

        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            # Fallback without drawtext if fontconfig lacks glyphs
            fallback_cmd = [
                FFMPEG_BIN, "-y",
                "-i", str(input_video),
                "-vf", "crop=iw*0.98:ih*0.98,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=contrast=1.03:saturation=1.04",
                "-af", "atempo=1.02",
                "-r", "30",
                "-c:v", "libx264",
                "-crf", "22",
                "-c:a", "aac",
                "-map_metadata", "-1",
                str(output_video)
            ]
            subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"  ✓ ویدیوی دگرگون‌شده ضدکپیرایت آماده شد: {output_video.name} ({output_video.stat().st_size:,} بایت)")
        return output_video


# ===========================================================================
# MODULE 4: Arabic SEO Generator with Gemini (تولید سئوی عربی میلیونی با هوش مصنوعی)
# ===========================================================================
class ArabicSEOGenerator:
    """Generates viral high-CTR Arabic metadata strictly as JSON."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_seo(self, base_title: str) -> dict:
        print("\n" + "=" * 60)
        print("🧠 [MODULE 4: Arabic SEO Generator] تولید شناسنامه سئوی ویرال با هوش مصنوعی...")
        print("=" * 60)

        fallback_seo = {
            "title": "تلاوة خاشعة تريح القلوب 🤍 أرح سمعك وقلبك #Shorts #Quran",
            "description": (
                "تلاوة خاشعة عطرة مباركة تأسر القلوب وتسكن الأرواح من الذكر الحكيم.\n"
                "قال تعالى: ﴿الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾.\n"
                "اللهم اجعل القرآن العظيم ربيع قلوبنا ونور صدورنا وجلاء همومنا وأحزاننا."
            ),
            "hashtags": ["#قرآن_كريم", "#تلاوة_خاشعة", "#راحة_نفسية", "#shorts", "#اكسبلور"],
            "tags": [
                "قران كريم", "تلاوة خاشعة", "راحة نفسية", "القرآن الكريم",
                "تلاوات نادرة", "سورة خاشعة", "قرآن", "shorts", "quran", "islam"
            ]
        }

        if not self.api_key:
            return fallback_seo

        prompt = f"""
أنت خبير محترف في سئو (SEO) وخوارزميات يوتيوب شورتس الإسلامية العربية.
قم بتحليل هذا العنوان القرآني لإنتاج بيانات سئو فيروسية تحقق ملايين المشاهدات:
"{base_title}"

يجب أن يكون الرد عبارة عن كائن JSON صالح فقط دون أي شروحات:
{{
  "title": "عنوان فيروسي جذاب عالي النقر أقل من 60 حرف يحتوي إيموجي و #Shorts",
  "description": "وصف روحاني خاشع من 3 أسطر باللغة العربية الفصحى مع دعاء وآية تطمئن القلوب",
  "hashtags": ["#قرآن_كريم", "#تلاوة_خاشعة", "#راحة_نفسية", "#shorts", "#اكسبلور"],
  "tags": ["10 علامات دلالية قوية وعالية البحث مفصولة بفواصل"]
}}
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        for attempt in range(1, 4):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    json_match = re.search(r"\{.*\}", text, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group(0))
                        print(f"  ✓ سئوی عربی جمنای با موفقیت تولید شد:")
                        print(f"    • عنوان: {parsed.get('title')}")
                        return parsed
            except Exception as e:
                time.sleep(2)

        return fallback_seo


# ===========================================================================
# MODULE 5: Golden-Hour Scheduler (ماژول زمانبندی در ساعات طلایی مکه و ریاض)
# ===========================================================================
class GoldenHourScheduler:
    """Calculates nearest Mecca/Riyadh golden posting time (06:00, 17:30, 22:00) and schedules upload."""

    @staticmethod
    def get_next_golden_time_iso() -> tuple[str, str]:
        now_utc = datetime.now(timezone.utc)
        now_riyadh = now_utc + RIYADH_TZ_OFFSET
        today_riyadh = now_riyadh.date()

        candidates = []
        for h, m in GOLDEN_HOURS_RIYADH:
            slot_riyadh = datetime(today_riyadh.year, today_riyadh.month, today_riyadh.day, h, m)
            if slot_riyadh <= now_riyadh.replace(tzinfo=None):
                slot_riyadh += timedelta(days=1)
            candidates.append(slot_riyadh)

        candidates.sort()
        target_riyadh = candidates[0]
        target_utc = target_riyadh - RIYADH_TZ_OFFSET
        publish_at_iso = target_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        display_label = f"{target_riyadh.strftime('%Y-%m-%d %I:%M %p')} مکه و ریاض (UTC+3)"

        return publish_at_iso, display_label


# ===========================================================================
# MASTER ORCHESTRATOR & FACTORY PIPELINE
# ===========================================================================
class MasterQuranFactory:
    """End-to-end automation engine executing 100% fresh trend discovery pipeline."""

    def __init__(self):
        self.youtube = self._authenticate_youtube()
        self.radar = ViralRadar(self.youtube)
        self.downloader = SecureDownloader(WORKSPACE_OUTPUT)
        self.anti_fingerprint = AntiFingerprintEngine(CHANNEL_WATERMARK)
        self.seo_engine = ArabicSEOGenerator(GEMINI_API_KEY)
        self.scheduler = GoldenHourScheduler()

    def _authenticate_youtube(self):
        token_path = Path(TOKEN_PICKLE_FILE)
        creds = None
        if token_path.exists():
            with open(token_path, "rb") as f:
                creds = pickle.load(f)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, "wb") as f:
                    pickle.dump(creds, f)
            else:
                raise RuntimeError(f"YouTube credentials missing or invalid: {TOKEN_PICKLE_FILE}")

        return build("youtube", "v3", credentials=creds)

    def run_factory_cycle(self):
        print("\n" + "#" * 70)
        print("🚀 [شروع چرخه تولید کارخانه خودکار: حالت الف - ترندیابی ۱۰۰٪ جدید]")
        print("#" * 70)

        # 1. 24h Viral Radar
        winner = self.radar.scan_top_short()

        # 2. Secure Downloader
        raw_video = self.downloader.download(winner)

        # 3. Anti-Fingerprint FFmpeg Engine
        processed_video = WORKSPACE_OUTPUT / f"fresh_trend_{winner['video_id']}_{int(time.time())}.mp4"
        clean_video = self.anti_fingerprint.process_video(raw_video, processed_video)

        # 4. Arabic SEO Generator
        seo = self.seo_engine.generate_seo(winner["title"])
        full_description = (
            f"{seo['title']}\n\n"
            f"{seo['description']}\n\n"
            f"{' '.join(seo.get('hashtags', []))}\n\n"
            f"اشترك في القناة ليصلك القرآن الكريم يومياً 🕊️ {CHANNEL_WATERMARK}"
        )

        # 5. Golden-Hour Scheduler
        publish_at_iso, display_time = self.scheduler.get_next_golden_time_iso()
        print("\n" + "=" * 60)
        print("⏰ [MODULE 5: Golden-Hour Scheduler] زمان‌بندی انتشار در نزدیک‌ترین ساعت طلایی:")
        print(f"  • ساعت طلایی: {display_time}")
        print(f"  • شناسه زمان UTC: {publish_at_iso}")
        print("=" * 60)

        # Publish via YouTube API with 3-attempt retry
        body = {
            "snippet": {
                "title": seo["title"][:100],
                "description": full_description,
                "tags": seo.get("tags", ["قرآن كريم", "shorts"]),
                "categoryId": "22",
                "defaultLanguage": "ar",
                "defaultAudioLanguage": "ar"
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_at_iso,
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(str(clean_video), chunksize=5*1024*1024, resumable=True, mimetype="video/*")
        request = self.youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        print(f"  [Uploading] در حال ارسال فایل به یوتیوب...")
        response = None
        for attempt in range(1, 4):
            try:
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        print(f"  [Upload Progress] پیشرفت آپلود: {int(status.progress() * 100)}%")
                if response and response.get("id"):
                    vid_id = response.get("id")
                    url = f"https://youtube.com/shorts/{vid_id}"

                    # Record to used IDs database to ensure it NEVER repeats
                    save_used_video_id(winner["video_id"])
                    save_used_video_id(vid_id)

                    print("\n" + "🎉" * 35)
                    print(f"✨ ویدیوی ترند جدید با موفقیت در یوتیوب زمان‌بندی شد!")
                    print(f"  • لینک شورتز: {url}")
                    print(f"  • عنوان جدید: {seo['title']}")
                    print(f"  • زمان انتشار: {display_time}")
                    print("🎉" * 35)
                    return {
                        "status": "SUCCESS",
                        "video_id": vid_id,
                        "url": url,
                        "scheduled_time": display_time
                    }
            except Exception as e:
                print(f"  ⚠️ خطای آپلود در تلاش {attempt}/3: {e}")
                time.sleep(5)

        print("  ⚠️ سقف روزانه آپلود یوتیوب یا خطا رخ داد.")
        return {"status": "ERROR"}


if __name__ == "__main__":
    factory = MasterQuranFactory()
    factory.run_factory_cycle()
