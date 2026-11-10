import os
import sys
import json
import subprocess
from pathlib import Path
import imageio_ffmpeg
import numpy as np
import scipy.io.wavfile as wavfile
from scipy.signal import butter, lfilter
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
FFMPEG_DIR = str(Path(FFMPEG_EXE).parent)
if FFMPEG_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

BASE_DIR = Path(r"C:\Users\Admin\.copilot\repos\youtube-shorts-autopilot")
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output" / "documentary_longform"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_FILE = Path(r"C:\Users\Admin\AppData\Local\Programs\antigravity\nabil_10min_mastered.mp3")
if not AUDIO_FILE.exists():
    AUDIO_FILE = BASE_DIR / "nabil_10min_mastered.mp3"

MUSIC_FILE = OUTPUT_DIR / "doc_cinematic_soundtrack.wav"
MIXED_AUDIO = OUTPUT_DIR / "doc_mixed_audio.mp3"
FINAL_DOC_VIDEO = OUTPUT_DIR / "dajjal_khorasan_full_documentary_1080p.mp4"
FONT_PATH = BASE_DIR / "Vazirmatn-Bold.ttf"

def get_audio_duration(file_path):
    cmd = [FFMPEG_EXE, "-hide_banner", "-i", str(file_path)]
    res = subprocess.run(cmd, capture_output=True, text=True, errors='ignore')
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            dur_str = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = dur_str.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 397.0

def generate_full_soundtrack(duration):
    if MIXED_AUDIO.exists() and MIXED_AUDIO.stat().st_size > 100_000:
        print("  ✓ Mixed audio already exists, skipping synthesis")
        return
    print(f"[1/4] Generating orchestral dark cinematic soundtrack ({duration:.1f}s)...")
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # Evolving minor key (D minor, A minor, G minor)
    sub = 0.35 * np.sin(2 * np.pi * 36.71 * t)
    drone = 0.25 * np.sin(2 * np.pi * 73.42 * t)
    
    # Evolving chords across the 6.5 minutes
    # Sections of 60 seconds
    section = (t / 60.0).astype(int)
    chord_freqs = [87.31, 98.0, 87.31, 92.5, 87.31, 110.0, 92.5]
    f_chord = np.array([chord_freqs[min(s, len(chord_freqs)-1)] for s in section])
    
    pad = 0.18 * np.sin(2 * np.pi * f_chord * t) + 0.14 * np.sin(2 * np.pi * 110.0 * t)
    
    # Slow cinematic heartbeat pulse (58 BPM)
    pulse = np.zeros_like(t)
    bpm = 58
    spb = 60.0 / bpm
    for beat in range(int(duration / spb)):
        t_start = int(beat * spb * sr)
        pulse_len = int(0.22 * sr)
        if t_start + pulse_len < len(pulse):
            pt = np.linspace(0, 0.22, pulse_len, endpoint=False)
            hit = np.sin(2 * np.pi * 50 * pt) * np.exp(-pt * 16)
            pulse[t_start:t_start + pulse_len] += 0.35 * hit
            
    b, a = butter(4, 550 / (sr / 2), btype='low')
    mix = sub + drone + pad + pulse
    filtered = lfilter(b, a, mix)
    
    fade_in = np.minimum(t / 2.0, 1.0)
    fade_out = np.minimum((duration - t) / 3.0, 1.0)
    final_music = filtered * fade_in * fade_out
    
    max_val = np.max(np.abs(final_music))
    if max_val > 0:
        final_music = (final_music / max_val) * 0.85
        
    wavfile.write(str(MUSIC_FILE), sr, (final_music * 32767).astype(np.int16))
    
    # Mix human voice + music (Voice 1.35, Music 0.26 with subtle ducking)
    mix_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(AUDIO_FILE),
        "-i", str(MUSIC_FILE),
        "-filter_complex", "[0:a]volume=1.35[v];[1:a]volume=0.25[m];[v][m]amix=inputs=2:duration=first[out]",
        "-map", "[out]",
        str(MIXED_AUDIO)
    ]
    subprocess.run(mix_cmd, capture_output=True, check=True)
    print("  ✓ Mixed human voice & cinematic music successfully!")

def create_16x9_scene_card(idx, bg_img_path, title_ar, sub_ar, out_path):
    w, h = 1920, 1080
    canvas = Image.new("RGB", (w, h), (10, 8, 18))
    
    if os.path.exists(bg_img_path):
        bg = Image.open(bg_img_path).convert("RGB")
        bg_w, bg_h = bg.size
        # Crop to 16:9
        target_r = 16 / 9
        curr_r = bg_w / bg_h
        if curr_r > target_r:
            nw = int(bg_h * target_r)
            bg = bg.crop(((bg_w - nw) // 2, 0, (bg_w + nw) // 2, bg_h))
        else:
            nh = int(bg_w / target_r)
            bg = bg.crop((0, (bg_h - nh) // 2, bg_w, (bg_h + nh) // 2))
        bg = bg.resize((w, h), Image.Resampling.LANCZOS)
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.75)
        canvas.paste(bg, (0, 0))
        
    # Dark cinematic vignette
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for y in range(h):
        alpha = int(190 * (y / h)**1.8)
        v_draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
    for x in range(w // 2, w):
        alpha = int(140 * ((x - w // 2) / (w // 2))**1.4)
        v_draw.line([(x, 0), (x, h)], fill=(0, 0, 0, alpha))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), vignette).convert("RGB")
    
    draw = ImageDraw.Draw(canvas)
    font_main = ImageFont.truetype(str(FONT_PATH), 64)
    font_sub = ImageFont.truetype(str(FONT_PATH), 42)
    font_badge = ImageFont.truetype(str(FONT_PATH), 30)
    
    # Top Right Badge
    badge_text = "وثائقي أحداث النهاية | الشيخ نبيل العوضي"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = w - bw - 80, 60
    draw.rounded_rectangle([bx - 18, by - 8, bx + bw + 18, by + bh + 12], radius=8, fill=(180, 25, 25, 230))
    draw.text((bx, by), badge_text, font=font_badge, fill=(255, 255, 255))
    
    # Lower Third Title
    tx = w - 100
    ty = h - 220
    # Shadow
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 3)]:
        draw.text((tx + ox, ty + oy), title_ar, font=font_main, fill=(0, 0, 0), anchor="ra")
    draw.text((tx, ty), title_ar, font=font_main, fill=(255, 215, 0), anchor="ra")
    
    # Sub
    for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((tx + ox, ty + 85 + oy), sub_ar, font=font_sub, fill=(0, 0, 0), anchor="ra")
    draw.text((tx, ty + 85), sub_ar, font=font_sub, fill=(240, 240, 240), anchor="ra")
    
    canvas.save(out_path, quality=95)
    return out_path

def build_visual_sequence(duration):
    print("[2/4] Building 16:9 cinematic visual scenes and procedural motion...")
    
    # We will construct 18 scenes covering the 6.5 minutes (~22s per scene)
    scenes_data = [
        ("خروج الدجال من بلاد خُراسان", "«يخرج الدجال من أرض بالمشرق يقال لها خراسان»", "dajjal_p3_scene3.png"),
        ("أول خروجه وأتباعه السبعون ألفاً", "يتبعه أقوام وجوههم كالمجانّ المطرقة من أصبهان", "dajjal_scene3_apocalypse.png"),
        ("سرعة طوافه العجيبة في الأرض", "كالغيث استدبرته الريح.. يمر على كل بقعة", "dajjal_p2_scene1.png"),
        ("فتنة السماء والأرض والأموال", "يأمر السماء فتمطر، والأرض فتنبت، وتتبعه كنوزها", "dajjal_p2_scene3.png"),
        ("الأعرابي وإحياء والديه بالوهم", "شياطين تتمثل له على صورة أبيه وأمه", "dajjal_scene2_gates.png"),
        ("الشاب المؤمن الذي لا يهاب الدجال", "يقول له: أشهد أنك الدجال الذي حدثنا عنه رسول الله ﷺ", "dajjal_p3_scene2.png"),
        ("شطر الشاب نصفين ثم إحياؤه", "يمشي بين القطعتين ثم يدعوه فيقوم يتهلل وجهه!", "dajjal_scene1_island.png"),
        ("عجز الدجال عن قتله مرة أخرى", "يجعل الله رقبته نحاساً فلا يستطيع إليه سبيلاً", "dajjal_p3_scene1.png"),
        ("المسير نحو مكة المكرمة", "يُمنع من دخولها، والملائكة تحرس أبوابها بالسيوف", "dajjal_p4_scene3.png"),
        ("محاصرة المدينة المنورة وطيبتها", "يقف عند الضريب الأحمر.. وترجف المدينة ثلاث رجفات", "dajjal_p2_scene2.png"),
        ("خروج المنافقين والكفار إليه", "يوم الخلاص.. لا يبقى فيها منافق إلا خرج إليه", "dajjal_p3_scene3.png"),
        ("التوجه إلى بيت المقدس والشام", "المؤمنون محاصرون في جبل الدخان ببيت المقدس", "dajjal_p4_scene2.png"),
        ("صلاة الفجر وإمامة المهدي", "تقام الصلاة فيتقدم إمام المسلمين ليصلي بهم", "dajjal_p4_scene1.png"),
        ("نزول عيسى بن مريم عليه السلام", "ينزل عند المنارة البيضاء شرقي دمشق بين ملكين", "dajjal_p4_scene1.png"),
        ("طلب الدجال واللحاق به", "يخرج عيسى عليه السلام فيطلبه، فإذا رآه ذاب كالملح", "dajjal_p4_scene2.png"),
        ("مقتل الدجال عند باب لُد بفلسطين", "يدركه بباب لُد فيقتله بحربته ويريهم دمه فيها!", "dajjal_p4_scene2.png"),
        ("هزيمة أتباعه واندحار الفتنة", "ينادي الحجر والشجر: يا مسلم هذا ورائي.. إلا الغرقد", "dajjal_p4_scene3.png"),
        ("عهد السلام والبركة بعد هلاكه", "يملأ الأرض عدلاً وأمناً، وترفع الشحناء والعداوة", "dajjal_p4_scene3.png")
    ]
    
    scene_dur = duration / len(scenes_data)
    print(f"  Constructing {len(scenes_data)} scenes ({scene_dur:.1f}s each)...")
    
    rendered_clips = []
    concat_file = OUTPUT_DIR / "doc_concat.txt"
    
    with open(concat_file, "w", encoding="utf-8") as f_cat:
        for idx, (title, sub, img_name) in enumerate(scenes_data):
            img_src = ASSETS_DIR / img_name
            card_img = OUTPUT_DIR / f"card_{idx:02d}.jpg"
            create_16x9_scene_card(idx, str(img_src), title, sub, str(card_img))
            
            clip_path = OUTPUT_DIR / f"clip_{idx:02d}.mp4"
            frames = int(scene_dur * 25)
            
            # Alternate Zoom In / Zoom Out for each scene
            if idx % 2 == 0:
                zoom_filter = f"zoompan=z='min(zoom+0.0008,1.12)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=25"
            else:
                zoom_filter = f"zoompan=z='max(1.12-0.0008*on,1.01)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=25"
                
            cmd = [
                FFMPEG_EXE, "-y", "-hide_banner",
                "-loop", "1", "-i", str(card_img),
                "-vf", zoom_filter,
                "-t", f"{scene_dur:.2f}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                str(clip_path)
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            f_cat.write(f"file '{clip_path.name}'\n")
            rendered_clips.append(clip_path)
            if idx % 4 == 0:
                print(f"    Rendered scene {idx+1}/{len(scenes_data)}...")
                
    # Concatenate all visual clips
    v_raw = OUTPUT_DIR / "doc_visuals_raw.mp4"
    cmd_concat = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c", "copy",
        str(v_raw)
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)
    print("  ✓ Visual timeline assembled successfully!")
    return v_raw

def render_final_documentary(v_raw, duration):
    print("[3/4] Muxing 1080p documentary with mastered narration and soundtrack...")
    final_cmd = [
        FFMPEG_EXE, "-y", "-hide_banner",
        "-i", str(v_raw),
        "-i", str(MIXED_AUDIO),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{duration:.2f}",
        "-movflags", "+faststart",
        str(FINAL_DOC_VIDEO)
    ]
    subprocess.run(final_cmd, capture_output=True, check=True)
    print(f"  ✓ Full Documentary Rendered: {FINAL_DOC_VIDEO}")
    print(f"  ✓ Size: {FINAL_DOC_VIDEO.stat().st_size:,} bytes | Duration: {duration:.2f}s")
    return FINAL_DOC_VIDEO

def upload_longform_documentary(video_path, thumbnail_path):
    print("[4/4] Uploading Long-form Documentary to YouTube...")
    os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'
    
    import youtube_uploader
    
    title = "خروج المسيح الدجال من خراسان.. القصة الكاملة كما أخبر بها النبي ﷺ | الشيخ نبيل العوضي"
    description = (
        "الوثائقي الكامل: خروج المسيح الدجال من بلاد خُراسان، فتنته الكبرى، مسيره في الأرض، وحصاره للمدينة المنورة ومقتله عند باب لُد على يد نبي الله عيسى بن مريم عليه السلام.\n\n"
        "بصوت فضيلة الشيخ نبيل العوضي حفظه الله ورعاه.\n\n"
        "📌 قال رسول الله ﷺ: «يخرج الدجال من أرض بالمشرق يقال لها خراسان، يتبعه أقوام كأن وجوههم المجان المطرقة» (جامع الترمذي).\n\n"
        "اللهم إنا نعوذ بك من فتنة المحيا والممات، ومن عذاب جهنم، ومن شر فتنة المسيح الدجال 🤲\n\n"
        "لا تنسَ دعم الفيديو بالإعجاب والاشتراك في القناة ومشاركة المقطع ليعم الأجر والنفع 🌿\n\n"
        "#المسيح_الدجال #الشيخ_نبيل_العوضي #علامات_الساعة #خراسان #وثائقي #نهاية_العالم #الإسلام"
    )
    tags = [
        "المسيح_الدجال", "خروج_الدجال", "خراسان", "الشيخ_نبيل_العوضي",
        "نبيل_العوضي", "علامات_الساعة_الكبرى", "نزول_عيسى", "باب_لد",
        "وثائقي_إسلامي", "أشراط_الساعة", "نهاية_الزمان", "قصة_الدجال"
    ]
    pinned_comment = "🤲 اللهم إنا نعوذ بك من عذاب جهنم، ومن عذاب القبر، ومن فتنة المحيا والممات، ومن شر فتنة المسيح الدجال. اكتب (آمين) لتشارك الأجر واشترك بالقناة ليصلك كل جديد 🌿"
    
    # Upload long-form video
    # Note: If youtube_uploader supports set_thumbnail, pass thumbnail_path
    res = youtube_uploader.upload_short(
        channel_key="quran",
        video_path=str(video_path),
        title=title,
        description=description,
        tags=tags,
        pinned_comment=pinned_comment
    )
    return res

def main():
    dur = get_audio_duration(AUDIO_FILE)
    print(f"Audio Duration: {dur:.2f}s ({dur/60:.2f} minutes)")
    
    generate_full_soundtrack(dur)
    v_raw = build_visual_sequence(dur)
    final_video = render_final_documentary(v_raw, dur)
    
    thumb_path = BASE_DIR / "output" / "dajjal_10min_master_thumbnail.jpg"
    up_res = upload_longform_documentary(final_video, thumb_path)
    
    print("\n" + "=" * 65)
    print("=== LIVE LONG-FORM DOCUMENTARY UPLOAD RESULT ===")
    print(json.dumps(up_res, indent=2, ensure_ascii=False))
    print("=" * 65)

if __name__ == "__main__":
    main()
