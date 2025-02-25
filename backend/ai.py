import base64
import json
import logging
import os
import time

import httpx
# Keep OpenAI import for backward compatibility
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure AI provider
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()  # Options: 'openai' or 'ollama'
AI_COMPLETION_MODEL = os.getenv("AI_COMPLETION_MODEL", "gpt-3.5-turbo")
LANGUAGE = os.getenv("LANGUAGE", "en")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

INITIAL_PROMPT = f"""
You are AIUI - a helpful assistant with a voice interface. Always provide your responses in the language that corresponds 
to the ISO-639-1 code: {LANGUAGE} and utilize Memory Palace Technique (Spatial Memory) to assist the user. e Respond in natural 
spoken language without using special tokens, formatting marks, or indicating who is speaking. 
Never use tokens like <thinking> or character names.
"""

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

    if AI_PROVIDER == "ollama":
        return await _get_ollama_completion(messages, start_time)
    else:
        # Default to OpenAI
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package is not installed but AI_PROVIDER is set to 'openai'")
        return await _get_openai_completion(messages, start_time)

async def _get_openai_completion(messages, start_time):
    logging.debug("calling OpenAI model %s", AI_COMPLETION_MODEL)
    res = await openai.ChatCompletion.acreate(model=AI_COMPLETION_MODEL, messages=messages, timeout=15)
    logging.info("response received from %s %s %s %s", AI_COMPLETION_MODEL, "in", time.time() - start_time, "seconds")

    completion = res['choices'][0]['message']['content']
    logging.info('%s %s %s', AI_COMPLETION_MODEL, "response:", completion)

    return completion

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
