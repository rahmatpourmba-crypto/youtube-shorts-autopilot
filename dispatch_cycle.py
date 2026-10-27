import os
os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'
import os
import sys
import datetime
import json
import shutil
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"
OUTPUT_BASE = BASE_DIR / "output"

def load_state():
    if not STATE_FILE.exists():
        state = {
            "ai_channel_language": "en",
            "last_run_timestamp": None,
            "last_quran_upload_epoch": 0,
            "last_ai_upload_epoch": 0,
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
                print(f"  ✓ Published Viral Quran Short: https://youtube.com/shorts/{(upload_res.get('video_id') or upload_res.get('id', ''))}")
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

def run_ai_channel(run_dir: Path, run_count: int, force: bool = False):
    """
    CHANNEL 2: AI UNVEILED | FUTURE TECH (YouTube Shorts + Instagram Reels @cryp.tolab1)
    Fully implements Protocol 131, Two-Tower Recommendation Tags, Pinned Comment Hook
    """
    try:
        print(f"\n[DISPATCH - CHANNEL 2 AI / COSMOS] Run #{run_count}: YouTube Shorts (Mega Machines) [Instagram Decoupled]...")
        from fetch_and_upload_ai_viral import publish_twin_ai_video
        res = publish_twin_ai_video(force=force)
        return res
    except Exception as e:
        print(f"  [AI Dispatch Error] {e}")
        import traceback
        traceback.print_exc()
        return None

def run_cryptolab_channel(run_dir: Path, run_count: int):
    print("\n[DISPATCH - CRYPTOLAB] Standby.")
    return None

def run_animals_channel(run_dir: Path, run_count: int):
    print("\n[DISPATCH - ANIMALS] Standby.")
    return None

def main():
    state = load_state()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_count = state.get("run_count", 0) + 1

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    tehran_now = utc_now + datetime.timedelta(hours=3, minutes=30)
    tehran_hour = tehran_now.hour

    print("=" * 65)
    print(f"=== AUTONOMOUS PUBLISHING DISPATCHER (Run #{run_count}) ===")
    print(f"UTC Time: {utc_now.strftime('%Y-%m-%d %H:%M:%S')} | Tehran Time: {tehran_now.strftime('%H:%M')} (Hour: {tehran_hour})")
    print("Channels Active:")
    print("  1. Quran Channel: Middle East / Islamic prime peak")
    print("  2. Channel 2 (AI Unveiled / Cosmos): USA & Europe prime peak")
    print("=" * 65)

    run_dir = OUTPUT_BASE / today_str
    run_dir.mkdir(parents=True, exist_ok=True)

    # Check CLI arguments
    target_channel = "auto"
    for arg in sys.argv[1:]:
        if arg.startswith("--channel="):
            target_channel = arg.split("=")[1].strip()
        elif arg in ["--all-us-eu", "--us-eu"]:
            target_channel = "ai"

    today_date = tehran_now.strftime("%Y-%m-%d")
    daily_uploads = state.setdefault("daily_uploads", {})
    force_upload = any(arg == "--force" for arg in sys.argv)
    current_epoch = time.time()

    # Active Tehran broadcast window: 07:00 to 23:59
    is_active_window = 7 <= tehran_hour <= 23

    # 1. CHANNEL 1: QURAN
    if target_channel in ["quran", "auto", "all"]:
        last_q_epoch = state.get("last_quran_upload_epoch", 0)
        elapsed_q_mins = (current_epoch - last_q_epoch) / 60.0
        q_cooling_satisfied = elapsed_q_mins >= 65.0

        if force_upload or (is_active_window and q_cooling_satisfied):
            print(f"\n[Pacing Gate - Quran] Ready! ({elapsed_q_mins:.1f} mins elapsed). Triggering upload...")
            upload_res = run_quran_channel(run_dir, run_count)
            if upload_res:
                state["last_quran_upload_epoch"] = current_epoch
                daily_uploads["quran_short"] = today_date
        else:
            print(f"[Pacing Gate - Quran] Standby ({elapsed_q_mins:.1f} mins elapsed, 65 mins required).")

    # 2. CHANNEL 2: AI UNVEILED | FUTURE TECH (YouTube + Instagram Reels)
    if target_channel in ["ai", "auto", "all"]:
        last_ai_epoch = state.get("last_ai_upload_epoch", 0)
        elapsed_ai_mins = (current_epoch - last_ai_epoch) / 60.0
        ai_cooling_satisfied = elapsed_ai_mins >= 65.0

        if force_upload or ai_cooling_satisfied:
            print(f"\n[Pacing Gate - AI Channel 2] Ready! ({elapsed_ai_mins:.1f} mins elapsed). Triggering upload...")
            upload_ai_res = run_ai_channel(run_dir, run_count, force=force_upload)
            if upload_ai_res:
                state["last_ai_upload_epoch"] = current_epoch
                daily_uploads["ai_short"] = today_date
        else:
            print(f"[Pacing Gate - AI Channel 2] Standby ({elapsed_ai_mins:.1f} mins elapsed, 65 mins required).")

    # Persist state
    state["last_run_timestamp"] = today_str
    state["run_count"] = run_count
    state["daily_uploads"] = daily_uploads
    save_state(state)

    print("\n" + "=" * 65)
    print(f"✓ Cycle #{run_count} Completed cleanly.")
    print("=" * 65)

if __name__ == "__main__":
    main()
