"""
STICKMAN NARRATIVE & VISUAL STUDIO (موتور تولید سناریو و تصاویر استیک‌من برای ۳ کانال)
Engineered for:
1. AI Tools (AI Unveiled)
2. CryptoLab / PolyMint (Financial Psychology & Web3)
3. Mind & Nature (Facts & Wild Psychology)
"""
import random

STICKMAN_BANKS = {
    "ai": [
        {
            "hook": "FEELS ILLEGAL TO KNOW! 🤖⚡",
            "voice": "Meet Bob. Bob spends five hours writing emails and reports every single morning. Meet Alex. Alex gave his daily tasks to an autonomous AI agent in 2026. Alex is drinking coffee on a beach while earning double. Stop working like an NPC. Upgrade to AI today! Follow for secret tools.",
            "scenes": [
                {"title": "BOB: 5 HOURS OF MANUAL WORK", "sub": "Tired, Depressed, Underpaid 😫", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "ALEX: 10 SECONDS WITH AI", "sub": "Automating 99% of Tasks in 2026! 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "DON'T WORK LIKE AN NPC!", "sub": "Work Smarter, Not Harder ⚡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "THE AI REVOLUTION IS HERE", "sub": "Subscribe & Dominate in 2026 🧠👑", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "SECRET AI TOOL REVEALED 🤯",
            "voice": "Bob paid two thousand dollars for graphic design and video editing software. Alex used one free open-source AI model and created cinematic 4K visuals in ten seconds! Who was smarter? Don't let old software drain your wallet. Follow for daily AI hacks!",
            "scenes": [
                {"title": "BOB: PAID $2,000 FOR SOFTWARE", "sub": "Empty Wallet, Slow Results 💸", "mood": "sad", "arms": "down", "props": "papers"},
                {"title": "ALEX: FREE AI TOOL IN 10s", "sub": "Hollywood 4K Quality Instantly! 🎨✨", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "STOP WASTING YOUR MONEY!", "sub": "Free AI Alternatives in 2026 ⚡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "BECOME A SUPERHUMAN", "sub": "Subscribe for Daily AI Magic 🤖🔥", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "AI CODING MAGIC IN 2026 💻⚡",
            "voice": "Bob spent three sleepless weeks debugging five lines of broken code. Alex pasted his idea into an autonomous AI engineer, and it built a full production app in two minutes! Software development changed forever. Are you ready for 2026? Subscribe now!",
            "scenes": [
                {"title": "BOB: 3 WEEKS OF BUG HUNTING", "sub": "No Sleep, Broken Code 🖥️💥", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "ALEX: FULL APP IN 2 MINUTES", "sub": "Autonomous AI Built Everything! 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "CODING HAS EVOLVED!", "sub": "Build Anything With Natural Language 💡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "JOIN THE NEW TECH ELITE", "sub": "Follow For The Next Era 🤖✨", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        }
    ],
    "cryptolab": [
        {
            "hook": "POOR VS WEALTHY MINDSET 💰📈",
            "voice": "Bob keeps all his cash in a depreciating bank account losing value every day to inflation. Alex creates his own decentralized Web3 asset on PolyMint in two clicks. Bob complains about prices, while Alex builds real digital wealth. Discover PolyMint and take control of your financial future!",
            "scenes": [
                {"title": "BOB: CASH LOSING VALUE DAILY", "sub": "Inflation Eating His Hard Work 💸📉", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "ALEX: MINTS TOKENS ON POLYMINT", "sub": "Decentralized Wealth on Polygon! 🚀💎", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "DECENTRALIZATION IS FREEDOM", "sub": "Own Your Financial Destiny in 2026 🌐", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "JOIN POLYMINT TODAY", "sub": "https://ploymint.polyganfactorytoken.workers.dev 💎", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "THE 1% WEALTH RULE 🧠💎",
            "voice": "The average person trades forty years of their life working for paper money that governments print out of thin air. The wealthy create tokenized assets that work for them 24/7. Which side are you on? Build your decentralized future on PolyMint today. Link in bio!",
            "scenes": [
                {"title": "TRADING 40 YEARS FOR PAPER", "sub": "The Rat Race Traps 99% of People 🏃‍♂️💨", "mood": "sad", "arms": "down", "props": "papers"},
                {"title": "ASSETS WORKING 24/7 FOR YOU", "sub": "Smart Tokenization on Web3 🌐⚡", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "ESCAPE THE TRADITIONAL SYSTEM", "sub": "Build Real Value in The Digital Era 💎", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "LAUNCH YOUR TOKEN ON POLYMINT", "sub": "Official Platform: PolyMint 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        }
    ],
    "animals": [
        {
            "hook": "NEVER RUN FROM A PREDATOR! 🦁⚠️",
            "voice": "Bob sees a predator in the wild and runs for his life. Big mistake! Running triggers their natural hunting instinct and seals his fate. Alex stands tall, makes loud noise, and slowly backs away. The predator hesitates and walks off. Knowledge is survival! Follow for insane wildlife facts.",
            "scenes": [
                {"title": "BOB RUNS IN TERROR!", "sub": "Triggers Predator Kill Instinct 😱🏃", "mood": "sad", "arms": "head", "props": "none"},
                {"title": "ALEX STANDS GROUND CALMLY", "sub": "Predator Confused & Steps Back! 🛡️🦁", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "SURVIVAL RULE #1: NEVER FLEE", "sub": "Make Yourself Look 10X Bigger 🐾⚠️", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "INSANE NATURE SECRETS", "sub": "Subscribe to Stay Alive! 🧠🐺", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        },
        {
            "hook": "THE SMARTEST ANIMAL ON EARTH 🧠🐬",
            "voice": "Did you know crows can recognize human faces for years and even hold grudges? When Bob threw a rock at a crow, the entire flock remembered him and dive-bombed him for months! Never mess with intelligent birds. Nature is watching you! Follow for wild animal mysteries.",
            "scenes": [
                {"title": "BOB MESSED WITH A CROW!", "sub": "He Thought Birds Have No Memory 🪨🐦", "mood": "sad", "arms": "down", "props": "none"},
                {"title": "THE FLOCK STRIKES BACK!", "sub": "Crows Never Forget A Human Face! 😱🦅", "mood": "sad", "arms": "head", "props": "none"},
                {"title": "INSANE ANIMAL INTELLIGENCE", "sub": "They Share Information Across Flocks 🧠⚡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "WILD SECRETS EVERY DAY", "sub": "Subscribe to Wild Kingdom! 🐾👑", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        }
    ]
}

def get_stickman_episode(niche: str, run_count: int = 0):
    bank = STICKMAN_BANKS.get(niche, STICKMAN_BANKS["ai"])
    return bank[run_count % len(bank)]
