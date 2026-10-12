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

    # PRE-PRODUCTION ARCHITECTURE (ترندیابی و تولید پیش از موعد ۲ ساعته):
    # If run on schedule by GitHub Actions, video is pre-generated and scheduled to publish
    # 2 hours later at the exact Golden Peak hour.
    is_scheduled_run = os.environ.get("GITHUB_EVENT_NAME") == "schedule"
    scheduled_publish_time = None
    if is_scheduled_run:
        scheduled_dt = utc_now + datetime.timedelta(hours=2)
        scheduled_publish_time = scheduled_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f"[PRE-PRODUCTION] Pre-generating video now. YouTube Scheduled Publish set for: {scheduled_publish_time} (Golden Peak Window)")
    else:
        print("[DIRECT EXECUTION] Manual or local execution: Publishing immediately.")

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
        print("\n[DISPATCH] Executing Slot #3: CryptoLab Web3 Multilingual Release (London/NY Overlap)...")
        try:
            from cryptolab_multilingual import publish_next_cryptolab_language
            publish_next_cryptolab_language(publish_at=scheduled_publish_time)
        except Exception as e:
            print(f"  [CryptoLab Warning] {e}")

    elif slot_idx == 3:
        print("\n[DISPATCH] Executing Slot #4: Wild Kingdom (Animal Rescue & Epic Nature)...")
        animal_queries = ["wildlife animal rescue 4k nature", "cute dogs cats pets funny moments", "crazy animal moments nature"]
        an_query = animal_queries[run_count % len(animal_queries)]
        process_and_upload_trend(
            channel_key="animals",
            search_query=an_query,
            hook_banner="WAIT TILL THE END! 🐾❤️",
            category_id="15",
            run_dir=run_dir / "animals_wild",
            niche="animals",
            publish_at=scheduled_publish_time
        )

    elif slot_idx == 4:
        print("\n[DISPATCH] Executing Slot #5: AI Tools Channel (USA & Europe Tech Peak)...")
        ai_queries = ["trending insane AI tools tech 2026", "useful AI websites shorts productivity", "mind blowing AI tech software"]
        a_query = ai_queries[run_count % len(ai_queries)]
        process_and_upload_trend(
            channel_key="ai",
            search_query=a_query,
            hook_banner="INSANE AI TOOL! 🤖⚡",
            category_id="28",
            run_dir=run_dir / "ai_tools",
            niche="ai",
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
