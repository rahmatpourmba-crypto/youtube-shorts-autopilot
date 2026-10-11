import json
import datetime
from pathlib import Path
from metadata_optimizer import generate_luxury_thumbnail
from youtube_uploader import upload_short

BASE_DIR = Path(__file__).resolve().parent
MASTER_VIDEO = BASE_DIR / "cryptolab_master_en.mp4"
STATE_FILE = BASE_DIR / "state.json"

# Multi-lingual schedule optimized for the prime-time hours of each target continent
CRYPTOLAB_LANGUAGES = [
    {
        "code": "es",
        "name": "Spanish (Latin America & Spain)",
        "prime_time_utc": "19:00", # Peak afternoon/evening in Latin America
        "title": "🚀 ¡Crea Tu Propio Token Sin Programar! | PolyMint #crypto #web3",
        "badge": "CREA TU TOKEN SIN CÓDIGO! 🚀💎",
        "badge_color": (255, 180, 0),
        "badge_bg": (20, 15, 35),
        "desc": (
            "🚀 ¿Quieres lanzar tu propia criptomoneda en Polygon sin escribir una sola línea de código?\n\n"
            "Con PolyMint, despliega tu token ERC-20 en segundos de forma segura y profesional.\n\n"
            "🔥 Suscríbete a @1cryptoforgecrypto para dominar Web3 y herramientas crypto!\n\n"
            "#Crypto #Polygon #ERC20 #Web3 #Blockchain #Token #PolyMint #Shorts"
        ),
        "tags": ["Crypto", "Polygon", "ERC20", "Token", "Crear Token", "Web3", "Blockchain", "PolyMint", "Shorts"],
        "comment": "🚀 ¿Qué nombre le pondrías a tu propio token? ¡Déjalo en los comentarios! 👇💎"
    },
    {
        "code": "pt",
        "name": "Portuguese (Brazil & Portugal)",
        "prime_time_utc": "21:00", # Peak 6 PM Brasilia Time
        "title": "🚀 Crie Seu Próprio Token Sem Saber Programar! | PolyMint #crypto",
        "badge": "CRIE SEU TOKEN SEM CÓDIGO! 🚀🇧🇷",
        "badge_color": (0, 230, 120),
        "badge_bg": (15, 25, 20),
        "desc": (
            "🚀 Lance seu token ERC-20 na rede Polygon em poucos cliques e sem complicações!\n\n"
            "PolyMint é a ferramenta definitiva para quem quer empreender no mundo cripto.\n\n"
            "🔥 Inscreva-se no canal @1cryptoforgecrypto para tutoriais exclusivos de Web3!\n\n"
            "#Cripto #Polygon #Token #Web3 #Blockchain #ERC20 #PolyMint #Shorts"
        ),
        "tags": ["Cripto", "Polygon", "Criar Token", "Token ERC20", "Web3", "Blockchain", "Shorts"],
        "comment": "🇧🇷 Você já pensou em criar seu token para um projeto? Comente aqui embaixo! 👇🚀"
    },
    {
        "code": "ar",
        "name": "Arabic (Middle East & North Africa)",
        "prime_time_utc": "16:00", # Peak 7-8 PM Gulf Time
        "title": "🚀 أنشئ عملتك الرقمية الخاصة بدون أي برمجة! | PolyMint #crypto",
        "badge": "أنشئ عملتك الرقمية بدون كود! 🚀🪙",
        "badge_color": (212, 175, 55),
        "badge_bg": (18, 22, 35),
        "desc": (
            "🚀 هل ترغب في إطلاق عملتك المشفرة الخاصة على شبكة Polygon دون كتابة سطر برمجي واحد؟\n\n"
            "منصة PolyMint تتيح لك إنشاء عقود ERC-20 الذكية في ثوانٍ وبأمان تام.\n\n"
            "🔥 اشترك في قناة @1cryptoforgecrypto لمزيد من أسرار البلوكشين والعملات الرقمية!\n\n"
            "#عملات_رقمية #بلوكشين #كريبتو #بوليجون #Web3 #Shorts"
        ),
        "tags": ["عملات رقمية", "بلوكشين", "كريبتو", "انشاء توكن", "Polygon", "ERC20", "Shorts"],
        "comment": "🪙 ما هو المجال الذي تود إطلاق عملتك الرقمية فيه؟ شاركنا رأيك! 👇✨"
    },
    {
        "code": "de",
        "name": "German (DACH Region / Europe)",
        "prime_time_utc": "17:00", # Peak 7 PM CET
        "title": "🚀 Eigenen Krypto-Token ohne Programmierkenntnisse erstellen! | PolyMint",
        "badge": "TOKEN ERSTELLEN OHNE CODE! 🚀🇩🇪",
        "badge_color": (255, 215, 0),
        "badge_bg": (20, 20, 20),
        "desc": (
            "🚀 Erstelle deinen eigenen ERC-20 Token auf dem Polygon-Netzwerk ganz ohne Code.\n\n"
            "Schnell, sicher und intuitiv mit PolyMint.\n\n"
            "🔥 Abonniere @1cryptoforgecrypto für tägliche Web3 & Krypto Insights!\n\n"
            "#Krypto #Polygon #Blockchain #Web3 #Token #PolyMint #Shorts"
        ),
        "tags": ["Krypto", "Polygon", "Token erstellen", "Web3", "Blockchain", "Shorts"],
        "comment": "🚀 Welches Projekt planst du im Krypto-Bereich? Schreib es in die Kommentare! 👇"
    },
    {
        "code": "fr",
        "name": "French (France & Francophone Africa)",
        "prime_time_utc": "18:00", # Peak 8 PM Paris Time
        "title": "🚀 Créez Votre Propre Token Crypto Sans Coder! | PolyMint #web3",
        "badge": "CRÉEZ VOTRE TOKEN SANS CODE! 🚀🇫🇷",
        "badge_color": (0, 200, 255),
        "badge_bg": (15, 20, 35),
        "desc": (
            "🚀 Lancez facilement votre propre crypto-monnaie ERC-20 sur Polygon avec PolyMint.\n\n"
            "Pas besoin de compétences en programmation ou de smart contracts compliqués.\n\n"
            "🔥 Abonnez-vous à @1cryptoforgecrypto pour tout savoir sur le Web3 et les cryptos!\n\n"
            "#Crypto #Polygon #Blockchain #Web3 #Token #PolyMint #Shorts"
        ),
        "tags": ["Crypto", "Polygon", "Créer un token", "Web3", "Blockchain", "Shorts"],
        "comment": "🚀 Prêt à lancer votre premier projet Web3 ? Donnez votre avis ci-dessous ! 👇"
    },
    {
        "code": "hi",
        "name": "Hindi (India & South Asia)",
        "prime_time_utc": "13:30", # Peak 7 PM IST
        "title": "🚀 बिना कोडिंग अपना क्रिप्टो टोकन बनाएं! | PolyMint #crypto #web3",
        "badge": "बिना कोडिंग अपना टोकन बनाएं! 🚀🇮🇳",
        "badge_color": (255, 153, 51),
        "badge_bg": (20, 25, 40),
        "desc": (
            "🚀 Polygon नेटवर्क पर सिर्फ कुछ मिनटों में अपना ERC-20 टोकन लॉन्च करें, बिना किसी कोडिंग के!\n\n"
            "PolyMint आपको देता है सबसे आसान और सुरक्षित वेब3 अनुभव।\n\n"
            "🔥 Web3 और क्रिप्टो की दुनिया में आगे रहने के लिए @1cryptoforgecrypto को सब्सक्राइब करें!\n\n"
            "#Crypto #Polygon #Blockchain #Web3 #Hindi #Token #Shorts"
        ),
        "tags": ["Crypto", "Polygon", "Crypto in Hindi", "Web3", "Token Kaise Banaye", "Shorts"],
        "comment": "🚀 आप अपने टोकन का क्या नाम रखेंगे? कमेंट में जरूर बताएं! 👇🔥"
    },
    {
        "code": "ru",
        "name": "Russian (Eastern Europe & Central Asia)",
        "prime_time_utc": "15:00", # Peak 6 PM MSK
        "title": "🚀 Создай свой крипто-токен без программирования! | PolyMint #crypto",
        "badge": "СОЗДАЙ СВОЙ ТОКЕН БЕЗ КОДА! 🚀💎",
        "badge_color": (0, 220, 255),
        "badge_bg": (18, 18, 30),
        "desc": (
            "🚀 Запусти свой собственный токен стандарта ERC-20 на блокчейне Polygon за считанные секунды.\n\n"
            "PolyMint позволяет сделать это без знания кода и смарт-контрактов.\n\n"
            "🔥 Подписывайся на @1cryptoforgecrypto, чтобы не пропустить ключевые Web3 инструменты!\n\n"
            "#Крипта #Полигон #Блокчейн #Web3 #Токен #Shorts"
        ),
        "tags": ["Крипта", "Polygon", "Создать токен", "Web3", "Блокчейн", "Shorts"],
        "comment": "💎 Какое применение для своего токена вы видите? Напишите в комментариях! 👇"
    }
]

def publish_next_cryptolab_language():
    if not MASTER_VIDEO.exists():
        raise FileNotFoundError(f"Master video not found at {MASTER_VIDEO}")

    # Load state
    state = {}
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
            
    lang_idx = state.get("cryptolab_lang_index", 0) % len(CRYPTOLAB_LANGUAGES)
    curr_lang = CRYPTOLAB_LANGUAGES[lang_idx]
    
    print(f"\n[CRYPTOLAB] Publishing for Target Geography: {curr_lang['name']}")
    print(f"  Target Prime Time (UTC): {curr_lang['prime_time_utc']}")
    print(f"  Title: {curr_lang['title']}")

    # Generate custom luxury thumbnail in target language
    out_dir = BASE_DIR / "output" / f"cryptolab_{curr_lang['code']}"
    out_dir.mkdir(parents=True, exist_ok=True)
    thumb_path = out_dir / "thumbnail.jpg"

    import subprocess
    import shutil
    import imageio_ffmpeg
    ffmpeg_exe = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()
    
    cmd_thumb = [
        ffmpeg_exe, "-y",
        "-ss", "00:00:03.000",
        "-i", str(MASTER_VIDEO),
        "-vframes", "1",
        "-q:v", "2",
        str(thumb_path)
    ]
    subprocess.run(cmd_thumb, check=True)

    generate_luxury_thumbnail(
        str(thumb_path),
        str(thumb_path),
        niche="cryptolab", # 21 Mega-Prompt High-CTR Web3 Obsidian & Gold
        custom_text=curr_lang["badge"]
    )

    # Official PolyMint Links & Halal Crypto Authority Block
    POLYMINT_BRAND_BLOCK = (
        "📊 PolyMint Crypto Daily\n"
        "Islamic Scholars' View on Crypto\n\n"
        "🌐 https://ploymint.polyganfactorytoken.workers.dev\n"
        "✈️ https://t.me/polymint_crypto\n\n"
        "#crypto #bitcoin #cryptocurrency #blockchain #polygon #ethereum #defi #cryptonews #altcoin #halal "
        "#عملات_الرقمية #بيتكوين #كريبتو #بلوكشين #رمزارز #کریپتو #بیت_کوین #criptomonedas #criptomoedas #kriptopara #криптовалюта #加密货币"
    )

    # Combined full high-authority description: Title + Body + Brand Links
    full_description = f"{curr_lang['title']}\n\n{curr_lang['desc']}\n\n{POLYMINT_BRAND_BLOCK}"

    # Engagement & conversion comment for YouTube & Instagram
    pinned_comment_text = (
        "📊 PolyMint Crypto Daily — Islamic Scholars' View on Crypto\n"
        "🌐 Deploy your token: https://ploymint.polyganfactorytoken.workers.dev\n"
        "✈️ Telegram Community: https://t.me/polymint_crypto"
    )

    # Upload to CryptoLab YouTube Channel
    res = upload_short(
        channel_key="polygon",
        video_path=str(MASTER_VIDEO),
        title=curr_lang["title"],
        description=full_description,
        tags=curr_lang["tags"],
        category_id="28",
        thumbnail_path=str(thumb_path),
        pinned_comment=pinned_comment_text
    )

    # Cross-Post to CryptoLab Instagram Page (@cryp.tolab1)
    if res:
        try:
            print("  [CryptoLab] Cross-posting Reel to Instagram (@cryp.tolab1)...")
            from instagram_publisher import publish_instagram_reel
            ig_caption = f"{curr_lang['title']}\n\n{curr_lang['desc']}\n\n{POLYMINT_BRAND_BLOCK}"
            publish_instagram_reel(
                video_path=str(MASTER_VIDEO),
                caption=ig_caption,
                niche="cryptolab",
                thumbnail_path=str(thumb_path),
                initial_comment=pinned_comment_text
            )
        except Exception as e:
            print(f"  [Instagram Warning] CryptoLab Reel publish notice: {e}")

    # Clean up generated thumbnail
    try:
        if thumb_path.exists():
            thumb_path.unlink()
            print(f"  [Cleanup] Deleted CryptoLab thumbnail file: {thumb_path.name}")
    except Exception as e:

        print(f"  [Cleanup Warning] {e}")

    # Increment language index for tomorrow
    state["cryptolab_lang_index"] = lang_idx + 1
    state["cryptolab_last_lang"] = curr_lang["code"]
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


    return res

if __name__ == "__main__":
    publish_next_cryptolab_language()
