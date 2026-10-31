import re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from pathlib import Path
import random

# ==============================================================================
# 21 MEGA-PROMPT ULTRA-VIRAL ARCHITECTURE (معماری ۲۱ ترفند طلایی ویوی میلیاردی)
# ==============================================================================
# Techniques applied:
# 1. Persona & World-Class Growth Hacker Anchoring
# 2. Grounding & Anti-Hallucination (Strict safe metadata)
# 3. Curiosity Gap & Neuro-Hook Framing
# 6. Negative Constraints (Zero boring titles, zero weak verbs)
# 8. Cultural & Geographic Nuance Tuning (US/EU for AI, LATAM for Crypto, MENA for Quran)
# 15. Psychological Anchoring & Extreme CTR Drivers
# 17. Output Schema Enforcement (Strict length, emojis, #Shorts)
# ==============================================================================

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
    "islamic_mystery": {
        "title_templates": [
            "Shocking Signs of the End Times That Are Coming True Right Now! 😱 #shorts #islam",
            "What Actually Happens In The Grave? The Terrifying Truth! ⚡ #shorts #towards_eternity",
            "Signs of Dajjal Revealed: Are We in the Final Days? ⚠️ #shorts #islamicreminder"
        ],
        "luxury_badge": "SHOCKING TRUTH REVEALED ⚠️⚡",
        "badge_color": (255, 204, 0),  # Warning Gold
        "badge_bg": (25, 10, 5),        # Deep Mystery Dark Red/Brown
        "hashtags": ["#shorts", "#islam", "#dajjal", "#signsofdayofjudgment", "#endtimes", "#quran", "#towardseternity", "#viral"],
        "description_template": (
            "⚡ Powerful reminders and signs of the final hour. Discover the deep Islamic mysteries and prophecies coming true today.\n\n"
            "📖 Let this reminder soften your heart and bring you closer to Allah before it is too late.\n\n"
            "🤍 Share this reminder with everyone you know. Subscribe to @islamrazekhoshabkhte for daily faith-awakening reminders.\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            "#Shorts #Islam #EndOfTimes #Dajjal #IslamicReminder #Prophecies #QuranMiracles #TowardsEternity"
        ),
        "tags": [
            "Islam", "Signs of Day of Judgment", "Dajjal", "End of Times", "Islamic Reminder", 
            "Towards Eternity", "Quran Miracles", "Life After Death", "Grave", "Shorts", "Viral"
        ],
        "engagement_comment": "⚠️ Did you know about this sign before? Comment your thoughts below and share with your loved ones! 👇"
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
    },
    "cryptolab": {
        "title_templates": [
            "Create Your Own Crypto Token in 30 Seconds! 🚀💎 PolyMint #shorts #web3",
            "How to Launch an ERC-20 Token Without Coding! 🤯 Polygon #shorts #crypto",
            "This Secret Tool Lets Anyone Mint Tokens Easily! 🪙⚡ #shorts #polymint"
        ],
        "luxury_badge": "CREATE TOKEN NO CODE! 🚀💎",
        "badge_color": (255, 215, 0),   # Bright Liquid Gold
        "badge_bg": (28, 12, 48),       # Deep Polygon Obsidian Violet
        "description_template": (
            "🚀 Experience the future of decentralized Web3 tokenization on Polygon!\n\n"
            "💎 Official PolyMint Token Factory Platform: https://ploymint.polyganfactorytoken.workers.dev\n\n"
            "🔥 Subscribe for daily crypto humor, Web3 tools, and Polygon trading insights!\n\n"
            "#Crypto #Polygon #PolyMint #Web3 #Bitcoin #Ethereum #Trading #Shorts #Viral"
        ),
        "tags": ["Crypto", "Polygon", "Token", "PolyMint", "Web3", "Blockchain", "ERC20", "Trading", "Shorts"],
        "engagement_comment": "🚀 Have you ever created your own crypto token? Drop your thoughts below! 👇💎"
    }
}

def get_best_font(niche: str, size: int):
    """
    Selects the most authoritative, emotionally impactful bold font available on the system.
    """
    local_vazir = Path(__file__).resolve().parent / "Vazirmatn-Bold.ttf"
    if niche in ["quran", "islamic_mystery"]:
        candidates = [
            str(local_vazir),
            "C:/Windows/Fonts/BTitrBd.ttf",
            "C:/Windows/Fonts/IRTitr.ttf",
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf"
        ]
    elif niche in ["ai", "cryptolab"]:
        candidates = [
            str(local_vazir),
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf"
        ]
    else: # animals / general
        candidates = [
            str(local_vazir),
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf"
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
    CINEMA-GRADE 300M+ VIRAL THUMBNAIL ENGINE (MEGA-PROMPT DRIVEN):
    1. Color Enhancement: Micro-contrast punch + vibrant HDR color boost.
    2. Dynamic Vignette & Lighting: Darkens non-essential areas to draw 100% focus to the subject.
    3. Heavy Cinema Typography: Ultra-bold font with thick outer stroke, 3D drop shadow, and golden/neon styling.
    4. RTL Persian/Arabic Support: Prevents disconnected Arabic letters with native reshaping.
    5. Emotional Urgency / Curiosity Badge.
    """
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
    
    # Strip emojis that cause empty box glyphs in standard TTF fonts
    clean_text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF.,!?-]', '', raw_badge_text).strip()
    badge_text = format_text_direction(clean_text)
    badge_color = config["badge_color"]

    # 2. Cinematic Gradient Overlay (Darkens upper 35% for contrast)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_overlay = ImageDraw.Draw(overlay)
    
    # Upper gradient
    for y in range(int(h * 0.35)):
        alpha = int(210 * (1 - y / (h * 0.35)))
        d_overlay.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
        
    # Lower vignette gradient
    for y in range(int(h * 0.75), h):
        progress = (y - int(h * 0.75)) / (h * 0.25)
        alpha = int(190 * progress)
        d_overlay.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
        
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 3. Dynamic High-Impact Typography & Badge (Centered at top 12% - 20%)
    font_size = int(w * 0.058)
    font = get_best_font(niche, font_size)

    # Calculate Badge dimensions
    margin_x = int(w * 0.06)
    badge_top = int(h * 0.10)
    badge_height = int(h * 0.085)
    badge_bottom = badge_top + badge_height

    # Outer 3D glow & shadow
    draw.rounded_rectangle(
        [margin_x - 4, badge_top - 4 + 8, w - margin_x + 4, badge_bottom + 4 + 8],
        radius=32,
        fill=(0, 0, 0)
    )
    # Luxury Golden / Neon Frame
    draw.rounded_rectangle(
        [margin_x - 3, badge_top - 3, w - margin_x + 3, badge_bottom + 3],
        radius=32,
        fill=badge_color
    )
    # Inner Deep Dark Card
    inner_bg = config.get("badge_bg", (10, 18, 14))
    draw.rounded_rectangle(
        [margin_x, badge_top, w - margin_x, badge_bottom],
        radius=29,
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


# ==============================================================================
# SAFE TITLE TRUNCATION (fixes titles cut mid-word like "Sura #Shor..")
# ==============================================================================
YT_TITLE_MAX = 100

def smart_truncate(text: str, limit: int = YT_TITLE_MAX) -> str:
    """Trim to <= limit chars at a word boundary; never leaves a broken #hashtag."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit + 1]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    else:
        cut = cut[:limit]
    cut = cut.rstrip(" |-–—:،,")
    # drop a dangling partial hashtag or lone '#'
    parts = cut.split(" ")
    while parts and parts[-1].startswith("#") and parts[-1] not in text.split(" "):
        parts.pop()
    return " ".join(parts).rstrip(" |-–—:،,")[:limit]

def build_title_with_suffix(body: str, suffix: str, limit: int = YT_TITLE_MAX) -> str:
    """Keep the suffix (e.g. '#shorts #قرآن') intact; shorten only the body at word boundaries."""
    suffix = suffix.strip()
    room = limit - len(suffix) - 1
    body = smart_truncate(body, max(room, 10))
    return smart_truncate(f"{body} {suffix}".strip(), limit)

# 114 surah names for detection in captions (Arabic, without "ال" variants handled below)
SURAH_NAMES = [
    "الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس",
    "هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج",
    "المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة",
    "الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان",
    "الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن",
    "الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق",
    "التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان",
    "المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق",
    "الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر",
    "البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون",
    "الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس",
]

def _norm_ar(t: str) -> str:
    t = re.sub(r"[\u064B-\u0652\u0670]", "", t or "")  # strip tashkeel
    return t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("_", " ")

def detect_surah(caption: str):
    """Return surah name if caption says 'سورة X' / '#سورة_X'. Short/ambiguous names need the 'سورة' prefix."""
    norm = _norm_ar(caption)
    for name in sorted(SURAH_NAMES, key=len, reverse=True):
        n = _norm_ar(name)
        if re.search(r"سوره\s*" + re.escape(n) + r"(?![\w])", norm):
            return name
    return None

QURAN_GEO_HASHTAGS = ["#العراق", "#مصر", "#الجزائر"]
QURAN_BASE_HASHTAGS = ["#قرآن", "#تلاوة", "#القرآن_الكريم", "#تلاوة_خاشعة", "#راحة_نفسية", "#quran", "#shorts"]
QURAN_TITLE_HOOKS = [
    "تلاوة تقشعر لها الأبدان 😢",
    "صوت يهز القلوب 🤍",
    "أجمل تلاوة ستسمعها اليوم 🕊️",
    "تلاوة أبكت الملايين 💔",
    "لا تفوتك هذه التلاوة ✨",
    "استمع بقلبك 🎧",
]

_TITLE_SNIPPET_STOPWORDS = {
    "بصوت", "الشيخ", "القارئ", "للشيخ", "تلاوة", "تلاوه", "مقطع", "من", "في", "على", "عن",
    "مع", "هذه", "هذا", "التي", "الذي", "رحمه", "الله", "تعالى", "كاملة", "كامل",
}


def _title_snippet(caption: str, reciter_ar: str = "", max_words: int = 4) -> str:
    """Short human-readable phrase from the reel caption (hashtags/@/links/diacritics stripped).

    Titles used to be `hook | reciter` only, drawn from 6 templates, so distinct reels produced
    byte-identical titles. This snippet makes titles unique per reel (and better for search).
    """
    t = re.sub(r"https?://\S+|@\w+|#\S+", " ", caption or "")
    t = re.sub(r"[\u064B-\u0652\u0670\u0640]", "", t)
    t = re.sub(r"[^\w\u0600-\u06FF\s]+", " ", t)
    rec_words = set(re.sub(r"[^\w\u0600-\u06FF\s]+", " ", reciter_ar or "").split())
    words = [w for w in t.split()
             if len(w) > 1 and w not in rec_words and w not in _TITLE_SNIPPET_STOPWORDS]
    return " ".join(words[:max_words]).strip()


def build_viral_quran_metadata(caption: str, reciter_ar: str, reciter_tag: str, reciter_en: str = "", views: int = 0, rng=None):
    """Viral Arabic title/description/tags for a Quran reel. Title <= 100 chars, never cut mid-word."""
    rng = rng or random
    surah = detect_surah(caption or "")
    hook = rng.choice(QURAN_TITLE_HOOKS)
    snippet = _title_snippet(caption or "", reciter_ar)
    if surah:
        body = f"{hook} | سورة {surah} | {reciter_ar}"
    elif snippet:
        body = f"{hook} | {snippet} | {reciter_ar}"
    else:
        body = f"{hook} | {reciter_ar}"
    title = build_title_with_suffix(body, f"#{reciter_tag} #قرآن #shorts")

    hashtags = [f"#{reciter_tag}"] + QURAN_BASE_HASHTAGS[:5]
    if surah:
        hashtags.insert(1, "#سورة_" + surah.replace(" ", "_"))
    hashtags += QURAN_GEO_HASHTAGS + ["#quran", "#shorts"]
    seen, uniq = set(), []
    for h in hashtags:
        if h not in seen:
            seen.add(h); uniq.append(h)
    surah_line = f"📖 سورة {surah}\n" if surah else ""
    description = (
        f"{title}\n\n"
        f"🎙️ بصوت {reciter_ar}\n{surah_line}\n"
        "🌿 تلاوة خاشعة تريح القلب وتسكن الروح.\n"
        "🤍 اكتب من أي بلد تسمع: 🇮🇶 العراق | 🇪🇬 مصر | 🇩🇿 الجزائر\n"
        "📌 شارك المقطع ليكون صدقة جارية لك، واشترك لتصلك تلاوة جديدة كل مساء.\n\n"
        + " ".join(uniq)
    )
    tags = [reciter_ar, reciter_tag.replace("_", " "), reciter_en, "قرآن", "تلاوة", "تلاوة خاشعة",
            "القرآن الكريم", "راحة نفسية", "تلاوات العراق", "تلاوات مصر", "الجزائر", "Quran", "Quran recitation", "Shorts"]
    if surah:
        tags.insert(2, f"سورة {surah}")
    tags = [t for t in tags if t]
    # YouTube tag budget ~500 chars
    out, total = [], 0
    for t in tags:
        if total + len(t) + 1 > 480:
            break
        out.append(t); total += len(t) + 1
    return {"title": title, "description": description, "tags": out, "surah": surah, "hashtags": uniq}

# ==============================================================================
# 21 MEGA-PROMPT NEURO-HOOK & HIGH-CTR TITLE GENERATOR
# ==============================================================================
def apply_mega_prompt_ctr_engineering(raw_title: str, niche: str) -> str:
    """
    Applies the 21 Mega-Prompt Framework:
    - Curiosity Gap (شکاف کنجکاوی چالدینی)
    - Power Words & Emotion Magnifiers (واژه‌های برانگیزاننده کلیک)
    - Anti-Hallucination & Clean Formatting
    - Exact 60-70 Char Sweet-Spot for Mobile YouTube Shorts UI
    """
    if not raw_title or len(raw_title.strip()) < 5:
        templates = PREMIUM_METADATA_CONFIG.get(niche, PREMIUM_METADATA_CONFIG["animals"])["title_templates"]
        return random.choice(templates)

    clean = re.sub(r"[#＃][\w\d_]+", "", raw_title).strip()
    clean = re.sub(r"\s+", " ", clean)

    # Niche-specific neuro-engineering
    if niche == "islamic_mystery":
        power_hooks = [
            "The Shocking Truth About",
            "Signs Happening Right Now:",
            "What They Never Told You About",
            "The Untold Mystery of"
        ]
        hook = random.choice(power_hooks)
        engineered = build_title_with_suffix(f"{hook} {clean}", "⚠️⚡ #Shorts #Islam")

    elif niche == "quran":
        peace_hooks = [
            "تلاوة تسكن الروح وتريح القلب 🕊️",
            "راحة نفسية لا توصف.. استمع بقلبك 🤍",
            "سورة تفيض بالطمأنينة والنور 🌿"
        ]
        hook = random.choice(peace_hooks)
        engineered = build_title_with_suffix(f"{hook} {clean}", "✨ #Shorts #Quran")

    elif niche == "ai":
        tech_hooks = [
            "Mind-Blowing AI You Didn't Know! 🤯",
            "This Crazy AI Changes Everything! ⚡",
            "Top Insane AI Tools in 2026! 🚀"
        ]
        hook = random.choice(tech_hooks)
        engineered = build_title_with_suffix(f"{hook} {clean}", "#Shorts #AI")

    elif niche == "animals":
        wild_hooks = [
            "Wait Till You See This! 😱🐾",
            "Unbelievable Loyalty in The Wild! 🦁❤️",
            "Nature Moments That Shocked Millions! 🐾👑"
        ]
        hook = random.choice(wild_hooks)
        engineered = build_title_with_suffix(f"{hook} {clean}", "#Shorts #Wildlife")

    else:
        engineered = build_title_with_suffix(clean, "✨ #Shorts #Viral")

    return smart_truncate(engineered, YT_TITLE_MAX)

def get_optimized_metadata(niche: str, raw_title: str = None):
    """
    Returns high-CTR, luxury title, description, tags, and hashtags engineered with 165 Mega-Ultra Prompts.
    """
    try:
        from mega_prompt_youtube_engine import (
            generate_165_mega_title,
            generate_165_mega_description,
            generate_165_algorithmic_tags,
            generate_165_pinned_comment
        )
        title = smart_truncate(generate_165_mega_title(niche, raw_title=raw_title), YT_TITLE_MAX)
        desc = generate_165_mega_description(niche)
        tags = generate_165_algorithmic_tags(niche)
        comment = generate_165_pinned_comment(niche)
        config = PREMIUM_METADATA_CONFIG.get(niche, PREMIUM_METADATA_CONFIG["animals"])
        return {
            "title": title,
            "description": desc,
            "tags": tags,
            "hashtags": config.get("hashtags", ["#shorts", "#viral"]),
            "badge_text": config.get("luxury_badge", "VIRAL SHORTS ⚡"),
            "engagement_comment": comment
        }
    except Exception:
        config = PREMIUM_METADATA_CONFIG.get(niche, PREMIUM_METADATA_CONFIG["animals"])
        title = apply_mega_prompt_ctr_engineering(raw_title, niche)
        return {
            "title": title,
            "description": config["description_template"],
            "tags": config["tags"],
            "hashtags": config["hashtags"],
            "badge_text": config["luxury_badge"],
            "engagement_comment": config.get("engagement_comment")
        }

# ==============================================================================
# VIRAL ENGLISH METADATA (AI / Cosmos / Mega Machines channel)
# ==============================================================================
AI_TITLE_HOOKS = [
    "You Won't Believe This Machine 🤯",
    "This Looks Like the Future 🚀",
    "Engineering Level: Insane ⚙️",
    "Most Satisfying Tech You'll See Today 😮",
    "How Is This Even Possible? 🤖",
    "Mind-Blowing Engineering 🔥",
]
AI_BASE_HASHTAGS = ["#AI", "#tech", "#shorts", "#technology", "#engineering", "#future", "#viral", "#science"]
_AI_TOPIC_HASHTAGS = [
    (("robot", "robotics", "humanoid"), "#robotics"),
    (("ai", "artificial", "chatgpt", "neural"), "#artificialintelligence"),
    (("space", "nasa", "galaxy", "planet", "rocket", "webb", "cosmos", "mars"), "#space"),
    (("excavator", "crane", "truck", "mining", "machine", "machinery", "hydraulic"), "#machines"),
]

def build_viral_ai_metadata(caption: str, views: int = 0, rng=None):
    """Viral English title/description/tags. Title <= 100 chars, trimmed at word boundaries."""
    rng = rng or random
    words = set(re.findall(r"[a-z]+", (caption or "").lower()))
    lines = [re.sub(r"\s+", " ", re.sub(r"[#@]\S+", "", l)).strip() for l in (caption or "").splitlines()]
    lines = [l for l in lines if re.search(r"[A-Za-z]", l) and len(l) >= 12]
    hook = rng.choice(AI_TITLE_HOOKS)
    body = f"{hook} | {lines[0]}" if lines else hook
    topic = [h for kws, h in _AI_TOPIC_HASHTAGS if words & set(kws)]
    title = build_title_with_suffix(body, "#AI #tech #shorts")
    seen, hashtags = set(), []
    for h in AI_BASE_HASHTAGS + topic:
        if h.lower() not in seen:
            seen.add(h.lower()); hashtags.append(h)
    tags = ["AI", "tech", "technology", "engineering", "future tech", "mega machines", "heavy machinery",
            "satisfying", "science", "space", "robotics", "innovation", "shorts", "viral"]
    description = f"{title}\n\n🔥 Follow for daily mind-blowing AI, tech & engineering shorts!\n\n" + " ".join(hashtags)
    return {"title": title, "description": description, "tags": tags, "hashtags": hashtags}
