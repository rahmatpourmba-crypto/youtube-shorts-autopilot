"""
165 MEGA-ULTRA PROMPT & ALGORITHMIC SYNCHRONIZATION ENGINE
(موتور ۱۶۵ ترفند مگا اولترا ابر پرامپتی و هماهنگ‌سازی الگوریتم یوتیوب)

This module implements the 165 Golden Algorithmic & Neuro-Cognitive Techniques
reverse-engineered from top YouTube Growth Engineers and Deep Learning Recommendation Systems:
- Two-Tower Neural Network Alignment (Candidate Generation & Ranking)
- VVSA (Viewed vs Swiped Away) Optimization
- APV (Average Percentage Viewed) & Infinite Rewatch Loops
- Engagement Velocity Amplification (Comments/Likes ratio)
- Bayesian Reinforcement Learning on Winning Seed Keywords
- 100% Monetization Shield & Policy Guardrails
"""
import random
import re
from typing import Dict, List, Tuple

# ==============================================================================
# THE 165 MEGA-ULTRA PROMPT & YOUTUBE ALGORITHM PROTOCOLS
# ==============================================================================
MEGA_165_PROTOCOLS = {
    # --------------------------------------------------------------------------
    # GROUP 1: NEURO-HOOKS & PATTERN INTERRUPTS (Tricks 1 to 25)
    # --------------------------------------------------------------------------
    "T001_CURIOSITY_GAP": "Create an irresistible void of information that demands closure.",
    "T002_PATTERN_INTERRUPT": "Break visual/verbal expectations in the first 0.8 seconds.",
    "T003_EXTREME_CONTRAST": "Juxtapose opposites (e.g., $1 vs $1,000,000, Tiny vs Giant, Weakest vs Deadliest).",
    "T004_OPEN_LOOP_STAKES": "Introduce high stakes early and delay the resolution to the final second.",
    "T005_LOSS_AVERSION": "Frame content around avoiding costly mistakes ('Never do this', 'Why 99% fail').",
    "T006_FORBIDDEN_KNOWLEDGE": "Suggest secret, hidden, or insider revelations ('They don't want you to know').",
    "T007_SOCIAL_PROOF_ANOMALY": "Highlight behavior that contradicts conventional wisdom.",
    "T008_TEMPORAL_URGENCY": "Anchor to immediate relevance ('Happening right now', 'Before it's too late').",
    "T009_MICRO_CLIFFHANGER": "Insert narrative pivots every 4-6 seconds to reset dopamine.",
    "T010_THE_TWIST_HOOK": "Lead with a false assumption that flips midway.",
    "T011_IDENTITY_AFFIRMATION": "Target a specific tribe ('Programmers know this pain', 'Real traders relate').",
    "T012_COUNTER_INTUITIVE_TRUTH": "State a fact that sounds completely fake but is 100% proven.",
    "T013_SENSORY_MAGNET": "Use vivid visual and auditory cues (whisper, snap, neon flash, bass drop).",
    "T014_NEGATIVE_FRAME_HOOK": "Ban boring generic phrasing; forbid weak passive verbs.",
    "T015_THE_COUNTDOWN_TENSION": "Establish a numeric deadline or countdown to drive completion.",
    "T016_MORAL_OR_ETHICAL_DILEMMA": "Pose an urgent moral question that splits viewer opinion.",
    "T017_SUPERLATIVE_REALISM": "Use grounded superlatives backed by tangible specifics.",
    "T018_INCONGRUOUS_PAIRING": "Combine two unrelated things (Stickman + Prehistoric Raptor, Robot + Holy Verse).",
    "T019_IN_VIDEO_EYE_TRACKING": "Align focal points to the upper-third safe zone for mobile thumb scrolling.",
    "T020_AUDITORY_CONTRAST": "Cut audio completely for 0.5s before a punchline to create acoustic contrast.",
    "T021_DOPAMINE_MICRO_PUNCH": "Reward viewer attention every 3 seconds with visual shift.",
    "T022_THE_RELATABLE_PAIN": "Trigger acute emotional memory (loss of funds, debugging failure, betrayal).",
    "T023_COSMIC_OR_DIVINE_AWE": "Awaken transcendent reverence through sacred cadence and cosmic scale.",
    "T024_SUBTITLE_KINETIC_FLOW": "Display dynamic punchy subtitles with word-by-word active tracking.",
    "T025_ZERO_SPOILER_RULE": "Never reveal the ending in the title or opening banner.",

    # --------------------------------------------------------------------------
    # GROUP 2: TWO-TOWER RECOMMENDATION & SEMANTIC EMBEDDINGS (Tricks 26 to 50)
    # --------------------------------------------------------------------------
    "T026_QUERY_EMBEDDING_ALIGNMENT": "Match user query semantic vectors in YouTube Candidate Generation.",
    "T027_EXACT_MATCH_SEEDING": "Place the core high-volume keyword in the first 35 characters of title.",
    "T028_DUAL_EMBEDDING_TAGGING": "Combine 3 broad umbrella tags with 4 hyper-niche exact tags.",
    "T029_SEMANTIC_TRIAD_DESCRIPTION": "Construct 3-part descriptions: Hook, Contextual Synopsis, Platform Hub.",
    "T030_SEARCH_SUGGEST_HARVESTING": "Continuously harvest autocomplete tokens from YouTube Search API.",
    "T031_NEGATIVE_SEARCH_EXCLUSION": "Purge low-intent, muddy keywords that dilute audience classification.",
    "T032_SHORTS_SHELF_VECTORING": "Inject '#shorts' and primary niche hashtag to claim Shorts Carousel rank.",
    "T033_CO_OCCURRENCE_BOOSTING": "Group keywords that co-occur in top 1% trending competitor metadata.",
    "T034_CROSS_LINGUAL_BRIDGING": "Pair international English terms with native Arabic/Persian keywords.",
    "T035_METADATA_LENGTH_SWEETSPOT": "Optimize title length strictly between 50 and 68 characters for mobile feeds.",
    "T036_CANONICAL_URL_PRESERVATION": "Maintain clean official link anchoring (PolyMint official gateway).",
    "T037_CLUSTER_TAXONOMY_ANCHOR": "Align category ID with content archetype (22 People, 28 Tech, 15 Animals).",
    "T038_VOICE_SEARCH_NATURAL_PHRASING": "Incorporate conversational phrasing matching YouTube voice queries.",
    "T039_TOPICAL_AUTHORITY_DEPTH": "Publish within tight topical corridors to earn algorithmic creator trust.",
    "T040_CLICK_INTENT_PURITY": "Ensure 100% promise-to-delivery fidelity between title and video body.",
    "T041_EMBEDDING_DIVERSITY_PREVENTION": "Avoid mixing unrelated topics in one channel to protect audience graphs.",
    "T042_HIGH_VELOCITY_TIMESTAMPS": "Provide clean descriptive chapter marks for long-form documentaries.",
    "T043_SEARCH_INTENT_TRIAGE": "Identify whether search traffic is navigational, informational, or transactional.",
    "T044_GRAPH_SIMILARITY_HACKING": "Reference key entities (Prophet companions, AI models, crypto blockchains).",
    "T045_ALGORITHM_COLD_START_BOOST": "Ignite new uploads with instant seed signals via pinned comments.",
    "T046_TAG_CLOUD_CONCENTRATION": "Limit tags to 12-18 tightly unified terms; prevent semantic diffusion.",
    "T047_TITLE_TOKEN_DENSITY": "Maximize high-value nouns and verbs; eliminate filler articles.",
    "T048_METADATA_FRESHNESS_PING": "Signal timeliness with current year and era markers ('2026', 'Final Signs').",
    "T049_TRANSCRIPT_SEMANTIC_SYNC": "Ensure spoke words match title keywords for automatic closed-caption indexing.",
    "T050_RECOMMENDED_NEXT_MAPPING": "Design ending prompts that steer the recommendation engine to the next upload.",

    # --------------------------------------------------------------------------
    # GROUP 3: VVSA (VIEWED VS SWIPED AWAY) MAXIMIZERS (Tricks 51 to 70)
    # --------------------------------------------------------------------------
    "T051_ZERO_DEAD_AIR": "Start at timestamp 0.0 with maximum motion and auditory presence.",
    "T052_IN_VIDEO_SAFEZONE_BANNER": "Position dynamic top hook banners between Y:80 and Y:240.",
    "T053_MOTION_WARPING": "Begin video with dynamic camera pan or character lunge to force attention.",
    "T054_THUMBNAIL_PEAK_FRAME": "Extract thumbnail directly from video frame at maximum emotional peak.",
    "T055_VIBRANCY_OVERCLOCK": "Boost saturation by 14% and contrast by 9% for vibrant OLED displays.",
    "T056_UNSHARP_MASK_PUNCH": "Apply unsharp matrix (5:5:0.7) to guarantee crisp clarity on small screens.",
    "T057_FIRST_WORD_MAGNETISM": "The first spoken/written word must be high-energy ('Wait!', 'Never!', 'Look!').",
    "T058_VISUAL_SYMMETRY_SNAP": "Center the protagonist or stickman along the vertical center axis (X:540).",
    "T059_SWIPE_RESISTANT_HOOK": "Ask an unresolved question in the first 2 seconds that forces viewing.",
    "T060_COLOR_POP_HERO": "Use bright neon cyan, electric gold, or urgent crimson against deep obsidian.",
    "T061_ELIMINATE_STATIC_INTRO": "Ban logos, intro cards, or delayed theme music.",
    "T062_SPEED_VARIATION_ENTRY": "Start at 1.05x-1.08x speed to create immediate subconscious urgency.",
    "T063_THUMB_DRIVEN_COMPOSITION": "Leave bottom 30% clear for YouTube title, channel name, and sound icons.",
    "T064_FRAME_RATE_SMOOTHNESS": "Deliver strict 30/60 fps without frame drops or stutter.",
    "T065_ASPECT_RATIO_IMMERSION": "Enforce strict 1080x1920 (9:16) with zero pillarbox or letterbox bars.",
    "T066_FOCAL_POINT_LOCK": "Keep the action in the upper 60% of the screen where thumbs don't cover.",
    "T067_MICRO_VIGNETTE": "Subtly darken borders to direct 100% human focus to the center.",
    "T068_HIGH_FREQUENCY_TRANSITIONS": "Cut or transition scene every 3-4 seconds to hold attention.",
    "T069_AUDIO_DUCKING_CLARITY": "Duck background ambience by 12dB under voiceover to ensure pristine speech.",
    "T070_RETENTION_RADAR_CHECK": "Test if 75%+ of viewers will stay past 5 seconds.",

    # --------------------------------------------------------------------------
    # GROUP 4: APV & INFINITE REWATCH LOOP MECHANICS (Tricks 71 to 95)
    # --------------------------------------------------------------------------
    "T071_SEAMLESS_LOOP_BRIDGE": "Connect the final spoken word directly to the opening sentence.",
    "T072_SUB_25S_SWEETSPOT": "Cap Short duration at 18-24 seconds for effortless 120%+ APV.",
    "T073_INFORMATION_DENSITY": "Pack 45 seconds of content value into 20 seconds of runtime.",
    "T074_EASTER_EGG_INSPECTION": "Hide a subtle detail in frame that rewards a second or third watch.",
    "T075_AUDIO_LOOP_MATCH": "Fade out audio or match ending chord to opening frequency.",
    "T076_END_TWIST_REVELATION": "Deliver the climax at second 20 of a 22-second video.",
    "T077_RAPID_FIRE_PACING": "Maintain vocal pace at 160-180 words per minute.",
    "T078_NO_CONCLUSION_SLACK": "Cut the video the exact millisecond the punchline lands.",
    "T079_SPLIT_SCREEN_CONTRAST": "Use blurred motion background with tack-sharp foreground hero.",
    "T080_CYCLIC_NARRATIVE": "Make the end of the story explain the strange beginning.",
    "T081_SECONDARY_MICRO_ACTION": "Have background elements in subtle motion to stimulate subconscious eyes.",
    "T082_THE_PAUSE_CHALLENGE": "Display a rapid riddle or clue that makes viewers pause or rewatch.",
    "T083_PROGRESSION_INDICATOR": "Keep viewers anticipating the finale with subtle visual progression.",
    "T084_ENERGY_ACCELERANDO": "Slightly increase tempo and pitch across the video duration.",
    "T085_DOPAMINE_SATISFACTION": "Provide an intensely satisfying sensory conclusion.",
    "T086_RELATABLE_REACTION": "Stickman emotional breakdown or victory mirrors viewer emotions.",
    "T087_MEMETIC_SOUND_DESIGN": "Utilize universally recognized acoustic punctuation.",
    "T088_MULTI_CHARACTER_DYNAMICS": "Introduce conflict between two stickman/animal archetypes.",
    "T089_AVD_CALIBRATION": "Calibrate for average view duration exceeding 95% of total length.",
    "T090_STORYBOARD_COMPRESSION": "Storyboard in 3 acts: 0-4s Hook, 4-16s Struggle, 16-22s Payoff.",
    "T091_KINETIC_TEXT_ANIMATION": "Animate text with punchy pop-ins and color highlights.",
    "T092_ACOUSTIC_LOUDNESS_MASTER": "Normalize audio strictly to -14 LUFS with -1.5dB true peak.",
    "T093_STEREO_PAN_SUBTLETY": "Use subtle stereo widening to create immersive headphone experience.",
    "T094_ZERO_EXTRANEOUS_FRAMES": "Delete every millisecond of dead space or silent breaths.",
    "T095_VIRAL_COMPLETION_INDEX": "Target 85%+ completion rate to trigger algorithmic push to tier-2 seed pools.",

    # --------------------------------------------------------------------------
    # GROUP 5: ALGORITHMIC ENGAGEMENT & VELOCITY AMPLIFIERS (Tricks 96 to 120)
    # --------------------------------------------------------------------------
    "T096_COMMENT_BAIT_DILEMMA": "Ask an irresistible either/or question in the pinned comment.",
    "T097_COMMUNITY_TRIBE_PING": "Ask viewers to state their city/country or profession.",
    "T098_FIRST_HOUR_VELOCITY_ACCEL": "Maximize interactions within the first 60 minutes of release.",
    "T099_SALAT_OR_BLESSING_ANCHOR": "Invite viewers to send blessings upon the Prophet ﷺ on Quran videos.",
    "T100_DEBATE_CATALYST": "Feature a playful debate ('Coder vs Bug', 'Trader vs Bear Market').",
    "T101_EMOJI_VOTING_POLL": "Comment: 'React with 🔥 if you agree, 💀 if you don't!'",
    "T102_SHARE_TRIGGER_PSYCHOLOGY": "Give viewers an insight so shocking they must send it to friends.",
    "T103_PINNED_COMMENT_AUTHORITY": "Pin a high-value comment within 2 minutes of video upload.",
    "T104_HEART_AND_REPLY_LOOP": "Heart top user comments to trigger YouTube mobile push notifications.",
    "T105_SUBSCRIBER_PROMISE": "Promise specific daily value ('Subscribe for daily Quranic tranquility').",
    "T106_ALGORITHMIC_COEFFICIENT": "Compute Engagement Score = Views + (Likes * 12) + (Comments * 35).",
    "T107_SAVE_AND_BOOKMARK_HOOK": "Design content useful enough for viewers to save to playlists.",
    "T108_VIRAL_SPINOFF_REPLICATION": "When a video hits >100 views, produce 5 immediate thematic spin-offs.",
    "T109_SENTIMENT_RATIO_PROTECTION": "Maintain 98%+ like-to-dislike ratio with respectful messaging.",
    "T110_TRENDING_SOUND_ALIGNMENT": "Tag high-velocity trending audio IDs in metadata when available.",
    "T111_CROSS_PLATFORM_SYNERGY": "Publish to YouTube Shorts and Instagram Reels simultaneously.",
    "T112_VIRAL_SEED_TIMING": "Publish at peak timezone windows (15:00 IRST for MENA, 03:30 IRST for US/EU).",
    "T113_AUDIENCE_RECURRENCE_LOOP": "Establish consistent daily appointment viewing for audience habits.",
    "T114_ALGORITHM_SATURATION_GUARD": "Space uploads across channels to prevent subscriber notification burnout.",
    "T115_DYNAMIC_ENGAGEMENT_TEXT": "End with subtle on-screen prompt: 'Subscribe for daily wisdom'.",
    "T116_IN_STREAM_POLL_SIMULATION": "Design the video so viewers mentally take a side within 5 seconds.",
    "T117_REWARD_ATTENTIVE_VIEWERS": "Acknowledge top commenters in future video concepts.",
    "T118_SURPRISE_FACTOR": "Incorporate a 1% unexpected twist that sparks comment discussions.",
    "T119_RESONANCE_AUDIT": "Review comment topics to detect unexpected audience interests.",
    "T120_VELOCITY_EXPONENTIAL_PUSH": "Feed velocity metrics into candidate generation pool every cycle.",

    # --------------------------------------------------------------------------
    # GROUP 6: 100% GREEN MONETIZATION & POLICY GUARDRAILS (Tricks 121 to 140)
    # --------------------------------------------------------------------------
    "T121_ADVERTISER_FRIENDLY_METADATA": "Zero profanity, zero hate speech, zero misleading shock value.",
    "T122_SEVEN_LAYER_FAIR_USE_TRANSFORM": "Transform video via speedup, pitch shift, color grade, loudnorm, frame extraction, watermark, audio remaster.",
    "T123_AUTOMATED_STRIKE_MONITOR": "Check channel monetization status and copyright claims every cycle.",
    "T124_HALAL_SOUND_PROTOCOL": "Strictly no unauthorized musical instruments on Quran channels.",
    "T125_SAFE_ZONE_TEXT_ANCHORING": "Ensure zero burned text touches system UI borders.",
    "T126_DISCLAIMER_ANCHORING": "Add educational/fair-use description markers where appropriate.",
    "T127_ZERO_DUPLICATE_METADATA": "Generate uniquely crafted titles and descriptions for every video.",
    "T128_COMMUNITY_GUIDELINE_SCANNER": "Filter all titles through YouTube policy blacklist before publishing.",
    "T129_AUTHENTIC_NATURAL_THUMBNAILS": "Thumbnails must be natural frames extracted from the actual video.",
    "T130_ACCURATE_METADATA_PROMISE": "Title must accurately describe the video content to prevent spam penalties.",
    "T131_REUSED_CONTENT_IMMUNITY": "Transform external footage with significant original commentary and value.",
    "T132_ZERO_BOT_ACTIVITY_CLEANLINESS": "Never purchase views, fake comments, or artificially inflate numbers.",
    "T133_SAFE_AFFILIATE_LINKING": "Anchor only official verified platform links (PolyMint official hub).",
    "T134_RATE_LIMIT_PREVENTION": "Use exponential backoff and randomized jitter on API calls.",
    "T135_TOKEN_REFRESH_RESILIENCE": "Auto-refresh OAuth tokens before expiry to prevent upload failures.",
    "T136_METADATA_SPAM_PROTECTION": "Never repeat identical keywords more than 3 times in description.",
    "T137_TRANSPARENT_BRANDING": "Include subtle channel watermark to establish authentic original identity.",
    "T138_LEGAL_SOUND_LICENSING": "Use public domain, Creative Commons, or generated audio assets.",
    "T139_AD_SUITABILITY_SELF_CERT": "Produce content strictly aligned with green-dollar advertiser guidelines.",
    "T140_AUDIT_TRAIL_LOGGING": "Log every audit and upload into persistent state for complete traceability.",

    # --------------------------------------------------------------------------
    # GROUP 7: MULTI-NICHE CULTURAL & ALGORITHMIC TUNING (Tricks 141 to 155)
    # --------------------------------------------------------------------------
    "T141_QURAN_KHUSHU_ENGINEERING": "Tuned to awaken tranquility, soul-soothing peace, and spiritual reflection.",
    "T142_ISLAMIC_MYSTERY_NARRATIVE": "Focus on Signs of the Hour, Dajjal, and authentic Hadith prophecies.",
    "T143_AI_FUTURISM_CYBERPUNK": "Tuned to high-tech breakthroughs, coder pain points, and robot humor.",
    "T144_WILDLIFE_INSTINCT_DRAMA": "Focus on predator vs prey, survival instincts, and animal intelligence.",
    "T145_CRYPTOLAB_WEB3_AUTHORITY": "Blend trader humor with genuine Web3 tokenization on Polygon.",
    "T146_ARABIC_CALLIGRAPHIC_REVERENCE": "Format Arabic text with native reshaping and traditional elegance.",
    "T147_PERSIAN_POETIC_WARMTH": "Craft Persian titles with emotional depth, clarity, and cultural resonance.",
    "T148_ENGLISH_INTERNATIONAL_GLOBAL": "Write English titles with clean, punchy grammar for global audiences.",
    "T149_POLYMINT_TOKEN_INTEGRATION": "Consistently promote PolyMint official token creation without spamming.",
    "T150_REGIONAL_PEAK_SYNCHRONIZATION": "Schedule Arabic/Persian for 15:00 IRST and English for 03:30 IRST.",
    "T151_LOCALIZED_HASHTAG_CLUSTERS": "Combine English viral tags (#shorts) with localized Arabic/Persian tags.",
    "T152_DOCUMENTARY_HISTORICAL_PACING": "Pace long-form documentaries for sustained 15-20 minute engagement.",
    "T153_STICKMAN_UNIVERSAL_LANGUAGE": "Use stickman animations as universal visual language understood globally.",
    "T154_BILINGUAL_INSTAGRAM_CAPTIONS": "Craft dual-language Arabic/Persian captions for Instagram Reels.",
    "T155_CROSS_NICHE_ISOLATION": "Keep channel identities strictly decoupled to prevent algorithmic confusion.",

    # --------------------------------------------------------------------------
    # GROUP 8: BAYESIAN SELF-LEARNING & AUTONOMOUS SCALING (Tricks 156 to 165)
    # --------------------------------------------------------------------------
    "T156_CONTINUOUS_PERFORMANCE_AUDIT": "Audit channels every cycle, calculate delta views, and record history.",
    "T157_WINNING_KEYWORD_REINFORCEMENT": "Automatically promote keywords from high-velocity videos to top priority.",
    "T158_UNDERPERFORMING_TOPIC_PURGE": "Automatically prune topics that fail to generate velocity over 3 cycles.",
    "T159_TOPIC_SPINOFF_GENERATOR": "Synthesize 5 new variations whenever an archetype demonstrates breakout.",
    "T160_DYNAMIC_QUERY_MUTATION": "Mutate search queries using winning seed tokens to uncover hidden trends.",
    "T161_PERSISTENT_GROWTH_BRAIN": "Store all intelligence in `growth_brain.json` committed to Git memory.",
    "T162_AUTONOMOUS_FALLBACK_CIRCUIT": "Trigger secondary viral archives if primary query returns no results.",
    "T163_RUNNER_CLOUD_OPTIMIZATION": "Utilize high-speed datacenter connections on GitHub Actions runners.",
    "T164_GROWTH_MILESTONE_TRACKER": "Track exact distance to 1,000 subscribers and 4,000 watch hours.",
    "T165_ALGORITHMIC_HARMONY_LOOP": "Continuously synchronize content generation with YouTube's recommendation core."
}

# ==============================================================================
# NICHE-SPECIFIC ALGORITHMIC KNOWLEDGE & TEMPLATE REPOSITORIES
# ==============================================================================
NICHE_PROMPT_PATTERNS = {
    "quran": {
        "title_hooks_arabic": [
            "تلاوة خاشعة تسكن الروح وتريح القلب 🕊️✨",
            "سورة مباركة تفيض بالسكينة والطمأنينة 🌿",
            "راحة نفسية لا توصف.. استمع بقلبك 🤍",
            "صوت يدخل إلى أعماق القلب.. تلاوة عطرة 🌿",
            "عندما يقرأ القارئ بقلبه.. تلاوة مبكية 🕊️"
        ],
        "title_hooks_persian": [
            "تلاوتی که دل‌ها را آرام می‌کند 🕊️ آرامش محض",
            "آرامش بی‌پایان با کلام الهی 🌿 تلاوت خاشعانه",
            "صدایی که به روح آرامش می‌بخشد 🤍 استماع با قلب",
            "آیاتی که هر دلی را به لرزه درمی‌آورد ✨ قرآن کریم"
        ],
        "title_hooks_english": [
            "Heart-Melting Quran Recitation That Brings Tears 🕊️",
            "Feel The Deep Peace In Your Soul | Beautiful Quran 🌿",
            "Listen With Your Heart | Emotional Recitation 🤍",
            "The Most Beautiful Sound in the World | Holy Quran ✨"
        ],
        "engagement_comments": [
            "🌿 صلوا على الحبيب المصطفى محمد ﷺ واكتب من أي بلد تسمع هذه التلاوة؟ 🤍✨",
            "🤍 اكتب كلمة (سبحان الله) لتكون لك صدقة جارية في ميزان حسناتك 🌿",
            "✨ اللهم اجعل القرآن الكريم ربيع قلوبنا ونور صدورنا.. اكتب دعاءك هنا 🕊️"
        ],
        "description_triad": (
            "🌿 تلاوة عطرة خاشعة تفيض بالسكينة والنور وتملأ القلب طمأنينة وسلاماً.\n\n"
            "📖 قال الله تعالى: ﴿الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ﴾\n\n"
            "🤍 شارك المقطع مع من تحب ليكون صدقة جارية لك، واشترك في قناة @TheHolyLight لتصلك التلاوات اليومية الخاشعة.\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            "#Shorts #Quran #قرآن_كريم #تلاوة_خاشعة #راحة_نفسية #آيات_قرآنية #QuranRecitation #ViralShorts"
        ),
        "two_tower_tags": [
            "قرآن كريم", "تلاوة خاشعة", "راحة نفسية", "قرآن", "سورة", "ايات قرانية",
            "Quran", "Quran recitation", "Holy Quran", "Peace", "Islam", "Shorts", "Viral"
        ]
    },

    "islamic_mystery": {
        "title_hooks": [
            "The Shocking Truth About",
            "Signs Happening Right Now:",
            "What Actually Happens In The Grave?",
            "Signs of Dajjal Revealed:",
            "The Terrifying Prophecy of"
        ],
        "engagement_comments": [
            "⚠️ Did you know about this sign before? What are your thoughts? Drop a comment below! 👇⚡",
            "🕊️ May Allah protect us all in the end times. Type 'Ameen' and share with loved ones! 🤍",
            "⚡ Which sign of the Day of Judgment shocks you the most? Share below! 👇"
        ],
        "description_triad": (
            "⚡ Powerful reminders and signs of the final hour. Discover the deep Islamic mysteries and prophecies coming true today.\n\n"
            "📖 Let this reminder soften your heart and bring you closer to Allah before it is too late.\n\n"
            "🤍 Share this reminder with everyone you know. Subscribe for daily faith-awakening reminders.\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            "#Shorts #Islam #EndOfTimes #Dajjal #IslamicReminder #Prophecies #QuranMiracles #TowardsEternity"
        ),
        "two_tower_tags": [
            "Islam", "Signs of Day of Judgment", "Dajjal", "End of Times", "Islamic Reminder",
            "Towards Eternity", "Quran Miracles", "Life After Death", "Shorts", "Viral", "Trending"
        ]
    },

    "ai": {
        "title_hooks": [
            "Mind-Blowing AI That Feels Illegal to Know! 🤖⚡",
            "This Crazy AI Changes Everything in 2026! 🤯",
            "Programmer vs AI: When Code Breaks at 3AM! 💻😭",
            "AI Takes Over! Human vs Machine Stickman 🦾💥",
            "Top Insane AI Tools You Must Try Today! 🚀"
        ],
        "engagement_comments": [
            "🤖 Will AI replace programmers by 2027? Drop your honest opinion below! 👇⚡",
            "💻 What's the most mind-blowing AI tool you used this year? Share your favorites! 🚀",
            "🤯 React with 🤖 if you think AI will change everything, or 💀 if you're worried!"
        ],
        "description_triad": (
            "⚡ Discover the most powerful AI breakthroughs and hilarious tech moments of 2026!\n\n"
            "🚀 From autonomous coding agents to stickman tech struggles, witness the future of automation.\n\n"
            "🔥 Hit Like and Subscribe to @AIUnveiled for daily high-velocity AI secrets and tech comedy!\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            "#Shorts #AI #Stickman #Programming #TechHumor #ArtificialIntelligence #Coding #Viral"
        ),
        "two_tower_tags": [
            "AI", "Artificial Intelligence", "AI Tools", "Stickman", "Animation", "Tech Humor",
            "Programmer Bug", "Coding", "Machine Learning", "Shorts", "Viral", "Trending", "2026"
        ]
    },

    "animals": {
        "title_hooks": [
            "Stickman vs Wild Animals: Pure Survival! 🦁⚠️",
            "Never Mess With Nature's Deadliest Beasts! 🦡⚡",
            "The Most Shocking Animal Intelligence Ever Seen! 🦅😱",
            "Jurassic Escape: Stickman vs Prehistoric Predator! 🦖🔥",
            "When Animals Have 200 IQ: Unbelievable Tactics! 🐾👑"
        ],
        "engagement_comments": [
            "🦁 Which animal would survive this clash? Vote in the comments below! 👇🐾",
            "🦡 Did you know honey badgers and crows are this smart? Rate this moment from 1 to 10! 🔥",
            "🐾 Would you dare to face this creature in the wild? Yes or No? Drop your answer! 👇"
        ],
        "description_triad": (
            "🐾 The animal kingdom is full of unbelievable survival tactics, courage, and wild power!\n\n"
            "🦁 Witness incredible stickman encounters with the world's most resilient and dangerous creatures.\n\n"
            "❤️ If you love wild nature and thrilling animated adventures, Subscribe to @WildKingdom!\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            "#Shorts #Animals #Wildlife #Stickman #Animation #Nature #Predator #Survival #Viral"
        ),
        "two_tower_tags": [
            "Animals", "Wildlife", "Stickman", "Animation", "Nature", "Lion", "Honey Badger",
            "Crow Memory", "Predator", "Survival", "Shorts", "Viral", "Trending"
        ]
    },

    "cryptolab": {
        "title_hooks": [
            "When You Buy The Dip And It Keeps Dipping! 😭📉",
            "Create Your Own Crypto Token in 30 Seconds! 🚀💎",
            "100x Leverage Trader Regret: Stickman Pain! 💀💸",
            "How to Launch an ERC-20 Token Without Coding! 🪙⚡",
            "Bull vs Bear Market Madness: The Trader Rollercoaster! 🐂🐻"
        ],
        "engagement_comments": [
            "💸 Have you ever been liquidated on high leverage? Share your funniest trading story! 👇😭",
            "🚀 Ready to create your own token on Polygon? Check out PolyMint in description! 💎",
            "📉 Are we in a Bull or Bear market right now? Drop 🐂 or 🐻 below!"
        ],
        "description_triad": (
            "🚀 Experience the future of decentralized Web3 tokenization on Polygon!\n\n"
            "💎 Official PolyMint Token Factory Platform: https://ploymint.polyganfactorytoken.workers.dev\n"
            "✨ Create, deploy, and manage your own custom ERC-20 tokens on Polygon without writing a single line of code!\n\n"
            "🔥 Subscribe to CryptoLab for daily trading comedy, Web3 tools, and Polygon ecosystem updates!\n\n"
            "─── ⋆⋅☆⋅⋆ ───\n"
            "#Crypto #Polygon #PolyMint #Web3 #Trading #Bitcoin #Ethereum #Stickman #Shorts #Viral"
        ),
        "two_tower_tags": [
            "Crypto", "Polygon", "PolyMint", "Web3", "Token", "ERC20", "Trading",
            "Stickman Animation", "Bitcoin", "Ethereum", "Trading Humor", "Shorts", "Viral"
        ]
    }
}

# ==============================================================================
# 165 MEGA-ENGINE CORE FUNCTIONS
# ==============================================================================

def generate_165_mega_title(niche: str, raw_title: str = None, run_count: int = 1) -> str:
    """
    Applies Protocols T001 to T025 & T035:
    - Curiosity Gap & Pattern Interrupt
    - Strict 50-68 character sweetspot for YouTube Shorts mobile UI
    - High-velocity emojis and #Shorts anchor
    """
    config = NICHE_PROMPT_PATTERNS.get(niche, NICHE_PROMPT_PATTERNS["animals"])

    clean_raw = ""
    if raw_title:
        # Strip preexisting hashtags and extraneous punctuation
        clean_raw = re.sub(r"[#＃][\w\d_]+", "", raw_title).strip()
        clean_raw = re.sub(r"\s+", " ", clean_raw)

    if niche == "quran":
        # 100% Authentic Arabic Title only for global Islamic algorithm reach
        hooks = config.get("title_hooks_arabic", config["title_hooks_arabic"])
        hook = hooks[run_count % len(hooks)]
        tag = "#Shorts #Quran" 

        if clean_raw and len(clean_raw) > 5 and not any(k in clean_raw.lower() for k in ["http", "mp4", "www"]):
            from metadata_optimizer import build_title_with_suffix
            title = build_title_with_suffix(f"{hook} | {clean_raw}", tag)
        else:
            title = f"{hook} {tag}"

    else:
        hooks = config.get("title_hooks", ["Mind-Blowing Truth! 😱"])
        hook = hooks[run_count % len(hooks)]
        niche_tag = f"#Shorts #{niche.capitalize()}"

        if clean_raw and len(clean_raw) > 5 and not any(k in clean_raw.lower() for k in ["http", "mp4", "www"]):
            from metadata_optimizer import build_title_with_suffix
            title = build_title_with_suffix(f"{hook} - {clean_raw}", niche_tag)
        else:
            title = f"{hook} {niche_tag}"

    # Enforce strict length constraint (T035: under 70 characters for mobile display)
    # Old logic cut titles mid-word ("Sura #Shor.."). Trim at word boundaries, <=100 chars.
    from metadata_optimizer import smart_truncate
    return smart_truncate(title, 100)

def generate_165_mega_description(niche: str, channel_key: str = None) -> str:
    """
    Applies Protocols T029 (Semantic Triad) and T133 (Official Platform Gateway).
    """
    config = NICHE_PROMPT_PATTERNS.get(niche, NICHE_PROMPT_PATTERNS["animals"])
    return config.get("description_triad", "Viral high-retention Short #Shorts #Viral")

def generate_165_algorithmic_tags(niche: str, winning_keywords: List[str] = None) -> List[str]:
    """
    Applies Protocols T028 (Dual-Embedding Tagging) and T046 (Tag Cloud Concentration):
    Combines core umbrella tags with learned high-velocity keywords.
    """
    config = NICHE_PROMPT_PATTERNS.get(niche, NICHE_PROMPT_PATTERNS["animals"])
    base_tags = list(config.get("two_tower_tags", ["Shorts", "Viral"]))

    if winning_keywords:
        for kw in winning_keywords:
            if kw and len(kw) > 3 and kw not in base_tags and len(base_tags) < 18:
                base_tags.append(kw)

    return base_tags[:16]

def generate_165_pinned_comment(niche: str, run_count: int = 1) -> str:
    """
    Applies Protocols T096 (Comment-Bait Dilemma), T099 (Blessing Anchor), and T103.
    Drives comment velocity within first 60 minutes to push video into broader recommendation pools.
    """
    config = NICHE_PROMPT_PATTERNS.get(niche, NICHE_PROMPT_PATTERNS["animals"])
    comments = config.get("engagement_comments", ["What are your thoughts on this? Comment below! 👇"])
    return comments[run_count % len(comments)]

def get_165_adaptive_query(niche: str, run_count: int, winning_topics: List[str] = None) -> Tuple[str, str]:
    """
    Applies Protocols T026, T030, T157, and T160:
    Dynamically generates high-velocity YouTube search query and in-video hook banner,
    incorporating real learned winning tokens from channel audits.
    """
    # 1. Check if winning keywords exist in brain
    winner = None
    if winning_topics and len(winning_topics) > 0:
        # Pick top winner
        winner = random.choice(winning_topics[:5])

    if niche == "quran":
        queries = [
            ("تلاوة خاشعة تريح القلب قرآن كريم", "تلاوة خاشعة تريح القلوب 🕊️"),
            ("سورة يس الرحمن الواقعة تلاوة خاشعة", "راحة نفسية لا توصف 🌿"),
            ("اجمل تلاوة قران كريم في العالم راحة نفسية", "استمع بقلبك 🤍✨"),
            ("تلاوة مبكية تهز القلوب قرآن كريم", "سكينة وطمأنينة 🕊️")
        ]
        if winner and len(winner) > 3:
            return (f"{winner} تلاوة خاشعة قرآن كريم", f"{winner} 🕊️ راحة نفسية")
        return queries[run_count % len(queries)]

    elif niche == "islamic_mystery":
        queries = [
            ("Dajjal signs coming true end times towards eternity shorts", "SIGNS COMING TRUE ⚠️"),
            ("Signs of the day of judgment happening right now shorts", "FINAL HOUR SIGNS ⚡"),
            ("What happens in the grave towards eternity islamic reminder", "THE GRAVE REALITY 😱"),
            ("The untold mystery of Tamim Al Dari island Dajjal", "THE SECRET ISLAND 🏝️⚠️")
        ]
        if winner:
            return (f"{winner} signs coming true end times shorts", f"{winner.upper()} ⚠️")
        return queries[run_count % len(queries)]

    elif niche == "ai":
        queries = [
            ("ai stickman animation funny shorts", "AI TAKES OVER! 🤖⚡"),
            ("robot vs stickman funny viral animation shorts", "HUMAN VS MACHINE 🦾💥"),
            ("programmer bug fixing stickman animation shorts", "CODE BREAKS AT 3AM 💻😭"),
            ("future technology 2026 stickman animation shorts", "FUTURE TECH 2026 🚀🤯"),
            ("ai tools that feel illegal to know shorts", "MIND-BLOWING AI ⚡")
        ]
        if winner:
            clean_w = re.sub(r"\b(stickman|animation|viral|shorts)\b", "", winner, flags=re.IGNORECASE).strip()
            clean_w = clean_w if clean_w else winner
            return (f"stickman {clean_w} animation viral shorts", f"{clean_w.upper()[:22]} 🤖⚡")
        return queries[run_count % len(queries)]

    elif niche == "animals":
        queries = [
            ("stickman vs wild animals animation shorts", "STICKMAN SURVIVAL 🦁⚠️"),
            ("stickman animal attack funny animation shorts", "NEVER MESS WITH ANIMALS! 😱🐾"),
            ("stickman dinosaur prehistoric survival shorts", "JURASSIC ESCAPE! 🦖🔥"),
            ("stickman vs honey badger bear animals shorts", "NATURE'S DEADLIEST BEAST 🦡⚡"),
            ("crow memory intelligent animal stickman shorts", "CROW 200 IQ MOMENT 🦅🧠")
        ]
        if winner:
            clean_w = re.sub(r"\b(stickman|animation|viral|shorts)\b", "", winner, flags=re.IGNORECASE).strip()
            clean_w = clean_w if clean_w else winner
            return (f"stickman {clean_w} animation viral shorts", f"{clean_w.upper()[:22]} 🐾🔥")
        return queries[run_count % len(queries)]

    elif niche == "cryptolab":
        queries = [
            ("crypto stickman animation funny shorts", "TRADER LIQUIDATED 😭💸"),
            ("bitcoin trading stickman funny animation", "BUY THE DIP THEY SAID! 📉💥"),
            ("stickman crypto millionaire animation shorts", "100X LEVERAGE REGRET 💀💎"),
            ("trading emotional roller coaster stickman", "BULL VS BEAR MADNESS 🐂🐻")
        ]
        if winner:
            clean_w = re.sub(r"\b(stickman|animation|viral|shorts|crypto)\b", "", winner, flags=re.IGNORECASE).strip()
            clean_w = clean_w if clean_w else winner
            return (f"crypto stickman {clean_w} funny animation shorts", f"{clean_w.upper()[:22]} 💸")
        return queries[run_count % len(queries)]

    return ("viral animation shorts", "WATCH TILL END! ⚡")

def audit_monetization_safety_165(title: str, description: str, tags: List[str]) -> Tuple[bool, List[str]]:
    """
    Applies Protocols T121 to T140:
    Strict Pre-Upload Policy Gate verifying 100% compliance with YouTube Advertiser-Friendly Guidelines.
    """
    violations = []

    # Advertiser-Unfriendly Keyword Blacklist
    blacklist = [
        "suicide", "murder", "terror", "blood", "gore", "weapon", "drugs",
        "porn", "sex", "kill", "death penalty", "torture", "hack credit card"
    ]

    full_text = f"{title} {description} {' '.join(tags)}".lower()
    for word in blacklist:
        if re.search(r"\b" + re.escape(word) + r"\b", full_text):
            violations.append(f"Forbidden advertiser-unfriendly word detected: '{word}'")

    # Repetitive metadata spam check (T136)
    words = title.split()
    for w in set(words):
        if len(w) > 3 and words.count(w) > 3:
            violations.append(f"Excessive keyword repetition in title: '{w}'")

    is_safe = len(violations) == 0
    return is_safe, violations