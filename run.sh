#!/bin/bash
set -e

CONTAINER_LABEL="created_by=aiui_script"

# Only include local TTS options
TTS_OPTIONS=("EDGETTS")

check_env_var() {
    if [[ -z "${!1}" ]]; then
        echo "Error: $1 is not set."
        exit 1
    fi
}

remove_containers() {
    if [ "$(docker ps -a -q -f "label=$1")" ]; then
        docker rm -f $(docker ps -a -q -f "label=$1")
    fi
}

build_docker() {
    ARCH=$(uname -m)
    if [ "$ARCH" == "arm64" ]; then
        docker buildx build --platform linux/arm64 -t aiui .
    else
        docker build -t aiui .
    fi
}

run_docker() {
    if [ "$1" == "EDGETTS" ]; then
        docker run -d -e AI_PROVIDER=ollama -e OLLAMA_HOST=${OLLAMA_HOST:-http://localhost:11434} -e AI_COMPLETION_MODEL=${AI_COMPLETION_MODEL:-deepseek-r1:8b} -e TTS_PROVIDER=EDGETTS -e EDGETTS_VOICE=${EDGETTS_VOICE:-en-US-EricNeural} -e STT_PROVIDER=vosk -p 8000:80 --label "$CONTAINER_LABEL" aiui
    else
        echo "Invalid argument. Please provide one of the following:"
        for i in "${TTS_OPTIONS[@]}"
        do
            echo "$i"
        done
        exit 1
    fi
}

# No longer need to check for OpenAI API key
remove_containers "$CONTAINER_LABEL"
build_docker
run_docker "${1:-EDGETTS}"  # Default to EDGETTS if no argument provided
