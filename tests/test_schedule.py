"""Schedule policy tests + simulated multi-day run with random GitHub cron drops."""
import datetime as dt
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dispatch_cycle as dc

UTC = dt.timezone.utc


def test_slot_tables():
    assert dc.QURAN_SLOTS_UTC_MIN == [13*60 + 90*i for i in range(8)]
    assert dc.AI_SLOTS_UTC_MIN == [(13*60 + 45 + 90*i) % 1440 for i in range(8)]
    allm = sorted(dc.QURAN_SLOTS_REL + dc.AI_SLOTS_REL)
    assert all(b - a >= 45 for a, b in zip(allm, allm[1:]))


def test_after_midnight_same_day():
    st = {"quran_daily_date": "2026-11-01", "quran_daily_count": 6, "last_quran_upload_epoch": 0}
    ok, idx, _ = dc.quran_gate(st, dt.datetime(2026, 11, 1, 22, 0, tzinfo=UTC))  # 01:00 Baghdad
    assert ok and idx == 6
    assert dc.schedule_day_key(dt.datetime(2026, 11, 2, 12, 59, tzinfo=UTC)) == "2026-11-01"


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
    for seed in range(500):
        ups = simulate(seed)
        for ch in ("quran", "ai"):
            ts = [t for c, t in ups if c == ch]
            days = {}
            for t in ts:
                days.setdefault(dc.schedule_day_key(t), []).append(t)
            assert sorted(days) == ["2026-11-01", "2026-11-02"], (seed, ch, sorted(days))
            assert all(len(v) == 8 for v in days.values()), (seed, ch, {k: len(v) for k, v in days.items()})
            assert all((b - a).total_seconds() >= 90*60 for a, b in zip(ts, ts[1:])), (seed, ch)
        allts = sorted(t for _, t in ups)
        assert all((b - a).total_seconds() >= 45*60 for a, b in zip(allts, allts[1:])), seed
        assert min(allts) >= dt.datetime(2026, 11, 1, 13, 0, tzinfo=UTC)
        for t in allts:
            assert dc._rel(t) < dc.LATEST_UPLOAD_REL_MIN


if __name__ == "__main__":
    test_slot_tables(); test_after_midnight_same_day(); test_nothing_before_start()
    test_simulated_two_days_random_drops()
    ups = simulate(1)
    for c, t in ups:
        print(c, t.strftime("%m-%d %H:%M UTC"))
    print("OK")
