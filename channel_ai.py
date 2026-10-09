import os
import json
from pathlib import Path
from PIL import Image, ImageDraw
from video_utils import generate_eye_catching_thumbnail, create_short_from_audio_and_slides
from voice_generator import generate_speech

AI_TOPICS = {
    "en": [
        {
            "hook": "Top 3 Mind-Blowing AI Tools You Didn't Know Existed!",
            "script": "Stop doing repetitive work manually! Here are 3 insane AI tools that feel illegal to know. First, Perplexity AI for ultra-fast accurate research. Second, v0 dev for creating full websites in seconds. And third, Claude 3.7 for solving complex coding problems. Follow for daily AI secrets!",
            "badge": "NEW AI TOOLS ⚡",
            "title": "3 Insane AI Tools in 2026!",
            "tags": ["#AI", "#ArtificialIntelligence", "#TechTrends", "#Shorts", "#ChatGPT", "#Productivity"]
        },
        {
            "hook": "This AI Agent Does Your Entire Job While You Sleep!",
            "script": "AI agents are taking over! You can now deploy autonomous bots that scrape leads, analyze markets, and write code automatically. Don't fall behind in the AI revolution. Subscribe to stay ahead of the game!",
            "badge": "AUTOMATION 🤖",
            "title": "Autonomous AI Agents Are Here!",
            "tags": ["#AIAgents", "#FutureOfWork", "#TechNews", "#Shorts", "#AI"]
        }
    ],
    "fa": [
        {
            "hook": "۳ ابزار هوش مصنوعی که زندگیت رو زیر و رو می‌کنه!",
            "script": "دیگه نیازی نیست ساعت‌ها وقتت رو تلف کنی! این سه تا هوش مصنوعی فوق‌العاده رو ذخیره کن: اولی Perplexity برای پیدا کردن جواب‌های دقیق علمی و کاری، دومی Gamma برای ساخت اسلاید و پرزنتیشن تو چند ثانیه، و سومی Claude برای برنامه‌نویسی بدون باگ. برای ترفندهای بیشتر سابسکرایب کن!",
            "badge": "هوش مصنوعی خفن 🔥",
            "title": "۳ ابزار معجزه‌آسای هوش مصنوعی",
            "tags": ["#هوش_مصنوعی", "#تکنولوژی", "#ترفند", "#shorts", "#فناوری", "#یوتیوب_فارسی"]
        },
        {
            "hook": "چطوری با هوش مصنوعی در سال جدید درآمد دلاری داشته باشیم؟",
            "script": "کسب درآمد دلاری با هوش مصنوعی سخت نیست، فقط باید بدونی از چه ابزارهایی استفاده کنی! تولید محتوای خودکار، ادیت ویدیو با یک کلیک و ترجمه همزمان پادکست‌ها الان بازار به شدت داغی دارن. سابسکرایب کن تا تو ویدیوهای بعدی کامل یادت بدم!",
            "badge": "درآمد دلاری 💰",
            "title": "کسب درآمد با ابزارهای AI",
            "tags": ["#درآمد_دلاری", "#هوش_مصنوعی", "#کسب_و_کار", "#shorts", "#آموزش"]
        }
    ]
}

def generate_ai_slide(hook: str, language: str, output_path: str):
    width, height = 1080, 1920
    # Cyberpunk dark background
    img = Image.new("RGB", (width, height), (10, 10, 20))
    draw = ImageDraw.Draw(img)

    # Vertical gradient: deep purple to dark blue
    for y in range(height):
        ratio = y / height
        r = int(15 * (1 - ratio) + 5 * ratio)
        g = int(5 * (1 - ratio) + 20 * ratio)
        b = int(35 * (1 - ratio) + 55 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Tech grid borders
    draw.rounded_rectangle([50, 450, width - 50, 1450], radius=40, fill=(20, 25, 45), outline=(0, 230, 255), width=4)
    
    # Glowing header badge
    draw.rounded_rectangle([150, 520, width - 150, 620], radius=30, fill=(0, 230, 255))
    draw.text((width // 2, 570), "AI REVOLUTION 2026", fill=(0, 0, 0), anchor="mm")
    
    # Text
    draw.text((width // 2, 850), hook, fill=(255, 255, 255), anchor="mm")
    draw.text((width // 2, 1150), "🤖 NEW TECH BREAKTHROUGH 🚀", fill=(0, 255, 170), anchor="mm")
    
    img.save(output_path, "JPEG", quality=95)
    return output_path

def produce_ai_short(output_dir: str, language: str, index: int = 0):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    topics = AI_TOPICS.get(language, AI_TOPICS["en"])
    topic = topics[index % len(topics)]
    
    # 1. Voiceover
    audio_path = str(out / "audio.mp3")
    generate_speech(topic["script"], language, audio_path)
    
    # 2. Slide
    slide_path = str(out / "slide.jpg")
    generate_ai_slide(topic["hook"], language, slide_path)
    
    # 3. Create Short Video
    video_path = str(out / "ai_short.mp4")
    create_short_from_audio_and_slides([slide_path], audio_path, video_path)
    
    # 4. Generate Thumbnail
    thumb_path = str(out / "thumbnail.jpg")
    generate_eye_catching_thumbnail(
        title=topic["title"],
        subtitle="FUTURE IS NOW 🤖",
        badge=topic["badge"],
        output_path=thumb_path,
        bg_color1=(15, 10, 35),
        bg_color2=(0, 100, 150)
    )
    
    # 5. Metadata
    metadata = {
        "language": language,
        "title": f"{topic['title']} #Shorts #AI",
        "description": f"{topic['hook']}\n\n{topic['script']}\n\nSubscribe for daily cutting-edge AI breakthroughs and tools!",
        "tags": topic["tags"],
        "category_id": "28" # Science & Technology
    }
    with open(out / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    return {
        "video": video_path,
        "thumbnail": thumb_path,
        "metadata": str(out / "metadata.json")
    }
