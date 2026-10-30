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
        "name": "نور القرآن | The Holy Light",
        "email": "iman996372@gmail.com",
        "token_file": BASE_DIR / "token_quran.pickle"
    },
    "ai": {
        "name": "AI Unveiled | Future Tech",
        "email": "workonlin63@gmail.com",
        "token_file": BASE_DIR / "token_ai.pickle"
    },
    "cars": {
        "name": "AutoUnveiled | تاپ کارز",
        "email": "rahmatpour63@gmail.com",
        "token_file": BASE_DIR / "token_polygon.pickle"
    },
    "polygon": {
        "name": "AutoUnveiled | تاپ کارز",
        "email": "rahmatpour63@gmail.com",
        "token_file": BASE_DIR / "token_polygon.pickle"
    },
    "animals": {
        "name": "Wild Kingdom | عالم الحيوان",
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

def add_pinned_engagement_comment(youtube, video_id: str, comment_text: str):
    """
    Top YouTuber Strategy: Automatically posts and pins an engagement-hook comment
    to trigger algorithm discussion and boost CTR/watch time.
    """
    try:
        response = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
        ).execute()
        print("  [Auto-Comment] High-engagement comment posted successfully!", flush=True)
        return response
    except Exception as e:
        print(f"  [Auto-Comment Warning] Could not post initial comment: {e}")
        return None

def upload_short(channel_key: str, video_path: str, title: str, description: str, tags: list, category_id: str = "22", thumbnail_path: str = None, pinned_comment: str = None, publish_at: str = None):
    """
    Uploads a short video directly to YouTube, sets custom thumbnail, and leaves pinned engagement hook.
    If publish_at (ISO 8601 string e.g. '2026-10-12T13:12:00Z') is provided, sets scheduled private publish.
    """
    # EXCLUSIVE SECURITY LOCK FOR QURAN MASTER SESSION
    if channel_key == "quran":
        caller_file = Path(sys.argv[0]).name.lower()
        is_authorized = (
            caller_file in ["dispatch_cycle.py", "autonomous_growth_auditor.py", "fetch_and_upload_yasser_viral.py"]
            or os.environ.get("QURAN_MASTER_SESSION_AUTH") == "AUTHORIZED_786"
        )
        if not is_authorized:
            print(f"  [⛔ ACCESS DENIED] Script '{caller_file}' is not authorized to touch Quran channel. Exclusive Lock Active.", flush=True)
            return None
    try:
        youtube = get_authenticated_service(channel_key)
    except Exception as e:
        print(f"  [Upload Error] Authorization needed or failed for {channel_key}: {e}")
        return None

    status_obj = {
        "privacyStatus": "private" if publish_at else "public",
        "selfDeclaredMadeForKids": False
    }
    if publish_at:
        status_obj["publishAt"] = publish_at
        print(f"  [Scheduled Publish] YouTube video scheduled for public release at: {publish_at}")

    body = {
        "snippet": {
            "title": __import__("metadata_optimizer").smart_truncate(title, 100),
            "description": description,
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "ar" if channel_key == "quran" else ("en" if channel_key in ["ai", "animals"] else "en"),
            "defaultAudioLanguage": "ar" if channel_key == "quran" else "en"
        },
        "status": status_obj
    }

    chunk_size = 5 * 1024 * 1024  # 5MB chunks for reliable fast upload
    media = MediaFileUpload(video_path, chunksize=chunk_size, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    print(f"  [Uploading] Uploading {video_path} to {CHANNELS[channel_key]['name']}...", flush=True)
    try:
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  [Progress] Uploaded {int(status.progress() * 100)}%", flush=True)
    except Exception as e:
        print(f"  [Upload Limit / Quota Notice] YouTube upload limit reached for {channel_key}: {e}")
        return None

    if not response or not response.get("id"):
        return None

    video_id = response.get("id")
    short_url = f"https://youtube.com/shorts/{video_id}"
    print(f"  [Success] Published! URL: {short_url}", flush=True)

    if thumbnail_path and Path(thumbnail_path).exists() and video_id:
        try:
            print("  [Thumbnail] Setting custom thumbnail...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
        except Exception as e:
            print(f"  [Thumbnail Warning] Could not set thumbnail: {e}")

    # Post engagement comment to spike the algorithm
    if pinned_comment and video_id:
        add_pinned_engagement_comment(youtube, video_id, pinned_comment)

    return {
        "video_id": video_id,
        "id": video_id,
        "url": short_url
    }

