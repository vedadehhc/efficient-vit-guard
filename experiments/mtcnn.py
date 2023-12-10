from datasets import load_dataset
from facenet_pytorch import MTCNN
import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageDraw
import time

mtcnn = MTCNN(device="cpu")
# mtcnn = torch.load('pruned_facenet_before_ft.pt')

dataset = load_dataset("wider_face")
results = {"img_idx":[], "illum":[], "occ":[], "time":[],"gt_bbox":[], "pred_bbox": [], "mse": []}

data = dataset["train"]
start_time = time.time()
idx=0
for datapoint in data:
    im = datapoint["image"]
    bbox = datapoint["faces"]["bbox"]
    illum = datapoint["faces"]["illumination"]
    occ = datapoint["faces"]["occlusion"]

    if len(bbox) == 1:
       
        bbox = [bbox[0][0]] + [bbox[0][1]] + [bbox[0][0]+bbox[0][2]] + [bbox[0][1]+bbox[0][3]]

        img_path = f"/home/dnori/efficient-vit-guard/assets/face_images/{idx}.png"
        img = Image.open(img_path)

        subprocess_start_time = time.time()
        boxes, _ = mtcnn.detect(img)
        if boxes is None:
            idx+=1
        else:
            pred_bbox = boxes[0]
            gt_bbox = np.array(bbox)

            subprocess_end_time = time.time()
            elapsed_time = subprocess_end_time - subprocess_start_time
            results["time"].append(elapsed_time)
            
            results["img_idx"].append(idx)
            results["illum"].append(illum[0])
            results["occ"].append(occ[0])
            
            results["pred_bbox"].append(pred_bbox)
            results["gt_bbox"].append(gt_bbox)

            mse = np.linalg.norm(pred_bbox - gt_bbox)
            results["mse"].append(mse)        
            idx+=1

            frame_draw = img.copy()
            draw = ImageDraw.Draw(frame_draw)
            draw.rectangle(pred_bbox.tolist(), outline=(255, 0, 0), width=6)
            frame_draw.save(f"/home/dnori/efficient-vit-guard/assets/mtcnn_results/{idx}.png")
            print(f"Done, {elapsed_time}s.")
            
    if idx >= 1000:
        break

results_df = pd.DataFrame(results)
results_df.to_csv(f"/home/dnori/efficient-vit-guard/assets/mtcnn_unpruned.csv", index=False)

print(f"Avg Time: {sum(results_df['time'].tolist())/len(results_df['time'].tolist())}")
print(f"Avg MSE: {sum(results_df['mse'].tolist())/len(results_df['mse'].tolist())}")