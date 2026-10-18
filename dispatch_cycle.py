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
    100% DEDICATED QURAN CHANNEL PIPELINE (Pinterest Aesthetic Stories + Yasser Al-Dosari / Youssef Saghir)
    """
    print(f"\n[DISPATCH - QURAN PINTEREST AESTHETIC] Window Active: Quranic Story & Soul-Touching Recitation (Run #{run_count})...")
    from quran_pinterest_aesthetic_engine import render_quran_aesthetic_short
    from youtube_uploader import upload_short, CHANNELS
    
    out_dir = run_dir / "quran_aesthetic"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Render Master Aesthetic Short
    quran_data = render_quran_aesthetic_short(story_index=run_count, output_dir=out_dir)
    
    # UPLOADS PAUSED BY USER INSTRUCTION
    print(f"\n🛑 [UPLOADS PAUSED] Render completed successfully. Uploads to YouTube and Instagram are disabled by user directive.")
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
