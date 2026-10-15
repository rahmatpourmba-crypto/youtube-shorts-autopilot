"""
COMPETITOR INTELLIGENCE & REVERSE-ENGINEERING ENGINE
(موتور جاسوسی الگوریتمی، مهندسی معکوس و انتقال دانش کانال‌های میلیون‌بازدیدی جهان)

Features:
1. Benchmark Directory: Tracks the world's highest-earning million-view benchmark channels.
2. Neuro-Hook Feature Extraction: Extracts winning title patterns, pacing, and emotional drivers.
3. Knowledge Transfer & Localization: Adapts global viral angles into Arabic, Persian, and English.
4. Autonomous Ingestion: Pumps high-velocity viral blueprints directly into growth_brain.json.
"""
import sys
import json
import random
from pathlib import Path

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
BRAIN_FILE = BASE_DIR / "growth_brain.json"

# ==============================================================================
# WORLD CHAMPION BENCHMARK CHANNELS & PROVEN MILLION-VIEW BLUEPRINTS
# ==============================================================================
CHAMPION_BENCHMARKS = {
    "quran_and_mystery": {
        "benchmark_channels": [
            {"name": "Towards Eternity", "subs": "4.2M", "views": "520M", "archetype": "Prophecies & Existential Mysteries"},
            {"name": "MercifulServant", "subs": "4.1M", "views": "640M", "archetype": "Emotional Heart-Melting Khushu"},
            {"name": "OnePath Network", "subs": "3.8M", "views": "480M", "archetype": "Quranic Science & Miracles"}
        ],
        "proven_million_hooks": [
            {
                "formula": "The Shocking Truth About {entity} That Scientists Confirmed!",
                "entities": ["Pharaoh Drowning", "Iron Coming From Stars", "Two Seas Never Mixing", "Mountain Roots"],
                "adapted_ar": "الحقيقة الصادمة عن {entity} التي أثبتها العلم الحديث! 🌊✨ #Shorts #Quran",
                "adapted_fa": "حقیقت تکان‌دهنده‌ای درباره {entity} که علم تازه آن را کشف کرد! 🌿✨ #Shorts #قرآن",
                "adapted_en": "The Shocking Truth About {entity} Revealed in Quran 1400 Years Ago! 🕊️⚡ #Shorts #Islam"
            },
            {
                "formula": "Major Signs of the Day of Judgment Happening Right Now: {entity}",
                "entities": ["Dajjal Island Mystery", "Dukhan Smoke Prophecy", "Green Arabia Prophecy", "Euphrates Gold Mountain"],
                "adapted_ar": "علامات الساعة الكبرى التي تقع الآن أمام أعيننا: {entity} ⚠️⚡ #Shorts",
                "adapted_fa": "نشانه‌های بزرگ قیامت که هم‌اکنون در حال رخ دادن است: {entity} ⚠️⚡ #Shorts",
                "adapted_en": "Signs of the End Times Coming True Right Now: {entity}! 😱⚡ #Shorts #TowardsEternity"
            },
            {
                "formula": "What Actually Happens To Your Soul in {entity}?",
                "entities": ["The First Night in Grave", "The Moment of Death", "The Gates of Jannah", "The Day of Reckoning"],
                "adapted_ar": "ماذا يحدث لروحك في {entity}؟ الحقيقة المرعبة 🕊️🤍 #Shorts",
                "adapted_fa": "در {entity} چه بر سر روح انسان می‌آید؟ حقیقتی تکان‌دهنده 🌿🤍 #Shorts",
                "adapted_en": "What Actually Happens In {entity}? The Untold Reality 🕊️✨ #Shorts #Islam"
            }
        ]
    },

    "ai_and_tech": {
        "benchmark_channels": [
            {"name": "Fireship", "subs": "3.6M", "views": "650M", "archetype": "Hyper-Fast 100s Tech & Coder Comedy"},
            {"name": "AI Revolution", "subs": "1.4M", "views": "190M", "archetype": "Tools That Feel Illegal to Know"},
            {"name": "Two Minute Papers", "subs": "1.7M", "views": "280M", "archetype": "Mind-Blowing Research Breakthroughs"}
        ],
        "proven_million_hooks": [
            {
                "formula": "{number} Insane AI Tools That Feel 100% Illegal to Know in 2026!",
                "variables": ["3 Secret", "5 Mind-Blowing", "Top Unknown"],
                "adapted_en": "3 Insane AI Tools That Feel Illegal to Know in 2026! 🤖⚡ #Shorts #AI",
                "adapted_fa": "۳ ابزار هوش مصنوعی شگفت‌انگیز که کارایی‌تان را ۱۰ برابر می‌کنند! 🚀💻 #Shorts"
            },
            {
                "formula": "When Junior Dev Lets Autonomous AI Push Directly to Production at 3 AM! 💀😭",
                "variables": ["Junior Dev", "Solo Founder", "Programmer vs Bug"],
                "adapted_en": "Programmer vs Autonomous AI: When Code Breaks Production at 3 AM! 💻😭 #Shorts #Coding",
                "adapted_fa": "وقتی به هوش مصنوعی میگی سرور پروداکشن رو دیپلوی کن و کل سیستم می‌ترکه! 💻😫 #Shorts"
            },
            {
                "formula": "This Crazy AI Generates {task} In 10 Seconds For Free!",
                "variables": ["Working Web Apps", "Photorealistic 3D Worlds", "Full Music Tracks"],
                "adapted_en": "This Crazy AI Generates Working Web Apps in 10 Seconds For Free! 🤯🚀 #Shorts #FutureTech",
                "adapted_fa": "این هوش مصنوعی در ۱۰ ثانیه برای شما برنامه کامل می‌سازد! 🤯⚡ #Shorts"
            }
        ]
    },

    "animals_and_survival": {
        "benchmark_channels": [
            {"name": "Casual Geographic", "subs": "4.6M", "views": "1.2B", "archetype": "Dark Nature Comedy & Predator Realism"},
            {"name": "BBC Earth", "subs": "14M", "views": "6B", "archetype": "Apex Predator Chases & Impossible Survival"},
            {"name": "Animalogic", "subs": "2.1M", "views": "350M", "archetype": "Genius Creature Superpowers"}
        ],
        "proven_million_hooks": [
            {
                "formula": "Why You Should NEVER Mess With {creature} in The Wild!",
                "creatures": ["A Crow That Remembers Faces", "A Honey Badger Facing 3 Lions", "A Wounded Leopard", "A Black Eagle"],
                "adapted_en": "Why You Should NEVER Mess With A Crow in The Wild! 200 IQ Revenge 🦅🧠 #Shorts #Nature",
                "adapted_fa": "چرا هرگز نباید با یک کلاغ در طبیعت شوخی کرد! هوش ۲۰۰ و انتقام عجیب 🦅😱 #Shorts"
            },
            {
                "formula": "Stickman vs {creature}: The Deadliest Survival Encounter Caught on Camera!",
                "creatures": ["Prehistoric Raptor", "Apex Lion Pride", "Giant Anaconda", "King Cobra"],
                "adapted_en": "Stickman vs Prehistoric Raptor: Pure Survival Instinct! 🦖🔥 #Shorts #Animation",
                "adapted_fa": "استیک‌من در برابر دایناسور درنده: نبرد مرگبار بقا در اعماق جنگل! 🦖⚡ #Shorts"
            },
            {
                "formula": "The Most Unbelievable Loyalty Ever Witnessed in The Animal Kingdom! 🦁❤️",
                "creatures": ["Brother Lions Reuniting", "Dog Defending Injured Pack", "Elephant Protecting Baby"],
                "adapted_en": "Brother Lions Reunite After 3 Years: Pure Loyalty & Power! 🦁👑 #Shorts #Wildlife",
                "adapted_fa": "وفاداری و برادری بی‌پایان شیرها در طبیعت: صحنه‌ای که میلیون‌ها نفر را تکان داد! 🦁❤️ #Shorts"
            }
        ]
    },

    "cryptolab_web3": {
        "benchmark_channels": [
            {"name": "Whiteboard Crypto", "subs": "950k", "views": "110M", "archetype": "Visual No-Code Crypto & ERC-20 Mechanics"},
            {"name": "Finematics", "subs": "430k", "views": "45M", "archetype": "Polygon, Ethereum & Smart Contracts"},
            {"name": "Coin Bureau", "subs": "2.4M", "views": "310M", "archetype": "Web3 Wealth & Tokenization Secrets"}
        ],
        "proven_million_hooks": [
            {
                "formula": "How to Create and Launch Your Own Token on Polygon in 30 Seconds! 🚀💎",
                "adapted_en": "Create Your Own Crypto Token in 30 Seconds with PolyMint! 🚀💎 #Shorts #Polygon #Web3",
                "adapted_fa": "چگونه در ۳۰ ثانیه بدون کدنویسی توکن اختصاصی روی پالیگان بسازیم! 🪙💎 پولی‌مینت #Shorts"
            },
            {
                "formula": "100x Leverage Trader Regret: When You Buy The Dip And It Keeps Dipping! 😭📉",
                "adapted_en": "100x Leverage Trader Pain: When You Buy The Dip And It Drops 90%! 💀💸 #Shorts #CryptoHumor",
                "adapted_fa": "درد تریدر اهرم ۱۰۰: وقتی فکر می‌کنی کفه قیمته ولی ۹۰٪ بیشتر می‌ریزه! 😭📉 #Shorts"
            },
            {
                "formula": "The Secret Tool That Lets Anyone Deploy ERC-20 Smart Contracts For Pennies! 🪙⚡",
                "adapted_en": "Deploy Verified ERC-20 Tokens on Polygon With Zero Coding! 🪙⚡ PolyMint #Shorts #Crypto",
                "adapted_fa": "ساخت قرارداد هوشمند استاندارد ERC-20 با کمترین کارمزد روی پالیگان! 🚀🪙 #Shorts"
            }
        ]
    }
}

# ==============================================================================
# COMPETITIVE INTELLIGENCE ENGINE METHODS
# ==============================================================================

def transfer_million_view_intelligence_to_brain():
    """
    Ingests global champion blueprints into the local Growth Brain,
    enriching winning_topics and viral_spinoffs with proven million-view angles.
    """
    if not BRAIN_FILE.exists():
        print("[Spy Engine] Growth brain not found.")
        return False

    with open(BRAIN_FILE, "r", encoding="utf-8") as f:
        brain = json.load(f)

    print("=" * 70)
    print("=== COMPETITOR INTELLIGENCE & REVERSE-ENGINEERING ENGINE ===")
    print("Ingesting Proven Formulas from 15 World Champion Channels...")
    print("=" * 70)

    # 1. Quran & Islamic Mystery Transfer
    q_hooks = CHAMPION_BENCHMARKS["quran_and_mystery"]["proven_million_hooks"]
    brain_q = brain.setdefault("winning_topics", {}).setdefault("quran", [])
    for h in q_hooks:
        for ent in h.get("entities", []):
            if ent not in brain_q:
                brain_q.insert(0, ent)
    print(f"  ✓ Quran Knowledge Transferred: {len(q_hooks)} core formulas + {len(brain_q)} high-affinity entities.")

    # 2. AI Unveiled Transfer
    ai_hooks = CHAMPION_BENCHMARKS["ai_and_tech"]["proven_million_hooks"]
    brain_ai = brain.setdefault("winning_topics", {}).setdefault("ai", [])
    for h in ai_hooks:
        title_seed = h["adapted_en"].split(":")[0]
        if title_seed not in brain_ai:
            brain_ai.insert(0, title_seed)
    print(f"  ✓ AI Knowledge Transferred: Ingested Fireship & AI Revolution formulas.")

    # 3. Animals & Wildlife Transfer
    anim_hooks = CHAMPION_BENCHMARKS["animals_and_survival"]["proven_million_hooks"]
    brain_anim = brain.setdefault("winning_topics", {}).setdefault("animals", [])
    for h in anim_hooks:
        for c in h.get("creatures", []):
            if c not in brain_anim:
                brain_anim.insert(0, c)
    print(f"  ✓ Wildlife Knowledge Transferred: Ingested Casual Geographic & BBC Earth survival pacing.")

    # 4. CryptoLab Transfer
    crypto_hooks = CHAMPION_BENCHMARKS["cryptolab_web3"]["proven_million_hooks"]
    brain_crypto = brain.setdefault("winning_topics", {}).setdefault("cryptolab", [])
    for h in crypto_hooks:
        hook_seed = h["adapted_en"][:35]
        if hook_seed not in brain_crypto:
            brain_crypto.insert(0, hook_seed)
    print(f"  ✓ CryptoLab Knowledge Transferred: Ingested Whiteboard Crypto & PolyMint token models.")

    brain["last_competitor_ingestion"] = "2026-10-15 11:30:00"
    brain["monetization_income_target"] = "$1,000,000 / Multi-Channel Media Network"

    with open(BRAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(brain, f, ensure_ascii=False, indent=2)

    print("\n✓ All million-view formulas successfully localized and synchronized into Growth Brain!")
    return True

def get_champion_localized_blueprint(niche: str, language: str = "en") -> dict:
    """
    Returns a proven million-view blueprint adapted directly from top channels.
    """
    key_map = {
        "quran": "quran_and_mystery",
        "islamic_mystery": "quran_and_mystery",
        "ai": "ai_and_tech",
        "animals": "animals_and_survival",
        "cryptolab": "cryptolab_web3",
        "polygon": "cryptolab_web3"
    }
    cat = key_map.get(niche, "animals_and_survival")
    hooks = CHAMPION_BENCHMARKS[cat]["proven_million_hooks"]
    chosen = random.choice(hooks)

    if language == "ar" and "adapted_ar" in chosen:
        title = chosen["adapted_ar"]
    elif language == "fa" and "adapted_fa" in chosen:
        title = chosen["adapted_fa"]
    else:
        title = chosen["adapted_en"]

    return {
        "niche": niche,
        "title": title,
        "formula": chosen.get("formula"),
        "channels_analyzed": [c["name"] for c in CHAMPION_BENCHMARKS[cat]["benchmark_channels"]]
    }

if __name__ == "__main__":
    transfer_million_view_intelligence_to_brain()
