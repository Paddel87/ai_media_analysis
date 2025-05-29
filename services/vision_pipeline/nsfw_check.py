import os
import json
import random

INPUT_FOLDER = "data/objects/sample_job"
OUTPUT_FILE = "data/meta/sample_job/nsfw_scores.json"

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

results = {}

# Dummy NSFW estimator
def fake_nsfw_score():
    return round(random.uniform(0.0, 1.0), 2)

# Process each cropped image
for img_file in sorted(os.listdir(INPUT_FOLDER)):
    if not img_file.endswith((".jpg", ".png", ".webp")):
        continue
    score = fake_nsfw_score()
    results[img_file] = score
    print(f"{img_file} → NSFW score: {score}")

# Write results to JSON
with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"Saved NSFW scores to: {OUTPUT_FILE}")
