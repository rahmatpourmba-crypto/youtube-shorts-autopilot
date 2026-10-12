import sys
import pickle
from pathlib import Path
from googleapiclient.discovery import build

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

channels = [
    ('quran', 'token_quran.pickle'),
    ('ai', 'token_ai.pickle'),
    ('polygon', 'token_polygon.pickle'),
    ('animals', 'token_animals.pickle')
]

for ch_name, token_file in channels:
    print("=" * 65)
    print(f"FORENSIC DEEP AUDIT: {ch_name.upper()}")
    p = Path(token_file)
    if not p.exists():
        print("  Token not found.")
        continue
    with open(p, 'rb') as f:
        creds = pickle.load(f)
    yt = build('youtube', 'v3', credentials=creds)

    # 1. Channel Details
    ch_res = yt.channels().list(part='snippet,status,brandingSettings,contentDetails', mine=True).execute()
    ch_item = ch_res['items'][0]
    print(f"  Channel Title: {ch_item['snippet']['title']}")
    print(f"  Channel Status: {ch_item.get('status', {})}")
    
    # 2. Uploads Playlist
    uploads_playlist_id = ch_item['contentDetails']['relatedPlaylists']['uploads']
    
    # Get last 5 videos from Uploads playlist
    pl_items = yt.playlistItems().list(part='snippet,contentDetails', playlistId=uploads_playlist_id, maxResults=5).execute()
    v_ids = [item['contentDetails']['videoId'] for item in pl_items.get('items', [])]
    
    if v_ids:
        v_details = yt.videos().list(part='snippet,status,contentDetails,processingDetails,statistics', id=','.join(v_ids)).execute()
        for v in v_details.get('items', []):
            vid = v['id']
            snip = v['snippet']
            stat = v['status']
            cd = v['contentDetails']
            pd = v.get('processingDetails', {})
            stats = v.get('statistics', {})
            print(f"  --------------------------------------------------")
            print(f"  Video ID: {vid} | Views: {stats.get('viewCount', 0)} | Likes: {stats.get('likeCount', 0)}")
            print(f"  Title: {snip['title']}")
            print(f"  Privacy: {stat.get('privacyStatus')} | UploadStatus: {stat.get('uploadStatus')} | Processing: {pd.get('processingStatus')}")
            print(f"  Duration: {cd.get('duration')} | Dimension: {cd.get('dimension')} | Definition: {cd.get('definition')}")
            print(f"  Rejection Reason: {stat.get('rejectionReason')} | Failure Reason: {stat.get('failureReason')}")
            print(f"  Has Custom Thumbnail: {cd.get('hasCustomThumbnail')} | Licensed: {cd.get('licensedContent')}")
            print(f"  Category ID: {snip.get('categoryId')} | Tags Count: {len(snip.get('tags', []))}")
            print(f"  Published At: {snip.get('publishedAt')}")
