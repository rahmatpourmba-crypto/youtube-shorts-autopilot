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
FONT_PATH = None
for _fp in [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/tahomabd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]:
    if os.path.exists(_fp):
        FONT_PATH = _fp
        break
if FONT_PATH is None:
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

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
    f_hook = ImageFont.truetype(FONT_PATH, 44)
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
    f_main = ImageFont.truetype(FONT_PATH, 54)
    draw.text((W//2, 1490), main_title, font=f_main, fill=WHITE, anchor="mm")

    f_sub = ImageFont.truetype(FONT_PATH, 40)
    draw.text((W//2, 1610), subtitle, font=f_sub, fill=GOLD_TEXT, anchor="mm")

    f_brand = ImageFont.truetype(FONT_PATH, 32)
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

    # Generate Thumbnail
    thumb_path = out_dir / "thumbnail.jpg"
    src_thumb = out_dir / "scene_1.jpg" if (out_dir / "scene_1.jpg").exists() else out_dir / "scene_0.jpg"
    shutil.copy2(src_thumb, thumb_path)

    return {
        "video": str(out_video_path),
        "thumbnail": str(thumb_path),
        "title": ep["scenes"][0]["title"] + " 🤯 #Shorts",
        "description": ep["voice"] + "\n\nOfficial Web3 Hub: https://ploymint.polyganfactorytoken.workers.dev #Shorts #Viral",
        "tags": [niche, "stickman", "shorts", "viral", "2026"]
    }
