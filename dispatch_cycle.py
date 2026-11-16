import os
os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'
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

# ---------------------------------------------------------------------------
# QURAN CHANNEL - MIDDLE EAST GOLDEN WINDOWS (Mecca/Riyadh UTC+3)
# Target: 5 high-impact viral slots per day:
#   Slot 1 (Fajr):      06:00 Riyadh (03:00 UTC)
#   Slot 2 (Zohr):      12:30 Riyadh (09:30 UTC)
#   Slot 3 (Afternoon): 17:00 Riyadh (14:00 UTC)
#   Slot 4 (Maghrib):   19:30 Riyadh (16:30 UTC)
#   Slot 5 (Isha/Night):22:00 Riyadh (19:00 UTC)
# ---------------------------------------------------------------------------
QURAN_DAILY_TARGET = 5

# UTC Minutes of Day:
# 03:00 UTC = 180 min
# 09:30 UTC = 570 min
# 14:00 UTC = 840 min
# 16:30 UTC = 990 min
# 19:00 UTC = 1140 min
QURAN_SLOTS_UTC_MIN = [180, 570, 840, 990, 1140]
QURAN_MIN_GAP_MIN = 110  # Minimum gap of ~2 hours between uploads

def _fmt_riyadh(utc_min: int) -> str:
    # Riyadh is UTC+3 (180 minutes)
    r = (utc_min + 180) % 1440
    return f"{r//60:02d}:{r%60:02d} Riyadh (UTC+3)"

def quran_gate(state: dict, utc_now: datetime.datetime):
    """
    Evaluates whether the current moment warrants a Quran short upload.
    Stateless check designed for frequent non-blocking cron pulses.
    """
    day = utc_now.strftime("%Y-%m-%d")
    count = state.get("quran_daily_count", 0) if state.get("quran_daily_date") == day else 0

    if count >= QURAN_DAILY_TARGET:
        return False, count, f"Daily target reached ({count}/{QURAN_DAILY_TARGET})"

    now_min = utc_now.hour * 60 + utc_now.minute
    due_min = QURAN_SLOTS_UTC_MIN[count] if count < len(QURAN_SLOTS_UTC_MIN) else QURAN_SLOTS_UTC_MIN[-1]

    # Slot is considered open if current time is at or after due_min (with 45 min tolerance before due)
    if now_min < (due_min - 30):
        return False, count, f"Next Quran slot #{count+1} opens at {_fmt_riyadh(due_min)}"

    ts = utc_now.timestamp()
    gap = (ts - state.get("last_quran_upload_epoch", 0)) / 60.0
    if gap < QURAN_MIN_GAP_MIN:
        return False, count, f"Minimum interval between uploads ({QURAN_MIN_GAP_MIN} min) not met (last was {gap:.0f} min ago)"

    return True, count, f"Quran slot #{count+1} ready ({_fmt_riyadh(due_min)}), current time: {utc_now.strftime('%H:%M')} UTC"

def record_quran_upload(state: dict, utc_now: datetime.datetime):
    day = utc_now.strftime("%Y-%m-%d")
    if state.get("quran_daily_date") != day:
        state["quran_daily_date"] = day
        state["quran_daily_count"] = 0
    state["quran_daily_count"] = state.get("quran_daily_count", 0) + 1
    state["last_quran_upload_epoch"] = utc_now.timestamp()

def run_quran_channel(run_dir: Path, run_count: int, max_retries: int = 3, slot_index: int = 0):
    """
    Executes Quran automation pipeline via MasterQuranFactory:
    - Zero-Quota Viral Radar
    - Strict Deduplication Engine
    - Retention Hook & Anti-Fingerprint FFmpeg Engine
    - Arabic High-CTR SEO Generator
    - Middle East Peak Scheduler
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n[DISPATCH - MASTER QURAN FACTORY] Attempt {attempt}/{max_retries} (Slot #{slot_index+1})...")
            from master_quran_factory import MasterQuranFactory
            factory = MasterQuranFactory()
            upload_res = factory.run_factory_cycle()
            if upload_res and upload_res.get("status") == "SUCCESS":
                print(f"  ✓ Successfully processed & uploaded: {upload_res.get('url')}")
                return upload_res
            print(f"  [Warning] Factory returned non-success: {upload_res}")
            if attempt < max_retries:
                time.sleep(10)
        except Exception as e:
            print(f"  [Error] Exception in run_quran_channel (attempt {attempt}): {e}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries:
                time.sleep(10)

    return None

def run_pass(state, force_upload, run_dir, run_count, daily_uploads, today_date, utc_now):
    uploaded = 0
    attempted = 0

    ok, slot_idx, reason = quran_gate(state, utc_now)
    if ok or force_upload:
        print(f"\n[Pacing Gate - Quran] GO: {reason}{' (FORCED)' if force_upload and not ok else ''}")
        attempted += 1
        upload_res = run_quran_channel(run_dir, run_count, slot_index=slot_idx)
        if upload_res:
            record_quran_upload(state, datetime.datetime.now(datetime.timezone.utc))
            uploaded += 1
            daily_uploads["quran_short"] = today_date
    else:
        print(f"[Pacing Gate - Quran] Standby: {reason}")

    return uploaded, attempted

def main():
    state = load_state()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_count = state.get("run_count", 0) + 1

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    riyadh_now = utc_now + datetime.timedelta(hours=3)

    print("=" * 65)
    print(f"=== QURAN AUTONOMOUS VIRAL DISPATCHER (Run #{run_count}) ===")
    print(f"UTC: {utc_now.strftime('%Y-%m-%d %H:%M:%S')} | Riyadh: {riyadh_now.strftime('%H:%M')}")
    print("Mode: 100% Quran Automation")
    print("Strategy: Zero-Quota Viral Radar + Middle East Peak Windows")
    print("=" * 65)

    run_dir = OUTPUT_BASE / today_str
    run_dir.mkdir(parents=True, exist_ok=True)

    force_upload = any(arg == "--force" for arg in sys.argv)
    today_date = riyadh_now.strftime("%Y-%m-%d")
    daily_uploads = state.setdefault("daily_uploads", {})

    # Execute single stateless pass (Zero Sleep / No runner deadlock)
    published, attempted = run_pass(state, force_upload, run_dir, run_count,
                                   daily_uploads, today_date, utc_now)

    state["last_run_timestamp"] = today_str
    state["run_count"] = run_count
    state["daily_uploads"] = daily_uploads
    save_state(state)

    print("\n" + "=" * 65)
    print(f"✓ Quran cycle #{run_count} completed. Published: {published}/{attempted}")
    print("=" * 65)

    if attempted and not published:
        print("::warning::Quran dispatcher attempted upload but did not succeed.")
        sys.exit(0)  # Exit clean to allow next cron trigger to retry without locking workflow

if __name__ == "__main__":
    main()
