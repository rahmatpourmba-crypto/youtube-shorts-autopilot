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
# SCHEDULE (owner policy, 2026-10-30): 8 Quran + 8 AI uploads/day.
#  * Each channel: >= 90 min between its own uploads (catch-up included).
#  * Across channels: any two uploads >= 45 min apart (no collisions).
#  * Day starts 16:00 Baghdad (13:00 UTC). The "schedule day" runs 13:00 UTC ->
#    13:00 UTC next day, so after-midnight slots count toward the same day.
#  Quran slots (Baghdad): 16:00 17:30 19:00 20:30 22:00 23:30 01:00 02:30
#  AI slots    (Baghdad): 16:45 18:15 19:45 21:15 22:45 00:15 01:45 03:15
# ---------------------------------------------------------------------------
BAGHDAD_OFFSET = datetime.timedelta(hours=3)
DAY_START_UTC_MIN = 13 * 60                 # 13:00 UTC = 16:00 Baghdad
SLOT_SPACING_MIN = 90
CHANNEL_MIN_GAP_MIN = 90                    # same-channel minimum gap (also for catch-up)
CROSS_CHANNEL_GAP_MIN = 45                  # any upload vs. the other channel's last upload
LATEST_UPLOAD_REL_MIN = 18 * 60             # drift tail: no uploads after 07:00 UTC (10:00 Baghdad)

QURAN_DAILY_TARGET = 8
AI_DAILY_TARGET = 8
QURAN_SLOTS_REL = [i * SLOT_SPACING_MIN for i in range(QURAN_DAILY_TARGET)]          # 13:00 .. 23:30 UTC
AI_SLOTS_REL = [45 + i * SLOT_SPACING_MIN for i in range(AI_DAILY_TARGET)]           # 13:45 .. 00:15 UTC
QURAN_SLOTS_UTC_MIN = [(DAY_START_UTC_MIN + r) % 1440 for r in QURAN_SLOTS_REL]
AI_SLOTS_UTC_MIN = [(DAY_START_UTC_MIN + r) % 1440 for r in AI_SLOTS_REL]
# Backwards-compatible names
QURAN_MIN_GAP_MIN = CHANNEL_MIN_GAP_MIN
AI_MIN_GAP_MIN = CHANNEL_MIN_GAP_MIN

def schedule_day_key(utc_now: datetime.datetime) -> str:
    return (utc_now - datetime.timedelta(minutes=DAY_START_UTC_MIN)).strftime("%Y-%m-%d")

def _rel(utc_now: datetime.datetime) -> int:
    return (utc_now.hour * 60 + utc_now.minute - DAY_START_UTC_MIN) % 1440

def _fmt(utc_min: int) -> str:
    b = (utc_min + 180) % 1440
    return f"{b//60:02d}:{b%60:02d} Baghdad"

def _gate(state, utc_now, prefix, other_prefix, slots_rel, slots_utc, target, label):
    day = schedule_day_key(utc_now)
    rel = _rel(utc_now)
    count = state.get(f"{prefix}_daily_count", 0) if state.get(f"{prefix}_daily_date") == day else 0
    if count >= target:
        return False, count, f"daily target reached ({count}/{target})"
    if rel >= LATEST_UPLOAD_REL_MIN:
        return False, count, f"outside {label} window (now {utc_now.strftime('%H:%M')} UTC)"
    due = slots_rel[count]
    if rel < due:
        return False, count, f"next {label} slot #{count+1} at {_fmt(slots_utc[count])}"
    ts = utc_now.timestamp()
    gap = (ts - state.get(f"last_{prefix}_upload_epoch", 0)) / 60.0
    if gap < CHANNEL_MIN_GAP_MIN:
        return False, count, f"min gap {CHANNEL_MIN_GAP_MIN} min not met ({gap:.0f} min)"
    xgap = (ts - state.get(f"last_{other_prefix}_upload_epoch", 0)) / 60.0
    if xgap < CROSS_CHANNEL_GAP_MIN:
        return False, count, f"cross-channel gap {CROSS_CHANNEL_GAP_MIN} min not met ({xgap:.0f} min since {other_prefix})"
    return True, count, f"{label} slot #{count+1} due ({_fmt(slots_utc[count])}), now {utc_now.strftime('%H:%M')} UTC"

def _record(state, utc_now, prefix):
    day = schedule_day_key(utc_now)
    if state.get(f"{prefix}_daily_date") != day:
        state[f"{prefix}_daily_date"] = day
        state[f"{prefix}_daily_count"] = 0
    state[f"{prefix}_daily_count"] = state.get(f"{prefix}_daily_count", 0) + 1
    state[f"last_{prefix}_upload_epoch"] = utc_now.timestamp()

def quran_gate(state: dict, utc_now: datetime.datetime):
    """Return (should_upload, slot_index, reason). Pure: easy to test."""
    return _gate(state, utc_now, "quran", "ai", QURAN_SLOTS_REL, QURAN_SLOTS_UTC_MIN, QURAN_DAILY_TARGET, "Quran")

def ai_gate(state: dict, utc_now: datetime.datetime):
    """Return (should_upload, slot_index, reason). Pure: easy to test."""
    return _gate(state, utc_now, "ai", "quran", AI_SLOTS_REL, AI_SLOTS_UTC_MIN, AI_DAILY_TARGET, "AI")

def ai_day_key(utc_now: datetime.datetime) -> str:
    return schedule_day_key(utc_now)

def record_quran_upload(state: dict, utc_now: datetime.datetime):
    _record(state, utc_now, "quran")

def record_ai_upload(state: dict, utc_now: datetime.datetime):
    _record(state, utc_now, "ai")

def run_quran_channel(run_dir: Path, run_count: int, max_retries: int = 2, slot_index: int = 0):
    """Viral Instagram Quran reels (<45s, >=1M views; logged fallback >=500k) -> YouTube Quran channel."""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n[DISPATCH - QURAN VIRAL REELS] Attempt {attempt}/{max_retries} (slot #{slot_index+1})")
            from fetch_and_upload_yasser_viral import find_and_download_viral_reel, HISTORY_FILE
            from youtube_uploader import upload_short, CHANNELS
            import dedupe_guard

            # Rotate to the next reciter on retry: re-scanning the same hashtags 10s later returns
            # the same (already rejected) candidates, so the old retry loop could never recover.
            reel_data = find_and_download_viral_reel(slot_index=slot_index + (attempt - 1))
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
                dd = reel_data.get("dedupe") or {}
                dedupe_guard.record_and_push("quran", reel_data["code"], upload_res.get("video_id"),
                                             reel_data["title"], dd.get("fp"), dd.get("sha256"), dd.get("phash"))
                print(f"  ✓ Published: https://youtube.com/shorts/{(upload_res.get('video_id') or upload_res.get('id', ''))}")
                return upload_res
            print(f"  [Warning] Upload attempt {attempt} did not return video ID; releasing claim for a later retry.")
            dd = reel_data.get("dedupe") or {}
            dedupe_guard.release_claim("quran", dd.get("claim_keys") or [reel_data["code"]], HISTORY_FILE)
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
    """Returns (uploaded, attempted): attempted counts channels whose gate said GO."""
    uploaded = 0
    attempted = 0
    # 1. CHANNEL 1: QURAN — 8/day from 16:00 Baghdad, >=90 min apart, >=45 min from AI
    if target_channel in ["quran", "auto", "all"]:
        ok, slot_idx, reason = quran_gate(state, utc_now)
        if ok or force_upload:
            print(f"\n[Pacing Gate - Quran] GO: {reason}{' (forced)' if force_upload and not ok else ''}")
            attempted += 1
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
            attempted += 1
            upload_ai_res = run_ai_channel(run_dir, run_count, force=force_upload)
            if upload_ai_res:
                record_ai_upload(state, datetime.datetime.now(datetime.timezone.utc)); uploaded += 1
                daily_uploads["ai_short"] = today_date
        else:
            print(f"[Pacing Gate - AI Channel 2] Standby: {ai_reason}")

    return uploaded, attempted


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

    published, attempted = run_pass(state, target_channel, force_upload, run_dir, run_count,
                                   daily_uploads, today_date, utc_now)

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
                                    min(remaining, 91))
        if wait is None:
            break
        save_state(state)
        print(f"\n[Catch-up] next due slot opens in {wait} min; waiting inside this run...")
        time.sleep(wait * 60 + 5)
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        pass_up, pass_att = run_pass(state, target_channel, False, run_dir, run_count, daily_uploads, today_date, utc_now)
        published += pass_up
        attempted += pass_att
        if not pass_up:
            print("[Catch-up] pass published nothing; stopping catch-up to avoid a retry loop")
            break

    # Persist state
    state["last_run_timestamp"] = today_str
    state["run_count"] = run_count
    state["daily_uploads"] = daily_uploads
    save_state(state)

    print("\n" + "=" * 65)
    print(f"✓ Cycle #{run_count} Completed cleanly. (published {published}/{attempted} attempts)")
    print("=" * 65)

    # A gate said GO but nothing was published -> the run must be RED, otherwise a starved
    # pipeline looks healthy for days (that is exactly how 59 Quran reels were burned silently).
    if attempted and not published:
        print(f"::error::Dispatcher published 0/{attempted} attempted slots - content sourcing or "
              f"upload failed, see the log above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
