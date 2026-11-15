import os
import sys
import json
import time
import socket
from pathlib import Path
import subprocess
import requests
import imageio_ffmpeg

socket.setdefaulttimeout(45)

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
FFMPEG_DIR = str(Path(FFMPEG_EXE).parent)
if FFMPEG_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'

BASE_DIR = Path(r"C:\Users\Admin\.copilot\repos\youtube-shorts-autopilot")
BRAIN_DIR = Path(r"C:\Users\Admin\.gemini\antigravity\brain\07cbd881-98d7-4279-9a49-744c1a04aca6")
OUTPUT_DIR = BASE_DIR / "output" / "batch_tomorrow_6_slots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

import youtube_uploader

RECITER_BASE = "https://everyayah.com/data/Yasser_Ad-Dussary_128kbps"

# 6 Golden Slots for Monday, November 16, 2026:
SLOTS = [
    {
        "slot": 1,
        "name": "fajr",
        "already_uploaded": "zde9tPFLTQc",
        "title": "وَالْفَجْرِ ۝ وَلَيَالٍ عَشْرٍ 🌅✨ تلاوة تسكن الروح في الصباح | الشيخ ياسر الدوسري #Shorts",
        "surah_name": "سورة الفجر",
        "ayah_codes": ["089001", "089002", "089003", "089004"],
        "subtitles": [
            (0.0, 5.0, "﴿ وَٱلۡفَجۡرِ ﴾"),
            (5.0, 11.5, "﴿ وَلَيَالٍ عَشۡرٖ ﴾"),
            (11.5, 17.5, "﴿ وَٱلشَّفۡعِ وَٱلۡوَتۡرِ ﴾"),
            (17.5, 25.0, "﴿ وَٱلَّيۡلِ إِذَا يَسۡرِ ﴾"),
        ],
        "images": [BRAIN_DIR / "fajr_scene1_dawn_1794763757091.jpg"],
        "publish_at": "2026-11-16T04:30:00.000Z", # 08:00 Tehran / 07:30 Riyadh
        "top_hook": "🌅 سورة الفجر | الشيخ ياسر الدوسري",
        "top_sub": "تلاوة صباحية مباركة تفيض سكينة وطمأنينة",
        "pinned": "🌅 ابدأ يومك بذكر الله.. اكتب (سبحان الله وبحمده) واشترك في القناة ليصلك القرآن يومياً 🌿",
        "tags": ["سورة_الفجر", "ياسر_الدوسري", "القرآن_الكريم", "تلاوة_صباحية", "أذكار_الصباح", "راحة_نفسية", "Shorts", "Quran"]
    },
    {
        "slot": 2,
        "name": "taha",
        "already_uploaded": "TzboQo5O6l8",
        "title": "طه ۝ مَا أَنزَلْنَا عَلَيْكَ الْقُرْآنَ لِتَشْقَىٰ 🌿✨ | الشيخ ياسر الدوسري #Shorts #Quran",
        "surah_name": "سورة طه",
        "ayah_codes": ["020001", "020002", "020003", "020004"],
        "subtitles": [
            (0.0, 4.0, "﴿ طه ﴾"),
            (4.0, 11.0, "﴿ مَآ أَنزَلۡنَا عَلَيۡكَ ٱلۡقُرۡءَانَ لِتَشۡقَىٰٓ ﴾"),
            (11.0, 17.5, "﴿ إِلَّا تَذۡكِرَةٗ لِّمَن يَخۡشَىٰ ﴾"),
            (17.5, 27.0, "﴿ تَنزِيلٗا مِّمَّنۡ خَلَقَ ٱلۡأَرۡضَ وَٱلسَّمَٰوَٰتِ ٱلۡعُلَى ﴾"),
        ],
        "images": [
            BRAIN_DIR / "taha_scene1_oasis_png_1794763776346.jpg",
            BRAIN_DIR / "taha_scene2_canyon_png_1794763874231.jpg"
        ],
        "publish_at": "2026-11-16T09:30:00.000Z", # 13:00 Tehran / 12:30 Riyadh
        "top_hook": "🌿 سورة طه | الشيخ ياسر الدوسري",
        "top_sub": "ما أنزلنا عليك القرآن لتشقى.. سكينة تريح القلوب",
        "pinned": "🤍 ما أنزل الله القرآن ليشقى قلبك بل لتسعد.. اكتب (لا إله إلا الله) واشترك في القناة 🌿",
        "tags": ["سورة_طه", "ياسر_الدوسري", "القرآن_الكريم", "تلاوة_خاشعة", "راحة_نفسية", "Shorts", "Quran"]
    },
    {
        "slot": 3,
        "name": "rahman",
        "already_uploaded": "cySjOwn-K-M",
        "title": "الرَّحْمَٰنُ ۝ عَلَّمَ الْقُرْآنَ 🌸✨ عروس القرآن | الشيخ ياسر الدوسري #Shorts #Quran",
        "surah_name": "سورة الرحمن",
        "ayah_codes": ["055001", "055002", "055003", "055004", "055005"],
        "subtitles": [
            (0.0, 4.0, "﴿ ٱلرَّحۡمَٰنُ ﴾"),
            (4.0, 9.0, "﴿ عَلَّمَ ٱلۡقُرۡءَانَ ﴾"),
            (9.0, 14.5, "﴿ خَلَقَ ٱلۡإِنسَٰنَ ﴾"),
            (14.5, 20.0, "﴿ عَلَّمَهُ ٱلۡبَيَانَ ﴾"),
            (20.0, 27.0, "﴿ ٱلشَّمۡسُ وَٱلۡقَمَرُ بِحُسۡبَانٖ ﴾"),
        ],
        "images": [BRAIN_DIR / "rahman_scene1_jannah_1794763851824.jpg"],
        "publish_at": "2026-11-16T13:00:00.000Z", # 16:30 Tehran / 16:00 Riyadh
        "top_hook": "🌸 عروس القرآن.. سورة الرحمن",
        "top_sub": "تلاوة تفيض بالجمال والرحمة والسكينة",
        "pinned": "🌸 فبأي آلاء ربكما تكذبان.. اكتب (الحمدلله رب العالمين) اعترافاً بنعم الله العظيمة 🤍",
        "tags": ["سورة_الرحمن", "ياسر_الدوسري", "عروس_القرآن", "تلاوة_خاشعة", "راحة_نفسية", "Shorts", "Quran"]
    },
    {
        "slot": 4,
        "name": "qaf",
        "already_uploaded": "05g4AT8nprI",
        "title": "وَنَحْنُ أَقْرَبُ إِلَيْهِ مِنْ حَبْلِ الْوَرِيدِ 🕊️ تلاوة تهز الوجدان | الشيخ ياسر الدوسري #Shorts",
        "surah_name": "سورة ق",
        "ayah_codes": ["050016"],
        "subtitles": [
            (0.0, 9.5, "﴿ وَلَقَدۡ خَلَقۡنَا ٱلۡإِنسَٰنَ\\Nوَنَعۡلَمُ مَا تُوَسۡوِسُ بِهِۦ نَفۡسُهُۥ ﴾"),
            (9.5, 21.0, "﴿ وَنَحۡنُ أَقۡرَبُ إِلَيۡهِ\\Nمِنۡ حَبۡلِ ٱلۡوَرِيدِ ﴾"),
        ],
        "images": [BRAIN_DIR / "maryam_scene2_supplication_1794756778814.jpg"],
        "publish_at": "2026-11-16T15:30:00.000Z", # 19:00 Tehran / 18:30 Riyadh
        "top_hook": "🕊️ سورة ق | الشيخ ياسر الدوسري",
        "top_sub": "ونحن أقرب إليه من حبل الوريد.. خشوع تام",
        "pinned": "🌿 قال تعالى: ﴿وَنَحْنُ أَقْرَبُ إِلَيْهِ مِنْ حَبْلِ الْوَرِيدِ﴾.. اكتب (يا رب) وشارك الأجر 🤲",
        "tags": ["سورة_ق", "ياسر_الدوسري", "حبل_الوريد", "تلاوة_خاشعة", "مؤثرة", "Shorts", "Quran"]
    },
    {
        "slot": 5,
        "name": "waqiah",
        "already_uploaded": "AIPJjPyTZss",
        "title": "إِذَا وَقَعَتِ الْوَاقِعَةُ 🌌✨ تلاوة جليلة تأخذك لعالم آخر | الشيخ ياسر الدوسري #Shorts",
        "surah_name": "سورة الواقعة",
        "ayah_codes": ["056001", "056002", "056003", "056004", "056005", "056006"],
        "subtitles": [
            (0.0, 5.0, "﴿ إِذَا وَقَعَتِ ٱلۡوَاقِعَةُ ﴾"),
            (5.0, 10.5, "﴿ لَيۡسَ لِوَقۡعَتِهَا كَاذِبَةٌ ﴾"),
            (10.5, 15.0, "﴿ خَافِضَةٞ رَّافِعَةٌ ﴾"),
            (15.0, 20.0, "﴿ إِذَا رُجَّتِ ٱلۡأَرۡضُ رَجّٗا ﴾"),
            (20.0, 28.0, "﴿ وَبُسَّتِ ٱلۡجِبَالُ بَسّٗا ۝ فَكَانَتۡ هَبَآءٗ مُّنۢبَثّٗا ﴾"),
        ],
        "images": [BRAIN_DIR / "mulk_scene1_heavens_png_1794760664115.jpg"],
        "publish_at": "2026-11-16T18:00:00.000Z", # 21:30 Tehran / 21:00 Riyadh
        "top_hook": "🌌 سورة الواقعة | الشيخ ياسر الدوسري",
        "top_sub": "أهوال القيامة.. تلاوة تخشع لها القلوب",
        "pinned": "🌌 اللهم اجعلنا من أصحاب اليمين ولا تجعلنا من أصحاب الشمال.. اكتب (آمين) 🤲🌿",
        "tags": ["سورة_الواقعة", "ياسر_الدوسري", "القرآن_الكريم", "يوم_القيامة", "تلاوة_خاشعة", "Shorts", "Quran"]
    },
    {
        "slot": 6,
        "name": "sajdah",
        "already_uploaded": "zGVdfjBj9cg",
        "title": "تلاوة خاشعة تسكن الروح قبل النوم 🕊️ سورة السجدة | الشيخ ياسر الدوسري #Shorts",
        "surah_name": "سورة السجدة",
        "ayah_codes": ["032015"],
        "subtitles": [
            (0.0, 11.5, "﴿ إِنَّمَا يُؤۡمِنُ بِـَٔايَٰتِنَا ٱلَّذِينَ إِذَا ذُكِّرُواْ بِهَا\\Nخَرُّواْ سُجَّدٗا ﴾"),
            (11.5, 23.0, "﴿ وَسَبَّحُواْ بِحَمۡدِ رَبِّهِمۡ\\Nوَهُمۡ لَا يَسۡتَكۡبِرُونَ ۩ ﴾"),
        ],
        "images": [BRAIN_DIR / "mulk_scene3_quran_night_png_1794760864834.jpg"],
        "publish_at": "2026-11-16T20:00:00.000Z", # 23:30 Tehran / 23:00 Riyadh
        "top_hook": "🕊️ سورة السجدة | تلاوة قبل النوم",
        "top_sub": "خروا سجداً وسبحوا بحمد ربهم.. راحة نفسية",
        "pinned": "🤍 اختم يومك بسجدة وتسبيح.. اكتب (سبحان الله وبحمده، أستغفر الله العظيم) 🌿🕊️",
        "tags": ["سورة_السجدة", "ياسر_الدوسري", "قبل_النوم", "راحة_نفسية", "تلاوة_خاشعة", "Shorts", "Quran"]
    }
]

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def download_slot_audio(session, slot_info):
    name = slot_info["name"]
    files = []
    for code in slot_info["ayah_codes"]:
        dest = OUTPUT_DIR / f"{name}_{code}.mp3"
        if not (dest.exists() and dest.stat().st_size > 1000):
            url = f"{RECITER_BASE}/{code}.mp3"
            downloaded = False
            for attempt in range(1, 6):
                try:
                    r = session.get(url, timeout=30)
                    r.raise_for_status()
                    with open(dest, "wb") as f:
                        f.write(r.content)
                    downloaded = True
                    break
                except Exception as ex:
                    print(f"    [Retry {attempt}/5] downloading {code}.mp3: {ex}")
                    time.sleep(2)
            if not downloaded:
                raise RuntimeError(f"Failed to download {code}.mp3 after 5 attempts")
            time.sleep(0.3)
        files.append(dest)
        
    concat_txt = OUTPUT_DIR / f"{name}_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for fl in files:
            f.write(f"file '{fl.resolve()}'\n")
            
    raw_audio = OUTPUT_DIR / f"{name}_raw.mp3"
    subprocess.run([FFMPEG_EXE, "-y", "-hide_banner", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(raw_audio)], check=True)
    
    # Process atempo 1.02
    mastered_audio = OUTPUT_DIR / f"{name}_atempo.mp3"
    subprocess.run([FFMPEG_EXE, "-y", "-hide_banner", "-i", str(raw_audio), "-filter:a", "atempo=1.02,volume=1.15", "-c:a", "libmp3lame", "-b:a", "192k", str(mastered_audio)], check=True)
    
    # Get duration
    dur_cmd = [FFMPEG_EXE, "-hide_banner", "-i", str(mastered_audio)]
    res = subprocess.run(dur_cmd, capture_output=True, text=True, errors="ignore")
    duration = 25.0
    for l in res.stderr.splitlines():
        if "Duration:" in l:
            dur_str = l.split("Duration:")[1].split(",")[0].strip()
            h, m, s = dur_str.split(":")
            duration = float(h) * 3600 + float(m) * 60 + float(s)
            break
            
    return mastered_audio, duration

def generate_ass(slot_info, total_duration):
    ass_path = OUTPUT_DIR / f"{slot_info['name']}.ass"
    
    events_str = f"Dialogue: 0,0:00:00.00,0:00:07.00,TopHook,,0,0,0,,{{\\b1\\c&H00D4FF&}}{slot_info['top_hook']}{{\\r}}\\N{{\\fs38\\c&HFFFFFF&}}{slot_info['top_sub']}\n"
    
    for start_t, end_t, text in slot_info["subtitles"]:
        clamped_end = min(end_t, total_duration - 3.5)
        if start_t < clamped_end:
            events_str += f"Dialogue: 0,{format_time(start_t)},{format_time(clamped_end)},Ayah,,0,0,0,,{text}\n"
            
    events_str += f"Dialogue: 0,{format_time(total_duration - 3.5)},{format_time(total_duration)},Dua,,0,0,0,,🤲 اكتب شيء تؤجر عليه في التعليقات\\N{{\\fs40\\c&HFFFFFF&}}واشترك في القناة ليصلك القرآن يومياً 🕊️\n"
    
    ass_content = f"""[Script Info]
Title: {slot_info['name']}
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopHook,Vazirmatn,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,8,40,40,240,1
Style: Ayah,Vazirmatn,56,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,380,1
Style: Dua,Vazirmatn,52,&H0050FF50,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{events_str}
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)
    return ass_path

def render_short(slot_info, audio_file, duration, ass_path):
    final_mp4 = OUTPUT_DIR / f"viral_{slot_info['name']}_scheduled.mp4"
    if final_mp4.exists() and final_mp4.stat().st_size > 1_000_000:
        print(f"  ✓ Video already rendered: {final_mp4.name}")
        return final_mp4
        
    imgs = slot_info["images"]
    num_imgs = len(imgs)
    dur_per_img = duration / num_imgs
    
    sub_clips = []
    for idx, img_p in enumerate(imgs, 1):
        c_out = OUTPUT_DIR / f"{slot_info['name']}_part{idx}.mp4"
        frames = int(dur_per_img * 30)
        zoom_expr = f"min(zoom+0.0013,1.14)" if idx % 2 != 0 else f"max(1.14-0.0013*on,1.02)"
        
        cmd = [
            FFMPEG_EXE, "-y", "-hide_banner",
            "-loop", "1", "-i", str(img_p),
            "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='{zoom_expr}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
            "-t", f"{dur_per_img:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
            str(c_out)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        sub_clips.append(c_out)
        
    concat_txt = OUTPUT_DIR / f"{slot_info['name']}_clips_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in sub_clips:
            f.write(f"file '{c.resolve()}'\n")
            
    v_concat = OUTPUT_DIR / f"{slot_info['name']}_raw_v.mp4"
    subprocess.run([FFMPEG_EXE, "-y", "-hide_banner", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(v_concat)], check=True)
    
    # Subtitles, watermark, color grading, anti-fingerprint
    ass_escaped = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    watermark_text = "@NourAlQuran"
    vf_chain = (
        f"subtitles='{ass_escaped}',"
        f"scale=1.02*iw:-1,crop=1080:1920,"
        f"eq=contrast=1.05:brightness=0.01:saturation=1.08,"
        f"drawtext=text='{watermark_text}':x=w-tw-40:y=240:fontsize=36:fontcolor=white@0.70:box=1:boxcolor=black@0.35:boxborderw=6"
    )
    
    final_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(v_concat),
        "-i", str(audio_file),
        "-vf", vf_chain,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1",
        "-shortest",
        str(final_mp4)
    ]
    subprocess.run(final_cmd, capture_output=True, check=True)
    print(f"  ✓ High-Production Video Rendered: {final_mp4.name} ({final_mp4.stat().st_size:,} bytes)")
    return final_mp4

def upload_and_schedule_slot(slot_info, video_path):
    print(f"  [YouTube API] Scheduling on channel 'quran' at {slot_info['publish_at']}...")
    
    desc = (
        f"تلاوة خاشعة عطرة تفيض سكينة وطمأنينة من {slot_info['surah_name']} المباركة 🕊️✨\n\n"
        f"بصوت فضيلة الشيخ الدكتور ياسر الدوسري حفظه الله ورعاه.\n\n"
        f"🤲 اكتب شيئاً تؤجر عليه في التعليقات واذكر الله ليكون شاهداً لك يوم القيامة.\n\n"
        f"📌 اشترك في قناة نور القرآن ليصلك كل يوم مقطع يريح قلبك 🌿\n\n"
        f"#{slot_info['name']} #ياسر_الدوسري #قرآن_كريم #تلاوة_خاشعة #راحة_نفسية #Shorts #Quran"
    )
    
    for attempt in range(1, 4):
        try:
            res = youtube_uploader.upload_short(
                channel_key="quran",
                video_path=str(video_path),
                title=slot_info["title"],
                description=desc,
                tags=slot_info["tags"],
                pinned_comment=slot_info["pinned"],
                publish_at=slot_info["publish_at"]
            )
            if res and res.get("id"):
                return res
        except Exception as e:
            print(f"    Warning (attempt {attempt}): {e}")
            time.sleep(5)
            
    return None

def main():
    print("=" * 70)
    print("=== MASTER BATCH SCHEDULER: 6 GOLDEN SLOTS FOR MONDAY, NOV 16 ===")
    print("=" * 70)
    
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    registry_file = BASE_DIR / "upload_registry.json"
    registry = {}
    if registry_file.exists():
        try:
            with open(registry_file, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception:
            registry = {}
            
    quran_reg = registry.setdefault("quran", [])
    
    scheduled_results = []
    
    for slot_info in SLOTS:
        s_num = slot_info["slot"]
        s_name = slot_info["name"]
        print(f"\n[{s_num}/6] >>> Processing Slot {s_num}: {slot_info['surah_name']} ({slot_info['publish_at']}) <<<")
        
        if slot_info.get("already_uploaded"):
            vid_id = slot_info["already_uploaded"]
            url = f"https://youtube.com/shorts/{vid_id}"
            print(f"  🌟 ALREADY SCHEDULED ON YOUTUBE: {url} (ID: {vid_id})")
            slot_record = {
                "code": f"mon_nov16_slot_{s_num}_{s_name}",
                "video_id": vid_id,
                "title": slot_info["title"],
                "publish_at": slot_info["publish_at"],
                "slot": s_num,
                "ts": int(time.time())
            }
            quran_reg.append(slot_record)
            scheduled_results.append(slot_record)
            continue
        
        # 1. Audio
        audio_file, duration = download_slot_audio(session, slot_info)
        print(f"  ✓ Audio duration: {duration:.2f}s")
        
        # 2. Subtitles
        ass_path = generate_ass(slot_info, duration)
        
        # 3. Render
        video_path = render_short(slot_info, audio_file, duration, ass_path)
        
        # 4. Upload & Schedule
        up_res = upload_and_schedule_slot(slot_info, video_path)
        if up_res and up_res.get("id"):
            vid_id = up_res.get("id")
            url = f"https://youtube.com/shorts/{vid_id}"
            print(f"  🌟 SUCCESS! Scheduled: {url} (ID: {vid_id})")
            
            slot_record = {
                "code": f"mon_nov16_slot_{s_num}_{s_name}",
                "video_id": vid_id,
                "title": slot_info["title"],
                "publish_at": slot_info["publish_at"],
                "slot": s_num,
                "ts": int(time.time())
            }
            quran_reg.append(slot_record)
            scheduled_results.append(slot_record)
            
            # Save registry immediately after each upload
            with open(registry_file, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        else:
            print(f"  ❌ Failed to schedule Slot {s_num}")
            
    print("\n" + "=" * 70)
    print("=== SUMMARY OF SCHEDULED 6 SLOTS FOR TOMORROW ===")
    print(json.dumps(scheduled_results, indent=2, ensure_ascii=False))
    print("=" * 70)

if __name__ == "__main__":
    main()
