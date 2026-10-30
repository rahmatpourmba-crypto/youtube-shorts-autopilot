"""Offline tests for ayah matching / subtitle building (no whisper, no network)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import quran_branding as qb  # noqa: E402


def fake_words(surah, ayahs, t0=0.0, step=0.5, drop_every=0):
    out, t = [], t0
    for a in ayahs:
        for i, w in enumerate(qb.normalize_ar(qb.quran_text()[(surah, a)]).split()):
            if drop_every and i % drop_every == drop_every - 1:
                t += step
                continue
            out.append((w, t, t + step))
            t += step
    return out


class TestQuranBranding(unittest.TestCase):
    def test_data_complete(self):
        self.assertEqual(len(qb.quran_text()), 6236)
        self.assertEqual(len(qb.translation("fa")), 6236)
        self.assertEqual(len(qb.translation("en")), 6236)
        self.assertEqual(len(qb.surahs()), 114)

    def test_normalize(self):
        self.assertEqual(qb.normalize_ar("إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ"), "انا اعطيناك الكوثر")

    def test_hints(self):
        self.assertEqual(qb.surah_hints("تلاوة #سورة_الملك"), [67])
        self.assertEqual(qb.surah_hints("Surah Yusuf beautiful"), [12])
        self.assertEqual(qb.surah_hints("ياسر الدوسري"), [])

    def test_match_multi_ayah_with_noise(self):
        m = qb.match_ayahs(fake_words(55, [13, 14, 15, 16], drop_every=5), "", log=lambda *a: None)
        self.assertIsNotNone(m)
        self.assertEqual(m["surah"], 55)
        self.assertEqual([a for a, _, _ in m["ayahs"]], [13, 14, 15, 16])
        starts = [s for _, s, _ in m["ayahs"]]
        self.assertEqual(starts, sorted(starts))

    def test_non_quran_rejected(self):
        words = [(w, i * .5, i * .5 + .5) for i, w in enumerate(
            qb.normalize_ar("مرحبا بكم في قناتنا اليوم نتحدث عن الطقس الجميل في المدينة وعن افضل المطاعم").split())]
        self.assertIsNone(qb.match_ayahs(words, "", log=lambda *a: None))

    def test_too_short_rejected(self):
        self.assertIsNone(qb.match_ayahs([("تبارك", 0, 1), ("الذي", 1, 2)], "", log=lambda *a: None))

    def test_ass_uses_verbatim_text(self):
        m = {"surah": 112, "ayahs": [(1, 0.0, 3.0), (2, 3.0, None)], "score": 99}
        ass = qb.build_ass(6.0, "الشيخ ياسر الدوسري", m, "fa")
        self.assertIn(qb.quran_text()[(112, 1)], ass)
        self.assertIn(qb.translation("fa")[(112, 2)], ass)
        self.assertIn("ياسر الدوسري", ass)
        self.assertNotIn(qb.quran_text()[(112, 3)], ass)

    def test_logo_exists(self):
        self.assertTrue(qb.ensure_logo().exists())


if __name__ == "__main__":
    unittest.main()
