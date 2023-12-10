from datasets import load_dataset
from facenet_pytorch import MTCNN
import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageDraw
import time

mtcnn = torch.load('pruned_facenet_before_ft.pt')
mtcnn.device = "cpu"
NUM_EPOCHS = 5
torch.requires_grad = True

dataset = load_dataset("wider_face")

data = dataset["train"]
start_time = time.time()

for epoch in range(NUM_EPOCHS):
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
      
      boxes = mtcnn(img)
      print(boxes[0])
        
    idx += 1
    if idx >= 1:
        break