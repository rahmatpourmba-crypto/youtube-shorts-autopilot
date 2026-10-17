import os
import sys
import json
import shutil
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

def process_and_upload_trend(channel_key: str, search_query: str, hook_banner: str, category_id: str, run_dir: Path, niche: str = None, publish_at: str = None):
    ch_info = CHANNELS[channel_key]
    out_dir = run_dir / f"channel_{channel_key}"
    out_dir.mkdir(parents=True, exist_ok=True)
    target_niche = niche or channel_key
    
    print(f"\n[{channel_key.upper()}] 1. Searching & Downloading real viral Short for: '{search_query}'...")
    data = search_and_download_viral_short(search_query, str(out_dir), niche=target_niche)
    print(f"  -> Original Title: {data['title']}")
    
    print(f"[{channel_key.upper()}] 2. Applying anti-copyright modifications (Speedup, Pitch Shift, Color Grade)...")
    edited_video = str(out_dir / "edited_viral_short.mp4")
    active_hook = data.get("hook_banner") or hook_banner
    res = apply_anti_copyright_edits(
        input_video=data["raw_video"],
        output_video=edited_video,
        hook_banner=active_hook,
        niche=target_niche
    )
    
    # 165 MEGA-ULTRA PROMPT & ALGORITHMIC METADATA OPTIMIZATION
    from autonomous_growth_auditor import get_mega_metadata_for_upload
    opt = get_mega_metadata_for_upload(niche=target_niche, raw_title=data.get("title"))
    title = opt["title"]
    desc = opt["description"]
    tags = opt["tags"]
    
    # Pre-Flight Quality Gate Audit (بازرسی هوشمند قبل از انتشار)
    from quality_gate import audit_video_before_publish
    audit = audit_video_before_publish(res["video"], res["thumbnail"], title, desc, tags)
    print(f"[{channel_key.upper()}] Pre-Flight Quality Gate Score: {audit['score']}/100")
    if audit["warnings"]:
        for w in audit["warnings"]:
            print(f"  [Audit Note] {w}")

    print(f"[{channel_key.upper()}] 3. Uploading to YouTube Channel: {ch_info['name']} ({ch_info['email']})...")
    upload_res = None
    if ch_info["token_file"].exists():
        upload_res = upload_short(
            channel_key=channel_key,
            video_path=res["video"],
            title=title,
            description=desc,
            tags=tags,
            category_id=category_id,
            thumbnail_path=res["thumbnail"],
            pinned_comment=opt.get("engagement_comment"),
            publish_at=publish_at
        )
    else:
        print(f"  [Notice] Token not found for {channel_key}. Saved locally at {res['video']}.")

    # 4. INSTAGRAM REELS INTEGRATION (انتشار خودکار در اینستاگرام)
    if channel_key == "quran" and upload_res:
        try:
            print(f"[{channel_key.upper()}] 4. Cross-posting to Instagram Reels (@abdol_basit_rahmatpour)...")
            from instagram_publisher import publish_instagram_reel, build_bilingual_quran_caption
            ig_caption = build_bilingual_quran_caption(base_title=title)
            publish_instagram_reel(video_path=res["video"], caption=ig_caption, niche="quran", thumbnail_path=res["thumbnail"])
        except Exception as e:
            print(f"  [Instagram Warning] Cross-posting failed: {e}")


    # AUTO CLEANUP TO FREE DISK SPACE (پاکسازی خودکار فایل‌ها برای تمامی کانال‌ها)
    try:

        raw_vid = Path(data["raw_video"])
        if raw_vid.exists():
            raw_vid.unlink()
            print(f"  [Cleanup] Deleted raw download: {raw_vid.name}")
        
        proc_vid = Path(res["video"])
        if proc_vid.exists() and upload_res:
            proc_vid.unlink()
            print(f"  [Cleanup] Deleted processed video after upload: {proc_vid.name}")

        thumb_img = Path(res["thumbnail"])
        if thumb_img.exists() and upload_res:
            thumb_img.unlink()
            print(f"  [Cleanup] Deleted thumbnail file: {thumb_img.name}")

        # Remove the channel run output directory if completely empty
        if out_dir.exists() and upload_res:
            shutil.rmtree(out_dir, ignore_errors=True)
            print(f"  [Cleanup] Fully cleared directory: {out_dir.name}")
    except Exception as e:
        print(f"  [Cleanup Warning] Error deleting temporary files: {e}")

    return upload_res

def process_and_upload_money_printer_turbo(channel_key: str, category_id: str, run_dir: Path, niche: str = None, language: str = "en", run_count: int = 1):
    """
    Executes 100% automated MoneyPrinter Turbo Short generation with Edge-TTS, Hormozi subtitles, and upload.
    """
    ch_info = CHANNELS[channel_key]
    out_dir = run_dir / f"turbo_{channel_key}"
    out_dir.mkdir(parents=True, exist_ok=True)
    target_niche = niche or channel_key

    from money_printer_turbo_engine import render_money_printer_turbo_short
    turbo_data = render_money_printer_turbo_short(
        niche=target_niche,
        output_dir=out_dir,
        language=language,
        run_count=run_count
    )

    title = turbo_data["title"]
    desc = turbo_data["description"]
    tags = turbo_data["tags"]

    print(f"\n[{channel_key.upper()}] 3. Uploading MoneyPrinter Turbo Short to {ch_info['name']}...")
    upload_res = None
    if ch_info["token_file"].exists():
        upload_res = upload_short(
            channel_key=channel_key,
            video_path=turbo_data["video"],
            title=title,
            description=desc,
            tags=tags,
            category_id=category_id,
            thumbnail_path=turbo_data["thumbnail"],
            pinned_comment=turbo_data.get("pinned_comment")
        )
    else:
        print(f"  [Notice] Token not found for {channel_key}. Output saved at {turbo_data['video']}.")

    if channel_key == "quran" and upload_res:
        try:
            print(f"[{channel_key.upper()}] 4. Cross-posting Turbo Reel to Instagram (@abdol_basit_rahmatpour)...")
            from instagram_publisher import publish_instagram_reel, build_bilingual_quran_caption
            ig_caption = build_bilingual_quran_caption(base_title=title)
            publish_instagram_reel(video_path=turbo_data["video"], caption=ig_caption, niche="quran", thumbnail_path=turbo_data["thumbnail"])
        except Exception as e:
            print(f"  [Instagram Warning] Cross-posting failed: {e}")

    return upload_res

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
    
    # 1. Quran Channel: 3 DISTINCT HIGH-RETENTION SHORTS (Including Towards Eternity style)
    print("\n" + "="*40 + "\n[QURAN CHANNEL] Producing 3 Distinct Daily Viral Shorts...\n" + "="*40)
    quran_batch = [
        # Video 1: Soul-Soothing Recitation (تلاوت خاشعانه و آرامش‌بخش)
        {
            "query": "تلاوة خاشعة تريح القلب قرآن كريم",
            "hook": "تلاوة خاشعة تريح القلوب",
            "niche": "quran",
            "style_label": "Recitation"
        },
        # Video 2: Towards Eternity Style (حقایق تکان‌دهنده، نشانه‌های قیامت و دجال - ویوهای میلیونی)
        {
            "query": "Dajjal signs coming true end times towards eternity shorts",
            "hook": "SIGNS COMING TRUE ⚠️",
            "niche": "islamic_mystery",
            "style_label": "Towards Eternity Style"
        },
        # Video 3: Inspirational Quranic Wisdom & Story (داستان‌های عبرت‌آموز و معجزات قرآن)
        {
            "query": "قصص القران عبر ومواعظ مؤثرة راحة نفسية",
            "hook": "معجزة قرآنية تهز القلوب",
            "niche": "quran",
            "style_label": "Quranic Wisdom"
        }
    ]
    for idx, q_item in enumerate(quran_batch, 1):
        print(f"\n--- [QURAN #{idx}/3 - {q_item['style_label']}] Processing: '{q_item['query']}' ---")
        process_and_upload_trend(
            channel_key="quran",
            search_query=q_item["query"],
            hook_banner=q_item["hook"],
            category_id="22",
            run_dir=run_dir / f"quran_{idx}",
            niche=q_item["niche"]
        )
    
    # 2. AI Channel (1 Video Daily)
    print("\n" + "="*40 + "\n[AI TOOLS CHANNEL] Producing 1 Daily Short...\n" + "="*40)
    ai_queries = ["trending insane AI tools 2026", "useful AI websites shorts", "mind blowing AI tech viral"]
    ai_query = ai_queries[(run_count - 1) % len(ai_queries)]
    process_and_upload_trend(
        channel_key="ai",
        search_query=ai_query,
        hook_banner="INSANE AI TOOL! 🤖⚡",
        category_id="28",
        run_dir=run_dir / "ai_1"
    )

    
    # 3. CryptoLab: Multi-Lingual Geo-Targeted Daily Release
    print("\n" + "="*40 + "\n[CRYPTOLAB CHANNEL] Publishing Multilingual Geo-Targeted Short...\n" + "="*40)
    try:
        from cryptolab_multilingual import publish_next_cryptolab_language
        publish_next_cryptolab_language()
    except Exception as e:
        print(f"  [CryptoLab Warning] Multilingual publish error: {e}")

    
    # 4. Animals Channel (1 Video Daily)
    print("\n" + "="*40 + "\n[ANIMALS CHANNEL] Producing 1 Daily Short...\n" + "="*40)
    animal_queries = ["wildlife animal rescue fight", "funny cute dogs cats pets", "crazy animal moments viral"]
    a_query = animal_queries[(run_count - 1) % len(animal_queries)]
    process_and_upload_trend(
        channel_key="animals",
        search_query=a_query,
        hook_banner="WAIT TILL THE END! 🐾❤️",
        category_id="15",
        run_dir=run_dir / "animals_1"
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
