import asyncio
import time
import subprocess
from pathlib import Path
import edge_tts
from gtts import gTTS
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

VOICE_MAP = {
    "en": "en-US-ChristopherNeural",
    "fa": "fa-IR-FaridNeural",
    "ar": "ar-SA-HamedNeural",
    "es": "es-ES-AlvaroNeural",
    "de": "de-DE-KillianNeural"
}

GTTS_LANG_MAP = {
    "en": "en",
    "fa": "fa",
    "ar": "ar",
    "es": "es",
    "de": "de"
}

async def _edge_tts_call(text: str, voice: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_speech(text: str, language: str, output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    lang_key = language.lower()
    voice = VOICE_MAP.get(lang_key, "en-US-ChristopherNeural")
    
    # 1. Try edge-tts with 2 retries
    for attempt in range(2):
        try:
            asyncio.run(asyncio.wait_for(_edge_tts_call(text, voice, output_path), timeout=25.0))
            if Path(output_path).exists() and Path(output_path).stat().st_size > 500:
                return output_path
        except Exception as e:
            print(f"    [TTS Warning] edge-tts attempt {attempt+1} failed: {e}")
            time.sleep(1)

    # 2. Fallback to gTTS
    try:
        print(f"    [TTS Info] Falling back to gTTS for language: {lang_key}")
        gtts_lang = GTTS_LANG_MAP.get(lang_key, "en")
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(output_path)
        if Path(output_path).exists() and Path(output_path).stat().st_size > 500:
            return output_path
    except Exception as e:
        print(f"    [TTS Warning] gTTS fallback failed: {e}")

    # 3. Emergency fallback: generate 10s silent audio with ffmpeg so pipeline continues
    print("    [TTS Alert] Generating emergency audio track...")
    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "10",
        "-q:a", "9",
        "-acodec", "libmp3lame",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path
