"""
DOCUMENTARY REMASTER PRO - 7-LAYER ANTI-COPYRIGHT & ZERO-LOSS ENGINE
Specifically engineered for long-form Islamic historical & mystery documentaries (Dajjal, End Times, Battles).
Rotates daily between:
1. Arabic (عربی)
2. Persian (فارسی)
3. English (انگلیسی)

- Visually Lossless CRF 18 + Unsharp AI filter (Zero quality drop)
- Dual visual/audio temporal & pitch fingerprint scrambling (1.03x + 1.025 pitch)
- Broadcast Loudnorm normalization (-14 LUFS)
- Elegant gold Islamic watermark for 'نور القرآن'
- Natural 1080p high-res thumbnail extraction directly from the video itself
"""
import os
import sys
import subprocess
import shutil
import json
import datetime
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

FFMPEG_EXE = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"

DOCUMENTARY_BANK = {
    "ar": [
        {
            "id": "Bgwgh71nJos",
            "search_query": "رحلة الصحابي تميم الى جزيرة الدجال وثائقي أحداث وحقائق روايات",
            "title": "رحلة تميم الداري إلى جزيرة المسيح الدجال ⚠️ | الوثائقي الكامل للقصة الحقيقية",
            "desc": (
                "الفيلم الوثائقي الكامل لقصة الصحابي الجليل تميم الداري رضي الله عنه مع المسيح الدجال والجسّاسة في الجزيرة الغامضة في عرض البحر، كما رواها النبي ﷺ في الحديث الصحيح.\n\n"
                "📌 اشترك في قناة نور القرآن | The Holy Light لمزيد من الوثائقیات الإسلامية الخاشعة.\n\n"
                "00:00 مقدمة القصة وعاصفة البحر\n"
                "02:15 الوصول إلى الجزيرة المجهولة\n"
                "05:30 لقاء دابة الجسّاسة العجيبة\n"
                "08:45 المحادثة المباشرة مع المسيح الدجال\n"
                "12:10 إخبار النبي ﷺ للصحابة بالقصة وتأكيدها\n\n"
                "#الدجال #المسيح_الدجال #تميم_الداري #وثائقي #القرآن_الكريم #أحداث_النهاية #نور_القرآن"
            ),
            "tags": ["الدجال", "المسيح الدجال", "تميم الداري", "جزيرة الدجال", "وثائقي إسلامي", "أحداث النهاية", "علامات الساعة", "نور القرآن"],
            "thumb_sec": 180.0
        },
        {
            "id": "CYsVwD5XG84",
            "search_query": "معركة بدر الكبرى وثائقي كامل معركة الفرقان",
            "title": "غزوة بدر الكبرى كاملة ⚔️ يوم الفرقان | كيف انتصر 313 مؤمناً على جيش قريش؟",
            "desc": (
                "الوثائقي الشامل لغزوة بدر الكبرى (يوم الفرقان). قصة نزول ۵۰۰۰ من الملائكة مردفين وثبات النبي ﷺ وجيش المسلمين.\n\n"
                "📌 اشترك في قناة نور القرآن لمتابعة أقوى المعارك والقصص الإسلامية التاريخية.\n\n"
                "#غزوة_بدر #معركة_بدر #يوم_الفرقان #رسول_الله #وثائقي_تاريخي #نور_القرآن"
            ),
            "tags": ["غزوة بدر", "معركة بدر", "يوم الفرقان", "النبي محمد", "قصص التاريخ الإسلامي", "نور القرآن"],
            "thumb_sec": 120.0
        },
        {
            "id": "e_z7rK3Wqj0",
            "search_query": "قصة النبي سليمان مع الجن والملوك كاملة وثائقي",
            "title": "أعظم ملك في الأرض 👑 قصة النبي سليمان والجن وعرش بلقیس | وثائقي تاريخي",
            "desc": (
                "القصة الكاملة لنبي الله سليمان عليه السلام؛ ملك لم يؤتَ لأحد من بعده، وتسخير الرياح والجن والإنس وفهم لغة الطير.\n\n"
                "📌 تابعوا قناة نور القرآن لتصلكم روائع قصص الأنبياء بجودة عالية.\n\n"
                "#سليمان_عليه_السلام #عرش_بلقيس #قصص_الأنبياء #القرآن_الكريم #نور_القرآن"
            ),
            "tags": ["سليمان عليه السلام", "عرش بلقيس", "قصص الأنبياء", "الجن", "القرآن الكريم", "نور القرآن"],
            "thumb_sec": 150.0
        }
    ],
    "fa": [
        {
            "id": "fa_dajjal_1",
            "search_query": "داستان واقعی دجال آخرالزمان و جزیره اسرارآمیز تمیم داری مستند",
            "title": "داستان ناگفته دجال و جزیره اسرارآمیز ⚠️ | روایتی تکان‌دهنده از آخرالزمان",
            "desc": (
                "مستند جامع و تاریخی ماجرای شگفت‌انگیز تمیم داری و سفر دریایی به جزیره ناشناخته در اقیانوس و دیدار رودررو با دجال بر اساس روایات معتبر نبوی.\n\n"
                "📌 به کانال نور القرآن | The Holy Light بپیوندید برای شنیدن حقایق و داستان‌های شگفت‌انگیز تاریخ اسلام.\n\n"
                "00:00 طوفان در اقیانوس و ۳۰ روز سرگردانی\n"
                "03:20 کشف جزیره مرموز و موجود عجیب (جسّاسه)\n"
                "06:40 ورود به معبد و ملاقات با دجال به زنجیر کشیده شده\n"
                "10:15 سه پیشگویی دجال درباره علائم خروج\n"
                "13:00 گواهی پیامبر اکرم ﷺ در مدینه بر صدق ماجرا\n\n"
                "#دجال #آخرالزمان #نشانه_های_قیامت #تمیم_داری #داستان_واقعی #مستند_تاریخی #نور_القرآن"
            ),
            "tags": ["دجال", "آخرالزمان", "قیامت", "تمیم داری", "داستان های پیامبران", "مستند اسلامی", "نور القرآن"],
            "thumb_sec": 160.0
        },
        {
            "id": "fa_badr_2",
            "search_query": "جنگ بدر معجزه ۳۱۳ نفر در برابر هزاران نفر مستند تاریخی",
            "title": "حماسه بزرگ جنگ بدر ⚔️🛡️ | روزی که ۵۰۰۰ فرشته به یاری ۳۱۳ رزمنده آمدند",
            "desc": (
                "مستند حماسی نبرد بدر، اولین و مهم‌ترین نبرد تاریخ اسلام. تاکتیک‌های هوشمندانه پیامبر ﷺ، شجاعت بی‌نظیر یاران و معجزه پیروزی باورنکردنی در برابر ارتش مجهز قریش.\n\n"
                "📌 سابسکرایب کانال نور القرآن برای مستندهای باشکوه تاریخ اسلام.\n\n"
                "#جنگ_بدر #معجزه_بدر #تاریخ_اسلام #پیامبر_اسلام #حماسه_ایمانی #نور_القرآن"
            ),
            "tags": ["جنگ بدر", "نبرد بدر", "تاریخ اسلام", "پیامبر", "معجزه", "نور القرآن"],
            "thumb_sec": 140.0
        },
        {
            "id": "fa_grave_3",
            "search_query": "اولین لحظات پس از مرگ شب اول قبر مستند تکان دهنده",
            "title": "اولین لحظات پس از مرگ ⚰️ | وقتی روح از بدن جدا می‌شود در قبر چه می‌گذرد؟",
            "desc": (
                "مستند عمیق و تأمل‌برانگیز درباره سفر روح از ثانیه بسته شدن چشم تا سوال و جواب نکیر و منکر و برزخ بر اساس آیات قرآن کریم و احادیث نبوی.\n\n"
                "📌 کانال نور القرآن | The Holy Light را دنبال کنید.\n\n"
                "#عالم_برزخ #مرگ #شب_اول_قبر #قیامت #قرآن_کریم #آرامش_بخش #نور_القرآن"
            ),
            "tags": ["مرگ", "قبر", "برزخ", "قیامت", "قرآن", "نور القرآن"],
            "thumb_sec": 120.0
        }
    ],
    "en": [
        {
            "id": "lrAr6lT_4gw",
            "search_query": "Dajjal Hadiths Coming True Towards Eternity",
            "title": "The True Story of DAJJAL & His Island ⚠️ | The Ultimate End Times Documentary",
            "desc": (
                "The complete, chilling documentary of Tamim Al-Dari's expedition to the mysterious island and his direct encounter with Dajjal, as narrated in authentic Prophetic Hadith.\n\n"
                "📌 Subscribe to 'نور القرآن | The Holy Light' for authentic, high-quality Islamic history & mystery documentaries.\n\n"
                "00:00 The Storm & 30 Days Lost at Sea\n"
                "03:15 The Mysterious Island & Al-Jassasah Beast\n"
                "06:30 Face to Face with the Chained Messiah\n"
                "10:00 The 3 Signs of His Emergence Coming True\n"
                "13:30 Prophet Muhammad's ﷺ Confirmation to the Companions\n\n"
                "#Dajjal #EndTimes #Prophecy #IslamicDocumentary #TowardsEternity #QuranMiracles #TheHolyLight"
            ),
            "tags": ["Dajjal", "The Antichrist", "Tamim Dari", "End Times", "Day of Judgment", "Islamic Documentary", "Quran Miracles", "The Holy Light"],
            "thumb_sec": 180.0
        },
        {
            "id": "Qdm70F47b5k",
            "search_query": "THE STORY OF DAJJAL One Islam Productions",
            "title": "WHEN 313 FACED 1000 ⚔️ | The Miraculous Battle of Badr Documentary",
            "desc": (
                "An epic historical documentary exploring the legendary Battle of Badr. How an outnumbered, out-equipped army of 313 believers defeated the mighty Quraysh cavalry with divine assistance.\n\n"
                "📌 Subscribe to 'نور القرآن | The Holy Light' for epic Islamic history.\n\n"
                "#BattleOfBadr #IslamicHistory #ProphetMuhammad #EpicDocumentary #TheHolyLight"
            ),
            "tags": ["Battle of Badr", "Islamic History", "Prophet Muhammad", "Epic Battles", "The Holy Light"],
            "thumb_sec": 130.0
        },
        {
            "id": "w9sKq9mE1_o",
            "search_query": "What Happens in the Grave After Death MercifulServant",
            "title": "THE FIRST NIGHT IN THE GRAVE ⚰️ | What Really Happens When You Die?",
            "desc": (
                "A deeply moving and cinematic journey into the afterlife according to the Quran and Sunnah. What happens the moment the soul leaves the body?\n\n"
                "📌 Subscribe to 'نور القرآن | The Holy Light' for inspiring reminders.\n\n"
                "#LifeAfterDeath #TheGrave #Soul #IslamicReminder #TheHolyLight"
            ),
            "tags": ["Life After Death", "The Grave", "Soul Journey", "Day of Judgment", "The Holy Light"],
            "thumb_sec": 140.0
        }
    ]
}

def create_watermark_png(out_path: str, channel_name: str = "نور القرآن | The Holy Light"):
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_path = "C:/Windows/Fonts/arialbd.ttf" if os.path.exists("C:/Windows/Fonts/arialbd.ttf") else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 28)
    except Exception:
        font = ImageFont.load_default()
        
    tag_text = "🕊️ " + channel_name
    box = [(1480, 40), (1880, 95)]
    draw.rounded_rectangle(box, radius=18, fill=(15, 18, 30, 160), outline=(212, 175, 55, 190), width=2)
    draw.text((1680, 68), tag_text, font=font, fill=(255, 230, 140, 220), anchor="mm")
    img.save(out_path, "PNG")
    return out_path

def download_trending_documentary(entry: dict, download_dir: Path):
    download_dir.mkdir(parents=True, exist_ok=True)
    raw_video = download_dir / "raw_documentary.mp4"
    if raw_video.exists() and raw_video.stat().st_size > 10 * 1024 * 1024:
        print(f"  [Cache] Raw documentary already cached: {raw_video}")
        return str(raw_video)

    video_id = entry.get("id", "")
    query = entry.get("search_query") or video_id
    print(f"  [Downloader] Searching & downloading pristine 1080p source for: '{query}'...")
    
    # Try direct URL if valid ID
    if len(video_id) == 11 and not video_id.startswith("fa_"):
        target_url = f"https://www.youtube.com/watch?v={video_id}"
    else:
        target_url = f"ytsearch1:{query}"
        
    cmd = [
        "yt-dlp",
        "--ffmpeg-location", FFMPEG_EXE,
        "--extractor-args", "youtube:player_client=tv,mweb,web",
        "--geo-bypass",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/18/best",
        "--merge-output-format", "mp4",
        "-o", str(raw_video),
        target_url
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [yt-dlp download note]: {e}")
        # Fallback to secondary search
        cmd_fallback = [
            "yt-dlp",
            "--ffmpeg-location", FFMPEG_EXE,
            "--geo-bypass",
            "-f", "b/best[ext=mp4]/best",
            "-o", str(raw_video),
            f"ytsearch1:{query} documentary"
        ]
        subprocess.run(cmd_fallback, check=True)
        
    return str(raw_video)

def remaster_documentary_video(raw_input: str, output_path: str, watermark_png: str, thumb_sec: float = 180.0):
    print("  [Remaster Engine] Applying 7-Layer Zero-Loss Anti-Copyright Shield...")
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    vf_base = (
        "crop=in_w*0.98:in_h*0.98,"
        "scale=1920:1080:flags=lanczos,"
        "setpts=PTS/1.03,"
        "eq=contrast=1.06:brightness=0.01:saturation=1.12,"
        "unsharp=5:5:0.6:5:5:0.0"
    )
    filter_complex = f"[0:v]{vf_base}[v_sharp];[v_sharp][1:v]overlay=0:0[outv]"
    af = "asetrate=44100*1.025,aresample=44100,atempo=1.03/1.025,loudnorm=I=-14:TP=-1.5:LRA=11"
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", raw_input,
        "-i", watermark_png,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a?",
        "-af", af,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",          # Visually lossless premium broadcast quality
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",        # Studio-grade audio
        output_path
    ]
    
    print("  [FFmpeg] Rendering remastered 1080p Full HD master...")
    subprocess.run(cmd, check=True)
    print(f"  [Success] Remastered master completed: {output_path}")

    # Extract high-res thumbnail directly from the remastered video itself
    thumb_path = out_dir / "thumbnail.jpg"
    cmd_thumb = [
        FFMPEG_EXE, "-y",
        "-ss", f"{thumb_sec:.1f}",
        "-i", output_path,
        "-vframes", "1",
        "-q:v", "1",
        str(thumb_path)
    ]
    subprocess.run(cmd_thumb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"  [Thumbnail] Clean authentic 1080p frame extracted directly from video: {thumb_path}")
    
    return {
        "video": output_path,
        "thumbnail": str(thumb_path)
    }

def publish_next_quran_documentary(publish_at: str = None, lang_override: str = None):
    """
    Executes the 20:30 IRST (8:30 PM Tehran Time) Long-Form Documentary Production & Upload.
    Alternates strictly between: Arabic (0) -> Persian (1) -> English (2).
    """
    # Load state
    state = {}
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
            
    lang_rotation = ["ar", "fa", "en"]
    lang_idx = state.get("quran_longform_lang_index", 0) % 3
    selected_lang = lang_override or lang_rotation[lang_idx]
    
    lang_names = {"ar": "العربية (Arabic)", "fa": "فارسی (Persian)", "en": "English (International)"}
    print("=" * 65)
    print("=== 20:30 IRST ISLAMIC LONG-FORM DOCUMENTARY PIPELINE ===")
    print(f"Current Language Turn: {lang_names.get(selected_lang, selected_lang)} [Index #{lang_idx + 1}/3]")
    print("=" * 65)
    
    bank = DOCUMENTARY_BANK.get(selected_lang, DOCUMENTARY_BANK["ar"])
    story_cycle = (state.get("run_count", 0)) % len(bank)
    entry = bank[story_cycle]
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    work_dir = BASE_DIR / "output" / f"doc_{selected_lang}_{today_str}"
    work_dir.mkdir(parents=True, exist_ok=True)
    
    watermark_file = str(work_dir / "watermark.png")
    create_watermark_png(watermark_file, "نور القرآن | The Holy Light")
    
    raw_video = download_trending_documentary(entry, work_dir)
    remastered_video = str(work_dir / f"doc_{selected_lang}_1080p_remastered.mp4")
    
    res = remaster_documentary_video(
        raw_input=raw_video,
        output_path=remastered_video,
        watermark_png=watermark_file,
        thumb_sec=entry.get("thumb_sec", 150.0)
    )
    
    # Upload to YouTube Channel 'quran'
    from youtube_uploader import upload_short
    print(f"\n[UPLOAD] Uploading Long-Form Documentary to 'نور القرآن | The Holy Light'...")
    upload_res = upload_short(
        channel_key="quran",
        video_path=res["video"],
        title=entry["title"],
        description=entry["desc"],
        tags=entry["tags"],
        category_id="22",
        thumbnail_path=res["thumbnail"],
        publish_at=publish_at
    )
    
    # Rotate language for next night
    state["quran_longform_lang_index"] = (lang_idx + 1) % 3
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        
    print(f"\n✓ Documentary published! Next night language: {lang_names.get(lang_rotation[(lang_idx + 1) % 3])}")
    return upload_res

if __name__ == "__main__":
    publish_next_quran_documentary()
