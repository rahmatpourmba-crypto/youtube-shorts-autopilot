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

# ---------------------------------------------------------------------------
# QURAN-ONLY MODE (owner policy 2026-11-02):
#   All other channels (AI, Animals, CryptoLab, Cars) are permanently disabled.
#   Focus 100% on Quran channel for maximum viral growth and million-view potential.
#
# SCHEDULE (owner policy 2026-11-03):
#   Quran: 5 uploads/day
#   Window: 16:00 -> 23:00 Tehran time (12:30 -> 19:30 UTC)
#   Spacing: >= 90 min between two uploads.
#   Slots (Tehran): 16:00, 17:30, 19:00, 20:30, 22:00
# ---------------------------------------------------------------------------
DAY_START_UTC_MIN = 12 * 60 + 30            # 12:30 UTC = 16:00 Tehran

QURAN_DAILY_TARGET = 5
QURAN_SLOT_START_REL = 0                    # 12:30 UTC = 16:00 Tehran
QURAN_SLOT_SPACING_MIN = 90
QURAN_MIN_GAP_MIN = 90
QURAN_SLOTS_REL = [QURAN_SLOT_START_REL + i * QURAN_SLOT_SPACING_MIN for i in range(QURAN_DAILY_TARGET)]
QURAN_SLOTS_UTC_MIN = [(DAY_START_UTC_MIN + r) % 1440 for r in QURAN_SLOTS_REL]
LATEST_UPLOAD_REL_MIN = 7 * 60              # 19:30 UTC = 23:00 Tehran, end of upload window

def schedule_day_key(utc_now: datetime.datetime) -> str:
    return (utc_now - datetime.timedelta(minutes=DAY_START_UTC_MIN)).strftime("%Y-%m-%d")

def _rel(utc_now: datetime.datetime) -> int:
    return (utc_now.hour * 60 + utc_now.minute - DAY_START_UTC_MIN) % 1440

def _fmt_tehran(utc_min: int) -> str:
    # Convert UTC minutes-of-day to Tehran (UTC+3:30)
    t = (utc_min + 210) % 1440
    return f"{t//60:02d}:{t%60:02d} Tehran"

def quran_gate(state: dict, utc_now: datetime.datetime):
    """Return (should_upload, slot_index, reason). Pure function."""
    day = schedule_day_key(utc_now)
    rel = _rel(utc_now)
    count = state.get("quran_daily_count", 0) if state.get("quran_daily_date") == day else 0

    if count >= QURAN_DAILY_TARGET:
        return False, count, f"daily target reached ({count}/{QURAN_DAILY_TARGET})"

    if rel >= LATEST_UPLOAD_REL_MIN:
        return False, count, f"outside Quran window (now {utc_now.strftime('%H:%M')} UTC)"

    due = QURAN_SLOTS_REL[count] if count < len(QURAN_SLOTS_REL) else QURAN_SLOTS_REL[-1]
    if rel < due:
        return False, count, f"next Quran slot #{count+1} at {_fmt_tehran(QURAN_SLOTS_UTC_MIN[count])}"

    ts = utc_now.timestamp()
    gap = (ts - state.get("last_quran_upload_epoch", 0)) / 60.0
    if gap < QURAN_MIN_GAP_MIN:
        return False, count, f"min gap {QURAN_MIN_GAP_MIN} min not met ({gap:.0f} min)"

    return True, count, f"Quran slot #{count+1} due ({_fmt_tehran(QURAN_SLOTS_UTC_MIN[count])}), now {utc_now.strftime('%H:%M')} UTC"

def record_quran_upload(state: dict, utc_now: datetime.datetime):
    day = schedule_day_key(utc_now)
    if state.get("quran_daily_date") != day:
        state["quran_daily_date"] = day
        state["quran_daily_count"] = 0
    state["quran_daily_count"] = state.get("quran_daily_count", 0) + 1
    state["last_quran_upload_epoch"] = utc_now.timestamp()

def run_quran_channel(run_dir: Path, run_count: int, max_retries: int = 3, slot_index: int = 0):
    """
    Viral Instagram Quran reels strategy optimized for million-view potential:
    - Only reels <= 50s with >= 1M views (fallback 500k)
    - Priority reciter: Yasser Al-Dosari (others only as fallback)
    - Duplicates allowed (best-performing reels may be re-uploaded)
    - Strong branding + ayah subtitles when possible
    - High-retention hooks and bilingual metadata
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n[DISPATCH - QURAN VIRAL] Attempt {attempt}/{max_retries} (slot #{slot_index+1})")
            from fetch_and_upload_yasser_viral import find_and_download_viral_reel, HISTORY_FILE
            from youtube_uploader import upload_short
            import dedupe_guard

            # Rotate reciter on retry so we don't keep hitting the same blocked candidates
            reel_data = find_and_download_viral_reel(slot_index=slot_index + (attempt - 1))
            if not reel_data:
                print(f"  [Error] No eligible viral reel on attempt {attempt}.")
                if attempt < max_retries:
                    time.sleep(12)
                    continue
                return None

            upload_res = upload_short(
                channel_key="quran",
                video_path=reel_data["video"],
                title=reel_data["title"],
                description=reel_data["description"],
                tags=reel_data["tags"],
                category_id="22",
                source_code=reel_data["code"]
            )

            if upload_res and upload_res.get("duplicate"):
                print(f"  [Dedupe] {reel_data['code']} already on channel ({upload_res.get('video_id')}); trying next")
                continue

            if upload_res:
                dd = reel_data.get("dedupe") or {}
                dedupe_guard.record_and_push(
                    "quran",
                    reel_data["code"],
                    upload_res.get("video_id"),
                    reel_data["title"],
                    dd.get("fp"),
                    dd.get("sha256"),
                    dd.get("phash")
                )
                print(f"  ✓ Published: https://youtube.com/shorts/{(upload_res.get('video_id') or upload_res.get('id', ''))}")
                print(f"  Source views on Instagram: {reel_data.get('views', 0):,}")
                return upload_res

            print(f"  [Warning] Upload attempt {attempt} returned no video ID; releasing claim.")
            dd = reel_data.get("dedupe") or {}
            dedupe_guard.release_claim("quran", dd.get("claim_keys") or [reel_data["code"]], HISTORY_FILE)
            if attempt < max_retries:
                time.sleep(15)

        except Exception as e:
            print(f"  [Self-Healing] Exception in run_quran_channel (attempt {attempt}): {e}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries:
                time.sleep(12)

    return None

def run_pass(state, force_upload, run_dir, run_count, daily_uploads, today_date, utc_now):
    """Only Quran channel is active."""
    uploaded = 0
    attempted = 0

    ok, slot_idx, reason = quran_gate(state, utc_now)
    if ok or force_upload:
        print(f"\n[Pacing Gate - Quran] GO: {reason}{' (forced)' if force_upload and not ok else ''}")
        attempted += 1
        upload_res = run_quran_channel(run_dir, run_count, slot_index=slot_idx)
        if upload_res:
            record_quran_upload(state, datetime.datetime.now(datetime.timezone.utc))
            uploaded += 1
            daily_uploads["quran_short"] = today_date
    else:
        print(f"[Pacing Gate - Quran] Standby: {reason}")

    return uploaded, attempted

def next_open_in_minutes(state, utc_now, horizon_min):
    """Minutes until next Quran slot opens."""
    for m in range(1, int(horizon_min) + 1):
        t = utc_now + datetime.timedelta(minutes=m)
        if quran_gate(state, t)[0]:
            return m
    return None

def main():
    state = load_state()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_count = state.get("run_count", 0) + 1

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    tehran_now = utc_now + datetime.timedelta(hours=3, minutes=30)

    print("=" * 65)
    print(f"=== QURAN-ONLY AUTONOMOUS DISPATCHER (Run #{run_count}) ===")
    print(f"UTC: {utc_now.strftime('%Y-%m-%d %H:%M:%S')} | Tehran: {tehran_now.strftime('%H:%M')}")
    print("Mode: 100% Quran channel only")
    print("Strategy: High-view Instagram viral reels from top reciters")
    print("Goal: Consistent daily output for algorithm + million-view potential")
    print("=" * 65)

    run_dir = OUTPUT_BASE / today_str
    run_dir.mkdir(parents=True, exist_ok=True)

    force_upload = any(arg == "--force" for arg in sys.argv)

    today_date = tehran_now.strftime("%Y-%m-%d")
    daily_uploads = state.setdefault("daily_uploads", {})

    published, attempted = run_pass(state, force_upload, run_dir, run_count,
                                   daily_uploads, today_date, utc_now)

    # Catch-up for missed slots (GitHub Actions is not perfectly reliable)
    catchup_budget = 0.0
    for arg in sys.argv[1:]:
        if arg.startswith("--catchup-minutes="):
            catchup_budget = float(arg.split("=", 1)[1] or 0)

    deadline = time.time() + catchup_budget * 60
    while catchup_budget > 0 and not force_upload:
        remaining = (deadline - time.time()) / 60.0
        wait = next_open_in_minutes(state, datetime.datetime.now(datetime.timezone.utc),
                                    min(remaining, 80))
        if wait is None:
            break
        save_state(state)
        print(f"\n[Catch-up] next Quran slot opens in {wait} min; waiting...")
        time.sleep(wait * 60 + 5)
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        pass_up, pass_att = run_pass(state, False, run_dir, run_count, daily_uploads, today_date, utc_now)
        published += pass_up
        attempted += pass_att
        if not pass_up:
            print("[Catch-up] nothing published; stopping to avoid loop")
            break

    state["last_run_timestamp"] = today_str
    state["run_count"] = run_count
    state["daily_uploads"] = daily_uploads
    save_state(state)

    print("\n" + "=" * 65)
    print(f"✓ Quran cycle #{run_count} finished. Published {published}/{attempted}")
    print("=" * 65)

    if attempted and not published:
        print("::error::Quran dispatcher published 0 of attempted slots - check sourcing or upload.")
        sys.exit(1)

if __name__ == "__main__":
    main()
