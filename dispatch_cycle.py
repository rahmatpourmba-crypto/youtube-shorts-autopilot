import os
import sys
import datetime
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"
OUTPUT_BASE = BASE_DIR / "output"

def load_state():
    if not STATE_FILE.exists():
        state = {
            "ai_channel_language": "en",
            "last_run_timestamp": None,
            "run_count": 0,
            "slot_index": 0
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return state
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def main():
    state = load_state()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_count = state.get("run_count", 0) + 1
    slot_idx = state.get("slot_index", 0) % 5

    # Determine current Tehran Time Hour (UTC + 3:30)
    utc_now = datetime.datetime.utcnow()
    tehran_now = utc_now + datetime.timedelta(hours=3, minutes=30)
    tehran_hour = tehran_now.hour

    print("=" * 65)
    print(f"=== 24/7 ACTIVE CYCLE DISPATCHER (Run #{run_count} | Slot #{slot_idx+1}/5) ===")
    print(f"UTC Time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')} | Tehran Time: {tehran_now.strftime('%H:%M')} (Hour: {tehran_hour})")
    print("Zero-Downtime Anti-Sleep Policy: Repository active every 4.8 hours.")
    print("=" * 65)

    run_dir = OUTPUT_BASE / today_str
    run_dir.mkdir(parents=True, exist_ok=True)

    from run_pipeline import process_and_upload_trend

    # IMMEDIATE PUBLIC PUBLISHING (انتشار فوری و ۱۰۰٪ عمومی):
    # Videos are published as PUBLIC immediately on upload so they are instantly visible in channel feeds.
    scheduled_publish_time = None
    print("[DIRECT PUBLIC EXECUTION] Publishing immediately as PUBLIC video.")

    # 5-SLOT MULTI-PEAK ZERO-DOWNTIME ARCHITECTURE:
    # Slot 0: 02:12 UTC (05:42 IRST) -> Pre-generate Quran Recitation for 07:42 IRST peak
    # Slot 1: 06:44 UTC (10:14 IRST) -> Midday Quran Wisdom / Towards Eternity
    # Slot 2: 11:12 UTC (14:42 IRST) -> Pre-generate CryptoLab for 16:42 IRST peak (London/NY overlap)
    # Slot 3: 15:44 UTC (19:14 IRST) -> Pre-generate Animals for 21:14 IRST peak (Global leisure peak)
    # Slot 4: 20:14 UTC (23:44 IRST) -> Pre-generate AI Tools for 03:44 IRST peak (US/Europe tech peak)
    
    if slot_idx == 0:
        print("\n[DISPATCH] Executing Slot #1: Morning Quran Recitation & Instagram Reel...")
        process_and_upload_trend(
            channel_key="quran",
            search_query="تلاوة خاشعة تريح القلب قرآن كريم",
            hook_banner="تلاوة خاشعة تريح القلوب 🕊️",
            category_id="22",
            run_dir=run_dir / "quran_morning",
            niche="quran",
            publish_at=scheduled_publish_time
        )

    elif slot_idx == 1:
        print("\n[DISPATCH] Executing Slot #2: Midday Quran Wisdom & Towards Eternity Style...")
        process_and_upload_trend(
            channel_key="quran",
            search_query="Dajjal signs coming true end times towards eternity shorts",
            hook_banner="SIGNS COMING TRUE ⚠️",
            category_id="22",
            run_dir=run_dir / "quran_towards_eternity",
            niche="islamic_mystery",
            publish_at=scheduled_publish_time
        )

    elif slot_idx == 2:
        print("\n[DISPATCH] Executing Slot #3: CryptoLab (Alternating PolyMint Promotion vs Stickman Wealth)...")
        # یک‌درمیان: اگر run_count زوج باشد تبلیغ PolyMint، اگر فرد باشد انیمیشن استیک‌من ثروت
        if run_count % 2 == 0:
            print("  -> Channel Mode: Official PolyMint Web3 Platform Promotion 🚀")
            try:
                from cryptolab_multilingual import publish_next_cryptolab_language
                publish_next_cryptolab_language(publish_at=scheduled_publish_time)
            except Exception as e:
                print(f"  [CryptoLab Promo Warning] {e}")
        else:
            print("  -> Channel Mode: 100% Original Stickman Financial Psychology Episode 🎭📈")
            from stickman_engine import build_stickman_video
            from youtube_uploader import upload_short
            cl_dir = run_dir / "cryptolab_stickman"
            cl_video = cl_dir / "stickman_crypto.mp4"
            prod = build_stickman_video("cryptolab", run_count=run_count, out_video_path=cl_video)
            upload_short(
                channel_key="polygon",
                video_path=prod["video"],
                title=prod["title"],
                description=prod["description"],
                tags=prod["tags"],
                category_id="27",
                thumbnail_path=prod["thumbnail"],
                publish_at=scheduled_publish_time
            )

    elif slot_idx == 3:
        print("\n[DISPATCH] Executing Slot #4: Wild Kingdom (100% Stickman Mind & Nature Secrets)...")
        from stickman_engine import build_stickman_video
        from youtube_uploader import upload_short
        an_dir = run_dir / "animals_stickman"
        an_video = an_dir / "stickman_nature.mp4"
        prod = build_stickman_video("animals", run_count=run_count, out_video_path=an_video)
        upload_short(
            channel_key="animals",
            video_path=prod["video"],
            title=prod["title"],
            description=prod["description"],
            tags=prod["tags"],
            category_id="15",
            thumbnail_path=prod["thumbnail"],
            publish_at=scheduled_publish_time
        )

    elif slot_idx == 4:
        print("\n[DISPATCH] Executing Slot #5: AI Tools Channel (100% Stickman Tech in 2026)...")
        from stickman_engine import build_stickman_video
        from youtube_uploader import upload_short
        ai_dir = run_dir / "ai_stickman"
        ai_video = ai_dir / "stickman_ai.mp4"
        prod = build_stickman_video("ai", run_count=run_count, out_video_path=ai_video)
        upload_short(
            channel_key="ai",
            video_path=prod["video"],
            title=prod["title"],
            description=prod["description"],
            tags=prod["tags"],
            category_id="28",
            thumbnail_path=prod["thumbnail"],
            publish_at=scheduled_publish_time
        )

    # Rotate Slot & Update State
    state["slot_index"] = slot_idx + 1
    state["last_run_timestamp"] = today_str
    state["run_count"] = run_count
    save_state(state)

    print("\n" + "=" * 65)
    print(f"✓ Cycle #{run_count} Completed. Next Slot #{((slot_idx + 1) % 5) + 1} queued in < 5 hours.")
    print("=" * 65)

if __name__ == "__main__":
    main()
