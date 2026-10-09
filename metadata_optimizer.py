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

def generate_luxury_thumbnail(frame_image_path: str, output_path: str, niche: str = "animals", custom_text: str = None):
    """
    Renders a luxury, high-CTR cover frame with:
    - High-contrast color enhancement
    - Vignette frame
    - Elegant rounded luxury badge with golden/neon border
    """
    img = Image.open(frame_image_path).convert("RGB")
    w, h = img.size
    
    config = PREMIUM_METADATA_CONFIG.get(niche, PREMIUM_METADATA_CONFIG["animals"])
    badge_text = custom_text or config["luxury_badge"]
    badge_color = config["badge_color"]
    badge_bg = config["badge_bg"]
    
    draw = ImageDraw.Draw(img)
    
    # 1. Subtle cinematic top and bottom shading
    top_overlay = Image.new("RGBA", (w, int(h * 0.22)), (0, 0, 0, 140))
    img.paste(top_overlay, (0, 0), mask=top_overlay)
    
    # 2. Luxury Badge Card at the top (golden/neon border)
    margin_x = int(w * 0.06)
    badge_top = int(h * 0.08)
    badge_bottom = badge_top + int(h * 0.075)
    
    # Outer luxury glow border
    draw.rounded_rectangle(
        [margin_x - 3, badge_top - 3, w - margin_x + 3, badge_bottom + 3],
        radius=28,
        fill=badge_color
    )
    # Inner dark royal card
    draw.rounded_rectangle(
        [margin_x, badge_top, w - margin_x, badge_bottom],
        radius=25,
        fill=badge_bg
    )
    
    # Bold text inside badge
    draw.text(
        (w // 2, (badge_top + badge_bottom) // 2),
        badge_text,
        fill=badge_color,
        anchor="mm"
    )
    
    # 3. Save as high-quality JPEG
    img.save(output_path, "JPEG", quality=96)
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

