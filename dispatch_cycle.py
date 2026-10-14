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

def run_quran_channel(run_dir: Path, run_count: int):
    """
    15:00 IRST (3:00 PM Tehran Time) Window:
    Dedicated to Quran Channel (تلاوت‌های خاشعه، آرامش‌بخش، حکمت‌های قرآنی) + Instagram Reel
    """
    from run_pipeline import process_and_upload_trend
    quran_type = run_count % 2
    if quran_type == 0:
        print("\n[DISPATCH - QURAN] 15:00 IRST Window: High-Emotion Quran Recitation & Instagram Reel...")
        process_and_upload_trend(
            channel_key="quran",
            search_query="تلاوة خاشعة تريح القلب قرآن كريم",
            hook_banner="تلاوة خاشعة تريح القلوب 🕊️",
            category_id="22",
            run_dir=run_dir / "quran_recitation",
            niche="quran",
            publish_at=None
        )
    else:
        print("\n[DISPATCH - QURAN] 15:00 IRST Window: Quran Wisdom & Towards Eternity Style...")
        process_and_upload_trend(
            channel_key="quran",
            search_query="Dajjal signs coming true end times towards eternity shorts",
            hook_banner="SIGNS COMING TRUE ⚠️",
            category_id="22",
            run_dir=run_dir / "quran_wisdom",
            niche="islamic_mystery",
            publish_at=None
        )

def run_cryptolab_channel(run_dir: Path, run_count: int):
    """
    03:30 IRST (8:00 PM NY / 5:00 PM CA) USA & Europe Peak Window:
    Alternating PolyMint multilingual promotion vs Stickman financial psychology
    """
    print("\n[DISPATCH - CRYPTOLAB] 03:30 IRST (USA/Europe Peak): Web3 Wealth & PolyMint...")
    if run_count % 2 == 0:
        print("  -> Channel Mode: Official PolyMint Web3 Platform Promotion 🚀")
        try:
            from cryptolab_multilingual import publish_next_cryptolab_language
            publish_next_cryptolab_language(publish_at=None)
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
            publish_at=None
        )

def run_animals_channel(run_dir: Path, run_count: int):
    """
    03:30 IRST (USA/Europe Peak):
    Wild Kingdom 100% Stickman Mind & Nature Secrets
    """
    print("\n[DISPATCH - ANIMALS] 03:30 IRST (USA/Europe Peak): Wild Kingdom Mind & Nature Secrets...")
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
        publish_at=None
    )

def run_ai_channel(run_dir: Path, run_count: int):
    """
    03:30 IRST (USA/Europe Peak):
    AI Unveiled 100% Stickman Tech in 2026
    """
    print("\n[DISPATCH - AI UNVEILED] 03:30 IRST (USA/Europe Peak): Stickman Tech 2026...")
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
        publish_at=None
    )

def main():
    state = load_state()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_count = state.get("run_count", 0) + 1

    # Determine current Tehran Time (UTC + 3:30)
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    tehran_now = utc_now + datetime.timedelta(hours=3, minutes=30)
    tehran_hour = tehran_now.hour

    print("=" * 65)
    print(f"=== AUTONOMOUS PUBLISHING DISPATCHER (Run #{run_count}) ===")
    print(f"UTC Time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')} | Tehran Time: {tehran_now.strftime('%H:%M')} (Hour: {tehran_hour})")
    print("Target Architecture:")
    print("  1. 15:00 IRST (11:30 UTC): Quran Channel (Middle East / Islamic prime peak)")
    print("  2. 03:30 IRST (00:00 UTC): AI, CryptoLab, Animals (USA & Europe prime peak)")
    print("=" * 65)

    run_dir = OUTPUT_BASE / today_str
    run_dir.mkdir(parents=True, exist_ok=True)

    # Check CLI arguments for manual override
    target_channel = None
    for arg in sys.argv[1:]:
        if arg.startswith("--channel="):
            target_channel = arg.split("=")[1].strip()
        elif arg == "--all-us-eu":
            target_channel = "us_eu"

    if target_channel == "quran":
        run_quran_channel(run_dir, run_count)
    elif target_channel == "cryptolab":
        run_cryptolab_channel(run_dir, run_count)
    elif target_channel == "animals":
        run_animals_channel(run_dir, run_count)
    elif target_channel == "ai":
        run_ai_channel(run_dir, run_count)
    elif target_channel == "quran_longform":
        from documentary_remaster_pro import publish_next_quran_documentary
        publish_next_quran_documentary()
    elif target_channel == "us_eu":
        run_cryptolab_channel(run_dir, run_count)
        run_animals_channel(run_dir, run_count)
        run_ai_channel(run_dir, run_count)
    else:
        # AUTOMATED SCHEDULE ROUTING:
        # Window 1: 15:00 IRST (11:30 UTC) -> Quran Channel Daily Shorts & Reel
        # Window 2: 20:30 IRST (17:00 UTC) -> Quran Channel Long-Form Documentary (Arabic/Persian/English)
        # Window 3: 03:30 IRST (00:00 UTC) -> US & Europe Channels (CryptoLab, Animals, AI)
        if 13 <= tehran_hour <= 16:
            print("\n[SCHEDULE MATCH] 15:00 IRST Window -> Publishing Quran Channel Shorts & Reel...")
            run_quran_channel(run_dir, run_count)
        elif 19 <= tehran_hour <= 22:
            print("\n[SCHEDULE MATCH] 20:30 IRST Window -> Publishing Quran Long-Form Documentary...")
            from documentary_remaster_pro import publish_next_quran_documentary
            publish_next_quran_documentary()
        elif tehran_hour in [23, 0, 1, 2, 3, 4, 5]:
            print("\n[SCHEDULE MATCH] 03:30 IRST Window (USA & Europe Peak) -> Publishing CryptoLab, Animals, and AI Channels...")
            run_cryptolab_channel(run_dir, run_count)
            run_animals_channel(run_dir, run_count)
            run_ai_channel(run_dir, run_count)
        else:
            # Fallback round-robin for intermediate hours
            slot_idx = state.get("slot_index", 0) % 4
            print(f"\n[FALLBACK] Intermediate hour {tehran_hour} -> Executing slot #{slot_idx + 1}/4...")
            if slot_idx == 0:
                run_quran_channel(run_dir, run_count)
            elif slot_idx == 1:
                run_cryptolab_channel(run_dir, run_count)
            elif slot_idx == 2:
                run_animals_channel(run_dir, run_count)
            else:
                run_ai_channel(run_dir, run_count)
            state["slot_index"] = slot_idx + 1

    # Update State
    state["last_run_timestamp"] = today_str
    state["run_count"] = run_count
    save_state(state)

    print("\n" + "=" * 65)
    print(f"✓ Cycle #{run_count} Completed successfully.")
    print("=" * 65)

if __name__ == "__main__":
    main()
