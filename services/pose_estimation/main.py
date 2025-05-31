import cv2
import numpy as np
import torch
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import mmcv
from mmpose.apis import inference_topdown
from mmpose.apis import init_model
from mmpose.structures import merge_data_samples
import uvicorn

app = FastAPI(title="Pose Estimation Service")

# Modell-Konfiguration
config_file = 'configs/body_2d_keypoint/topdown_heatmap/coco/td-hm_hrnet-w48_8xb32-210e_coco-256x192.py'
checkpoint_file = 'https://download.openmmlab.com/mmpose/top_down/hrnet/hrnet_w48_coco_256x192-b9e0b3ab_20200708.pth'

# Modell initialisieren
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = init_model(config_file, checkpoint_file, device=device)

@app.post("/analyze")
async def analyze_pose(file: UploadFile = File(...)):
    try:
        # Bild einlesen
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Pose Estimation durchführen
        results = inference_topdown(model, img)
        results = merge_data_samples(results)
        
        # Ergebnisse formatieren
        keypoints = results.pred_instances.keypoints.cpu().numpy()
        scores = results.pred_instances.keypoint_scores.cpu().numpy()
        
        # JSON-Response erstellen
        response = {
            "keypoints": keypoints.tolist(),
            "scores": scores.tolist(),
            "num_people": len(keypoints)
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)