import sys
import pickle
from googleapiclient.discovery import build
from pathlib import Path

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

for ch, token_name in [('quran', 'token_quran.pickle'), ('ai', 'token_ai.pickle'), ('polygon', 'token_polygon.pickle'), ('animals', 'token_animals.pickle')]:
    print('='*55)
    print(f"Checking Channel: {ch}")
    tp = Path(token_name)
    if not tp.exists():
        print("  Token not found")
        continue
    with open(tp, 'rb') as f:
        creds = pickle.load(f)
    yt = build('youtube', 'v3', credentials=creds)
    ch_res = yt.channels().list(part='snippet,statistics', mine=True).execute()
    item = ch_res['items'][0]
    title = item['snippet']['title']
    views = item['statistics'].get('viewCount', 0)
    subs = item['statistics'].get('subscriberCount', 0)
    video_count = item['statistics'].get('videoCount', 0)
    print(f"  Channel: {title} | Subs: {subs} | Total Views: {views} | Videos: {video_count}")
    
    v_res = yt.search().list(part='snippet', forMine=True, type='video', maxResults=5, order='date').execute()
    v_ids = [i['id']['videoId'] for i in v_res.get('items', []) if 'videoId' in i.get('id', {})]
    if v_ids:
        details = yt.videos().list(part='snippet,status,statistics,contentDetails', id=','.join(v_ids)).execute()
        for d in details.get('items', []):
            vid = d['id']
            v_title = d['snippet']['title'][:40]
            privacy = d['status']['privacyStatus']
            upload_status = d['status']['uploadStatus']
            v_views = d['statistics'].get('viewCount', 0)
            likes = d['statistics'].get('likeCount', 0)
            published_at = d['snippet'].get('publishedAt', '')[:10]
            print(f"    - [{vid}] ({published_at}) {privacy} | {v_views} views | {likes} likes | {v_title}")
