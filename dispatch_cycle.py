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

    # 5-SLOT ROUND-ROBIN ARCHITECTURE (هر ۵ ساعت یک هدف طلایی):
    # Slot 0: Morning Peak (8:00 AM IRST) -> Quran Recitation + Instagram Reel
    # Slot 1: Midday Tech (12:48 PM IRST) -> AI Tools Channel
    # Slot 2: Evening World Peak (17:36 PM IRST) -> Towards Eternity Viral Quran + CryptoLab Multilingual
    # Slot 3: Night Wildlife (22:24 PM IRST) -> Animals & Wildlife Channel
    # Slot 4: Late Night Wisdom (03:12 AM IRST) -> Quranic Story / Wisdom + CryptoLab Reel
    
    if slot_idx == 0:
        print("\n[DISPATCH] Executing Slot #1: Morning Quran Recitation & Instagram Reel...")
        process_and_upload_trend(
            channel_key="quran",
            search_query="تلاوة خاشعة تريح القلب قرآن كريم",
            hook_banner="تلاوة خاشعة تريح القلوب 🕊️",
            category_id="22",
            run_dir=run_dir / "quran_morning",
            niche="quran"
        )

    elif slot_idx == 1:
        print("\n[DISPATCH] Executing Slot #2: AI Tools Channel (USA & Europe Tech Peak)...")
        ai_queries = ["trending insane AI tools 2026", "useful AI websites shorts", "mind blowing AI tech viral"]
        a_query = ai_queries[run_count % len(ai_queries)]
        process_and_upload_trend(
            channel_key="ai",
            search_query=a_query,
            hook_banner="INSANE AI TOOL! 🤖⚡",
            category_id="28",
            run_dir=run_dir / "ai_tools",
            niche="ai"
        )

    elif slot_idx == 2:
        print("\n[DISPATCH] Executing Slot #3: Towards Eternity Style (Worldwide Viral) + CryptoLab Release...")
        # 1. Towards Eternity High-CTR Video
        process_and_upload_trend(
            channel_key="quran",
            search_query="Dajjal signs coming true end times towards eternity shorts",
            hook_banner="SIGNS COMING TRUE ⚠️",
            category_id="22",
            run_dir=run_dir / "quran_towards_eternity",
            niche="islamic_mystery"
        )
        # 2. CryptoLab Multilingual Release
        try:
            from cryptolab_multilingual import publish_next_cryptolab_language
            publish_next_cryptolab_language()
        except Exception as e:
            print(f"  [CryptoLab Warning] {e}")

    elif slot_idx == 3:
        print("\n[DISPATCH] Executing Slot #4: Wild Kingdom (Animal Rescue & Epic Nature)...")
        animal_queries = ["wildlife animal rescue fight", "funny cute dogs cats pets", "crazy animal moments viral"]
        an_query = animal_queries[run_count % len(animal_queries)]
        process_and_upload_trend(
            channel_key="animals",
            search_query=an_query,
            hook_banner="WAIT TILL THE END! 🐾❤️",
            category_id="15",
            run_dir=run_dir / "animals_wild",
            niche="animals"
        )

    elif slot_idx == 4:
        print("\n[DISPATCH] Executing Slot #5: Quranic Wisdom & Miracles Story...")
        process_and_upload_trend(
            channel_key="quran",
            search_query="قصص القران عبر ومواعظ مؤثرة راحة نفسية",
            hook_banner="معجزة قرآنية تهز القلوب ✨",
            category_id="22",
            run_dir=run_dir / "quran_wisdom",
            niche="quran"
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
