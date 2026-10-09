import os
import sys
import pickle
from pathlib import Path

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

BASE_DIR = Path(__file__).resolve().parent
CLIENT_SECRETS_FILE = BASE_DIR / "client_secrets.json"

CHANNELS = {
    "quran": {
        "name": "Quranic Channel",
        "email": "iman996372@gmail.com",
        "token_file": BASE_DIR / "token_quran.pickle"
    },
    "ai": {
        "name": "AI Tools Channel",
        "email": "workonlin63@gmail.com",
        "token_file": BASE_DIR / "token_ai.pickle"
    },
    "polygon": {
        "name": "PolyMint Channel",
        "email": "rahmatpour63@gmail.com",
        "token_file": BASE_DIR / "token_polygon.pickle"
    },
    "animals": {
        "name": "Animals Channel",
        "email": "ammm37474@gmail.com",
        "token_file": BASE_DIR / "token_animals.pickle"
    }
}

def get_authenticated_service(channel_key: str):
    info = CHANNELS.get(channel_key)
    if not info:
        raise ValueError(f"Unknown channel: {channel_key}")
        
    token_path = info["token_file"]
    creds = None
    
    if token_path.exists():
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRETS_FILE.exists():
                raise FileNotFoundError(f"Missing client_secrets.json at {CLIENT_SECRETS_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE), SCOPES
            )
            print(f"\n[OAuth] Authorizing {info['name']} ({info['email']})...")
            creds = flow.run_local_server(port=0, prompt="consent")
            
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
            
    return build("youtube", "v3", credentials=creds)

def upload_short(channel_key: str, video_path: str, title: str, description: str, tags: list, category_id: str = "22", thumbnail_path: str = None):
    """
    Uploads a short video directly to YouTube and sets custom thumbnail.
    """
    try:
        youtube = get_authenticated_service(channel_key)
    except Exception as e:
        print(f"  [Upload Error] Authorization needed or failed for {channel_key}: {e}")
        return None

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    print(f"  [Uploading] Uploading {video_path} to {CHANNELS[channel_key]['name']}...")
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  [Progress] Uploaded {int(status.progress() * 100)}%")

    video_id = response.get("id")
    short_url = f"https://youtube.com/shorts/{video_id}"
    print(f"  [Success] Published! URL: {short_url}")

    if thumbnail_path and Path(thumbnail_path).exists() and video_id:
        try:
            print("  [Thumbnail] Setting custom thumbnail...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
        except Exception as e:
            print(f"  [Thumbnail Warning] Could not set thumbnail: {e}")

    return {
        "video_id": video_id,
        "url": short_url
    }
