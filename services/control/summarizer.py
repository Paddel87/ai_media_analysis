import json
import os
import requests

SUMMARY_INPUT = "data/meta/sample_job/chunk-meta.json"
SUMMARY_OUTPUT = "data/meta/sample_job/meta-summary.json"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def load_metadata(path):
    with open(path, "r") as f:
        return json.load(f)

def save_summary(path, summary):
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)

def summarize(metadata):
    prompt = {
        "contents": [{
            "role": "user",
            "parts": [{
                "text": f"""Analyze the following metadata and summarize:
- Identify sexual acts, body positions, emotions, presence of bondage or restraints
- List recognized persons and suggest labels
- Return result as structured JSON

METADATA:
{json.dumps(metadata)}"""
            }]
        }]
    }

    response = requests.post(
        f"{API_URL}?key={GEMINI_API_KEY}",
        json=prompt
    )

    if response.ok:
        reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(reply)
    else:
        raise Exception(f"LLM Error: {response.text}")

# Main logic
if __name__ == "__main__":
    meta = load_metadata(SUMMARY_INPUT)
    summary = summarize(meta)
    save_summary(SUMMARY_OUTPUT, summary)
    print(f"Saved summary to: {SUMMARY_OUTPUT}")
