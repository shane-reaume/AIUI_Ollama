import logging
import os
import time
import uuid

# Get TTS provider configuration first
LANGUAGE = os.getenv("LANGUAGE", "en")
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "EDGETTS")

# Only import what's actually needed based on the provider
import edge_tts  # Always import edge_tts since it's our default/only supported provider now
from util import delete_file

# Unused settings kept for backwards compatibility
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", None)
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE", "EXAVITQu4vr4xnSDxMaL")
EDGETTS_VOICE = os.getenv("EDGETTS_VOICE", "en-US-EricNeural")


async def to_speech(text, background_tasks):
    if TTS_PROVIDER == "EDGETTS":
        return await _edge_tts_to_speech(text, background_tasks)
    else:
        # Force EdgeTTS if an invalid provider is specified
        logging.warning(f"Unsupported TTS_PROVIDER: {TTS_PROVIDER}. Falling back to EdgeTTS.")
        return await _edge_tts_to_speech(text, background_tasks)


async def _edge_tts_to_speech(text, background_tasks):
    start_time = time.time()

    communicate = edge_tts.Communicate(text, EDGETTS_VOICE)
    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    await communicate.save(filepath)

    background_tasks.add_task(delete_file, filepath)

    logging.info('TTS time: %s %s', time.time() - start_time, 'seconds')
    return filepath

# Function references for other TTS providers are removed since we're only supporting EdgeTTS
