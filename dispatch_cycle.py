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

def run_quran_channel(run_dir: Path, run_count: int, max_retries: int = 2):
    """
    VIRAL QURAN CHANNEL PIPELINE (Sheikh Yasser Al-Dosari & Elite Reciters >100k Views from Instagram)
    Direct Unmodified Re-Upload to YouTube Quran Channel with Self-Healing Auto-Recovery
    """
    import time
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n[DISPATCH - QURAN VIRAL REELS] Attempt {attempt}/{max_retries}: Elite Quran Reciters (>100k Views, <50s)...")
            from fetch_and_upload_yasser_viral import find_and_download_viral_reel
            from youtube_uploader import upload_short, CHANNELS
            
            reel_data = find_and_download_viral_reel(min_views=100000, max_duration=49.9)
            if not reel_data:
                print("  [Self-Healing] High threshold search returned no reels. Relaxing threshold to >20,000 views...")
                reel_data = find_and_download_viral_reel(min_views=20000, max_duration=49.9)

            if not reel_data:
                print(f"  [Error] No viral reel available on attempt {attempt}.")
                if attempt < max_retries:
                    time.sleep(10)
                    continue
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
                print(f"  ✓ Published Viral Short: https://youtube.com/shorts/{(upload_res.get('video_id') or upload_res.get('id', ''))}")
                return upload_res
            else:
                print(f"  [Warning] Upload attempt {attempt} did not return video ID.")
                if attempt < max_retries:
                    time.sleep(15)
        except Exception as e:
            print(f"  [Self-Healing Recovery] Exception in run_quran_channel (attempt {attempt}): {e}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries:
                time.sleep(10)
    return None



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

    try:
        import time as _t
        force_upload = any(arg == "--force" for arg in sys.argv)
        last_upload_epoch = state.get("last_quran_upload_epoch", 0)
        current_epoch = _t.time()
        elapsed_mins = (current_epoch - last_upload_epoch) / 60.0
        tehran_h = tehran_now.hour

        # Active prime broadcast windows in Tehran: 07:00 to 23:59
        is_active_window = 7 <= tehran_h <= 23
        cooling_satisfied = elapsed_mins >= 65.0

        if target_channel in ["quran", None, "auto"]:
            if force_upload:
                print(f"[Pacing Gate] Force flag active! Executing upload immediately...")
                upload_res = run_quran_channel(run_dir, run_count)
                if upload_res:
                    state["last_quran_upload_epoch"] = current_epoch
                    daily_uploads["quran_short"] = today_date
            elif not is_active_window:
                print(f"[Pacing Gate] Tehran time {tehran_now.strftime('%H:%M')} is outside active hours (07:00 - 23:59). Sleep standby.")
            elif not cooling_satisfied:
                print(f"[Pacing Gate] Cooling window active: {elapsed_mins:.1f} mins since last upload (min 65 mins required). Standby.")
            else:
                print(f"[Pacing Gate] Active window & cooling satisfied ({elapsed_mins:.1f} mins elapsed). Triggering upload...")
                upload_res = run_quran_channel(run_dir, run_count)
                if upload_res:
                    state["last_quran_upload_epoch"] = current_epoch
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
    except Exception as e:
        print(f"\n[CRASH PREVENTED & RECOVERED] General dispatch exception caught: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Guarantee state persistence & heartbeat timestamp
        state["last_run_timestamp"] = today_str
        state["run_count"] = run_count
        state["daily_uploads"] = daily_uploads
        save_state(state)

    print("\n" + "=" * 65)
    print(f"✓ Cycle #{run_count} Completed successfully.")
    print("=" * 65)

if __name__ == "__main__":
    main()
