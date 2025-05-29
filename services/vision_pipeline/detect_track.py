import os
import cv2
import uuid

INPUT_FOLDER = "data/frames/sample_job"
OUTPUT_FOLDER = "data/objects/sample_job"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Dummy person detector (replace with YOLO later)
def fake_person_detector(image):
    height, width, _ = image.shape
    # Pretend we detect a person in center of frame
    x1 = width // 4
    y1 = height // 4
    x2 = x1 + width // 2
    y2 = y1 + height // 2
    return [(x1, y1, x2, y2)]

# Iterate over input frames
for img_file in sorted(os.listdir(INPUT_FOLDER)):
    if not img_file.endswith((".jpg", ".png", ".webp")):
        continue
    img_path = os.path.join(INPUT_FOLDER, img_file)
    image = cv2.imread(img_path)

    boxes = fake_person_detector(image)
    for i, (x1, y1, x2, y2) in enumerate(boxes):
        crop = image[y1:y2, x1:x2]
        filename = f"{uuid.uuid4().hex[:8]}_{img_file}"
        out_path = os.path.join(OUTPUT_FOLDER, filename)
        cv2.imwrite(out_path, crop)
        print(f"Saved crop: {out_path}")
