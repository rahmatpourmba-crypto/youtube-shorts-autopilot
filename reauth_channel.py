"""
ONE-CLICK GOOGLE OAUTH RE-AUTHENTICATOR FOR ALL 4 CHANNELS
Permanently links your Google Accounts to the 'trand-508710' In-Production Project!

Usage:
  python reauth_channel.py quran
  python reauth_channel.py ai
  python reauth_channel.py polygon
  python reauth_channel.py animals
"""

import sys
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
CLIENT_SECRETS = BASE_DIR / "client_secrets.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

CHANNELS = {
    "quran": {
        "name": "نور القرآن | The Holy Light",
        "email": "iman996372@gmail.com",
        "token_file": BASE_DIR / "token_quran.pickle"
    },
    "ai": {
        "name": "AI Unveiled | Future Tech",
        "email": "workonlin63@gmail.com",
        "token_file": BASE_DIR / "token_ai.pickle"
    },
    "polygon": {
        "name": "PolyMint Channel (CryptoLab)",
        "email": "rahmatpour63@gmail.com",
        "token_file": BASE_DIR / "token_polygon.pickle"
    },
    "animals": {
        "name": "Wild Kingdom | عالم الحيوان",
        "email": "ammm37474@gmail.com",
        "token_file": BASE_DIR / "token_animals.pickle"
    }
}

def reauth(channel_key: str):
    info = CHANNELS.get(channel_key)
    if not info:
        print(f"[Error] Unknown channel '{channel_key}'. Choose from: {list(CHANNELS.keys())}")
        return

    print("=" * 65)
    print(f"=== PERMANENT LIFETIME OAUTH: {info['name'].upper()} ===")
    print(f"Target Google Account: {info['email']}")
    print(f"Token Output: {info['token_file'].name}")
    print("=" * 65)

    if not CLIENT_SECRETS.exists():
        print(f"[Error] client_secrets.json not found at {CLIENT_SECRETS}")
        return

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
    print("\n[Step 1] Opening browser for Google Authorization...")
    print(f"IMPORTANT: Please ensure you select/log in with '{info['email']}' and click 'Allow / ادامه'...\n")

    try:
        creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")
        with open(info["token_file"], "wb") as f:
            pickle.dump(creds, f)
        print(f"\n✓ SUCCESS! Lifetime permanent token generated and saved to: {info['token_file'].name}")
    except Exception as e:
        print(f"\n[OAuth Error] {e}")

if __name__ == "__main__":
    ch = sys.argv[1].lower() if len(sys.argv) > 1 else "ai"
    reauth(ch)
