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
    VIRAL QURAN CHANNEL PIPELINE (Sheikh Yasser Al-Dosari >500k Views from Instagram)
    Direct Unmodified Re-Upload to YouTube Quran Channel
    """
    print(f"\n[DISPATCH - QURAN VIRAL REELS] Window Active: Sheikh Yasser Al-Dosari (>500k Views)...")
    from fetch_and_upload_yasser_viral import find_and_download_viral_reel
    from youtube_uploader import upload_short, CHANNELS
    
    reel_data = find_and_download_viral_reel(min_views=500000)
    if not reel_data:
        print("  [Notice] Live Instagram search did not return eligible reel. Trying general top viral...")
        reel_data = find_and_download_viral_reel(min_views=50000)

    if not reel_data:
        print("  [Error] No viral reel available to upload.")
        return None

    print(f"\n[QURAN] Uploading Unmodified Viral Short to {CHANNELS['quran']['name']}...")
    upload_res = upload_short(
        channel_key="quran",
        video_path=reel_data["video"],
        title=reel_data["title"],
        description=reel_data["description"],
        tags=reel_data["tags"],
        category_id="22"
    )

    if upload_res:
        from fetch_and_upload_yasser_viral import load_history, save_history
        history = load_history()
        history.append(reel_data["code"])
        save_history(history)
        print(f"  ✓ Published Viral Short: https://youtube.com/shorts/{upload_res['id']}")

    return upload_res



def run_cryptolab_channel(run_dir: Path, run_count: int):
    print("\n[DISPATCH - CRYPTOLAB] On hold: 100% Focused on Quran Channel.")
    return None

def run_animals_channel(run_dir: Path, run_count: int):
    print("\n[DISPATCH - ANIMALS] On hold: 100% Focused on Quran Channel.")
    return None

def run_ai_channel(run_dir: Path, run_count: int):
    print("\n[DISPATCH - AI] On hold: 100% Focused on Quran Channel.")
    return None

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

    # 0. RUN AUTONOMOUS GROWTH AUDITOR & HYPER-GROWTH EMPIRE SYNC
    try:
        from autonomous_growth_auditor import audit_and_optimize_all_channels
        audit_and_optimize_all_channels()
        from hyper_growth_empire_engine import synchronize_hyper_growth_empire
        synchronize_hyper_growth_empire()
    except Exception as e:
        print(f"[Hyper Growth Empire Note]: {e}")

    # Check CLI arguments for manual override
    target_channel = None
    for arg in sys.argv[1:]:
        if arg.startswith("--channel="):
            target_channel = arg.split("=")[1].strip()
        elif arg in ["--all-us-eu", "--us-eu"]:
            target_channel = "us_eu"

    today_date = tehran_now.strftime("%Y-%m-%d")
    daily_uploads = state.setdefault("daily_uploads", {})

    if target_channel == "quran":
        run_quran_channel(run_dir, run_count)
        daily_uploads["quran_short"] = today_date
    elif target_channel == "cryptolab":
        run_cryptolab_channel(run_dir, run_count)
    elif target_channel == "animals":
        run_animals_channel(run_dir, run_count)
    elif target_channel == "ai":
        run_ai_channel(run_dir, run_count)
    elif target_channel == "quran_longform":
        from documentary_remaster_pro import publish_next_quran_documentary
        publish_next_quran_documentary()
        daily_uploads["quran_longform"] = today_date
    elif target_channel in ["us_eu", "all_us_eu", "all-us-eu"]:
        run_cryptolab_channel(run_dir, run_count)
        run_animals_channel(run_dir, run_count)
        run_ai_channel(run_dir, run_count)
        daily_uploads["us_eu"] = today_date
    else:
        # AUTOMATED SCHEDULE ROUTING & CATCH-UP:
        # If today's Quran short was NOT uploaded today, prioritize it immediately!
        if daily_uploads.get("quran_short") != today_date:
            print(f"\n[DAILY CATCHUP] Quran Daily Short for {today_date} has not been published yet! Publishing now...")
            run_quran_channel(run_dir, run_count)
            daily_uploads["quran_short"] = today_date
        elif 19 <= tehran_hour <= 22 and daily_uploads.get("quran_longform") != today_date:
            print("\n[SCHEDULE MATCH] 20:30 IRST Window -> Publishing Quran Long-Form Documentary...")
            from documentary_remaster_pro import publish_next_quran_documentary
            publish_next_quran_documentary()
            daily_uploads["quran_longform"] = today_date
        elif tehran_hour in [23, 0, 1, 2, 3, 4, 5] and daily_uploads.get("us_eu") != today_date:
            print("\n[SCHEDULE MATCH] 03:30 IRST Window (USA & Europe Peak) -> Publishing CryptoLab, Animals, and AI Channels...")
            run_cryptolab_channel(run_dir, run_count)
            run_animals_channel(run_dir, run_count)
            run_ai_channel(run_dir, run_count)
            daily_uploads["us_eu"] = today_date
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
    state["daily_uploads"] = daily_uploads
    save_state(state)

    print("\n" + "=" * 65)
    print(f"✓ Cycle #{run_count} Completed successfully.")
    print("=" * 65)

if __name__ == "__main__":
    main()
