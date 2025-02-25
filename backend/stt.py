import logging
import os
import shutil
import time
import uuid
import json
import wave

import ffmpeg
# Keep OpenAI import for backward compatibility
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import Vosk for local STT
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

from util import delete_file

LANGUAGE = os.getenv("LANGUAGE", "en")
STT_PROVIDER = os.getenv("STT_PROVIDER", "openai").lower()  # Options: 'openai' or 'vosk'
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "/app/vosk-model")

async def transcribe(audio):
    start_time = time.time()
    initial_filepath = f"/tmp/{uuid.uuid4()}{audio.filename}"

    with open(initial_filepath, "wb+") as file_object:
        shutil.copyfileobj(audio.file, file_object)

    converted_filepath = f"/tmp/ffmpeg-{uuid.uuid4()}{audio.filename}"

    logging.debug("running through ffmpeg")
    (
        ffmpeg
        .input(initial_filepath)
        .output(converted_filepath, format="wav", acodec="pcm_s16le", ac=1, ar=16000, loglevel="error")
        .run()
    )
    logging.debug("ffmpeg done")

    delete_file(initial_filepath)

    logging.info(f"Using STT provider: {STT_PROVIDER}")
    if STT_PROVIDER == "vosk":
        if not VOSK_AVAILABLE:
            raise ImportError("Vosk package is not installed but STT_PROVIDER is set to 'vosk'")
        return await _vosk_transcribe(converted_filepath, start_time)
    else:
        # Default to OpenAI
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package is not installed but STT_PROVIDER is set to 'openai'")
        return await _openai_transcribe(converted_filepath, start_time)

async def _openai_transcribe(audio_filepath, start_time):
    read_file = open(audio_filepath, "rb")

    logging.debug("calling whisper")
    transcription = (await openai.Audio.atranscribe("whisper-1", read_file, language=LANGUAGE))["text"]
    logging.info("STT response received from whisper in %s %s", time.time() - start_time, 'seconds')
    logging.info('user prompt: %s', transcription)

    delete_file(audio_filepath)

    return transcription

async def _vosk_transcribe(audio_filepath, start_time):
    if not os.path.exists(VOSK_MODEL_PATH):
        logging.warning(f"Vosk model not found at {VOSK_MODEL_PATH}. Please download a model from https://alphacephei.com/vosk/models")
        raise FileNotFoundError(f"Vosk model not found at {VOSK_MODEL_PATH}")
    
    logging.info(f"Loading Vosk model from {VOSK_MODEL_PATH}")
    try:
        model = Model(VOSK_MODEL_PATH)
        logging.debug("Vosk model loaded successfully")
        
        wf = wave.open(audio_filepath, "rb")
        logging.debug(f"Audio file opened: {audio_filepath}, rate={wf.getframerate()}")
        
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        results = []
        data_chunks_processed = 0
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            data_chunks_processed += 1
            if rec.AcceptWaveform(data):
                results.append(rec.Result())
        
        results.append(rec.FinalResult())
        logging.debug(f"Processed {data_chunks_processed} audio chunks")
        
        # Parse the JSON results
        all_text = ""
        for res in results:
            res_json = json.loads(res)
            if "text" in res_json:
                all_text += res_json["text"] + " "
        
        transcription = all_text.strip()
        
        logging.info("STT response received from Vosk in %s %s", time.time() - start_time, 'seconds')
        logging.info('user prompt: %s', transcription)
        
        delete_file(audio_filepath)
        
        return transcription
    except Exception as e:
        logging.error(f"Error during Vosk speech recognition: {e}")
        raise
