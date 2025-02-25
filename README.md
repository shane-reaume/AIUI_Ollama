![AIUI Ollama Logo]("./AIUI_Ollama.png")

# A Private Voice Interface for AI

> This project is based on [AIUI by lspahija](https://github.com/lspahija/AIUI), modified to run completely locally without any cloud dependencies.

Point-and-click user interfaces will soon be a thing of the past. The main user interface of the near future will be entirely voice-based.

AIUI is a platform that enables seamless two-way verbal communication with AI models. It works in both desktop and mobile browsers and now runs entirely on your local network with:

- **[Ollama](https://ollama.ai/)** for AI model inference
- **[Vosk](https://alphacephei.com/vosk/)** for local speech recognition
- **[EdgeTTS](https://github.com/rany2/edge-tts)** for local text-to-speech

No data leaves your network, providing a completely private AI assistant experience.

## Usage
To interact with AIUI, simply start speaking after navigating to the app in your browser. AIUI will listen to your voice input, process it using your local Ollama instance, and provide a synthesized speech response. You can have a natural, continuous conversation with the AI by speaking and listening to its responses.

## Prerequisites
- Docker and Docker Compose
- An [Ollama](https://ollama.ai/) instance running on your local network
- One or more Ollama models pulled to your server

## Quick Start
1. Clone the repo
```bash
git clone git@github.com:lspahija/AIUI.git
```

2. Change directory to AIUI
```bash
cd AIUI
```

3. Edit the `docker-compose.yml` file to point to your Ollama server
```yaml
environment:
  - OLLAMA_HOST=http://your-ollama-server:11434  # Change this to your Ollama host
  - AI_COMPLETION_MODEL=deepseek-r1:8b  # Change this to your preferred model
```

4. Start the container with Docker Compose
```bash
docker-compose up -d
```

5. Navigate to `localhost:8000` in a modern browser

## Configuration Options

### AI Provider
- `AI_PROVIDER`: Set to "ollama" to use Ollama locally
- `OLLAMA_HOST`: The URL of your Ollama instance
- `AI_COMPLETION_MODEL`: The name of the model to use (e.g., "deepseek-r1:8b")

### Speech-to-Text
- `STT_PROVIDER`: Set to "vosk" for local speech recognition
- `VOSK_MODEL_PATH`: Path to the Vosk model (default is set in the Docker image)

### Text-to-Speech
- `TTS_PROVIDER`: Set to "EDGETTS" for local text-to-speech
- `EDGETTS_VOICE`: The voice to use (e.g., "en-US-EricNeural")
- `LANGUAGE`: ISO-639-1 language code (default: "en")

## Troubleshooting

If you're having issues connecting to your Ollama server, you can use the included utility script:

```bash
./check_ollama.py --host http://your-ollama-server:11434
```

For more detailed setup and configuration options, see [LOCAL_SETUP.md](LOCAL_SETUP.md).

## Find this useful?
Please star both this repository and the [original AIUI repository](https://github.com/lspahija/AIUI)! It helps contributors gauge the popularity of the repo and determine how much time to allot to development.
