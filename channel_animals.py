import os
import json
from pathlib import Path
from PIL import Image, ImageDraw
from video_utils import generate_eye_catching_thumbnail, create_short_from_audio_and_slides
from voice_generator import generate_speech

ANIMAL_TOPICS = [
    {
        "lang": "en",
        "hook": "Unbelievable Animal Facts You Never Knew!",
        "script": "Did you know that sea otters hold hands while sleeping so they don't drift away? And octopuses have three hearts and blue blood! Animals are way smarter than we think. Subscribe for more crazy nature facts every day!",
        "badge": "ANIMAL FACTS 🐾",
        "title": "Crazy Facts About Animals!",
        "subtitle": "YOU WON'T BELIEVE THIS",
        "tags": ["#Animals", "#Wildlife", "#CuteAnimals", "#Nature", "#Shorts", "#AnimalLovers"]
    },
    {
        "lang": "fa",
        "hook": "۳ حقیقت عجیب و باورنکردنی درباره حیوانات!",
        "script": "می‌دونستی سمورهای دریایی موقع خوابیدن دست همدیگه رو می‌گیرن تا جریان آب اونا رو از هم جدا نکنه؟ و اینکه هشت‌پاها سه تا قلب و خون آبی رنگ دارن! دنیای حیوانات پر از شگفتیه. برای دیدن جذاب‌ترین ویدیوهای حیات وحش سابسکرایب کن!",
        "badge": "دنیای حیوانات 🦁",
        "title": "حقایق باورنکردنی حیوانات!",
        "subtitle": "رازهای شگفت‌انگیز حیات‌وحش",
        "tags": ["#حیوانات", "#حیات_وحش", "#جالب", "#دانستنی_ها", "#shorts", "#حیوانات_خانگی"]
    },
    {
        "lang": "en",
        "hook": "The Cutest Animal Moments That Will Melt Your Heart!",
        "script": "Look at these incredible animals being absolutely adorable! From baby pandas tumbling around to loyal dogs greeting their humans, animals bring so much joy into our lives. Hit like and subscribe to brighten your day!",
        "badge": "SUPER CUTE ❤️",
        "title": "Heartwarming Animal Moments",
        "subtitle": "PURE CUTENESS OVERLOAD",
        "tags": ["#CuteAnimals", "#Puppies", "#Kittens", "#FunnyAnimals", "#Shorts", "#Viral"]
    }
]

def generate_animal_slide(hook: str, output_path: str):
    width, height = 1080, 1920
    # Natural jungle emerald gradient background
    img = Image.new("RGB", (width, height), (15, 30, 20))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(15 * (1 - ratio) + 30 * ratio)
        g = int(35 * (1 - ratio) + 80 * ratio)
        b = int(25 * (1 - ratio) + 40 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Glow card
    draw.rounded_rectangle([60, 400, width - 60, 1500], radius=45, fill=(15, 35, 25), outline=(0, 255, 150), width=5)
    
    # Badge Pill
    draw.rounded_rectangle([140, 460, width - 140, 560], radius=25, fill=(255, 140, 0))
    draw.text((width // 2, 510), "🐾 WILDLIFE & CUTE PETS 🐾", fill=(255, 255, 255), anchor="mm")
    
    # Hook Text
    draw.text((width // 2, 850), hook, fill=(255, 255, 255), anchor="mm")
    draw.text((width // 2, 1150), "🦁 AMAZING NATURE SECRETS 🌿", fill=(255, 220, 0), anchor="mm")
    
    img.save(output_path, "JPEG", quality=95)
    return output_path

def produce_animal_short(output_dir: str, index: int = 0):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    topic = ANIMAL_TOPICS[index % len(ANIMAL_TOPICS)]
    lang = topic["lang"]
    
    # 1. Voiceover
    audio_path = str(out / "audio.mp3")
    generate_speech(topic["script"], lang, audio_path)
    
    # 2. Slide
    slide_path = str(out / "slide.jpg")
    generate_animal_slide(topic["hook"], slide_path)
    
    # 3. Create Short Video
    video_path = str(out / "animal_short.mp4")
    create_short_from_audio_and_slides([slide_path], audio_path, video_path)
    
    # 4. Generate Thumbnail
    thumb_path = str(out / "thumbnail.jpg")
    generate_eye_catching_thumbnail(
        title=topic["title"],
        subtitle=topic["subtitle"],
        badge=topic["badge"],
        output_path=thumb_path,
        bg_color1=(15, 45, 25),
        bg_color2=(255, 140, 0)
    )
    
    # 5. Metadata
    metadata = {
        "title": f"{topic['title']} #Shorts #Animals",
        "description": f"{topic['hook']}\n\n{topic['script']}\n\nSubscribe for daily fascinating animal facts and cute wildlife shorts!",
        "tags": topic["tags"],
        "category_id": "15" # Pets & Animals category in YouTube
    }
    with open(out / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    return {
        "video": video_path,
        "thumbnail": thumb_path,
        "metadata": str(out / "metadata.json")
    }
