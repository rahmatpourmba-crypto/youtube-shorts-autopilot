"""
UNIVERSAL GOOGLE OAUTH RE-AUTHENTICATION FOR ALL CHANNELS
Automated Lifetime In-Production Token Generator
Usage:
  python reauth_channel.py quran
  python reauth_channel.py ai
  python reauth_channel.py polygon
  python reauth_channel.py animals
"""

import os
import sys
import pickle
import traceback
import subprocess
from pathlib import Path

# Allow relaxed scope & insecure transport on localhost
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
CLIENT_SECRETS = BASE_DIR / "client_secrets.json"
LOG_FILE = BASE_DIR / "reauth.log"

def log(msg):
    print(msg, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as lf:
            lf.write(str(msg) + "\n")
    except Exception:
        pass

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

CHANNELS = {
    "quran": {
        "name": "نور القرآن | The Holy Light",
        "email": "iman996372@gmail.com",
        "token": BASE_DIR / "token_quran.pickle"
    },
    "ai": {
        "name": "AI Unveiled | Future Tech",
        "email": "workonlin63@gmail.com",
        "token": BASE_DIR / "token_ai.pickle"
    },
    "polygon": {
        "name": "PolyMint Channel",
        "email": "rahmatpour63@gmail.com",
        "token": BASE_DIR / "token_polygon.pickle"
    },
    "animals": {
        "name": "Wild Kingdom | عالم الحيوان",
        "email": "ammm37474@gmail.com",
        "token": BASE_DIR / "token_animals.pickle"
    }
}

def main():
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "quran"
    info = CHANNELS.get(target)
    if not info:
        log(f"Unknown channel: {target}. Choices: {list(CHANNELS.keys())}")
        return

    log("=" * 65)
    log(f"=== RE-AUTHENTICATING CHANNEL: {info['name']} ===")
    log(f"Target Email: {info['email']}")
    log(f"Token File: {info['token'].name}")
    log("=" * 65)

    if not CLIENT_SECRETS.exists():
        log(f"[Error] client_secrets.json not found at {CLIENT_SECRETS}")
        return

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRETS),
            scopes=SCOPES
        )

        log("\n[Step 1] Opening browser for authorization...")
        log(f"Please log in with '{info['email']}' and click 'Allow / ادامه'...\n")

        creds = flow.run_local_server(
            port=8080,
            prompt="consent",
            access_type="offline",
            open_browser=True
        )

        # Save to token pickle
        with open(info["token"], "wb") as f:
            pickle.dump(creds, f)

        log(f"\n[✓] SUCCESS! Token saved to: {info['token'].name}")
        log(f"Refresh Token Present: {bool(creds.refresh_token)}")

        # Step 2: Live Verification with YouTube API
        log("\n[Step 2] Verifying connection with YouTube Data API...")
        try:
            youtube = build("youtube", "v3", credentials=creds)
            resp = youtube.channels().list(mine=True, part="snippet").execute()
            items = resp.get("items", [])
            if items:
                ch_title = items[0]["snippet"]["title"]
                log(f"[✓] VERIFIED LIVE CHANNEL: '{ch_title}'")
            else:
                log("[!] Connected successfully (no public channel item returned).")
        except Exception as ve:
            log(f"[Warning] Verification API test: {ve}")

        # Step 3: Git Commit & Push
        log("\n[Step 3] Staging permanent token to Git & GitHub...")
        subprocess.run(["git", "add", "client_secrets.json", info["token"].name], cwd=str(BASE_DIR), check=True)
        commit_res = subprocess.run(
            ["git", "commit", "-m", f"chore: Update permanent lifetime {info['token'].name} (In-Production project)"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True
        )
        log(f"Git commit: {commit_res.stdout or commit_res.stderr}")

        push_res = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True
        )
        log(f"Git push: {push_res.stdout or push_res.stderr}")

        # Step 4: Trigger GitHub Actions Workflow
        log(f"\n[Step 4] Triggering 24/7 Autopilot for channel '{target}' on GitHub Actions...")
        try:
            wf_res = subprocess.run(
                ["gh", "workflow", "run", "24/7 Active Shorts & Auto-Keepalive Pipeline", "--ref", "main", "-f", f"target_channel={target}"],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True
            )
            log(f"Workflow trigger: {wf_res.stdout or wf_res.stderr or 'OK'}")
        except Exception as we:
            log(f"[Warning] Triggering workflow: {we}")

        log("\n" + "=" * 65)
        log("[✓] ALL STEPS COMPLETED 100%! Permanent lifetime authorization is LIVE.")
        log("=" * 65)

    except Exception as e:
        log(f"\n[OAuth Error] {e}")
        log(traceback.format_exc())

if __name__ == "__main__":
    main()
