# AIUI Local Setup with Ollama

This document describes how to run AIUI locally without any cloud dependencies using [Ollama](https://ollama.ai/) for AI completions and [Vosk](https://alphacephei.com/vosk/) for speech recognition.

## Prerequisites

1. **Docker**: Make sure you have Docker installed on your system.
2. **Ollama**: Either running on your local machine or on another computer in your network.

## Quick Start with Docker Compose

```bash
# Start AIUI with default configuration
docker-compose up -d
```

This will start AIUI on http://localhost:8000 using the configuration defined in docker-compose.yml.

## Configuration Options

The following environment variables can be set in docker-compose.yml:

### AI Provider
- `AI_PROVIDER`: Set to "ollama" to use Ollama (or "openai" to use OpenAI)
- `OLLAMA_HOST`: The URL of your Ollama instance (e.g., "http://localhost:11434")
- `AI_COMPLETION_MODEL`: The name of the model to use (e.g., "deepseek-r1:8b")

### Speech-to-Text
- `STT_PROVIDER`: Set to "vosk" for local speech recognition (or "openai" to use OpenAI Whisper)
- `VOSK_MODEL_PATH`: Path to the Vosk model inside the container (default: "/app/vosk-model")

### Text-to-Speech
- `TTS_PROVIDER`: Options include "EDGETTS", "gTTS", "ELEVENLABS", or "STREAMELEMENTS"
- `EDGETTS_VOICE`: The voice to use with Edge TTS (default: "en-US-EricNeural")
- `LANGUAGE`: The ISO-639-1 language code (default: "en")

## Available Ollama Models

To view available models on your Ollama instance:

```bash
curl http://YOUR_OLLAMA_HOST:11434/api/tags
```

## Troubleshooting

### Connection Issues
If you can't connect to your Ollama instance, check:
1. The correct URL is specified in `OLLAMA_HOST`
2. The Ollama server is running
3. Network connectivity between Docker and the Ollama server
4. Firewall settings

### Speech Recognition Issues
If speech recognition isn't working:
1. Check logs with `docker logs <container_id>`
2. Verify the Vosk model was downloaded correctly
3. Try adjusting your microphone settings

## Building Custom Docker Image

```bash
docker build -t aiui:custom .
```

## Running without Docker Compose

```bash
docker run -d \
  -e AI_PROVIDER=ollama \
  -e OLLAMA_HOST=http://192.168.0.55:11434 \
  -e AI_COMPLETION_MODEL=deepseek-r1:8b \
  -e STT_PROVIDER=vosk \
  -e TTS_PROVIDER=EDGETTS \
  -e EDGETTS_VOICE=en-US-EricNeural \
  -p 8000:80 \
  aiui
``` 