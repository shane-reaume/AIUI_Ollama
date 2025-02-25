#!/usr/bin/env python3
"""
A simple utility script to check if an Ollama server is accessible
and list the available models.
"""

import json
import sys
import argparse
import requests
from urllib.parse import urlparse

def check_ollama(host):
    """Check if Ollama server is accessible and list available models."""
    # Make sure the host has a scheme
    if not urlparse(host).scheme:
        host = f"http://{host}"
    
    # Ensure the host has a port
    if urlparse(host).port is None:
        host = f"{host}:11434"
    
    print(f"Checking Ollama server at {host}")
    
    try:
        # Check version
        version_url = f"{host}/api/version"
        version_response = requests.get(version_url, timeout=5)
        version_response.raise_for_status()
        version_data = version_response.json()
        print(f"✅ Connected to Ollama server, version: {version_data.get('version', 'unknown')}")
        
        # List models
        models_url = f"{host}/api/tags"
        models_response = requests.get(models_url, timeout=5)
        models_response.raise_for_status()
        models_data = models_response.json()
        
        if 'models' in models_data and models_data['models']:
            print("\nAvailable models:")
            print("=================")
            for model in models_data['models']:
                print(f"- {model['name']}")
                if 'details' in model and model['details']:
                    details = model['details']
                    if 'parameter_size' in details:
                        print(f"  Size: {details['parameter_size']}")
                    if 'family' in details:
                        print(f"  Family: {details['family']}")
                print()
        else:
            print("No models found on the server.")
        
        # Test a simple completion
        print("\nTesting a simple completion...")
        try:
            test_model = models_data['models'][0]['name'] if 'models' in models_data and models_data['models'] else "unknown"
            generate_url = f"{host}/api/generate"
            generate_data = {
                "model": test_model,
                "prompt": "Say hello",
                "stream": False
            }
            generate_response = requests.post(generate_url, json=generate_data, timeout=10)
            generate_response.raise_for_status()
            generate_result = generate_response.json()
            print(f"✅ Generated response from model {test_model}")
            print(f"Response: {generate_result.get('response', '')[:100]}...")
        except Exception as e:
            print(f"❌ Error testing completion: {e}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to Ollama server at {host}")
        print("Make sure the server is running and accessible from this machine.")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Ollama server and list available models")
    parser.add_argument("--host", default="http://localhost:11434", help="Ollama host URL (default: http://localhost:11434)")
    args = parser.parse_args()
    
    success = check_ollama(args.host)
    sys.exit(0 if success else 1) 