"""Regression tests for the two bugs that starved the Quran channel (Oct 2026):

1. `youtube_has_duplicate()` treated an identical *title* as a duplicate *video*. Titles are
   generated from 6 templates, so distinct reels collided and were skipped
   (run 41155681798: 3 reels rejected as "same title already on channel").
2. A claim was never released after a transient failure, so every failed download / branding /
   upload permanently blacklisted the reel (59 codes burned, only a handful published).

Run:  python3 tests/test_claim_release.py
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dedupe_guard as dg  # noqa: E402

TITLE = "استمع بقلبك 🎧 | الشيخ ياسر الدوسري #ياسر_الدوسري #قرآن #shorts"


class FakeYouTube:
    """Minimal channels().list / playlistItems().list stand-in."""

    def __init__(self, items):
        self.items = items
        self._kw = {}

    def channels(self):
        return self

    def playlistItems(self):
        return self

    def list(self, **kw):
        self._kw = kw
        return self

    def execute(self):
        if "mine" in self._kw:
            return {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU"}}}]}
        return {"items": [{"snippet": {"title": i["title"], "description": i["description"],
                                      "resourceId": {"videoId": i["id"]}}} for i in self.items]}


def test_identical_title_is_not_a_duplicate():
    yt = FakeYouTube([{"id": "vid1", "title": TITLE, "description": "desc\n\nref:ig/AAA"}])
    # Different reel, same templated title -> must NOT be blocked.
    assert dg.youtube_has_duplicate(yt, "BBB", TITLE) is None
    # Same reel -> still blocked by the hidden marker, even with an unrelated title.
    assert dg.youtube_has_duplicate(yt, "AAA", "unrelated title") == "vid1"
    # The old behaviour stays available as an explicit opt-in.
    assert dg.youtube_has_duplicate(yt, "BBB", TITLE, match_title=True) == "vid1"


class _Sandbox:
    """Point dedupe_guard at a throwaway directory with git disabled."""

    def __enter__(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._saved = {k: os.environ.get(k) for k in ("DEDUPE_GIT", "DEDUPE_REPO_DIR")}
        os.environ.pop("DEDUPE_GIT", None)
        os.environ["DEDUPE_REPO_DIR"] = str(self.tmp)
        self.history = self.tmp / "used_viral_reels.json"
        self.history.write_text("[]", encoding="utf-8")
        return self

    def __exit__(self, *exc):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)
        return False


def test_claim_then_release_allows_retry():
    with _Sandbox() as box:
        keys = ["CODE1", "fp_deadbeef"]
        assert dg.claim("quran", keys, history_file=box.history)
        assert json.loads(box.history.read_text(encoding="utf-8")) == ["CODE1"]
        assert (box.tmp / "claims" / "quran" / "CODE1").exists()

        assert dg.release_claim("quran", keys, history_file=box.history)
        assert json.loads(box.history.read_text(encoding="utf-8")) == []
        assert not (box.tmp / "claims" / "quran" / "CODE1").exists()
        # The reel is pickable again.
        assert dg.claim("quran", keys, history_file=box.history)


def test_download_failure_releases_claim():
    with _Sandbox() as box:
        cand = {"code": "CODE2", "caption": "تلاوة", "duration": 12.0}
        f, dd = dg.acquire_candidate("quran", cand, box.history, lambda c: None)
        assert f is None and dd is None
        assert not (box.tmp / "claims" / "quran" / "CODE2").exists()
        assert "CODE2" not in json.loads(box.history.read_text(encoding="utf-8"))


def test_successful_acquire_returns_claim_keys():
    with _Sandbox() as box:
        media = box.tmp / "v.mp4"
        media.write_bytes(b"VIDEO" * 2000)
        cand = {"code": "CODE3", "caption": "تلاوة", "duration": 12.0}
        f, dd = dg.acquire_candidate("quran", cand, box.history, lambda c: media)
        assert f == media
        assert dd["claim_keys"] == ["CODE3", dd["fp"]]

        # A visually identical file under a new reel code is still rejected by the media layer.
        dg.record_upload("quran", "CODE3", "vidX", "t", dd["fp"], dd["sha256"], dd["phash"])
        other = box.tmp / "v2.mp4"
        other.write_bytes(media.read_bytes())
        f2, _ = dg.acquire_candidate("quran", {"code": "CODE4", "caption": "x", "duration": 9.0},
                                     box.history, lambda c: other)
        assert f2 is None


if __name__ == "__main__":
    test_identical_title_is_not_a_duplicate()
    test_claim_then_release_allows_retry()
    test_download_failure_releases_claim()
    test_successful_acquire_returns_claim_keys()
    print("ALL CLAIM/RELEASE TESTS PASSED")
