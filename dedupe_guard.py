"""
Duplicate-upload guard (owner requirement: NEVER upload the same video twice).

Layers (any one of them blocks a duplicate):
  1. sync_latest()      - pull latest state from origin/main at run start and before every claim.
  2. claim()            - git-based distributed lock: a claim file per reel code and per
                          caption+duration fingerprint is committed and pushed to main BEFORE
                          downloading/uploading. Push success == lock acquired. On rejection we
                          fetch, re-check whether someone else claimed it, and only retry if not.
  3. media dedupe       - sha256 + perceptual frame hash (ffmpeg, cheap) of the downloaded file
                          compared against upload_registry.json (different reel codes, same video).
  4. YouTube check      - youtube_has_duplicate(): uploads playlist (playlistItems.list, 1 quota unit)
                          scanned for the hidden 'ref:' marker or an identical title.
Git operations run only when DEDUPE_GIT=1 (set in the workflow) so local/offline runs never push.
"""
import hashlib
import json
import os
import re
import subprocess
import time
import unicodedata
from pathlib import Path

BASE_DIR = Path(os.environ.get("DEDUPE_REPO_DIR") or Path(__file__).resolve().parent)
CLAIMS_DIR = "claims"
REGISTRY_FILE = "upload_registry.json"
MARKER_PREFIX = "ref:ig/"
PHASH_MAX_HAMMING = 6          # out of 64 bits per frame (averaged)


def _base():
    return Path(os.environ.get("DEDUPE_REPO_DIR") or BASE_DIR)


def git_enabled():
    return os.environ.get("DEDUPE_GIT") == "1"


def _git(*args, check=False):
    r = subprocess.run(["git", *args], cwd=_base(), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r


def sync_latest():
    """Bring the working copy up to date with origin/main (keeps local uncommitted state)."""
    if not git_enabled():
        return False
    for i in range(3):
        r = _git("pull", "--rebase", "--autostash", "-X", "theirs", "origin", "main")
        if r.returncode == 0:
            return True
        _git("rebase", "--abort")
        time.sleep(2 * (i + 1))
    print(f"  [Dedupe] WARNING: could not pull latest state: {r.stderr.strip()[:200]}")
    return False


# ---------------------------------------------------------------- fingerprints
def normalize_caption(caption: str) -> str:
    t = unicodedata.normalize("NFKC", caption or "").lower()
    t = re.sub(r"https?://\S+|@\w+|#", " ", t)
    t = re.sub(r"[\u064B-\u0652\u0640]", "", t)          # Arabic diacritics / tatweel
    t = re.sub(r"[^\w\u0600-\u06FF]+", " ", t)
    return " ".join(t.split())


def caption_fingerprint(caption: str, duration) -> str:
    """Same caption + same duration (rounded to 1s) from different reel codes == same video."""
    d = int(round(float(duration or 0)))
    h = hashlib.sha1(f"{normalize_caption(caption)}|{d}".encode("utf-8")).hexdigest()[:16]
    return f"fp_{h}"


def file_sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def perceptual_hash(path, frames=8):
    """List of 64-bit average-hashes (hex) of evenly spaced frames, or None if ffmpeg unavailable."""
    try:
        cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-vf",
               f"fps=1,scale=8:8,format=gray", "-frames:v", str(frames), "-f", "rawvideo", "-"]
        raw = subprocess.run(cmd, capture_output=True, timeout=60).stdout
        out = []
        for i in range(0, len(raw) - 63, 64):
            px = raw[i:i + 64]
            avg = sum(px) / 64.0
            bits = "".join("1" if p >= avg else "0" for p in px)
            out.append(f"{int(bits, 2):016x}")
        return out or None
    except Exception:
        return None


def phash_distance(a, b):
    if not a or not b:
        return 64
    n = min(len(a), len(b))
    return sum(bin(int(x, 16) ^ int(y, 16)).count("1") for x, y in zip(a[:n], b[:n])) / n


# ---------------------------------------------------------------- registry
def load_registry():
    p = _base() / REGISTRY_FILE
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_registry(reg):
    (_base() / REGISTRY_FILE).write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")


def media_is_duplicate(channel, path, code=None):
    """Return reason string if the downloaded file matches an already-uploaded video."""
    reg = load_registry().get(channel, [])
    sha = file_sha256(path)
    ph = perceptual_hash(path)
    for e in reg:
        if e.get("code") == code:
            continue
        if e.get("sha256") == sha:
            return f"identical file to {e.get('code')} ({e.get('video_id')})", sha, ph
        if ph and e.get("phash") and phash_distance(ph, e["phash"]) <= PHASH_MAX_HAMMING:
            return f"visually identical to {e.get('code')} ({e.get('video_id')})", sha, ph
    return None, sha, ph


def record_upload(channel, code, video_id, title, fp=None, sha=None, ph=None):
    reg = load_registry()
    reg.setdefault(channel, []).append({"code": code, "video_id": video_id, "title": title,
                                        "fp": fp, "sha256": sha, "phash": ph, "ts": int(time.time())})
    save_registry(reg)


# ---------------------------------------------------------------- claims (lock)
def _claim_paths(channel, keys):
    return [f"{CLAIMS_DIR}/{channel}/{re.sub(r'[^A-Za-z0-9_-]', '_', k)}" for k in keys if k]


def is_claimed(channel, keys):
    return any((_base() / p).exists() for p in _claim_paths(channel, keys))


def _reset_to_remote():
    """Move HEAD to origin/main, dropping our unpushed commit but keeping uncommitted work."""
    _git("fetch", "-q", "origin", "main")
    r = _git("-c", "rebase.autoStash=true", "rebase", "-q", "--onto", "origin/main", "HEAD")
    if r.returncode != 0:
        _git("rebase", "--abort")
        _git("stash", "-q")
        _git("reset", "-q", "--hard", "origin/main")
        _git("stash", "pop", "-q")


def commit_and_push(mutate, msg, max_tries=6):
    """Optimistic-concurrency write to main: mutate() edits files on top of the latest
    origin/main and returns the list of paths (or None to abort). Push success == committed.
    On rejection we drop our commit, reset to the new origin/main and re-run mutate()."""
    for i in range(max_tries):
        if git_enabled():
            _reset_to_remote() if i else sync_latest()
        paths = mutate()
        if paths is None:
            return False
        if not git_enabled():
            return True
        _git("add", "--", *paths, check=True)
        if _git("diff", "--cached", "--quiet").returncode == 0:
            return True
        _git("commit", "-q", "-m", msg, "--", *paths, check=True)
        if _git("push", "-q", "origin", "HEAD:main").returncode == 0:
            return True
        print(f"  [Dedupe] push rejected (try {i+1}), re-syncing and re-checking...")
        time.sleep(1.5 * (i + 1))
    print("  [Dedupe] could not push after retries")
    return False


def _rel(path):
    return str(Path(path).resolve().relative_to(_base().resolve()))


def claim(channel, keys, history_file=None, run_id=None, max_tries=6):
    """Atomically claim keys (reel code first, then fingerprints). True => this run owns them.
    Fails closed: if the claim cannot be pushed, the caller must NOT upload."""
    keys = [k for k in keys if k]
    paths = _claim_paths(channel, keys)
    run_id = run_id or os.environ.get("GITHUB_RUN_ID", "local")
    state = {"lost": False}

    def mutate():
        if is_claimed(channel, keys):
            state["lost"] = True
            return None
        hist = []
        if history_file is not None:
            try:
                hist = json.loads(Path(history_file).read_text(encoding="utf-8"))
            except Exception:
                hist = []
            if keys[0] in hist:
                state["lost"] = True
                return None
        for p in paths:
            fp = _base() / p
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(json.dumps({"run": run_id, "ts": int(time.time())}) + "\n", encoding="utf-8")
        out = list(paths)
        if history_file is not None:
            hist.append(keys[0])
            Path(history_file).write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")
            out.append(_rel(history_file))
        return out

    ok = commit_and_push(mutate, f"chore(claim): {channel} {keys[0]} [run {run_id}]", max_tries)
    if ok:
        print(f"  [Dedupe] Claimed {channel}:{keys[0]} (lock acquired)")
    elif state["lost"]:
        print(f"  [Dedupe] {channel}:{keys[0]} already used/claimed -> skip")
    return ok


def record_and_push(channel, code, video_id, title, fp=None, sha=None, ph=None):
    def mutate():
        record_upload(channel, code, video_id, title, fp, sha, ph)
        return [REGISTRY_FILE]
    return commit_and_push(mutate, f"chore(registry): {channel} {code} -> {video_id}")


# ---------------------------------------------------------------- YouTube check
def marker(code):
    return f"{MARKER_PREFIX}{code}"


def add_marker(description, code):
    m = marker(code)
    return description if m in (description or "") else f"{description or ''}\n\n{m}"


def youtube_has_duplicate(youtube, code, title, max_items=100):
    """Scan the channel's uploads playlist (1 quota unit/page). Returns video_id or None."""
    ch = youtube.channels().list(part="contentDetails", mine=True).execute()
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    token, seen, t_norm = None, 0, (title or "").strip().casefold()
    while seen < max_items:
        resp = youtube.playlistItems().list(part="snippet", playlistId=uploads, maxResults=50,
                                            pageToken=token).execute()
        for it in resp.get("items", []):
            sn = it.get("snippet", {})
            vid = sn.get("resourceId", {}).get("videoId")
            if marker(code) in (sn.get("description") or "") or code in (sn.get("description") or ""):
                return vid
            if t_norm and (sn.get("title") or "").strip().casefold() == t_norm:
                return vid
            seen += 1
        token = resp.get("nextPageToken")
        if not token:
            break
    return None


def acquire_candidate(channel, cand, history_file, download_fn):
    """Claim -> download -> media-dedupe. Returns (path, info) or (None, None).
    A claimed-but-rejected reel stays claimed (never retried) - safe default."""
    code = cand["code"]
    fp = caption_fingerprint(cand.get("caption", ""), cand.get("duration", 0))
    if not claim(channel, [code, fp], history_file=history_file):
        return None, None
    path = download_fn(cand)
    if not path:
        return None, None
    reason, sha, ph = media_is_duplicate(channel, path, code)
    if reason:
        print(f"  [Dedupe] {code} rejected: {reason}")
        return None, None
    return path, {"fp": fp, "sha256": sha, "phash": ph}
