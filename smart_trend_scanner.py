import subprocess
import json
import time
from pathlib import Path

def find_highest_velocity_viral_short(search_query: str, max_candidates: int = 10):
    """
    ULTRA-SMART VIRAL TREND SCANNER (ترندینگ‌یابی فوق هوشمند):
    Scans the top candidates, computes their Viral Growth Velocity,
    and returns the #1 exploding video right now.
    
    Formula:
    Viral Velocity = (Views / Days Since Upload) * Engagement Factor
    """
    cmd = [
        "yt-dlp",
        f"ytsearch{max_candidates}:{search_query} #shorts",
        "--match-filter", "duration <= 59 & duration >= 10",
        "--dump-json",
        "--flat-playlist", "False",
        "--no-playlist"
    ]
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    candidates = []
    
    now_ts = time.time()
    for line in res.stdout.strip().split("\n"):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            views = item.get("view_count") or 0
            likes = item.get("like_count") or 0
            timestamp = item.get("timestamp") or (now_ts - 86400 * 30)
            
            # Days since published
            days_active = max(1.0, (now_ts - timestamp) / 86400.0)
            
            # Engagement ratio
            engagement = (likes / views) if views > 0 else 0.05
            
            # Viral Velocity Score: prioritize fresh exploding videos over stale old ones
            viral_velocity = (views / (days_active ** 0.8)) * (1.0 + engagement * 10)
            
            candidates.append({
                "id": item.get("id"),
                "url": item.get("webpage_url") or f"https://www.youtube.com/watch?v={item.get('id')}",
                "title": item.get("title", ""),
                "views": views,
                "likes": likes,
                "days_active": round(days_active, 1),
                "velocity_score": viral_velocity,
                "tags": item.get("tags") or [],
                "description": item.get("description") or ""
            })
        except Exception:
            continue
            
    if not candidates:
        return None
        
    # Sort descending by Viral Velocity Score
    candidates.sort(key=lambda x: x["velocity_score"], reverse=True)
    best = candidates[0]
    print(f"  [Smart Trend Scanner] Top Trend Selected: '{best['title'][:60]}...'")
    print(f"    Views: {best['views']:,} | Age: {best['days_active']} days | Velocity Score: {best['velocity_score']:,.0f}")
    return best
