import os
import sys
import json
import datetime
from pathlib import Path

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from trend_downloader import search_and_download_viral_short, apply_anti_copyright_edits
from youtube_uploader import upload_short, CHANNELS

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"
OUTPUT_BASE = BASE_DIR / "output"

def load_state():
    if not STATE_FILE.exists():
        state = {
            "ai_channel_language": "en",
            "last_run_timestamp": None,
            "run_count": 0
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return state
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def process_and_upload_trend(channel_key: str, search_query: str, hook_banner: str, category_id: str, run_dir: Path):
    ch_info = CHANNELS[channel_key]
    out_dir = run_dir / f"channel_{channel_key}"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[{channel_key.upper()}] 1. Searching & Downloading real viral Short for: '{search_query}'...")
    data = search_and_download_viral_short(search_query, str(out_dir))
    print(f"  -> Original Title: {data['title']}")
    
    print(f"[{channel_key.upper()}] 2. Applying anti-copyright modifications (Speedup, Pitch Shift, Color Grade)...")
    edited_video = str(out_dir / "edited_viral_short.mp4")
    res = apply_anti_copyright_edits(
        input_video=data["raw_video"],
        output_video=edited_video,
        hook_banner=hook_banner,
        niche=channel_key
    )
    
    # Premium Luxury Metadata Optimization
    from metadata_optimizer import get_optimized_metadata
    opt = get_optimized_metadata(niche=channel_key, raw_title=data.get("title"))
    title = opt["title"]
    desc = opt["description"]
    tags = opt["tags"]
    
    print(f"[{channel_key.upper()}] 3. Uploading to YouTube Channel: {ch_info['name']} ({ch_info['email']})...")
    if ch_info["token_file"].exists():
        upload_res = upload_short(
            channel_key=channel_key,
            video_path=res["video"],
            title=title,
            description=desc,
            tags=tags,
            category_id=category_id,
            thumbnail_path=res["thumbnail"]
        )
        return upload_res
    else:
        print(f"  [Notice] Token not found for {channel_key}. Saved locally at {res['video']}.")
        return None

def main():
    state = load_state()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_count = state.get("run_count", 0) + 1
    
    current_ai_lang = state.get("ai_channel_language", "en")
    next_ai_lang = "fa" if current_ai_lang == "en" else "en"
    
    print("=" * 60)
    print(f"=== Starting Daily Real Trend Shorts Pipeline (Run #{run_count} - {today_str}) ===")
    print("1. Quranic Channel: Real viral Quran recitation [iman996372@gmail.com]")
    print(f"2. AI Tools Channel: Real viral AI Short [{current_ai_lang.upper()}] [workonlin63@gmail.com]")
    print("3. CryptoLab Channel: [PAUSED per user request]")
    print("4. Animals Channel: Real viral animals Short [ammm37474@gmail.com]")
    print("=" * 60)
    
    run_dir = OUTPUT_BASE / today_str
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Quran Channel
    quran_queries = ["تلاوة خاشعة quran recitation", "beautiful quran recitation shorts", "surah recitation peace"]
    q_query = quran_queries[(run_count - 1) % len(quran_queries)]
    process_and_upload_trend(
        channel_key="quran",
        search_query=q_query,
        hook_banner="راحة نفسية 🕊️ سورة من القرآن",
        category_id="22",
        run_dir=run_dir
    )
    
    # 2. AI Channel (Alternating English and Persian)
    if current_ai_lang == "en":
        ai_query = "trending insane AI tools 2026"
        ai_hook = "INSANE AI TOOL! 🤖⚡"
    else:
        ai_query = "ابزار هوش مصنوعی خفن کاربردی"
        ai_hook = "هوش مصنوعی فوق العاده 🔥"
        
    process_and_upload_trend(
        channel_key="ai",
        search_query=ai_query,
        hook_banner=ai_hook,
        category_id="28",
        run_dir=run_dir
    )
    
    # 3. CryptoLab: PAUSED per user request
    print("\n[CRYPTO] Skipped / Paused per user instructions.")
    
    # 4. Animals Channel
    animal_queries = ["wildlife animal rescue fight", "funny cute dogs cats pets", "crazy animal moments viral"]
    a_query = animal_queries[(run_count - 1) % len(animal_queries)]
    process_and_upload_trend(
        channel_key="animals",
        search_query=a_query,
        hook_banner="WAIT TILL THE END! 🐾❤️",
        category_id="15",
        run_dir=run_dir
    )
    
    # Update State
    state["ai_channel_language"] = next_ai_lang
    state["last_run_timestamp"] = today_str
    state["run_count"] = run_count
    save_state(state)
    
    print("\n" + "=" * 60)
    print("=== Daily Real Trend Pipeline Execution Completed! ===")
    print(f"Saved into: {run_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
