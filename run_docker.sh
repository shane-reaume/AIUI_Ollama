#!/bin/bash

# Script to build and run the AIUI Docker container

# Build the Docker image
echo "Building the Docker image..."
docker build -t aiui .

# Run the container
echo "Running the container..."
docker run -d \
  -e AI_PROVIDER=ollama \
  -e OLLAMA_HOST=http://192.168.0.55:11434 \
  -e AI_COMPLETION_MODEL=deepseek-r1:8b \
  -e STT_PROVIDER=vosk \
  -e TTS_PROVIDER=EDGETTS \
  -e EDGETTS_VOICE=en-US-EricNeural \
  -p 8000:80 \
  --name aiui \
  aiui

echo "AIUI should now be accessible at http://localhost:8000"
echo "To view logs: docker logs -f aiui"
echo "To stop: docker stop aiui && docker rm aiui" 