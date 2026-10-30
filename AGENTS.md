# STRICT AGENT ISOLATION DIRECTIVE: QURAN YOUTUBE CHANNEL

## ⛔ CRITICAL WORKSPACE IMMUNITY RULE:
The YouTube channel `نور القرآن | The Holy Light` (account `iman996372@gmail.com`, token `token_quran.pickle`) is **EXCLUSIVELY AND STRICTLY CONTROLLED BY THE DEDICATED MASTER QURAN SESSION**.

1. **NO OTHER SESSION OR AGENT** (including AI channel, Automotive channel, CryptoLab, or Persian Instagram pipelines) is permitted to:
   - Call `upload_short(channel_key="quran", ...)` or access `token_quran.pickle`.
   - Modify, block, or delete any Quran videos.
   - Create standalone scripts that upload to the Quran channel (e.g. `upload_quran_youtube.py`).
   - Overwrite or mutate Quran channel titles, descriptions, or tags.

2. **ENFORCEMENT:**
   - Any script not explicitly authorized by the Master Quran Dispatcher (`dispatch_cycle.py`) with `QURAN_MASTER_SESSION_AUTH='AUTHORIZED_786'` will be **BLOCKED INSTANTLY** by the security gate in `youtube_uploader.py`.
   - All other sessions must focus strictly on their designated channel keys (`"cars"`, `"ai"`, `"polygon"`, `"animals"`).

## Content mode (original Shorts by default)
`dispatch_cycle.py` now publishes ORIGINAL generated Shorts for the Quran and AI channels via `original_shorts.py`
(Quran: owned recitation clips in `assets/audio` + `data/quran_ayahs.json`; AI: script + TTS + kinetic captions + generated visuals).
The legacy Instagram reel re-upload path is disabled unless `ENABLE_REEL_REUPLOAD=true` is set — do not re-enable it
(unmodified re-uploads risk "reused content" rejection and copyright strikes).
