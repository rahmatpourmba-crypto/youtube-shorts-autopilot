import os
import sys
import subprocess
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from mutagen.mp3 import MP3
from gtts import gTTS

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

BG_DARK = (15, 18, 30)
WHITE = (255, 255, 255)
CYAN_NEON = (0, 240, 255)
GOLD_TEXT = (255, 215, 0)
FONT_CANDIDATES = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/tahomabd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)

def get_font(size):
    if FONT_PATH:
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()

def draw_stickman(draw, center_x, center_y, scale=1.0, mood="neutral", arms="down", props="none"):
    head_r = int(45 * scale)
    body_len = int(120 * scale)
    leg_len = int(90 * scale)
    arm_len = int(80 * scale)
    th = max(4, int(7 * scale))

    head_box = [center_x - head_r, center_y - head_r, center_x + head_r, center_y + head_r]
    head_color = WHITE if mood != "sad" else (255, 130, 130)
    draw.ellipse(head_box, fill=BG_DARK, outline=head_color, width=th)

    eye_r = max(2, int(6 * scale))
    if mood == "sad":
        draw.ellipse([center_x - 18*scale, center_y - 12*scale, center_x - 18*scale + eye_r, center_y - 12*scale + eye_r], fill=WHITE)
        draw.ellipse([center_x + 12*scale, center_y - 12*scale, center_x + 12*scale + eye_r, center_y - 12*scale + eye_r], fill=WHITE)
        draw.arc([center_x - 20*scale, center_y + 10*scale, center_x + 20*scale, center_y + 35*scale], 200, 340, fill=WHITE, width=th-2)
        draw.ellipse([center_x + 35*scale, center_y - 30*scale, center_x + 45*scale, center_y - 15*scale], fill=CYAN_NEON)
    elif mood == "happy":
        draw.ellipse([center_x - 20*scale, center_y - 10*scale, center_x - 5*scale, center_y + 5*scale], fill=CYAN_NEON)
        draw.ellipse([center_x + 5*scale, center_y - 10*scale, center_x + 20*scale, center_y + 5*scale], fill=CYAN_NEON)
        draw.line([(center_x - 5*scale, center_y - 5*scale), (center_x + 5*scale, center_y - 5*scale)], fill=CYAN_NEON, width=th-2)
        draw.arc([center_x - 22*scale, center_y + 5*scale, center_x + 22*scale, center_y + 32*scale], 20, 160, fill=WHITE, width=th-1)
    else:
        draw.ellipse([center_x - 18*scale, center_y - 10*scale, center_x - 18*scale + eye_r, center_y - 10*scale + eye_r], fill=WHITE)
        draw.ellipse([center_x + 12*scale, center_y - 10*scale, center_x + 12*scale + eye_r, center_y - 10*scale + eye_r], fill=WHITE)
        draw.line([(center_x - 15*scale, center_y + 15*scale), (center_x + 15*scale, center_y + 15*scale)], fill=WHITE, width=th-2)

    neck_y = center_y + head_r
    pelvis_y = neck_y + body_len
    draw.line([(center_x, neck_y), (center_x, pelvis_y)], fill=head_color, width=th)

    shoulder_y = neck_y + int(25 * scale)
    if arms == "head":
        draw.line([(center_x, shoulder_y), (center_x - 50*scale, shoulder_y - 30*scale)], fill=head_color, width=th)
        draw.line([(center_x - 50*scale, shoulder_y - 30*scale), (center_x - 30*scale, neck_y - 10*scale)], fill=head_color, width=th)
        draw.line([(center_x, shoulder_y), (center_x + 50*scale, shoulder_y - 30*scale)], fill=head_color, width=th)
        draw.line([(center_x + 50*scale, shoulder_y - 30*scale), (center_x + 30*scale, neck_y - 10*scale)], fill=head_color, width=th)
    elif arms == "celebrate":
        draw.line([(center_x, shoulder_y), (center_x - 60*scale, shoulder_y - 60*scale)], fill=head_color, width=th)
        draw.line([(center_x, shoulder_y), (center_x + 60*scale, shoulder_y - 60*scale)], fill=head_color, width=th)
    else:
        draw.line([(center_x, shoulder_y), (center_x - 45*scale, shoulder_y + arm_len)], fill=head_color, width=th)
        draw.line([(center_x, shoulder_y), (center_x + 45*scale, shoulder_y + arm_len)], fill=head_color, width=th)

    draw.line([(center_x, pelvis_y), (center_x - 40*scale, pelvis_y + leg_len)], fill=head_color, width=th)
    draw.line([(center_x, pelvis_y), (center_x + 40*scale, pelvis_y + leg_len)], fill=head_color, width=th)

    if props == "papers":
        p_box = [center_x - 140*scale, pelvis_y - 20*scale, center_x - 60*scale, pelvis_y + 40*scale]
        draw.rectangle(p_box, fill=(230, 230, 230), outline=WHITE, width=2)
        p_box2 = [center_x - 130*scale, pelvis_y - 40*scale, center_x - 50*scale, pelvis_y + 20*scale]
        draw.rectangle(p_box2, fill=(210, 210, 210), outline=WHITE, width=2)
    elif props == "laptop":
        draw.polygon([
            (center_x + 30*scale, shoulder_y + 50*scale),
            (center_x + 120*scale, shoulder_y + 40*scale),
            (center_x + 130*scale, shoulder_y + 90*scale),
            (center_x + 40*scale, shoulder_y + 100*scale)
        ], fill=(30, 60, 100), outline=CYAN_NEON)
        draw.line([(center_x + 80*scale, shoulder_y - 40*scale), (center_x + 60*scale, shoulder_y - 10*scale)], fill=GOLD_TEXT, width=5)
        draw.line([(center_x + 60*scale, shoulder_y - 10*scale), (center_x + 95*scale, shoulder_y - 10*scale)], fill=GOLD_TEXT, width=5)
        draw.line([(center_x + 95*scale, shoulder_y - 10*scale), (center_x + 75*scale, shoulder_y + 30*scale)], fill=GOLD_TEXT, width=5)

def render_stickman_frame(hook, main_title, subtitle, stickman_cfg, out_path, brand_label):
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    for x in range(0, W, 80):
        draw.line([(x, 0), (x, H)], fill=(22, 28, 45), width=1)
    for y in range(0, H, 80):
        draw.line([(0, y), (W, y)], fill=(22, 28, 45), width=1)

    draw.rounded_rectangle([(60, 90), (W-60, 230)], radius=30, fill=(25, 32, 58), outline=CYAN_NEON, width=4)
    f_hook = get_font(44)
    draw.text((W//2, 160), hook, font=f_hook, fill=CYAN_NEON, anchor="mm")

    draw_stickman(
        draw, 
        center_x=stickman_cfg.get("x", 540), 
        center_y=stickman_cfg.get("y", 700), 
        scale=stickman_cfg.get("scale", 2.0),
        mood=stickman_cfg.get("mood", "neutral"),
        arms=stickman_cfg.get("arms", "down"),
        props=stickman_cfg.get("props", "none")
    )

    draw.rounded_rectangle([(60, 1420), (W-60, 1720)], radius=35, fill=(22, 30, 52), outline=GOLD_TEXT, width=3)
    f_main = get_font(54)
    draw.text((W//2, 1490), main_title, font=f_main, fill=WHITE, anchor="mm")

    f_sub = get_font(40)
    draw.text((W//2, 1610), subtitle, font=f_sub, fill=GOLD_TEXT, anchor="mm")

    f_brand = get_font(32)
    draw.text((W//2, 1820), brand_label, font=f_brand, fill=(130, 160, 210), anchor="mm")

    img.save(out_path, quality=95)

def build_stickman_video(niche: str, run_count: int, out_video_path: str):
    from stickman_stories_bank import get_stickman_episode
    ep = get_stickman_episode(niche, run_count=run_count)
    
    out_dir = Path(out_video_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    voice_path = out_dir / "voice.mp3"

    tts = gTTS(text=ep["voice"], lang='en', tld='us')
    tts.save(str(voice_path))
    audio_dur = MP3(str(voice_path)).info.length
    scene_dur = max(4.0, audio_dur / len(ep["scenes"]))

    brand_map = {
        "ai": "STICKMAN TECH 2026 🤖⚡ | AI Unveiled",
        "cryptolab": "POLYMINT | WEB3 WEALTH 💰📈",
        "animals": "WILD KINGDOM 🐾👑 | Nature Secrets"
    }
    brand_label = brand_map.get(niche, "STICKMAN SERIES ⚡")

    clips = []
    for i, sc in enumerate(ep["scenes"]):
        frame_img = out_dir / f"scene_{i}.jpg"
        render_stickman_frame(
            hook=ep["hook"],
            main_title=sc["title"],
            subtitle=sc["sub"],
            stickman_cfg=sc,
            out_path=frame_img,
            brand_label=brand_label
        )
        c_out = out_dir / f"c_{i}.mp4"
        cmd = [
            FFMPEG_EXE, "-y",
            "-loop", "1", "-i", str(frame_img),
            "-c:v", "libx264", "-t", str(scene_dur),
            "-pix_fmt", "yuv420p", "-r", "30",
            str(c_out)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        clips.append(c_out)

    concat_file = out_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for c in clips:
            f.write(f"file '{c.name}'\n")

    temp_video = out_dir / "temp_silent.mp4"
    cmd_cat = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(temp_video)
    ]
    subprocess.run(cmd_cat, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    cmd_final = [
        FFMPEG_EXE, "-y",
        "-i", str(temp_video),
        "-i", str(voice_path),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_video_path)
    ]
    subprocess.run(cmd_final, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # High-CTR Viral Thumbnail Engine
    thumb_path = out_dir / "thumbnail.jpg"
    build_viral_stickman_thumbnail(ep, niche, thumb_path, brand_label)

    return {
        "video": str(out_video_path),
        "thumbnail": str(thumb_path),
        "title": ep["scenes"][0]["title"] + " 🤯 #Shorts",
        "description": ep["voice"] + "\n\nOfficial Web3 Hub: https://ploymint.polyganfactorytoken.workers.dev #Shorts #Viral",
        "tags": [niche, "stickman", "shorts", "viral", "2026"]
    }

def build_viral_stickman_thumbnail(ep, niche, out_path, brand_label):
    """
    HIGH-CTR VIRAL SHORTS THUMBNAIL ENGINE:
    - 12px Neon Edge Frame (Instant eye catch in YouTube mobile feed)
    - Radial Spotlight Glow behind hero stickman
    - Expressive 2.3x Hero Stickman
    - Red Alert/Exclamation badge
    - 3D Drop-Shadowed Shock Hook Typography
    """
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), (10, 12, 22))
    draw = ImageDraw.Draw(img)

    # 1. Background grid with cyber glow
    grid_color = (24, 30, 48)
    for x in range(0, W, 70):
        draw.line([(x, 0), (x, H)], fill=grid_color, width=1)
    for y in range(0, H, 70):
        draw.line([(0, y), (W, y)], fill=grid_color, width=1)

    # 2. Glowing radial spotlight behind stickman
    for r in range(400, 100, -25):
        alpha_intensity = int(18 * (1 - r / 400))
        glow_color = (15 + alpha_intensity, 25 + alpha_intensity * 2, 45 + alpha_intensity * 3)
        draw.ellipse([540 - r, 720 - r, 540 + r, 720 + r], fill=glow_color)

    # 3. Outer Neon Border Frame
    border_color = CYAN_NEON if niche == "ai" else (GOLD_TEXT if niche == "cryptolab" else (255, 60, 60))
    for b in range(12):
        draw.rectangle([b, b, W - b - 1, H - b - 1], outline=border_color, width=1)

    # 4. Top Shock Alert Pill / Header
    draw.rounded_rectangle([(50, 80), (W - 50, 240)], radius=35, fill=(20, 24, 42), outline=border_color, width=6)
    f_hook = get_font(50)
    draw.text((W // 2, 160), ep.get("hook", "SHOCKING TRUTH! ⚠️"), font=f_hook, fill=border_color, anchor="mm")

    # 5. Stickman Hero
    hero_cfg = ep["scenes"][1] if len(ep["scenes"]) > 1 else ep["scenes"][0]
    draw_stickman(
        draw,
        center_x=540,
        center_y=720,
        scale=2.3,
        mood=hero_cfg.get("mood", "happy"),
        arms=hero_cfg.get("arms", "celebrate"),
        props=hero_cfg.get("props", "laptop" if niche in ["ai", "cryptolab"] else "none")
    )

    # 6. High-Contrast Red Warning Alert Circle near stickman
    draw.ellipse([690, 510, 790, 610], fill=(230, 30, 30), outline=(255, 255, 255), width=5)
    f_excl = get_font(68)
    draw.text((740, 555), "!", font=f_excl, fill=(255, 255, 255), anchor="mm")

    # 7. Giant Punchy Bottom Card with 3D Drop Shadow
    card_top = 1380
    card_bottom = 1750
    # Shadow
    draw.rounded_rectangle([(46, card_top + 10), (W - 46, card_bottom + 10)], radius=40, fill=(0, 0, 0))
    # Main Card
    draw.rounded_rectangle([(50, card_top), (W - 50, card_bottom)], radius=40, fill=(18, 22, 38), outline=GOLD_TEXT, width=5)

    # Big Title with shadow
    title_text = hero_cfg.get("title", "DON'T MISS THIS!")
    f_title = get_font(56)
    draw.text((W // 2 + 3, card_top + 100 + 3), title_text, font=f_title, fill=(0, 0, 0), anchor="mm")
    draw.text((W // 2, card_top + 100), title_text, font=f_title, fill=(255, 255, 255), anchor="mm")

    # Subtitle
    sub_text = hero_cfg.get("sub", "The 1% Secret Revealed 💎")
    f_sub = get_font(42)
    draw.text((W // 2, card_top + 220), sub_text, font=f_sub, fill=GOLD_TEXT, anchor="mm")

    # Bottom Brand Bar
    f_brand = get_font(34)
    draw.text((W // 2, 1840), brand_label, font=f_brand, fill=(140, 170, 220), anchor="mm")

    img.save(out_path, quality=98)
    return str(out_path)
