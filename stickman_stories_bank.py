"""
STICKMAN NARRATIVE & VISUAL STUDIO (موتور تولید سناریو و تصاویر استیک‌من برای ۳ کانال)
Engineered for:
1. AI Tools (AI Unveiled) - 100% Stickman Tech in 2026
2. CryptoLab / PolyMint (Financial Psychology & Web3)
3. Mind & Nature (Facts & Wild Wildlife Psychology)

Optimized for:
- 10-22s Golden Sweet Spot (35-50 words voiceover)
- In-video high-curiosity hook banner
- Contrast psychology (Bob vs Alex / Myth vs Reality)
- 4-scene synchronized storyboards
"""
import random

STICKMAN_BANKS = {
    "ai": [
        {
            "hook": "FEELS ILLEGAL TO KNOW! 🤖⚡",
            "voice": "Bob spends five hours writing reports every morning. Alex automated his entire job with an autonomous AI agent in twenty seconds. Alex makes double while drinking coffee. Stop working like an NPC. Upgrade your brain to AI. Subscribe for secret tools!",
            "scenes": [
                {"title": "BOB: 5 HOURS OF MANUAL WORK", "sub": "Tired, Depressed, Underpaid 😫", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "ALEX: 20 SECONDS WITH AI", "sub": "Autonomous AI Agent In 2026! 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "DON'T WORK LIKE AN NPC!", "sub": "Work Smarter, Not Harder ⚡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "THE AI REVOLUTION IS HERE", "sub": "Subscribe & Dominate in 2026 🧠👑", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "SECRET AI TOOL IN 2026 🤯",
            "voice": "Bob paid two thousand dollars for complex video editing software. Alex used one free AI prompt and generated Hollywood quality 4K video in ten seconds. Don't let old software drain your wallet. Follow for daily free AI tools!",
            "scenes": [
                {"title": "BOB: PAID $2,000 FOR SOFTWARE", "sub": "Empty Wallet, Slow Results 💸", "mood": "sad", "arms": "down", "props": "papers"},
                {"title": "ALEX: 1 FREE AI PROMPT", "sub": "Hollywood 4K Quality Instantly! 🎨✨", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "STOP WASTING YOUR MONEY!", "sub": "Free AI Alternatives in 2026 ⚡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "BECOME A SUPERHUMAN", "sub": "Subscribe for Daily AI Magic 🤖🔥", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "AI CODING MAGIC 2026 💻⚡",
            "voice": "Bob spent three sleepless weeks debugging five lines of broken code. Alex pasted his idea into an autonomous AI engineer and launched a full app in two minutes. Software engineering changed forever. Follow for the new coding era!",
            "scenes": [
                {"title": "BOB: 3 WEEKS OF BUG HUNTING", "sub": "No Sleep, Broken Code 🖥️💥", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "ALEX: FULL APP IN 2 MINUTES", "sub": "Autonomous AI Built Everything! 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "CODING HAS EVOLVED!", "sub": "Build Anything With Natural Language 💡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "JOIN THE NEW TECH ELITE", "sub": "Follow For The Next Era 🤖✨", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "YOUR RESUME IS OBSOLETE! 📄❌",
            "voice": "Bob sent two hundred resumes and got zero replies. Alex used an AI agent that tailored his portfolio to fifty companies in ten minutes, landing three executive interviews. The job market transformed. Subscribe to stay ahead!",
            "scenes": [
                {"title": "BOB: 200 RESUMES REJECTED", "sub": "Ghosted By Everyone 😭", "mood": "sad", "arms": "down", "props": "papers"},
                {"title": "ALEX: AI TAILORED PORTFOLIO", "sub": "3 Interviews In 24 Hours! 🎯", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "APPLY SMARTER WITH AI", "sub": "Let Intelligent Agents Work For You ⚡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "BEAT THE ALGORITHM", "sub": "Subscribe For Career AI Secrets 💼🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "HOW RICH PEOPLE USE AI 🧠💵",
            "voice": "Average people ask AI to write funny jokes. The top one percent use AI agents to automate e-commerce, research investments, and clone their businesses. Change how you look at artificial intelligence. Follow for elite tactics!",
            "scenes": [
                {"title": "USING AI FOR JOKES 🥱", "sub": "Wasting The Most Powerful Tool", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "THE 1% AUTOMATING WEALTH", "sub": "Digital Clones & Automated Stores 💰", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "AI IS YOUR CAPITAL", "sub": "Deploy Agents, Multiply Output 📈", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "LEVEL UP YOUR WEALTH", "sub": "Follow AI Unveiled Today 🤖👑", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "LEARN ANYTHING IN 10 MIN 📚⚡",
            "voice": "Bob buys four hundred dollar courses and forgets everything in two days. Alex feeds textbooks into his personalized AI tutor, mastering difficult concepts in minutes through interactive quizzes. Learn ten times faster. Subscribe now!",
            "scenes": [
                {"title": "BOB: EXPENSIVE DUSTY COURSES", "sub": "$400 Spent, Zero Retained 🤦‍♂️", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "ALEX: PERSONAL AI PROFESSOR", "sub": "Master Any Skill in 10 Minutes 🎓✨", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "SPEED LEARNING UNLOCKED", "sub": "Transform How Your Brain Learns ⚡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "NEVER FALL BEHIND", "sub": "Subscribe For Daily Super-Learning 🧠", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "THE SECRET PROMPT TRICK 🤫⚡",
            "voice": "Most people write lazy three word prompts and get generic answers. When you assign your AI a world-class persona and exact constraints, its output becomes genius tier. Stop whispering to AI. Command it like a CEO! Follow for prompt masterclasses.",
            "scenes": [
                {"title": "LAZY 3-WORD PROMPTS 🥱", "sub": "Garbage In, Garbage Out 🗑️", "mood": "sad", "arms": "down", "props": "laptop"},
                {"title": "THE CEO PROMPT METHOD", "sub": "Persona + Constraints = Brilliance 💎", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "CONTROL THE MACHINE", "sub": "Unlock Hidden Model Capabilities 🧠", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "BECOME A PROMPT ARCHITECT", "sub": "Subscribe for Master Hacks 🤖🔥", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "AI AGENTS WILL REPLACE APPS 📱💥",
            "voice": "In 2026, you will never open fifty separate apps. You will speak one command to your local AI assistant, and it will book flights, order food, and update your calendar automatically. Welcome to agentic intelligence. Follow to see the future!",
            "scenes": [
                {"title": "50 APPS CLUTTERING SCREEN", "sub": "Wasting Hours Every Single Day 📱⌛", "mood": "sad", "arms": "down", "props": "none"},
                {"title": "1 AI AGENT DOES EVERYTHING", "sub": "Voice Commands To Full Execution 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "THE DEATH OF STATIC APPS", "sub": "Agentic AI Takes Over in 2026 🌐", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "WELCOME TO TOMORROW", "sub": "Subscribe for Next-Gen Tech ⚡🤖", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "FREE AI VOICE CLONING 🎙️✨",
            "voice": "Bob spent thousands renting sound studios and voice actors. Alex cloned his voice with thirty seconds of clean audio and produced ten audiobooks in one afternoon. Content creation is democratic now. Follow for creator tools!",
            "scenes": [
                {"title": "BOB: $3,000 STUDIO BILLS", "sub": "Studio Time, Endless Retakes 🎙️💸", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "ALEX: INSTANT VOICE CLONE", "sub": "10 Audiobooks In 1 Afternoon! 🎧⚡", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "CONTENT FOR EVERYONE", "sub": "Scale Your Presence Globally 🌍", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "CREATE LIKE A PRO", "sub": "Subscribe for Creator AI Hacks 🎨", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "CAN AI THINK LIKE HUMAN? 🧠🤖",
            "voice": "Scientists tested AI models against complex logic puzzles. While humans panic under pressure, neural networks broke down millions of variables in milliseconds. Artificial general intelligence is arriving faster than you think. Stay informed. Subscribe today!",
            "scenes": [
                {"title": "HUMAN PANIC UNDER PRESSURE", "sub": "Overwhelmed By Complexity 🤯", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "NEURAL NETWORKS IN 10ms", "sub": "Flawless Multi-Step Reasoning 💡", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "AGI IS ON THE HORIZON", "sub": "The Greatest Shift in History 🌐", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "PREPARE FOR 2026", "sub": "Follow AI Unveiled 🤖👑", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        }
    ],
    "cryptolab": [
        {
            "hook": "POOR VS WEALTHY MINDSET 💰📈",
            "voice": "Bob keeps all his cash in a bank losing value to inflation every single day. Alex mints decentralized digital assets on PolyMint in two clicks. Bob complains about prices, while Alex builds real Web3 freedom. Discover PolyMint and own your future!",
            "scenes": [
                {"title": "BOB: CASH LOSING VALUE DAILY", "sub": "Inflation Eating His Hard Work 💸📉", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "ALEX: MINTS TOKENS ON POLYMINT", "sub": "Decentralized Wealth on Polygon! 🚀💎", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "DECENTRALIZATION IS FREEDOM", "sub": "Own Your Financial Destiny in 2026 🌐", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "JOIN POLYMINT TODAY", "sub": "https://ploymint.polyganfactorytoken.workers.dev 💎", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "THE 1% WEALTH SECRET 🧠💎",
            "voice": "The average person trades forty years for paper currency that governments inflate away. The wealthy create tokenized assets that generate value around the clock. Which side are you on? Build your decentralized future on PolyMint today. Link in description!",
            "scenes": [
                {"title": "TRADING 40 YEARS FOR PAPER", "sub": "The Rat Race Traps 99% of People 🏃‍♂️💨", "mood": "sad", "arms": "down", "props": "papers"},
                {"title": "ASSETS WORKING 24/7 FOR YOU", "sub": "Smart Tokenization on Web3 🌐⚡", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "ESCAPE THE TRADITIONAL SYSTEM", "sub": "Build Real Value in The Digital Era 💎", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "LAUNCH YOUR TOKEN ON POLYMINT", "sub": "Official Platform: PolyMint 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "WHY INFLATION RUINS YOU 💸📉",
            "voice": "A dollar saved ten years ago lost nearly half its purchasing power today. Paper money has no hard limit. Tokenized digital assets on Polygon have immutable math. Stop holding melting ice. Discover smart decentralized tokenization on PolyMint!",
            "scenes": [
                {"title": "YOUR SAVINGS ARE MELTING 🧊", "sub": "Paper Currency Devalued Fast 📉", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "IMMUTABLE CODE WINS", "sub": "Mathematically Secured Assets 💎🔐", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "PROTECT YOUR HARD WORK", "sub": "Decentralized Finance Is The Shield 🛡️", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "EXPERIENCE POLYMINT", "sub": "polyganfactorytoken.workers.dev 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "CREATE A TOKEN IN 60 SEC ⚡🪙",
            "voice": "Bob thought launching a cryptocurrency required a team of fifty developers and huge capital. Alex used PolyMint to deploy a verified token on Polygon with zero coding in sixty seconds. The barriers are gone. Launch your Web3 project now!",
            "scenes": [
                {"title": "BOB: 'I NEED $50,000 FOR TECH'", "sub": "Stuck in Excuses & Confusion 🤯", "mood": "sad", "arms": "down", "props": "papers"},
                {"title": "ALEX: DEPLOYED IN 60 SECONDS", "sub": "Instant Polygon Token on PolyMint! ⚡", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "ZERO CODING REQUIRED", "sub": "Full Smart Contract Automation 🛠️", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "BUILD ON POLYMINT", "sub": "Join The Polygon Web3 Movement 🌐💎", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "DO NOT BUY AT THE TOP! 📉⚠️",
            "voice": "Bob buys hype coins when they trend everywhere and panics when they drop. Alex builds foundational assets, mints his own utilities, and stays emotionally calm. Learn crypto psychology. Build real value on PolyMint today!",
            "scenes": [
                {"title": "BOB: FOMO AT THE PEAK 😱", "sub": "Buying Green, Selling Red 💸💥", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "ALEX: CALCULATED BUILDER", "sub": "Focusing on Real Token Utility 🧠📈", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "PSYCHOLOGY IS 90% OF CRYPTO", "sub": "Never Trade on Pure Emotion 🧘‍♂️", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "BECOME A BUILDER", "sub": "Explore PolyMint Web3 Hub 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "THE GAS FEE TRICK ⛽💡",
            "voice": "Bob spent eighty dollars on Ethereum gas fees just to move a ten dollar token. Alex moved ten thousand dollars on Polygon for less than a single penny. Stop burning your money on slow networks. Build on Polygon with PolyMint!",
            "scenes": [
                {"title": "BOB: $80 GAS FEE ON $10 😭", "sub": "Transaction Fees Eating Everything", "mood": "sad", "arms": "down", "props": "papers"},
                {"title": "ALEX: $0.001 ON POLYGON", "sub": "Lightning Fast & Ultra Cheap ⚡🏎️", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "SCALE WITHOUT EXPENSE", "sub": "Next Generation Layer 2 Power 🌐", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "USE POLYMINT ON POLYGON", "sub": "Official Factory Platform 💎🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "WHY BANKS FEAR WEB3 🏦🔒",
            "voice": "Banks can freeze your account, block your transfers, and charge hidden fees. Web3 smart contracts run on mathematical consensus with zero middlemen. You are your own bank. Learn how decentralization protects you. Start on PolyMint today!",
            "scenes": [
                {"title": "FROZEN BANK ACCOUNTS 🚫", "sub": "Zero Control Over Your Own Money", "mood": "sad", "arms": "head", "props": "papers"},
                {"title": "UNSTOPPABLE WEB3 CODE", "sub": "You Control The Private Keys 🔐💎", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "MATHEMATICAL SOVEREIGNTY", "sub": "No Middlemen, No Permission Needed 🌐", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "DISCOVER POLYMINT", "sub": "Your Portal To Web3 Freedom 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "WHAT IS TOKENOMICS? 📊🧠",
            "voice": "Bob launched a token with unlimited supply and wondered why the price crashed to zero. Alex programmed strict deflationary burns and fair distribution. Good tokenomics makes or breaks a project. Master Web3 token design on PolyMint!",
            "scenes": [
                {"title": "BOB: UNLIMITED PRINTING 📉", "sub": "Token Collapsed To Zero 💸", "mood": "sad", "arms": "down", "props": "papers"},
                {"title": "ALEX: FIXED SUPPLY & BURNS", "sub": "Sustainable Value Creation 📈🔥", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "TOKENOMICS IS EVERYTHING", "sub": "Design Rules Before You Launch 💡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "DEPLOY WITH POLYMINT", "sub": "Pre-Engineered Smart Contracts 🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "PASSIVE WEB3 WEALTH 💰⚡",
            "voice": "Most people think crypto is staring at candlesticks twenty-four seven. Smart investors deploy automated liquidity and stake utility tokens. Let your digital assets work while you sleep. Build your Web3 portfolio on PolyMint!",
            "scenes": [
                {"title": "BOB: GLUED TO CHARTS 24/7", "sub": "Stress, Headaches, Red Candles 📊😫", "mood": "sad", "arms": "head", "props": "laptop"},
                {"title": "ALEX: AUTOMATED REWARDS", "sub": "Earning Yield While Sleeping 🛌💵", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "LEVERAGE SMART PROTOCOLS", "sub": "Digital Capital Efficiency 🌐", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "START WITH POLYMINT", "sub": "Unlock Polygon Opportunities 💎🚀", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        },
        {
            "hook": "THE FUTURE OF FINANCE 🌐💎",
            "voice": "Every stock, real estate deed, and digital asset will be tokenized on blockchain by twenty thirty. You are early to the biggest financial migration in human history. Position yourself now with PolyMint on Polygon. Link below!",
            "scenes": [
                {"title": "OLD SLOW PAPER SYSTEM", "sub": "Filing Cabinets & Bureaucracy 🗄️🐌", "mood": "sad", "arms": "down", "props": "papers"},
                {"title": "GLOBAL ASSET TOKENIZATION", "sub": "Trillions Moving On-Chain 🚀🌍", "mood": "happy", "arms": "celebrate", "props": "laptop"},
                {"title": "YOU ARE STILL EARLY", "sub": "Build Foundations in Web3 💎", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "BUILD ON POLYMINT", "sub": "ploymint.polyganfactorytoken.workers.dev 🌐", "mood": "happy", "arms": "celebrate", "props": "laptop"}
            ]
        }
    ],
    "animals": [
        {
            "hook": "NEVER RUN FROM A PREDATOR! 🦁⚠️",
            "voice": "Bob sees a predator in the wild and runs for his life. Fatal mistake! Running triggers their hunting chase instinct. Alex stands tall, makes loud noise, and slowly backs away. The predator hesitates and retreats. Knowledge is survival! Follow for wild animal secrets.",
            "scenes": [
                {"title": "BOB RUNS IN TERROR!", "sub": "Triggers Predator Chase Instinct 😱🏃", "mood": "sad", "arms": "head", "props": "none"},
                {"title": "ALEX STANDS GROUND CALMLY", "sub": "Predator Confused & Backs Away! 🛡️🦁", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "SURVIVAL RULE #1: NEVER RUN", "sub": "Make Yourself Look 10X Bigger 🐾⚠️", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "INSANE NATURE SECRETS", "sub": "Subscribe to Stay Alive! 🧠🐺", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        },
        {
            "hook": "THE SMARTEST BIRD ON EARTH 🧠🦅",
            "voice": "Did you know crows recognize human faces for years and teach their babies who is dangerous? When Bob threw a rock at a crow, the whole flock remembered him and dive-bombed him for months! Never mess with intelligent birds. Nature is watching you! Follow for more.",
            "scenes": [
                {"title": "BOB MESSED WITH A CROW!", "sub": "Thought Birds Have No Memory 🪨🐦", "mood": "sad", "arms": "down", "props": "none"},
                {"title": "THE FLOCK STRIKES BACK!", "sub": "Crows Never Forget A Face! 😱🦅", "mood": "sad", "arms": "head", "props": "none"},
                {"title": "INSANE ANIMAL MEMORY", "sub": "Generational Knowledge In Birds 🧠⚡", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "WILD SECRETS EVERY DAY", "sub": "Subscribe to Wild Kingdom! 🐾👑", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        },
        {
            "hook": "HONEY BADGER DOES NOT CARE! 🦡🔥",
            "voice": "The honey badger has skin so thick that bee stings and machetes barely scratch it. It gets bitten by deadly venomous cobras, takes a two hour nap, and wakes up to finish eating the snake! Fearlessness is an evolutionary superpower. Follow for nature beasts!",
            "scenes": [
                {"title": "BITTEN BY A DEADLY COBRA!", "sub": "Lethal Venom In Its Bloodstream 🐍⚠️", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "SLEEPS 2 HOURS & WAKES UP", "sub": "Immune System Shrugs Off Poison! 💪🦡", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "ZERO FEAR IN THE SAVANNA", "sub": "Attacks Lions & Leopards Fearlessly 🦁", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "NATURE'S ULTIMATE TANK", "sub": "Subscribe For Beast Stories 🐾👑", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        },
        {
            "hook": "OCTOPUS HAS NINE BRAINS 🐙🧠",
            "voice": "An octopus has one central brain and eight mini brains in each tentacle. Each arm can taste, explore, and open jars independently while the main body sleeps. They can even change color in milliseconds to match any background. Alien intelligence lives on Earth! Follow for ocean wonders.",
            "scenes": [
                {"title": "9 INDEPENDENT BRAINS!", "sub": "Each Arm Thinks For Itself 🐙💡", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "INSTANT SHAPE-SHIFTING", "sub": "Camouflage in 200 Milliseconds 🌊🎨", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "CAN OPEN JARS & ESCAPE", "sub": "True Invertebrate Masterminds 🧠🔓", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "OCEAN ALIENS ARE REAL", "sub": "Subscribe to Wild Kingdom 🌊👑", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        },
        {
            "hook": "WHY WOLVES NEVER SURRENDER 🐺❄️",
            "voice": "A lone wolf can track prey for fifty miles in freezing blizzards without stopping. When challenged, they never whine or quit. They depend on pack discipline and relentless endurance. Adopt the wolf mindset. Never stop hunting your goals! Follow for wildlife inspiration.",
            "scenes": [
                {"title": "50 MILES IN BLIZZARD ❄️", "sub": "Unmatched Endurance & Focus 🐺", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "PACK DISCIPLINE WINS", "sub": "Loyalty & Strategic Teamwork 🐾🤝", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "NEVER SURRENDER UNDER PRESSURE", "sub": "The Wolf Mentality in Nature 🏔️", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "UNLEASH YOUR INNER WOLF", "sub": "Subscribe to Wild Kingdom 🐺👑", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        },
        {
            "hook": "THE IMMORTAL JELLYFISH 🌊✨",
            "voice": "When the Turritopsis jellyfish gets old, injured, or starves, it does something impossible. It reverts its cells back into a baby polyp, restarting its entire life cycle from scratch. It is biologically immortal! Discover the deepest secrets of nature. Subscribe now!",
            "scenes": [
                {"title": "OLD AGE & INJURY ARRIVES ⏳", "sub": "Most Animals Accept The End 🥀", "mood": "sad", "arms": "down", "props": "none"},
                {"title": "REVERSES BACK TO A BABY!", "sub": "Cellular Rebirth & Eternal Life 🪼✨", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "BIOLOGICALLY IMMORTAL", "sub": "Defying The Rules of Mortality 🌊🔬", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "UNBELIEVABLE NATURE FACTS", "sub": "Subscribe For Daily Wonders 🐾👑", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        },
        {
            "hook": "THE FASTEST STRIKE ON EARTH 🥊🦐",
            "voice": "The mantis shrimp strikes with the speed of a bullet, boiling the water around its claws and creating miniature shockwaves that shatter aquarium glass! Never underestimate small creatures. Nature packs devastating power in tiny packages. Follow for more jaw dropping facts!",
            "scenes": [
                {"title": "LOOKS LIKE A TINY SHRIMP 🦐", "sub": "Harmless Colors On The Ocean Floor", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "STRIKE ACCELERATION OF A BULLET", "sub": "Water Boils & Shockwaves Explode! 💥🌊", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "CAN BREAK AQUARIUM GLASS", "sub": "Most Powerful Punch in The World 🥊", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "RESPECT THE WILD", "sub": "Subscribe to Wild Kingdom 🐾🔥", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        },
        {
            "hook": "HOW ELEPHANTS GRIEVE 🐘💔",
            "voice": "When an elephant passes away, the herd gathers in silence, gently touches the bones with their trunks, and stands guard for days in mourning. They possess deep emotional intelligence and remember loved ones for decades. Animals feel just like us. Follow for heartwarming facts.",
            "scenes": [
                {"title": "SILENT HERD GATHERING 🐘", "sub": "Touching Fallen Bones Gently 🕊️", "mood": "sad", "arms": "head", "props": "none"},
                {"title": "DEEP EMOTIONAL INTELLIGENCE", "sub": "Remembering Family For 50 Years 🧠❤️", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "MORE EMPATHETIC THAN HUMANS", "sub": "Pure Compassion in The Wild 🌍", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "PROTECT OUR WILDLIFE", "sub": "Subscribe to Wild Kingdom 🐾👑", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        },
        {
            "hook": "PENGUIN PROPOSAL IS REAL 🐧💍",
            "voice": "When a male gentoo penguin finds his true love, he searches the entire beach for the smoothest pebble to give her. If she accepts the pebble, they mate for life and build their nest together! True romance exists in the Antarctic. Follow for adorable nature stories!",
            "scenes": [
                {"title": "SEARCHING FOR THE PERFECT STONE", "sub": "Hundreds of Pebbles Examined 🪨🐧", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "SHE ACCEPTS THE PEBBLE! 💍", "sub": "Mates For Life in Freezing Ice ❤️❄️", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "NATURE'S PURE ROMANCE", "sub": "Building A Future Together 🏔️", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "WILD LOVE STORIES", "sub": "Subscribe to Wild Kingdom 🐾👑", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        },
        {
            "hook": "DOLPHINS CALL BY NAME 🐬🗣️",
            "voice": "Dolphins create a unique signature whistle for themselves, just like human names! Other dolphins call them by their specific whistle across miles of open ocean. They even recognize family whistles after twenty years apart. Animal intelligence is mind blowing. Follow for daily wonders!",
            "scenes": [
                {"title": "UNIQUE SIGNATURE WHISTLES 🎵", "sub": "Every Dolphin Has A Real Name 🐬💡", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "CALLING ACROSS THE OCEAN", "sub": "Complex Social Language in Water 🌊🗣️", "mood": "happy", "arms": "celebrate", "props": "none"},
                {"title": "REMEMBERING AFTER 20 YEARS", "sub": "Unbreakable Bond Across Time 🧠✨", "mood": "neutral", "arms": "down", "props": "none"},
                {"title": "THE SECRETS OF NATURE", "sub": "Subscribe to Wild Kingdom 🐾👑", "mood": "happy", "arms": "celebrate", "props": "none"}
            ]
        }
    ]
}

def get_stickman_episode(niche: str, run_count: int = 0):
    bank = STICKMAN_BANKS.get(niche, STICKMAN_BANKS["ai"])
    return bank[run_count % len(bank)]
