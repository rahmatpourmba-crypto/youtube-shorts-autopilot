import re

# Comprehensive Halal & Moral Safety Blacklist (لیست سیاه کلمات و مفاهیم غیراخلاقی و غیرشرعی)
FORBIDDEN_KEYWORDS = [
    # Immoral, nudity, revealing attire, romance, adult, dance & inappropriate women
    "bikini", "sexy", "hot girl", "lingerie", "naked", "nude", "kiss", "kissing", 
    "dating", "girlfriend", "boyfriend", "romance", "romantic", "adult", "erotic",
    "dance", "dancing", "dancer", "dancers", "twerk", "belly dance", "model", "actress", "cleavage",
    "tiktok dance", "dance challenge", "viral dance", "female model",
    "رقص", "زن", "دختر", "عاشقانه", "برهنه", "بیکینی", "دوست دختر", "لب گرفتن", "مبتذل", "بی حجاب", "دنس",
    
    # Inappropriate Ads, Scam & Gambling Sponsors
    "sponsor", "betting app", "casino promo", "1xbet", "parimatch", "stake",
    "تبلیغ نامناسب", "شرط‌بندی", "سایت بت",

    # LGBTQ+ and illicit relations
    "lgbt", "pride", "gay", "lesbian", "trans", "queer", "homosexual", "rainbow flag",
    "همجنس", "گی", "لزبين", "ترنس", "زنا", "لواط",
    
    # Alcohol, drugs, gambling
    "alcohol", "beer", "wine", "vodka", "whiskey", "cocktail", "bar", "pub", 
    "drunk", "drugs", "weed", "casino", "gambling", "betting", "poker",
    "شراب", "مشروب", "آبجو", "الکل", "مست", "قمار", "شرط بندی", "کازینو", "مواد مخدر",
    
    # Anti-religious, Shirk, Magic, Astrology
    "shirk", "magic", "sorcery", "witchcraft", "tarot", "horoscope", "zodiac", 
    "astrology", "pagan", "idol", "fortune telling",
    "شرک", "سحر", "جادو", "فال", "طالع بینی", "بت پرستی",
    
    # Music & Songs (ممنوعیت انواع موسیقی و ترانه)
    "music", "song", "remix", "beat", "melody", "audio track", "soundtrack",
    "concert", "singer", "pop", "rap", "hip hop", "rock", "dj", "musical",
    "آهنگ", "موزیک", "ترانه", "خواننده", "کنسرت", "موسیقی", "ریمیکس"
]

def is_content_halal_and_clean(title: str, description: str = "", tags: list = None) -> bool:
    """
    Checks if a video's title, description, or tags contain any forbidden or sinful content.
    Returns True if 100% clean, False if it violates moral or Islamic guidelines.
    """
    text_to_scan = f"{title} {description} {' '.join(tags or [])}".lower()
    
    for word in FORBIDDEN_KEYWORDS:
        # Match word or subphrase
        pattern = r"\b" + re.escape(word.lower()) + r"\b"
        if re.search(pattern, text_to_scan):
            return False
            
    return True

def clean_search_query_for_halal(query: str, niche: str) -> str:
    """
    Appends negative filter tags and halal/no-music enforcement to queries.
    """
    if niche == "quran":
        return f"{query} بدون موسيقى no music -song -dance -remix"
    elif niche == "ai":
        # Pure tech tutorial and software interfaces without women/dancing/songs
        return f"{query} tech tool screen tutorial no music -dance -dancing -girl -women -song -remix"
    elif niche == "animals":
        # Pure natural wildlife documentary without dance or human music
        return f"{query} wildlife documentary pure nature sounds no music -dance -dancing -girl -women -song"
    return f"{query} no music -song -dance"
