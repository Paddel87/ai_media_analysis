# Demo runner for pipeline modules
import os
print("Running full AI Media Analysis test pipeline...")

os.system("python3 services/vision_pipeline/detect_track.py")
os.system("python3 services/vision_pipeline/nsfw_check.py")
os.system("python3 services/control/summarizer.py")
print("Done.")
