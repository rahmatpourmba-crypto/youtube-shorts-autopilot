import os
import sys
import json
import requests
from pathlib import Path

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ayrshare API Key
AYRSHARE_API_KEY = os.environ.get("AYRSHARE_API_KEY") or "C4CA0622-A7AB41CC-BCC97E84-37166BE4"
AYRSHARE_POST_URL = "https://app.ayrshare.com/api/post"
AYRSHARE_MEDIA_UPLOAD_URL = "https://app.ayrshare.com/api/media/upload"

def upload_media_to_ayrshare(file_path: str):
    """
    Uploads video file to Ayrshare media storage and returns public URL.
    """
    headers = {
        "Authorization": f"Bearer {AYRSHARE_API_KEY}"
    }
    with open(file_path, "rb") as f:
        files = {"file": f}
        res = requests.post(AYRSHARE_MEDIA_UPLOAD_URL, headers=headers, files=files)
        res_data = res.json()
        if res.status_code == 200 and "url" in res_data:
            return res_data["url"]
        else:
            raise RuntimeError(f"Media upload failed: {res_data}")

def publish_instagram_reel(video_path: str, caption: str, media_url: str = None):
    """
    Publishes a vertical video as an Instagram Reel via Ayrshare.
    """
    headers = {
        "Authorization": f"Bearer {AYRSHARE_API_KEY}",
        "Content-Type": "application/json"
    }

    # If public media_url is not provided, upload local file
    if not media_url:
        print("  [Instagram] Uploading video to Ayrshare media CDN...")
        media_url = upload_media_to_ayrshare(video_path)
        print(f"  [Instagram] CDN URL generated: {media_url[:60]}...")

    payload = {
        "post": caption,
        "platforms": ["instagram"],
        "mediaUrls": [media_url],
        "instagramOptions": {
            "reels": True,
            "shareToFeed": True
        }
    }

    print("  [Instagram] Publishing Reel to @abdol_basit_rahmatpour...")
    res = requests.post(AYRSHARE_POST_URL, headers=headers, json=payload)
    res_data = res.json()

    if res.status_code == 200 and res_data.get("status") == "success":
        post_id = res_data.get("id")
        post_url = res_data.get("postUrl")
        print(f"  [Instagram Success] Published Reel! URL: {post_url or post_id}")
        return res_data
    else:
        print(f"  [Instagram Notice] Result: {res_data}")
        return res_data

if __name__ == "__main__":
    print("Testing connection...")
    r = requests.get("https://app.ayrshare.com/api/user", headers={"Authorization": f"Bearer {AYRSHARE_API_KEY}"})
    print(r.json().get("displayNames"))
