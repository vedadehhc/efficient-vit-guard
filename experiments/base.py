from datasets import load_dataset
import numpy as np
import os
import pandas as pd
from PIL import Image
import subprocess
import time

dataset = load_dataset("wider_face")
results = {"img_idx":[], "illum":[], "occ":[], "time":[],"bbox":[]}

data = dataset["train"]
start_time = time.time()
idx=0
for datapoint in data:
    im = datapoint["image"]
    bbox = datapoint["faces"]["bbox"]
    illum = datapoint["faces"]["illumination"]
    occ = datapoint["faces"]["occlusion"]

    if len(bbox) == 1:

        img_path = f"../assets/face_images/{idx}.png"
        output_path = f"../assets/results/{idx}.png"
        results["img_idx"].append(idx)
        results["illum"].append(illum[0])
        results["occ"].append(occ[0])

        if os.path.exists(img_path):
            pass
        else:
            im.save(img_path, format="PNG")

        bbox = [bbox[0][0]] + [bbox[0][1]] + [bbox[0][0]+bbox[0][2]] + [bbox[0][1]+bbox[0][3]]
        results["bbox"].append(bbox)

        command = [
            "python",
            "efficientvit/demo_sam_model.py",
            "--model",
            "l1",
            "--image_path",
            img_path,
            "--output_path",
            output_path,
            "--mode",
            "box",
            "--box",
            str(bbox),
            "--idx",
            str(idx)
        ]
        
        subprocess_start_time = time.time()
        subprocess.run(command)
        subprocess_end_time = time.time()
        elapsed_time = subprocess_end_time - subprocess_start_time
        results["time"].append(elapsed_time)
        idx+=1

    if idx >= 1000:
        break

results_df = pd.DataFrame(results)
results_df.to_csv(f"/home/dnori/efficient-vit-guard/assets/results.csv", index=False)