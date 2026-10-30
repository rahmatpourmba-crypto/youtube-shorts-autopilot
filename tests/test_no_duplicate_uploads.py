"""Offline mock test: two concurrent runs (separate clones of one origin) race for the same
viral reel. Proves exactly one upload, the loser picks another reel, the same video re-posted
under a different reel code is rejected, and a stale/lost-state run is still blocked.
Run:  python3 tests/test_no_duplicate_uploads.py
"""
import json, os, shutil, subprocess, sys, tempfile, time
from multiprocessing import Process, Barrier, Manager
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def sh(cwd, *a):
    subprocess.run(a, cwd=cwd, check=True, capture_output=True)


def make_origin(tmp):
    origin = tmp / "origin.git"
    sh(tmp, "git", "init", "-q", "--bare", "-b", "main", str(origin))
    seed = tmp / "seed"
    sh(tmp, "git", "clone", "-q", str(origin), str(seed))
    (seed / "used_viral_reels.json").write_text("[]")
    (seed / "upload_registry.json").write_text("{}")
    for c in ("user.email", "user.name"):
        sh(seed, "git", "config", c, "t")
    sh(seed, "git", "add", ".")
    sh(seed, "git", "commit", "-q", "-m", "seed")
    sh(seed, "git", "push", "-q", "origin", "HEAD:main")
    return origin


def clone(tmp, origin, name):
    d = tmp / name
    sh(tmp, "git", "clone", "-q", str(origin), str(d))
    for c in ("user.email", "user.name"):
        sh(d, "git", "config", c, name)
    return d


CANDS = [  # ranked: both runs prefer A
    {"code": "DdECoeAKqy_", "caption": "ياسر الدوسري #تلاوة", "duration": 27.17},
    {"code": "REEL_B", "caption": "other recitation", "duration": 31.0},
    {"code": "REEL_C", "caption": "third", "duration": 20.0},
]


class FakeYouTube:
    """Shared 'channel' persisted in a JSON file so both processes see it."""
    def __init__(self, path): self.path = path
    def _items(self): return json.loads(Path(self.path).read_text()) if Path(self.path).exists() else []
    def channels(self): return self
    def playlistItems(self): return self
    def list(self, **kw):
        self._kw = kw; return self
    def execute(self):
        if "mine" in self._kw:
            return {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU"}}}]}
        return {"items": [{"snippet": {"title": i["title"], "description": i["description"],
                                       "resourceId": {"videoId": i["id"]}}} for i in self._items()]}
    def insert(self, title, description):
        items = self._items(); vid = f"vid{len(items)+1}"
        items.append({"id": vid, "title": title, "description": description})
        Path(self.path).write_text(json.dumps(items)); return vid


def run_cycle(workdir, channel_file, media_dir, barrier, results, name, cands=CANDS, sync=True):
    os.environ.update(DEDUPE_GIT="1", DEDUPE_REPO_DIR=str(workdir), GITHUB_RUN_ID=name)
    sys.path.insert(0, str(REPO))
    import dedupe_guard as dg
    if barrier: barrier.wait()
    if sync: dg.sync_latest()
    used = set(json.loads((workdir / "used_viral_reels.json").read_text()))
    yt = FakeYouTube(channel_file)

    def download(c):  # same physical video for identical content
        p = Path(media_dir) / f"{name}_{c['code']}.mp4"
        p.write_bytes(("VIDEO:" + c["caption"]).encode() * 2000); return p

    for cand in [c for c in cands if c["code"] not in used]:
        f, dd = dg.acquire_candidate("quran", cand, workdir / "used_viral_reels.json", download)
        if not f:
            continue
        title = "Title " + cand["caption"]
        desc = dg.add_marker("desc", cand["code"])
        if dg.youtube_has_duplicate(yt, cand["code"], title):
            results.append((name, "yt-dup", cand["code"])); return
        time.sleep(0.5)  # slow upload widens the race window
        vid = yt.insert(title, desc)
        dg.record_and_push("quran", cand["code"], vid, title, dd["fp"], dd["sha256"], dd["phash"])
        results.append((name, "uploaded", cand["code"])); return
    results.append((name, "nothing", None))


def main():
    tmp = Path(tempfile.mkdtemp())
    try:
        origin = make_origin(tmp)
        a, b = clone(tmp, origin, "runA"), clone(tmp, origin, "runB")
        chan, media = tmp / "channel.json", tmp / "media"; media.mkdir()
        with Manager() as m:
            res, bar = m.list(), Barrier(2)
            ps = [Process(target=run_cycle, args=(d, str(chan), str(media), bar, res, d.name)) for d in (a, b)]
            [p.start() for p in ps]; [p.join(120) for p in ps]
            res = list(res)
        items = json.loads(chan.read_text())
        codes = [i["description"].split("ref:ig/")[-1] for i in items]
        print("concurrent results:", res); print("channel:", codes)
        assert len(codes) == len(set(codes)), "DUPLICATE UPLOAD!"
        assert codes.count("DdECoeAKqy_") == 1, "reel A must be uploaded exactly once"
        assert sorted(r[2] for r in res) == ["DdECoeAKqy_", "REEL_B"], res

        # Same caption+duration under a NEW reel code (re-post) -> rejected by fingerprint claim
        c = clone(tmp, origin, "runC")
        res2 = []
        run_cycle(c, str(chan), str(media), None, res2, "runC",
                  cands=[{"code": "REPOST_1", "caption": "ياسر  الدوسري #تلاوة", "duration": 27.4}])
        print("repost:", res2); assert res2[0][1] == "nothing", res2

        # Lost state push: a stale clone whose history is empty and that never pulls still can't
        # re-upload, because the claim push is rejected and the remote claim is detected.
        stale = clone(tmp, origin, "stale"); root = subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"], cwd=stale,
                             capture_output=True, text=True).stdout.strip()
        sh(stale, "git", "reset", "-q", "--hard", root)
        res3 = []
        run_cycle(stale, str(chan), str(media), None, res3, "stale", cands=CANDS[:1], sync=False)
        print("stale:", res3); assert res3[0][1] == "nothing", res3

        # YouTube-side check: claims wiped (e.g. repo history rewritten) -> uploads playlist blocks it
        sys.path.insert(0, str(REPO)); import dedupe_guard as dg
        assert dg.youtube_has_duplicate(FakeYouTube(str(chan)), "DdECoeAKqy_", "x")
        assert len(json.loads(chan.read_text())) == 2
        print("ALL DEDUPE TESTS PASSED: only one upload per video")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
