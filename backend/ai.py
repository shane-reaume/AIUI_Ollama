import base64
import json
import logging
import os
import time

import httpx

# Configure AI provider - force Ollama only
AI_PROVIDER = "ollama"  # Only option now: 'ollama'
AI_COMPLETION_MODEL = os.getenv("AI_COMPLETION_MODEL", "llama3:8b")
LANGUAGE = os.getenv("LANGUAGE", "en")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

INITIAL_PROMPT = f"""You are a confidant assistant with a voice interface so respond in a natural conversational tone, speaking in the language that corresponds 
to the ISO-639-1 code: {LANGUAGE} and utilizes Interactive Engagement as this should be a conversation."""

async def get_completion(user_prompt, conversation_thus_far):
    if _is_empty(user_prompt):
        raise ValueError("empty user prompt received")

    start_time = time.time()
    messages = [
        {
            "role": "system",
            "content": INITIAL_PROMPT
        }
    ]

    messages.extend(json.loads(base64.b64decode(conversation_thus_far)))
    messages.append({"role": "user", "content": user_prompt})

    # Only use Ollama for completion
    return await _get_ollama_completion(messages, start_time)

async def _get_ollama_completion(messages, start_time):
    logging.debug("calling Ollama model %s at %s", AI_COMPLETION_MODEL, OLLAMA_HOST)
    
    # For Ollama v0.5.11, we need to use the generate endpoint with a flat prompt
    try:
        # First check if the Ollama server is available
        async with httpx.AsyncClient() as client:
            try:
                # Check server is up
                version_check = await client.get(f"{OLLAMA_HOST}/api/version", timeout=5.0)
                version_check.raise_for_status()
                version_data = version_check.json()
                logging.info(f"Connected to Ollama server, version: {version_data.get('version', 'unknown')}")
            except Exception as e:
                logging.error(f"Error connecting to Ollama server: {e}")
                raise ConnectionError(f"Could not connect to Ollama server at {OLLAMA_HOST}: {e}")
            
            # Build prompt from messages
            prompt = ""
            for msg in messages:
                role_prefix = "User: " if msg["role"] == "user" else "Assistant: "
                if msg["role"] == "system":
                    prompt += f"{msg['content']}\n\n"
                else:
                    prompt += f"{role_prefix}{msg['content']}\n"
            
            # Add final prompt ending
            prompt += "Assistant: "
            
            # Send generate request
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": AI_COMPLETION_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            completion = result["response"]
            logging.info("Response received from Ollama %s in %s seconds", AI_COMPLETION_MODEL, time.time() - start_time)
            logging.info('Ollama %s response: %s', AI_COMPLETION_MODEL, completion)
            
            return completion
            
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error with Ollama API call: {e}")
        if e.response.status_code == 404:
            logging.error(f"API endpoint not found. Check your Ollama version.")
        elif e.response.status_code == 400:
            logging.error(f"Bad request: {e.response.text}")
        raise
    except Exception as e:
        logging.error(f"Error calling Ollama: {e}")
        raise

def _is_empty(user_prompt: str):
    return not user_prompt or user_prompt.isspace()
