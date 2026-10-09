import sys
from pathlib import Path
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from youtube_uploader import get_authenticated_service

def inspect():
    youtube = get_authenticated_service("polygon")
    
    # Get channel info
    ch_req = youtube.channels().list(part="snippet,statistics,contentDetails", mine=True)
    ch_res = ch_req.execute()
    
    items = ch_res.get("items", [])
    if not items:
        print("No channel found for this account.")
        return

    channel = items[0]
    snippet = channel["snippet"]
    stats = channel.get("statistics", {})
    
    print("=" * 60)
    print("Channel Title:", snippet.get("title"))
    print("Custom URL:", snippet.get("customUrl", "None"))
    print("Channel ID:", channel.get("id"))
    print("Channel Link: https://www.youtube.com/channel/" + channel.get("id"))
    print("Subscribers:", stats.get("subscriberCount", "0"))
    print("Total Videos:", stats.get("videoCount", "0"))
    print("Total Views:", stats.get("viewCount", "0"))
    print("=" * 60)
    
    # Check the latest video status (4XWGffTQbu8)
    vid_req = youtube.videos().list(part="snippet,status,statistics", id="4XWGffTQbu8")
    vid_res = vid_req.execute()
    if vid_res.get("items"):
        v = vid_res["items"][0]
        print("\nLatest Video:")
        print("  Title:", v["snippet"]["title"])
        print("  Privacy:", v["status"]["privacyStatus"])
        print("  Upload Status:", v["status"].get("uploadStatus"))
        print("  Direct Link: https://youtube.com/shorts/" + v["id"])

if __name__ == "__main__":
    inspect()
