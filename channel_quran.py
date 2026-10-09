import os
import json
from pathlib import Path
from PIL import Image, ImageDraw
from video_utils import generate_eye_catching_thumbnail, create_short_from_audio_and_slides
from voice_generator import generate_speech

QURANIC_THEMES = [
    {
        "surah": "سورة الشرح (آية ٥-٦)",
        "arabic_text": "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا ۝ إِنَّ مَعَ الْعُسْرِ يُسْرًا",
        "recitation_script": "بسم الله الرحمن الرحيم. فإن مع العسر يسرا، إن مع العسر يسرا. صدق الله العظيم.",
        "badge": "تلاوة خاشعة",
        "title": "راحة نفسية وطمأنينة لا توصف 🕊️",
        "tags": ["#قرآن", "#قرآن_كريم", "#تلاوة_خاشعة", "#shorts", "#quran", "#راحة_نفسية"]
    },
    {
        "surah": "سورة طه (آية ٤٦)",
        "arabic_text": "قَالَ لَا تَخَافَا ۖ إِنَّنِي مَعَكُمَا أَسْمَعُ وَأَرَىٰ",
        "recitation_script": "بسم الله الرحمن الرحيم. قال لا تخافا، إنني معكما أسمع وأرى. صدق الله العظيم.",
        "badge": "طمأنينة للقلب",
        "title": "لا تخف، الله معك دائماً ✨",
        "tags": ["#قرآن", "#آيات_قرآنية", "#طمأنينة", "#shorts", "#quran_kareem"]
    },
    {
        "surah": "سورة البقرة (آية ٢٨٦)",
        "arabic_text": "لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا",
        "recitation_script": "بسم الله الرحمن الرحيم. لا يكلف الله نفسا إلا وسعها. صدق الله العظيم.",
        "badge": "رسالة لك اليوم",
        "title": "رسالة أمل وفرج قريب 🌿",
        "tags": ["#قرآن", "#دعاء", "#إسلاميات", "#shorts", "#رسائل_قرآنية"]
    }
]

def generate_quran_slide(text: str, surah: str, output_path: str):
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), (10, 25, 20)) # Deep emerald green
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(height):
        ratio = y / height
        r = int(10 * (1 - ratio) + 5 * ratio)
        g = int(35 * (1 - ratio) + 18 * ratio)
        b = int(25 * (1 - ratio) + 12 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Golden ornate border
    draw.rectangle([40, 40, width - 40, height - 40], outline=(218, 165, 32), width=5)
    draw.rectangle([55, 55, width - 55, height - 55], outline=(180, 140, 20), width=2)

    # Card center
    draw.rounded_rectangle([80, 500, width - 80, 1420], radius=40, fill=(15, 45, 35), outline=(255, 215, 0), width=3)
    
    # Text
    draw.text((width // 2, 700), "﷽", fill=(255, 215, 0), anchor="mm")
    draw.text((width // 2, 950), text, fill=(255, 255, 255), anchor="mm")
    draw.text((width // 2, 1200), surah, fill=(218, 165, 32), anchor="mm")
    
    img.save(output_path, "JPEG", quality=95)
    return output_path

def produce_quran_short(output_dir: str, index: int = 0):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    theme = QURANIC_THEMES[index % len(QURANIC_THEMES)]
    
    # 1. Generate Voiceover
    audio_path = str(out / "audio.mp3")
    generate_speech(theme["recitation_script"], "ar", audio_path)
    
    # 2. Generate Slide
    slide_path = str(out / "slide.jpg")
    generate_quran_slide(theme["arabic_text"], theme["surah"], slide_path)
    
    # 3. Create Short Video
    video_path = str(out / "quran_short.mp4")
    create_short_from_audio_and_slides([slide_path], audio_path, video_path)
    
    # 4. Generate Thumbnail
    thumb_path = str(out / "thumbnail.jpg")
    generate_eye_catching_thumbnail(
        title=theme["surah"],
        subtitle=theme["title"],
        badge=theme["badge"],
        output_path=thumb_path,
        bg_color1=(5, 30, 20),
        bg_color2=(20, 60, 45)
    )
    
    # 5. Metadata
    metadata = {
        "title": f"{theme['title']} | {theme['surah']} #Shorts",
        "description": f"تلاوة عطرة خاشعة من {theme['surah']}.\n{theme['arabic_text']}\n\nاشترك في القناة ليصلك كل جديد يومياً.",
        "tags": theme["tags"],
        "category_id": "22"
    }
    with open(out / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    return {
        "video": video_path,
        "thumbnail": thumb_path,
        "metadata": str(out / "metadata.json")
    }
