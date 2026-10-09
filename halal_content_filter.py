import re

# Comprehensive Halal & Moral Safety Blacklist (لیست سیاه کلمات و مفاهیم غیراخلاقی و غیرشرعی)
FORBIDDEN_KEYWORDS = [
    # Immoral, nudity, revealing attire, romance, adult
    "bikini", "sexy", "hot girl", "lingerie", "naked", "nude", "kiss", "kissing", 
    "dating", "girlfriend", "boyfriend", "romance", "romantic", "adult", "erotic",
    "dance", "dancing", "twerk", "belly dance", "model", "actress", "cleavage",
    "رقص", "زن", "دختر", "عاشقانه", "برهنه", "بیکینی", "دوست دختر", "لب گرفتن", "مبتذل",
    
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
    "آهنگ", "موزیک", "ترانه", "خواننده", "کنسرت", "موسیقی", "دنس", "ریمیکس"
]

def is_content_halal_and_clean(title: str, description: str = "", tags: list = None) -> bool:
    """
    Checks if a video's title, description, or tags contain any forbidden or sinful content.
    Returns True if 100% clean, False if it violates moral or Islamic guidelines.
    """
    text_to_scan = f"{title} {description} {' '.join(tags or [])}".lower()
    
    for word in FORBIDDEN_KEYWORDS:
        # Match whole word or exact pattern
        pattern = r"\b" + re.escape(word.lower()) + r"\b"
        if re.search(pattern, text_to_scan):
            return False
            
    return True

def clean_search_query_for_halal(query: str, niche: str) -> str:
    """
    Appends negative filter tags and halal/no-music enforcement to queries.
    """
    if niche == "quran":
        # Pure authentic Quran without any background music or tunes
        return f"{query} بدون موسيقى no music -song -dance -remix"
    elif niche == "ai":
        # Pure tech tutorial and tool demonstrations without background songs
        return f"{query} no music tutorial tech -song -dance -remix"
    elif niche == "animals":
        # Pure natural wildlife sounds without songs or background beats
        return f"{query} wildlife documentary pure nature sounds no music -song -dance -remix"
    return f"{query} no music -song -dance"
