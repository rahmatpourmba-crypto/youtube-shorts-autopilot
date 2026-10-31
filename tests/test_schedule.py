"""Schedule policy tests + simulated multi-day run with random GitHub cron drops."""
import datetime as dt
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dispatch_cycle as dc

UTC = dt.timezone.utc


def test_slot_tables():
    # Quran: 5 uploads/day, 17:00 Tehran (13:30 UTC) every 89 min.
    assert dc.QURAN_DAILY_TARGET == 5
    assert dc.QURAN_SLOTS_UTC_MIN == [(13 * 60 + 30 + 89 * i) for i in range(5)]
    assert [f"{m // 60:02d}:{m % 60:02d}" for m in dc.QURAN_SLOTS_UTC_MIN] == \
        ["13:30", "14:59", "16:28", "17:57", "19:26"]
    # Tehran (UTC+3:30) 17:00 .. 22:56
    tehran = [((m + 210) % 1440) for m in dc.QURAN_SLOTS_UTC_MIN]
    assert tehran[0] == 17 * 60 and tehran[-1] == 22 * 60 + 56
    # AI: unchanged, 8 uploads/day every 90 min.
    assert dc.AI_DAILY_TARGET == 8
    assert dc.AI_SLOTS_UTC_MIN == [(13 * 60 + 45 + 90 * i) % 1440 for i in range(8)]
    allm = sorted(dc.QURAN_SLOTS_REL + dc.AI_SLOTS_REL)
    assert all(b - a >= dc.CROSS_CHANNEL_GAP_MIN for a, b in zip(allm, allm[1:]))


def test_quran_last_slot():
    day = "2026-11-01"
    st = {"quran_daily_date": day, "quran_daily_count": 4, "last_quran_upload_epoch": 0,
          "last_ai_upload_epoch": 0}
    # 19:26 UTC (22:56 Tehran) is the 5th and last slot.
    ok, idx, reason = dc.quran_gate(st, dt.datetime(2026, 11, 1, 19, 30, tzinfo=UTC))
    assert ok and idx == 4, reason
    # Target reached -> no 6th upload.
    st["quran_daily_count"] = 5
    assert not dc.quran_gate(st, dt.datetime(2026, 11, 1, 20, 0, tzinfo=UTC))[0]
    # Before the first slot (16:59 Tehran) nothing happens.
    assert not dc.quran_gate({}, dt.datetime(2026, 11, 1, 13, 29, tzinfo=UTC))[0]


def test_after_midnight_same_day():
    assert dc.schedule_day_key(dt.datetime(2026, 11, 2, 12, 59, tzinfo=UTC)) == "2026-11-01"
    # AI slot 8 (00:15 UTC) still belongs to the previous schedule day.
    st = {"ai_daily_date": "2026-11-01", "ai_daily_count": 7, "last_ai_upload_epoch": 0,
          "last_quran_upload_epoch": 0}
    ok, idx, reason = dc.ai_gate(st, dt.datetime(2026, 11, 2, 0, 20, tzinfo=UTC))
    assert ok and idx == 7, reason
    assert dc.schedule_day_key(dt.datetime(2026, 11, 2, 0, 20, tzinfo=UTC)) == "2026-11-01"


def test_nothing_before_start():
    for h in range(7, 13):
        t = dt.datetime(2026, 11, 1, h, 30, tzinfo=UTC)
        assert not dc.quran_gate({}, t)[0] and not dc.ai_gate({}, t)[0]


def _crons(day0, days):
    out = []
    t = day0
    while t < day0 + dt.timedelta(days=days):
        m, h = t.minute, t.hour
        if m in (18, 48) or (m in (3, 33) and (13 <= h <= 23 or h == 0)):
            out.append(t)
        t += dt.timedelta(minutes=1)
    return out


def simulate(seed, days=2, drop=0.4):
    rnd = random.Random(seed)
    state, uploads = {}, []
    day0 = dt.datetime(2026, 11, 1, 7, 0, tzinfo=UTC)
    busy_until = day0
    for trig in _crons(day0, days):
        if rnd.random() < drop or trig < busy_until:   # dropped, or coalesced into running run
            continue
        now = trig + dt.timedelta(minutes=rnd.randint(1, 15))  # GitHub delay + setup
        deadline = now + dt.timedelta(minutes=100)

        def run_pass(now):
            n = 0
            t0 = now
            for ch, gate, rec in (("quran", dc.quran_gate, dc.record_quran_upload),
                                  ("ai", dc.ai_gate, dc.record_ai_upload)):
                if gate(state, t0)[0]:
                    now = now + dt.timedelta(minutes=rnd.randint(2, 9))  # upload duration
                    rec(state, now)
                    uploads.append((ch, now))
                    n += 1
            return n, now

        _, now = run_pass(now)
        while True:
            remaining = (deadline - now).total_seconds() / 60
            if remaining <= 0:
                break
            wait = dc.next_open_in_minutes(state, "auto", now, min(remaining, 91))
            if wait is None:
                break
            now = now + dt.timedelta(minutes=wait, seconds=5)
            n, now = run_pass(now)
            if not n:
                break
        busy_until = now
    return uploads


def test_simulated_two_days_random_drops():
    targets = {"quran": dc.QURAN_DAILY_TARGET, "ai": dc.AI_DAILY_TARGET}
    min_gap = {"quran": dc.QURAN_MIN_GAP_MIN, "ai": dc.CHANNEL_MIN_GAP_MIN}
    for seed in range(500):
        ups = simulate(seed)
        for ch in ("quran", "ai"):
            ts = [t for c, t in ups if c == ch]
            days = {}
            for t in ts:
                days.setdefault(dc.schedule_day_key(t), []).append(t)
            assert sorted(days) == ["2026-11-01", "2026-11-02"], (seed, ch, sorted(days))
            assert all(len(v) == targets[ch] for v in days.values()), \
                (seed, ch, {k: len(v) for k, v in days.items()})
            assert all((b - a).total_seconds() >= min_gap[ch] * 60 for a, b in zip(ts, ts[1:])), (seed, ch)
        allts = sorted(t for _, t in ups)
        assert all((b - a).total_seconds() >= dc.CROSS_CHANNEL_GAP_MIN * 60
                   for a, b in zip(allts, allts[1:])), seed
        assert min(allts) >= dt.datetime(2026, 11, 1, 13, 30, tzinfo=UTC)
        for t in allts:
            assert dc._rel(t) < dc.LATEST_UPLOAD_REL_MIN


if __name__ == "__main__":
    test_slot_tables(); test_quran_last_slot(); test_after_midnight_same_day()
    test_nothing_before_start()
    test_simulated_two_days_random_drops()
    ups = simulate(1)
    for c, t in ups:
        print(c, t.strftime("%m-%d %H:%M UTC"))
    print("OK")
