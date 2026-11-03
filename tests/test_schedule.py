"""Quran-channel schedule policy tests + simulated multi-day run with random GitHub cron drops.

Owner policy 2026-11-03: the Quran channel is the only active channel; 5 uploads/day inside the
16:00-23:00 Tehran window (12:30-19:30 UTC), at least 90 minutes apart.
"""
import datetime as dt
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dispatch_cycle as dc

UTC = dt.timezone.utc


def test_slot_tables():
    # 5 slots/day, 90 min apart, starting at 12:30 UTC (16:00 Tehran).
    assert dc.QURAN_DAILY_TARGET == 5
    assert dc.QURAN_SLOTS_REL == [0, 90, 180, 270, 360]
    assert dc.QURAN_SLOTS_UTC_MIN == [12 * 60 + 30 + 90 * i for i in range(5)]
    assert [f"{m // 60:02d}:{m % 60:02d}" for m in dc.QURAN_SLOTS_UTC_MIN] == \
        ["12:30", "14:00", "15:30", "17:00", "18:30"]
    assert dc.QURAN_MIN_GAP_MIN == 90
    assert dc.LATEST_UPLOAD_REL_MIN == 7 * 60          # 19:30 UTC = 23:00 Tehran
    # Tehran (UTC+3:30): 16:00 .. 22:00, inside the 16:00-23:00 window.
    assert dc._fmt_tehran(dc.QURAN_SLOTS_UTC_MIN[0]) == "16:00 Tehran"
    assert dc._fmt_tehran(dc.QURAN_SLOTS_UTC_MIN[-1]) == "22:00 Tehran"


def test_window_and_last_slot():
    day = "2026-11-01"
    st = {"quran_daily_date": day, "quran_daily_count": 4, "last_quran_upload_epoch": 0}
    # 18:30 UTC (22:00 Tehran) is the 5th and last slot.
    ok, idx, reason = dc.quran_gate(st, dt.datetime(2026, 11, 1, 18, 30, tzinfo=UTC))
    assert ok and idx == 4, reason
    # Nothing after 19:30 UTC (23:00 Tehran).
    assert not dc.quran_gate(st, dt.datetime(2026, 11, 1, 19, 30, tzinfo=UTC))[0]
    assert not dc.quran_gate(st, dt.datetime(2026, 11, 1, 22, 0, tzinfo=UTC))[0]
    # Target reached -> no 6th upload.
    st["quran_daily_count"] = 5
    assert not dc.quran_gate(st, dt.datetime(2026, 11, 1, 17, 0, tzinfo=UTC))[0]


def test_min_gap_enforced():
    last = dt.datetime(2026, 11, 1, 14, 0, tzinfo=UTC)
    st = {"quran_daily_date": "2026-11-01", "quran_daily_count": 1,
          "last_quran_upload_epoch": last.timestamp()}
    assert not dc.quran_gate(st, dt.datetime(2026, 11, 1, 15, 0, tzinfo=UTC))[0]
    ok, idx, reason = dc.quran_gate(st, dt.datetime(2026, 11, 1, 15, 31, tzinfo=UTC))
    assert ok and idx == 1, reason


def test_nothing_before_start():
    for h in range(0, 12):
        t = dt.datetime(2026, 11, 1, h, 30, tzinfo=UTC)
        assert not dc.quran_gate({}, t)[0], t


def test_day_key_boundary():
    # The schedule day rolls over at 12:30 UTC (16:00 Tehran).
    assert dc.schedule_day_key(dt.datetime(2026, 11, 2, 12, 29, tzinfo=UTC)) == "2026-11-01"
    assert dc.schedule_day_key(dt.datetime(2026, 11, 2, 12, 30, tzinfo=UTC)) == "2026-11-02"
    assert dc.schedule_day_key(dt.datetime(2026, 11, 2, 0, 20, tzinfo=UTC)) == "2026-11-01"


def _crons(day0, days):
    """Trigger minutes from daily_shorts.yml (every 15 min inside the upload window)."""
    out, t = [], day0
    while t < day0 + dt.timedelta(days=days):
        m, h = t.minute, t.hour
        if m in (18, 48) or (m in (3, 33) and (13 <= h <= 23 or h == 0)):
            out.append(t)
        t += dt.timedelta(minutes=1)
    return out


def simulate(seed, days=2, drop=0.25):
    """One dispatcher run per surviving cron: a first pass plus catch-up until the 100-min budget
    is spent (workers are serialised by the workflow's concurrency group).

    Returns (start, finish) pairs: the gate is decided at `start`, the upload is recorded at
    `finish` (which is what the next gate check measures the 90-min gap from).
    """
    rnd = random.Random(seed)
    state, uploads = {}, []
    day0 = dt.datetime(2026, 11, 1, 7, 0, tzinfo=UTC)
    busy_until = day0
    for trig in _crons(day0, days):
        if rnd.random() < drop or trig < busy_until:   # dropped, or coalesced into a running run
            continue
        start = trig + dt.timedelta(minutes=rnd.randint(1, 15))  # GitHub delay + setup
        deadline = start + dt.timedelta(minutes=100)
        now = start

        def pass_once(now):
            if not dc.quran_gate(state, now)[0]:
                return False, now
            t0 = now
            now = now + dt.timedelta(minutes=rnd.randint(2, 9))  # upload duration
            dc.record_quran_upload(state, now)
            uploads.append((t0, now))
            return True, now

        _, now = pass_once(now)
        while True:
            remaining = (deadline - now).total_seconds() / 60
            if remaining <= 0:
                break
            wait = dc.next_open_in_minutes(state, now, min(remaining, 80))
            if wait is None:
                break
            now = now + dt.timedelta(minutes=wait, seconds=5)
            got, now = pass_once(now)
            if not got:
                break
        busy_until = now
    return uploads


def _check(ups, seed, expect_full):
    """Window, spacing and per-day count invariants shared by both simulations."""
    days = {}
    for t0, _ in ups:
        days.setdefault(dc.schedule_day_key(t0), []).append(t0)
    assert sorted(days) == ["2026-11-01", "2026-11-02"], (seed, sorted(days))
    for k, v in days.items():
        assert len(v) <= dc.QURAN_DAILY_TARGET, (seed, k, len(v))
        # Total span of 5 slots at >= 90 min is 6 h against a 7 h window, so a late catch-up
        # (which the 90-min gap then delays further) can squeeze the 5th slot out.
        if expect_full:
            assert len(v) == dc.QURAN_DAILY_TARGET, (seed, k, len(v))
        else:
            assert len(v) >= 3, (seed, k, len(v))
    # 90-min spacing measured the way the gate does: previous finish -> next start.
    for (_, prev), (nxt, _) in zip(ups, ups[1:]):
        assert (nxt - prev).total_seconds() >= dc.QURAN_MIN_GAP_MIN * 60, seed
    assert min(t0 for t0, _ in ups) >= dt.datetime(2026, 11, 1, 12, 30, tzinfo=UTC), seed
    for t0, _ in ups:
        assert dc._rel(t0) < dc.LATEST_UPLOAD_REL_MIN, (seed, t0)


def test_simulated_day_without_drops():
    # Reliable triggers -> the full 5 uploads/day the owner asked for.
    for seed in range(200):
        _check(simulate(seed, drop=0.0), seed, expect_full=True)


def test_simulated_two_days_random_drops():
    # 25% of GitHub cron pulses dropped: the target degrades gracefully but never over-posts.
    for seed in range(300):
        _check(simulate(seed, drop=0.25), seed, expect_full=False)


if __name__ == "__main__":
    test_slot_tables(); test_window_and_last_slot(); test_min_gap_enforced()
    test_nothing_before_start(); test_day_key_boundary()
    test_simulated_day_without_drops(); test_simulated_two_days_random_drops()
    for t0, t1 in simulate(1, drop=0.0):
        print(t0.strftime("%m-%d %H:%M UTC"), "->", t1.strftime("%H:%M"))
    print("OK")
