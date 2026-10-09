import os
import json
from pathlib import Path
from PIL import Image, ImageDraw
from video_utils import generate_eye_catching_thumbnail, create_short_from_audio_and_slides
from voice_generator import generate_speech

WEBSITE_URL = "https://ploymint.polyganfactorytoken.workers.dev"
TELEGRAM_URL = "https://t.me/polymint_token_factory"

POLYGON_PROMO = {
    "fa": {
        "hook": "پولی مینت — توکن خودت رو بساز!",
        "script": "پولی مینت! بدون کدنویسی و بدون زحمت، فقط با ۱۲.۵ ماتیک توکن اختصاصی ERC-20 خودت رو روی شبکه پالیگان بساز. اسم، نماد و تعداد عرضه رو انتخاب کن؛ توکن در چند ثانیه توی کیف پولته و مالکیت صد درصد با خودته! آموزش و شروع در لینک توضیحات.",
        "badge": "فقط ۱۲.۵ MATIC 🔥",
        "title": "ساخت ارز دیجیتال بدون کدنویسی",
        "subtitle": "پولی مینت روی پالیگان",
        "tags": ["#پالیگان", "#ارز_دیجیتال", "#پولی_مینت", "#کریپتو", "#میم_کوین", "#Polygon", "#Shorts"]
    },
    "en": {
        "hook": "PolyMint — Launch Your Token with Zero Code!",
        "script": "PolyMint! Launch your custom ERC-20 crypto token on Polygon for just 12.5 MATIC. Zero coding, zero hassle! Choose your name, symbol, and total supply. Your token is minted in seconds directly into your wallet with 100% ownership. Start today via link in description!",
        "badge": "ONLY 12.5 MATIC 🚀",
        "title": "Create Crypto Token in 60s!",
        "subtitle": "POLYMINT ON POLYGON",
        "tags": ["#PolyMint", "#Polygon", "#Crypto", "#TokenCreation", "#Web3", "#MemeCoin", "#Shorts"]
    },
    "ar": {
        "hook": "بولي مينت — أنشئ عملتك المشفرة بدون برمجة!",
        "script": "بولي مينت! أطلق عملتك الرقمية الخاصة على شبكة بوليجون مقابل ١٢.٥ ماتيك فقط وبدون أي خبرة برمجية. حدد اسم العملة ورمزها والعدد؛ وخلال ثوانٍ ستكون في محفظتك بملكية كاملة مئة بالمئة. الرابط في صندوق الوصف!",
        "badge": "١٢.٥ ماتيك فقط 💎",
        "title": "أنشئ عملتك الرقمية بثوانٍ!",
        "subtitle": "POLYMINT على شبكة بوليجون",
        "tags": ["#بولي_مينت", "#بوليجون", "#عملات_رقمية", "#كريبتو", "#بلاك_تشين", "#Shorts"]
    },
    "es": {
        "hook": "¡PolyMint — Crea tu propio token sin programar!",
        "script": "¡PolyMint! Lanza tu propio token ERC-20 en Polygon por solo 12.5 MATIC y sin programar. Elige el nombre, símbolo y suministro. Tu token se crea en segundos directamente en tu billetera con propiedad del cien por ciento. ¡Enlace en la descripción!",
        "badge": "SOLO 12.5 MATIC ⚡",
        "title": "Crea Cripto Token en Polygon",
        "subtitle": "POLYMINT SIN CÓDIGO",
        "tags": ["#PolyMint", "#Polygon", "#Criptomonedas", "#Web3", "#Token", "#Shorts"]
    },
    "de": {
        "hook": "PolyMint — Erstelle deinen eigenen Token ohne Code!",
        "script": "PolyMint! Starte deinen eigenen ERC-20 Krypto-Token auf Polygon für nur 12.5 MATIC. Ohne Programmieren! Wähle Name, Symbol und Gesamtmenge. Dein Token landet in Sekunden in deiner Wallet mit hundert Prozent Eigentum. Link in der Beschreibung!",
        "badge": "NUR 12.5 MATIC 🟣",
        "title": "Eigener Token auf Polygon",
        "subtitle": "POLYMINT NO-CODE",
        "tags": ["#PolyMint", "#Polygon", "#Krypto", "#Web3", "#TokenErstellen", "#Shorts"]
    }
}

def generate_polygon_slide(hook: str, language: str, output_path: str):
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), (19, 13, 42))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(19 * (1 - ratio) + 130 * ratio)
        g = int(13 * (1 - ratio) + 71 * ratio)
        b = int(42 * (1 - ratio) + 229 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Glow card
    draw.rounded_rectangle([60, 380, width - 60, 1520], radius=45, fill=(15, 10, 30), outline=(130, 71, 229), width=5)
    
    # Brand Pill
    draw.rounded_rectangle([120, 440, width - 120, 550], radius=25, fill=(130, 71, 229))
    draw.text((width // 2, 495), "🚀 POLYMINT — TOKEN FACTORY 🟣", fill=(255, 255, 255), anchor="mm")
    
    # Hook Text
    draw.text((width // 2, 750), hook, fill=(255, 255, 255), anchor="mm")
    
    # Feature checklist
    draw.text((width // 2, 950), "✅ 100% No-Code | ERC-20 on Polygon", fill=(0, 255, 180), anchor="mm")
    draw.text((width // 2, 1050), "💎 Only 12.5 MATIC Total Cost", fill=(255, 215, 0), anchor="mm")
    draw.text((width // 2, 1150), "⚡ Minted to Your Wallet in Seconds", fill=(0, 230, 255), anchor="mm")
    draw.text((width // 2, 1250), "🌐 Multi-Language Support (8 Languages)", fill=(255, 255, 255), anchor="mm")

    # CTA Button
    draw.rounded_rectangle([120, 1360, width - 120, 1460], radius=25, fill=(0, 200, 83))
    draw.text((width // 2, 1410), "START NOW: ploymint.polyganfactorytoken.workers.dev", fill=(0, 0, 0), anchor="mm")
    
    img.save(output_path, "JPEG", quality=95)
    return output_path

def produce_polygon_short(output_dir: str, language: str):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    data = POLYGON_PROMO.get(language, POLYGON_PROMO["en"])
    
    # 1. Voiceover
    audio_path = str(out / "audio.mp3")
    generate_speech(data["script"], language, audio_path)
    
    # 2. Slide
    slide_path = str(out / "slide.jpg")
    generate_polygon_slide(data["hook"], language, slide_path)
    
    # 3. Create Short Video
    video_path = str(out / "polygon_short.mp4")
    create_short_from_audio_and_slides([slide_path], audio_path, video_path)
    
    # 4. Generate Thumbnail
    thumb_path = str(out / "thumbnail.jpg")
    generate_eye_catching_thumbnail(
        title=data["title"],
        subtitle=data["subtitle"],
        badge=data["badge"],
        output_path=thumb_path,
        bg_color1=(25, 10, 50),
        bg_color2=(130, 71, 229)
    )
    
    # 5. Metadata with user links
    full_description = (
        f"{data['hook']}\n\n"
        f"🎯 بدون کدنویسی، بدون زحمت، فقط با ۱۲.۵ MATIC توکن اختصاصی ERC-20 روی شبکه پالیگان (Polygon) بساز.\n\n"
        f"✅ اسم، نماد و عرضه رو خودت انتخاب کن\n"
        f"✅ توکن در چند ثانیه در کیف پولت ساخته میشه\n"
        f"✅ مالکیت ۱۰۰٪ با خودته\n"
        f"✅ پشتیبانی ۸ زبان (فارسی، عربی، انگلیسی، اسپانیایی و...)\n"
        f"✅ قابل فروش در صرافی‌ها و دکس‌ها\n\n"
        f"🌐 وبسایت رسمی شروع ساخت توکن:\n{WEBSITE_URL}\n\n"
        f"💬 کانال تلگرام و پشتیبانی:\n{TELEGRAM_URL}\n"
    )
    
    metadata = {
        "language": language,
        "title": f"{data['title']} | ۱۲.۵ MATIC #Shorts #Polygon",
        "description": full_description,
        "tags": data["tags"],
        "category_id": "27"
    }
    with open(out / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    return {
        "video": video_path,
        "thumbnail": thumb_path,
        "metadata": str(out / "metadata.json")
    }
