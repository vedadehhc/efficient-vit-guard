import subprocess
import time
from PIL import Image

def get_mask(img, bbox):
    img.save('masks/temp.png', format="PNG")
    
    command = [
            "python",
            "../efficientvit/demo_sam_model.py",
            "--model",
            "l1",
            "--image_path",
            '../server/masks/temp.png',
            "--output_path",
            "../server/masks/out.npy",
            "--mode",
            "box",
            "--box",
            str(bbox),
        ]
    
    subprocess.run(command)

if __name__ == '__main__':
    img = Image.open('../assets/img10.png')
    get_mask(img, [0,1,2,4])
