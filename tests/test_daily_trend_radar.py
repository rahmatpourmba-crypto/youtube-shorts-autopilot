import datetime
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from daily_trend_radar import (
    get_current_trend_profile,
    get_recommended_search_query,
    enrich_metadata_for_current_trend,
    DAYPART_PROFILES
)

class TestDailyTrendRadar(unittest.TestCase):
    def test_friday_profile(self):
        # 2026-11-06 is Friday. 08:30 UTC is 12:00 Tehran.
        dt = datetime.datetime(2026, 11, 6, 8, 30, tzinfo=datetime.timezone.utc)
        profile = get_current_trend_profile(dt)
        self.assertEqual(profile["key"], "friday_kahf")
        self.assertEqual(profile["target_surah"], "الكهف")

    def test_night_profile(self):
        # 2026-11-07 is Saturday. 19:00 UTC is 22:30 Tehran (Night).
        dt = datetime.datetime(2026, 11, 7, 19, 0, tzinfo=datetime.timezone.utc)
        profile = get_current_trend_profile(dt)
        self.assertEqual(profile["key"], "night_serenity")
        self.assertEqual(profile["target_surah"], "الملك")

    def test_morning_profile(self):
        # 2026-11-07 is Saturday. 08:30 UTC is 12:00 Tehran (Morning/Noon).
        dt = datetime.datetime(2026, 11, 7, 8, 30, tzinfo=datetime.timezone.utc)
        profile = get_current_trend_profile(dt)
        self.assertEqual(profile["key"], "morning_barakah")
        self.assertEqual(profile["target_surah"], "الواقعة")

    def test_afternoon_profile(self):
        # 2026-11-07 is Saturday. 14:30 UTC is 18:00 Tehran (Afternoon).
        dt = datetime.datetime(2026, 11, 7, 14, 30, tzinfo=datetime.timezone.utc)
        profile = get_current_trend_profile(dt)
        self.assertEqual(profile["key"], "afternoon_relief")
        self.assertEqual(profile["target_surah"], "يوسف")

    def test_enrich_metadata_night(self):
        dt = datetime.datetime(2026, 11, 7, 19, 0, tzinfo=datetime.timezone.utc)
        meta = enrich_metadata_for_current_trend(
            base_title="",
            caption="تلاوة خاشعة",
            reciter_ar="الشيخ ياسر الدوسري",
            reciter_tag="ياسر_الدوسري",
            reciter_en="Sheikh Yasser Al-Dosari",
            utc_now=dt
        )
        self.assertIn("الشيخ ياسر", meta["title"])
        self.assertIn("الشيخ ياسر الدوسري", meta["description"])
        self.assertIn("#shorts", meta["title"])
        self.assertEqual(meta["trend_profile"], "night_serenity")
        self.assertTrue(len(meta["tags"]) >= 5)

if __name__ == "__main__":
    unittest.main()
