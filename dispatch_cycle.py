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
# QURAN SCHEDULE (owner policy): exactly 8 uploads/day, 18:00-24:00 Baghdad (UTC+3)
# ---------------------------------------------------------------------------
BAGHDAD_OFFSET = datetime.timedelta(hours=3)
QURAN_DAILY_TARGET = 8
QURAN_WINDOW_START_MIN = 18 * 60          # 18:00 Baghdad = 15:00 UTC
QURAN_WINDOW_END_MIN = 24 * 60            # 24:00 Baghdad = 21:00 UTC
QURAN_SLOT_SPACING_MIN = 45
QURAN_MIN_GAP_MIN = 25                    # catch-up uploads never closer than this
QURAN_SLOTS_MIN = [QURAN_WINDOW_START_MIN + i * QURAN_SLOT_SPACING_MIN for i in range(QURAN_DAILY_TARGET)]

def quran_gate(state: dict, utc_now: datetime.datetime):
    """Return (should_upload, slot_index, reason). Pure: easy to test."""
    bag = utc_now + BAGHDAD_OFFSET
    day = bag.strftime("%Y-%m-%d")
    minute = bag.hour * 60 + bag.minute
    count = state.get("quran_daily_count", 0) if state.get("quran_daily_date") == day else 0
    if count >= QURAN_DAILY_TARGET:
        return False, count, f"daily target reached ({count}/{QURAN_DAILY_TARGET})"
    if not (QURAN_WINDOW_START_MIN <= minute < QURAN_WINDOW_END_MIN):
        return False, count, f"outside 18:00-24:00 Baghdad window (now {bag.strftime('%H:%M')})"
    due = QURAN_SLOTS_MIN[count]
    if minute < due:
        return False, count, f"next slot #{count+1} at {due//60:02d}:{due%60:02d} Baghdad"
    gap = (utc_now.timestamp() - state.get("last_quran_upload_epoch", 0)) / 60.0
    if gap < QURAN_MIN_GAP_MIN:
        return False, count, f"min gap {QURAN_MIN_GAP_MIN} min not met ({gap:.0f} min)"
    return True, count, f"slot #{count+1} due ({due//60:02d}:{due%60:02d} Baghdad), now {bag.strftime('%H:%M')}"

def record_quran_upload(state: dict, utc_now: datetime.datetime):
    day = (utc_now + BAGHDAD_OFFSET).strftime("%Y-%m-%d")
    if state.get("quran_daily_date") != day:
        state["quran_daily_date"] = day
        state["quran_daily_count"] = 0
    state["quran_daily_count"] = state.get("quran_daily_count", 0) + 1
    state["last_quran_upload_epoch"] = utc_now.timestamp()

# ---------------------------------------------------------------------------
# AI CHANNEL SCHEDULE (owner policy): exactly 8 uploads/day, English global audience.
# Slots are on the existing ':18' cron pulses and never inside the Quran window
# (15:00-21:00 UTC = 18:00-24:00 Baghdad).
#   EU evening / US morning : 12:18 13:18 14:18 UTC
#   EU late / US prime time : 21:18 22:18 23:18 00:18 01:18 UTC
# The "AI day" runs 06:00 UTC -> 06:00 UTC next day so the post-midnight slots
# count toward the same day. Separate counter: ai_daily_date / ai_daily_count.
# ---------------------------------------------------------------------------
AI_DAILY_TARGET = 8
AI_DAY_START_UTC_MIN = 6 * 60
AI_SLOTS_UTC_MIN = [12*60+18, 13*60+18, 14*60+18, 21*60+18, 22*60+18, 23*60+18, 0*60+18, 1*60+18]
AI_MIN_GAP_MIN = 25
AI_LATEST_CATCHUP_UTC_MIN = 2 * 60 + 30   # no catch-up uploads after 02:30 UTC
QURAN_WINDOW_UTC = (15 * 60, 21 * 60)

def _ai_rel(minute_utc: int) -> int:
    """Minutes since start of the AI day (06:00 UTC)."""
    return (minute_utc - AI_DAY_START_UTC_MIN) % (24 * 60)

AI_SLOTS_REL = [_ai_rel(m) for m in AI_SLOTS_UTC_MIN]

def ai_day_key(utc_now: datetime.datetime) -> str:
    return (utc_now - datetime.timedelta(minutes=AI_DAY_START_UTC_MIN)).strftime("%Y-%m-%d")

def ai_gate(state: dict, utc_now: datetime.datetime):
    """Return (should_upload, slot_index, reason). Pure: easy to test."""
    day = ai_day_key(utc_now)
    minute = utc_now.hour * 60 + utc_now.minute
    rel = _ai_rel(minute)
    count = state.get("ai_daily_count", 0) if state.get("ai_daily_date") == day else 0
    if count >= AI_DAILY_TARGET:
        return False, count, f"daily target reached ({count}/{AI_DAILY_TARGET})"
    if QURAN_WINDOW_UTC[0] <= minute < QURAN_WINDOW_UTC[1]:
        return False, count, f"inside Quran window 15:00-21:00 UTC (now {utc_now.strftime('%H:%M')} UTC)"
    if rel > _ai_rel(AI_LATEST_CATCHUP_UTC_MIN):
        return False, count, f"outside AI windows (now {utc_now.strftime('%H:%M')} UTC)"
    due = AI_SLOTS_REL[count]
    due_utc = AI_SLOTS_UTC_MIN[count]
    if rel < due:
        return False, count, f"next AI slot #{count+1} at {due_utc//60:02d}:{due_utc%60:02d} UTC"
    gap = (utc_now.timestamp() - state.get("last_ai_upload_epoch", 0)) / 60.0
    if gap < AI_MIN_GAP_MIN:
        return False, count, f"min gap {AI_MIN_GAP_MIN} min not met ({gap:.0f} min)"
    return True, count, f"AI slot #{count+1} due ({due_utc//60:02d}:{due_utc%60:02d} UTC), now {utc_now.strftime('%H:%M')} UTC"

def record_ai_upload(state: dict, utc_now: datetime.datetime):
    day = ai_day_key(utc_now)
    if state.get("ai_daily_date") != day:
        state["ai_daily_date"] = day
        state["ai_daily_count"] = 0
    state["ai_daily_count"] = state.get("ai_daily_count", 0) + 1
    state["last_ai_upload_epoch"] = utc_now.timestamp()

def run_quran_channel(run_dir: Path, run_count: int, max_retries: int = 2, slot_index: int = 0):
    """Viral Instagram Quran reels (<45s, >=1M views; logged fallback >=500k) -> YouTube Quran channel."""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n[DISPATCH - QURAN VIRAL REELS] Attempt {attempt}/{max_retries} (slot #{slot_index+1})")
            from fetch_and_upload_yasser_viral import find_and_download_viral_reel, load_history, save_history
            from youtube_uploader import upload_short, CHANNELS

            reel_data = find_and_download_viral_reel(slot_index=slot_index)
            if not reel_data:
                print(f"  [Error] No eligible viral reel on attempt {attempt}.")
                if attempt < max_retries:
                    time.sleep(10)
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
                print(f"  [Dedupe] {reel_data['code']} already on channel ({upload_res.get('video_id')}); picking another reel")
                continue
            if upload_res:
                import dedupe_guard
                dd = reel_data.get("dedupe") or {}
                dedupe_guard.record_and_push("quran", reel_data["code"], upload_res.get("video_id"),
                                             reel_data["title"], dd.get("fp"), dd.get("sha256"), dd.get("phash"))
                print(f"  ✓ Published: https://youtube.com/shorts/{(upload_res.get('video_id') or upload_res.get('id', ''))}")
                return upload_res
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

def run_pass(state, target_channel, force_upload, run_dir, run_count, daily_uploads, today_date, utc_now):
    uploaded = 0
    # 1. CHANNEL 1: QURAN — 8/day, 18:00-24:00 Baghdad, slot every 45 min
    if target_channel in ["quran", "auto", "all"]:
        ok, slot_idx, reason = quran_gate(state, utc_now)
        if ok or force_upload:
            print(f"\n[Pacing Gate - Quran] GO: {reason}{' (forced)' if force_upload and not ok else ''}")
            upload_res = run_quran_channel(run_dir, run_count, slot_index=slot_idx)
            if upload_res:
                record_quran_upload(state, datetime.datetime.now(datetime.timezone.utc)); uploaded += 1
                daily_uploads["quran_short"] = today_date
        else:
            print(f"[Pacing Gate - Quran] Standby: {reason}")

    # 2. CHANNEL 2: AI UNVEILED | FUTURE TECH (YouTube + Instagram Reels)
    if target_channel in ["ai", "auto", "all"]:
        ok_ai, ai_slot, ai_reason = ai_gate(state, utc_now)
        if ok_ai or force_upload:
            print(f"\n[Pacing Gate - AI Channel 2] GO: {ai_reason}{' (forced)' if force_upload and not ok_ai else ''}")
            upload_ai_res = run_ai_channel(run_dir, run_count, force=force_upload)
            if upload_ai_res:
                record_ai_upload(state, datetime.datetime.now(datetime.timezone.utc)); uploaded += 1
                daily_uploads["ai_short"] = today_date
        else:
            print(f"[Pacing Gate - AI Channel 2] Standby: {ai_reason}")

    return uploaded


def next_open_in_minutes(state, target_channel, utc_now, horizon_min):
    """Minutes until any channel gate opens (catch-up of due slots, honoring min gaps)."""
    for m in range(1, int(horizon_min) + 1):
        t = utc_now + datetime.timedelta(minutes=m)
        if target_channel in ["quran", "auto", "all"] and quran_gate(state, t)[0]:
            return m
        if target_channel in ["ai", "auto", "all"] and ai_gate(state, t)[0]:
            return m
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

    run_pass(state, target_channel, force_upload, run_dir, run_count, daily_uploads, today_date, utc_now)

    # CATCH-UP: GitHub cron is best-effort (runs are often dropped). If more slots are due
    # (only blocked by the min gap), keep this single run alive and publish them, spaced.
    catchup_budget = 0.0
    for arg in sys.argv[1:]:
        if arg.startswith("--catchup-minutes="):
            catchup_budget = float(arg.split("=", 1)[1] or 0)
    deadline = time.time() + catchup_budget * 60
    while catchup_budget > 0 and not force_upload:
        remaining = (deadline - time.time()) / 60.0
        wait = next_open_in_minutes(state, target_channel, datetime.datetime.now(datetime.timezone.utc),
                                    min(remaining, 46))
        if wait is None:
            break
        save_state(state)
        print(f"\n[Catch-up] next due slot opens in {wait} min; waiting inside this run...")
        time.sleep(wait * 60 + 5)
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if not run_pass(state, target_channel, False, run_dir, run_count, daily_uploads, today_date, utc_now):
            print("[Catch-up] pass published nothing; stopping catch-up to avoid a retry loop")
            break

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
