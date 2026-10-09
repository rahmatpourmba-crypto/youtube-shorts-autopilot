import re
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Professional, high-authority metadata configurations per channel niche
PREMIUM_METADATA_CONFIG = {
    "quran": {
        "title_templates": [
            "تلاوة خاشعة تسكن الروح وتريح القلب 🕊️✨ سورة مباركة #shorts #quran",
            "سورة تفيض بالسكينة والطمأنينة 🌿 بصوت تقشعر له الأبدان #shorts #القرآن",
            "راحة نفسية لا توصف.. استمع بقلبك 🤍 تلاوة ندية عطرة #shorts #قرآن_كريم"
        ],
        "luxury_badge": "تلاوة خاشعة تريح القلوب 🕊️✨",
        "badge_color": (212, 175, 55), # Luxury Gold
        "badge_bg": (15, 30, 22),       # Royal Emerald
        "hashtags": ["#shorts", "#quran", "#قرآن_كريم", "#تلاوة_خاشعة", "#راحة_نفسية", "#اسلاميات", "#quranrecitation"],
        "description_template": (
            "🌿 تلاوة عطرة خاشعة تفيض بالسكينة والنور وتملأ القلب طمأنينة وسلاماً.\n\n"
            "✨ قال الله تعالى: ﴿الَّذينَ آمَنوا وَتَطمَئِنُّ قُلوبُهُم بِذِكرِ اللَّهِ أَلا بِذِكرِ اللَّهِ تَطمَئِنُّ القُلوبُ﴾\n\n"
            "🤍 شارك المقطع مع من تحب ليكون صدقة جارية لك، واشترك في القناة لتصلك التلاوات اليومية الخاشعة.\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            "#Shorts #Quran #قرآن_كريم #تلاوة_خاشعة #راحة_نفسية #آيات_قرآنية #quran_kareem"
        ),
        "tags": [
            "قرآن كريم", "تلاوة خاشعة", "راحة نفسية", "قرآن", "سورة", "ايات قرانية", 
            "Quran", "Quran recitation", "Holy Quran", "Peace", "Islam", "Shorts", "Viral"
        ],
        "engagement_comment": "🌿 صلوا على الحبيب محمد ﷺ واكتب من أي بلد تستمع لهذه التلاوة المباركة؟ 🤍✨"
    },
    "ai": {
        "title_templates": [
            "Mind-Blowing AI Tools That Feel Illegal to Know in 2026! 🤖⚡ #shorts #ai",
            "This Crazy AI Tool Changes Everything! 🤯 Future is Here #shorts #tech",
            "Top Insane AI Tools You Must Try Today! 🚀 Productivity Hacks #shorts #aitools"
        ],
        "luxury_badge": "INSANE AI TOOLS 2026 🤖⚡",
        "badge_color": (0, 240, 255),  # Electric Neon Cyan
        "badge_bg": (20, 15, 45),       # Deep Cyberpunk Violet
        "hashtags": ["#shorts", "#ai", "#aitools", "#artificialintelligence", "#technology", "#productivity", "#futuretech"],
        "description_template": (
            "⚡ Discover the most powerful AI breakthroughs and secret productivity tools of 2026.\n\n"
            "🚀 These cutting-edge tools automate workflows, generate mind-blowing content, and feel like magic.\n\n"
            "🔥 Subscribe to @signsunveiledtv for daily high-value tech secrets and future AI developments!\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            "#Shorts #AI #ArtificialIntelligence #TechTrends #FutureTech #Productivity #AITools"
        ),
        "tags": [
            "AI", "Artificial Intelligence", "AI Tools", "Tech", "Technology", "Future Tech", 
            "ChatGPT", "Runway AI", "Productivity", "Software", "Shorts", "Viral", "Trending"
        ],
        "engagement_comment": "🤖 Which AI tool shocked you the most? Drop your favorite in the comments below! 👇⚡"
    },
    "animals": {
        "title_templates": [
            "Pure Brotherhood in the Wild! 🦁👑 Unbelievable Animal Rescue #shorts #wildlife",
            "The Most Heartwarming Animal Moment You'll See Today! ❤️🐾 #shorts #animals",
            "Unbelievable Wildlife Encounters Caught on Camera! 😱 Nature Secrets #shorts"
        ],
        "luxury_badge": "UNBELIEVABLE WILD MOMENTS! 🦁🐾",
        "badge_color": (255, 215, 0),  # Lion Gold
        "badge_bg": (40, 15, 10),       # Sunset Savanna Dark
        "hashtags": ["#shorts", "#animals", "#wildlife", "#nature", "#cuteanimals", "#viral", "#pets"],
        "description_template": (
            "🐾 Nature at its finest! Witness incredible moments of loyalty, survival, and pure beauty from the animal kingdom.\n\n"
            "🦁 The bond and instinct of these magnificent creatures will leave you in awe.\n\n"
            "❤️ If you love wildlife and adorable animal moments, hit Like and Subscribe to @funyanimal27!\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            "#Shorts #Animals #Wildlife #Nature #FunnyAnimals #CutePets #ViralShorts"
        ),
        "tags": [
            "Animals", "Wildlife", "Nature", "Cute Animals", "Funny Pets", "Lion", 
            "Animal Rescue", "Wild Animals", "Nature Documentary", "Shorts", "Viral", "Trending"
        ],
        "engagement_comment": "❤️🐾 Would you dare to get this close? Rate this animal moment from 1 to 10 below! 👇🦁"
    }
}

def get_best_font(niche: str, size: int):
    """
    Selects the most authoritative, emotionally impactful bold font available on the system.
    """
    candidates = []
    if niche == "quran":
        candidates = [
            "C:/Windows/Fonts/BTitrBd.ttf",
            "C:/Windows/Fonts/IRTitr.ttf",
            "C:/Windows/Fonts/A.Titraj.1.Bold.ttf",
            "C:/Windows/Fonts/IRNazaninBold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
    elif niche == "ai":
        candidates = [
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
    else: # animals / general
        candidates = [
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]

    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                continue
    return ImageFont.load_default()

def format_text_direction(text: str):
    """
    Handles Persian/Arabic bidirectional text and reshaping to prevent disconnected/reversed letters.
    """
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text

def generate_luxury_thumbnail(frame_image_path: str, output_path: str, niche: str = "animals", custom_text: str = None):
    """
    CINEMA-GRADE 300M+ VIRAL THUMBNAIL ENGINE:
    1. Color Enhancement: Micro-contrast punch + vibrant HDR color boost.
    2. Dynamic Vignette & Lighting: Darkens non-essential areas to draw 100% focus to the subject.
    3. Heavy Cinema Typography: Ultra-bold font with thick outer stroke, 3D drop shadow, and golden/neon styling.
    4. RTL Persian/Arabic Support: Prevents disconnected Arabic letters with native reshaping.
    5. Emotional Urgency / Curiosity Badge.
    """
    from PIL import ImageEnhance, ImageFilter

    img = Image.open(frame_image_path).convert("RGB")
    w, h = img.size

    # 1. Micro-Contrast & Saturation Punch
    enhancer_contrast = ImageEnhance.Contrast(img)
    img = enhancer_contrast.enhance(1.15)
    enhancer_color = ImageEnhance.Color(img)
    img = enhancer_color.enhance(1.18)
    enhancer_sharp = ImageEnhance.Sharpness(img)
    img = enhancer_sharp.enhance(1.35)

    config = PREMIUM_METADATA_CONFIG.get(niche, PREMIUM_METADATA_CONFIG["animals"])
    raw_badge_text = custom_text or config["luxury_badge"]
    badge_text = format_text_direction(raw_badge_text)
    badge_color = config["badge_color"]

    # 2. Top and Bottom Cinema Shadow Gradients (ensures text pops over any bright background)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_overlay = ImageDraw.Draw(overlay)
    
    # Top gradient
    for y in range(int(h * 0.28)):
        alpha = int(180 * (1 - y / (h * 0.28)))
        d_overlay.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
        
    # Bottom vignette gradient
    for y in range(int(h * 0.78), h):
        progress = (y - int(h * 0.78)) / (h * 0.22)
        alpha = int(170 * progress)
        d_overlay.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
        
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 3. Dynamic High-Impact Typography & Badge
    font_size = int(w * 0.065)
    font = get_best_font(niche, font_size)

    # Calculate Badge dimensions
    margin_x = int(w * 0.05)
    badge_top = int(h * 0.07)
    badge_height = int(h * 0.08)
    badge_bottom = badge_top + badge_height

    # Outer 3D glow & shadow
    shadow_color = (0, 0, 0, 200)
    draw.rounded_rectangle(
        [margin_x - 4, badge_top - 4 + 6, w - margin_x + 4, badge_bottom + 4 + 6],
        radius=30,
        fill=(0, 0, 0)
    )
    # Luxury Golden / Neon Frame
    draw.rounded_rectangle(
        [margin_x - 3, badge_top - 3, w - margin_x + 3, badge_bottom + 3],
        radius=30,
        fill=badge_color
    )
    # Inner Deep Dark Card
    inner_bg = config.get("badge_bg", (12, 12, 16))
    draw.rounded_rectangle(
        [margin_x, badge_top, w - margin_x, badge_bottom],
        radius=27,
        fill=inner_bg
    )

    # Text Position & Rendering
    text_pos = (w // 2, (badge_top + badge_bottom) // 2)

    # 4. Text Drop-Shadow & Deep Stroke for maximum readability
    for ox, oy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (0, -4), (4, 0), (-4, 0)]:
        draw.text((text_pos[0] + ox, text_pos[1] + oy), badge_text, font=font, fill=(0, 0, 0), anchor="mm")

    # Front Main Vibrant Text
    draw.text(text_pos, badge_text, font=font, fill=badge_color, anchor="mm")

    # 5. Save with High JPEG Quality
    img.save(output_path, "JPEG", quality=98)
    return output_path


def get_optimized_metadata(niche: str, raw_title: str = None):
    """
    Returns high-CTR, luxury title, description, tags, and hashtags.
    """
    config = PREMIUM_METADATA_CONFIG.get(niche, PREMIUM_METADATA_CONFIG["animals"])
    
    # Select or enhance title
    if raw_title and len(raw_title) > 10:
        clean = re.sub(r"[#＃][\w\d_]+", "", raw_title).strip()
        clean = re.sub(r"\s+", " ", clean)
        # Add high-converting emoji and clean #Shorts
        title = f"{clean[:75]} ✨ #Shorts"
    else:
        title = config["title_templates"][0]
        
    return {
        "title": title,
        "description": config["description_template"],
        "tags": config["tags"],
        "hashtags": config["hashtags"],
        "badge_text": config["luxury_badge"],
        "engagement_comment": config.get("engagement_comment")
    }

