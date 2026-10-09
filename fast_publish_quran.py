import os
import sys
from pathlib import Path
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from trend_downloader import apply_anti_copyright_edits
from youtube_uploader import upload_short

def main():
    raw_video = r"C:\Users\Admin\.gemini\antigravity\scratch\shorts_pipeline\output\real_trend_quran_20261009_190629\raw_download.mp4"
    out_dir = Path(r"C:\Users\Admin\.gemini\antigravity\scratch\shorts_pipeline\output\real_trend_quran_20261009_190629")
    edited_video = str(out_dir / "final_quran_short.mp4")

    print("[1/2] Ultra-fast encoding with multi-threading...", flush=True)
    res = apply_anti_copyright_edits(
        input_video=raw_video,
        output_video=edited_video,
        hook_banner="تلاوة خاشعة تريح القلب 🕊️✨"
    )
    print("  Encoding completed!", flush=True)

    print("[2/2] Uploading to Quran Channel (iman996372@gmail.com)...", flush=True)
    title = "تلاوة ندية تقشعر لها الأبدان ما شاء الله | القارئ جعفر السعدي #Shorts #Quran"
    desc = "تلاوة خاشعة عطرة تريح القلوب والنفس.\n\nاشترك في القناة للمزيد من التلاوات اليومية الخاشعة.\n\n#Shorts #Quran #قرآن #تلاوة_خاشعة"
    tags = ["Quran", "قرآن", "تلاوة_خاشعة", "راحة_نفسية", "Shorts", "Viral"]

    upload_res = upload_short(
        channel_key="quran",
        video_path=res["video"],
        title=title,
        description=desc,
        tags=tags,
        category_id="22",
        thumbnail_path=res["thumbnail"]
    )
    if upload_res:
        print(f"\n[SUCCESS] Quran Short Published: {upload_res['url']}", flush=True)
    else:
        print("\n[ERROR] Upload failed.", flush=True)

if __name__ == "__main__":
    main()
