import os
import json

CONFIG_PATH = "services/control/llm_config.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def get_available_provider(config):
    for name in config["fallback_order"]:
        provider = config["providers"].get(name)
        if provider and provider["enabled"] and os.getenv(provider["api_key_env"]):
            return name, os.getenv(provider["api_key_env"])
    raise RuntimeError("No available LLM provider found.")

if __name__ == "__main__":
    cfg = load_config()
    provider, key = get_available_provider(cfg)
    print(f"Using provider: {provider} (key present: {'yes' if key else 'no'})")
