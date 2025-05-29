import json
import os
import requests
from services.control.provider_router import load_config, get_available_provider

SUMMARY_INPUT = "data/meta/sample_job/chunk-meta.json"
SUMMARY_OUTPUT = "data/meta/sample_job/meta-summary.json"

API_ENDPOINTS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages"
}

def load_metadata(path):
    with open(path, "r") as f:
        return json.load(f)

def save_summary(path, summary):
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)

def query_llm(provider, api_key, metadata):
    headers = {"Content-Type": "application/json"}
    prompt_text = f"Analyze and summarize:
{json.dumps(metadata)}"

    if provider == "gemini":
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt_text}]
            }]
        }
        url = f"{API_ENDPOINTS[provider]}?key={api_key}"

    elif provider == "openrouter":
        payload = {
            "model": "claude-3-haiku",
            "messages": [{"role": "user", "content": prompt_text}]
        }
        headers["Authorization"] = f"Bearer {api_key}"
        url = API_ENDPOINTS[provider]

    elif provider == "openai":
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt_text}]
        }
        headers["Authorization"] = f"Bearer {api_key}"
        url = API_ENDPOINTS[provider]

    elif provider == "anthropic":
        headers.update({
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        })
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt_text}]
        }
        url = API_ENDPOINTS[provider]

    else:
        raise NotImplementedError(f"Provider '{provider}' not implemented.")

    response = requests.post(url, json=payload, headers=headers)
    if not response.ok:
        raise RuntimeError(f"{provider} API error: {response.status_code} {response.text}")

    # Output handling
    try:
        if provider == "gemini":
            return json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
        elif provider == "openrouter":
            return response.json()["choices"][0]["message"]["content"]
        elif provider == "openai":
            return response.json()["choices"][0]["message"]["content"]
        elif provider == "anthropic":
            return response.json()["content"][0]["text"]
    except Exception as e:
        return {"error": f"Failed to parse LLM response: {str(e)}"}

# Main logic
if __name__ == "__main__":
    cfg = load_config()
    try:
        provider, key = get_available_provider(cfg)
        print(f"Using provider: {provider}")
        meta = load_metadata(SUMMARY_INPUT)
        result = query_llm(provider, key, meta)
        save_summary(SUMMARY_OUTPUT, result)
    except Exception as e:
        print(f"Fallback failed: {e}")
