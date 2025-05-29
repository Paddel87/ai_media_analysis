import streamlit as st
import os
import json
from PIL import Image

DATA_PATH = "data/objects"
FEEDBACK_FILE = "data/operator/review_log.jsonl"

st.title("AI Media Analysis – Manual Object Review")

# Helper: write to feedback file
def save_feedback(filename, selected_label, custom_label):
    entry = {
        "filename": filename,
        "chosen_label": custom_label if custom_label else selected_label
    }
    with open(FEEDBACK_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

# Load object images from job folders
job_dirs = sorted(os.listdir(DATA_PATH))
if not job_dirs:
    st.info("No objects found for review.")
    st.stop()

for job in job_dirs:
    job_path = os.path.join(DATA_PATH, job)
    images = [f for f in os.listdir(job_path) if f.endswith((".jpg", ".png", ".webp"))]
    if not images:
        continue

    st.subheader(f"Job: {job}")
    for img_file in images:
        img_path = os.path.join(job_path, img_file)
        st.image(Image.open(img_path), caption=img_file, width=300)

        suggested_labels = ["rope", "gag", "mask", "unknown"]

        selected = st.selectbox(f"Suggested labels for {img_file}", suggested_labels, key=img_file)
        custom = st.text_input("Custom label (optional)", key=img_file+"_custom")

        if st.button("Save label", key=img_file+"_save"):
            save_feedback(img_file, selected, custom)
            st.success("Saved.")

    st.markdown("---")
