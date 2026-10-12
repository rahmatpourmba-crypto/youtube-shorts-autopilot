import subprocess
import json
import time
from pathlib import Path

def find_highest_velocity_viral_short(search_query: str, max_candidates: int = 25):
    """
    ULTRA-SMART VIRAL TREND SCANNER (ترندینگ‌یابی فوق هوشمند):
    Scans the top candidates, computes their Viral Growth Velocity,
    and returns the #1 exploding video right now.
    """
    cmd = [
        "yt-dlp",
        f"ytsearch{max_candidates}:{search_query}",
        "--match-filter", "duration >= 10 & duration <= 30",
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
            dur = item.get("duration") or 20
            
            # Strict 10-30s Duration Lock for Ultra-High Looping Retention
            if dur > 32 or dur < 8:
                continue

            # Strict Moral & Halal Safety Check
            from halal_content_filter import is_content_halal_and_clean
            title = item.get("title", "")
            desc = item.get("description", "")
            tags = item.get("tags") or []
            
            if not is_content_halal_and_clean(title, desc, tags):
                print(f"  [Halal Shield] Skipped non-compliant/unethical candidate: '{title[:50]}...'")
                continue
            
            # Days since published
            days_active = max(1.0, (now_ts - timestamp) / 86400.0)
            
            # Engagement ratio
            engagement = (likes / views) if views > 0 else 0.05
            
            # 15-24s Retention Bonus (MrBeast & TikTok Viral Sweet Spot)
            dur_bonus = 1.35 if 14 <= dur <= 25 else 1.0
            
            # Viral Velocity Score: prioritize fresh exploding short videos
            viral_velocity = (views / (days_active ** 0.8)) * (1.0 + engagement * 10) * dur_bonus

            # Chrono-Intelligence: Reverse-Engineer Original Video Peak Upload Hour
            import datetime
            orig_dt_utc = datetime.datetime.utcfromtimestamp(timestamp) if timestamp else datetime.datetime.utcnow()
            orig_tehran_dt = orig_dt_utc + datetime.timedelta(hours=3, minutes=30)
            seed_hour_utc = (orig_dt_utc.hour - 2) % 24
            
            candidates.append({
                "id": item.get("id"),
                "url": item.get("webpage_url") or f"https://www.youtube.com/watch?v={item.get('id')}",
                "title": title,
                "views": views,
                "likes": likes,
                "days_active": round(days_active, 1),
                "velocity_score": viral_velocity,
                "tags": tags,
                "description": desc,
                "original_pub_utc": f"{orig_dt_utc.hour:02d}:{orig_dt_utc.minute:02d} UTC",
                "original_pub_tehran": orig_tehran_dt.strftime("%H:%M IRST"),
                "optimal_seed_utc": f"{seed_hour_utc:02d}:{orig_dt_utc.minute:02d} UTC"
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
    if best.get("original_pub_utc"):
        print(f"    [Viral Chrono-Pattern] Original Peak: {best['original_pub_utc']} ({best['original_pub_tehran']}) | Optimal Seed Lead: {best['optimal_seed_utc']}")
    return best
