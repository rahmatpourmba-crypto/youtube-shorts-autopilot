"""Quran-channel schedule policy tests + simulated multi-day run with random GitHub cron drops.

Owner policy: 5 uploads/day inside 12:00-23:40 Tehran (08:30-20:10 UTC), at least 75 min apart.
Slots: 12:00, 15:00, 18:00, 20:30, 22:30 Tehran (08:30, 11:30, 14:30, 17:00, 19:00 UTC).
"""
import datetime as dt
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dispatch_cycle as dc

UTC = dt.timezone.utc


def test_slot_tables():
    assert dc.QURAN_DAILY_TARGET == 5
    assert dc.QURAN_SLOTS_REL == [0, 180, 360, 510, 630]
    assert dc.QURAN_SLOTS_UTC_MIN == [8 * 60 + 30 + r for r in [0, 180, 360, 510, 630]]
    assert [f"{m // 60:02d}:{m % 60:02d}" for m in dc.QURAN_SLOTS_UTC_MIN] == \
        ["08:30", "11:30", "14:30", "17:00", "19:00"]
    assert dc.QURAN_MIN_GAP_MIN == 75
    assert dc.LATEST_UPLOAD_REL_MIN == 700
    assert dc._fmt_tehran(dc.QURAN_SLOTS_UTC_MIN[0]) == "12:00 Tehran"
    assert dc._fmt_tehran(dc.QURAN_SLOTS_UTC_MIN[-1]) == "22:30 Tehran"


def test_window_and_last_slot():
    day = "2026-11-01"
    st = {"quran_daily_date": day, "quran_daily_count": 4, "last_quran_upload_epoch": 0}
    # 19:00 UTC (22:30 Tehran) is the 5th and last slot.
    ok, idx, reason = dc.quran_gate(st, dt.datetime(2026, 11, 1, 19, 0, tzinfo=UTC))
    assert ok and idx == 4, reason
    # Nothing after 20:15 UTC (23:45 Tehran).
    assert not dc.quran_gate(st, dt.datetime(2026, 11, 1, 20, 15, tzinfo=UTC))[0]
    # Target reached -> no 6th upload.
    st["quran_daily_count"] = 5
    assert not dc.quran_gate(st, dt.datetime(2026, 11, 1, 17, 0, tzinfo=UTC))[0]


def test_min_gap_enforced():
    last = dt.datetime(2026, 11, 1, 11, 30, tzinfo=UTC)
    st = {"quran_daily_date": "2026-11-01", "quran_daily_count": 1,
          "last_quran_upload_epoch": last.timestamp()}
    assert not dc.quran_gate(st, dt.datetime(2026, 11, 1, 12, 30, tzinfo=UTC))[0]
    ok, idx, reason = dc.quran_gate(st, dt.datetime(2026, 11, 1, 14, 30, tzinfo=UTC))
    assert ok and idx == 1, reason


def test_nothing_before_start():
    for h in range(0, 8):
        t = dt.datetime(2026, 11, 1, h, 30, tzinfo=UTC)
        assert not dc.quran_gate({}, t)[0], t


def test_day_key_boundary():
    # The schedule day rolls over at 08:30 UTC (12:00 Tehran).
    assert dc.schedule_day_key(dt.datetime(2026, 11, 2, 8, 29, tzinfo=UTC)) == "2026-11-01"
    assert dc.schedule_day_key(dt.datetime(2026, 11, 2, 8, 30, tzinfo=UTC)) == "2026-11-02"
    assert dc.schedule_day_key(dt.datetime(2026, 11, 2, 0, 20, tzinfo=UTC)) == "2026-11-01"


def _crons(day0, days):
    """Trigger minutes from daily_shorts.yml (every 15 min 24/7)."""
    out, t = [], day0
    while t < day0 + dt.timedelta(days=days):
        if t.minute % 15 == 0:
            out.append(t)
        t += dt.timedelta(minutes=1)
    return out


def simulate(seed, days=2, drop=0.25):
    rnd = random.Random(seed)
    state, uploads = {}, []
    day0 = dt.datetime(2026, 11, 1, 6, 0, tzinfo=UTC)
    busy_until = day0
    for trig in _crons(day0, days):
        if rnd.random() < drop or trig < busy_until:
            continue
        start = trig + dt.timedelta(minutes=rnd.randint(1, 15))
        deadline = start + dt.timedelta(minutes=100)
        now = start

        def pass_once(now):
            if not dc.quran_gate(state, now)[0]:
                return False, now
            t0 = now
            now = now + dt.timedelta(minutes=rnd.randint(2, 9))
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
    days = {}
    for t0, _ in ups:
        days.setdefault(dc.schedule_day_key(t0), []).append(t0)
    assert sorted(days) == ["2026-11-01", "2026-11-02"], (seed, sorted(days))
    for k, v in days.items():
        assert len(v) <= dc.QURAN_DAILY_TARGET, (seed, k, len(v))
        if expect_full:
            assert len(v) == dc.QURAN_DAILY_TARGET, (seed, k, len(v))
        else:
            assert len(v) >= 3, (seed, k, len(v))
    for (_, prev), (nxt, _) in zip(ups, ups[1:]):
        assert (nxt - prev).total_seconds() >= dc.QURAN_MIN_GAP_MIN * 60, seed
    assert min(t0 for t0, _ in ups) >= dt.datetime(2026, 11, 1, 8, 30, tzinfo=UTC), seed
    for t0, _ in ups:
        assert dc._rel(t0) < dc.LATEST_UPLOAD_REL_MIN, (seed, t0)


def test_simulated_day_without_drops():
    for seed in range(200):
        _check(simulate(seed, drop=0.0), seed, expect_full=True)


def test_simulated_two_days_random_drops():
    for seed in range(300):
        _check(simulate(seed, drop=0.25), seed, expect_full=False)
