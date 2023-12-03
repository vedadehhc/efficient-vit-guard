from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import numpy as np
import cv2

from vit import get_mask

app = Flask(__name__)
CORS(app)

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
        
    # Extract bounding box coordinates from form data
    try:
        bbox = [int(request.form[key]) for key in ['x_1', 'y_1', 'x_2', 'y_2']]
        x_1, y_1, x_2, y_2 = bbox
    except (ValueError, KeyError):
        return "Invalid or missing bounding box coordinates", 400

    if file:
        # Read the image via file.stream
        img = Image.open(file.stream)
        seg_mask = get_mask(img, bbox)

        # Convert PIL image to numpy array
        img_np = np.array(img)

        size = max(x_2 - x_1, y_2 - y_1) // 4
        if size % 2 == 0: 
            size += 1

        # Apply blur using OpenCV
        blurred_img_np = cv2.GaussianBlur(img_np, (size, size), 0)
        
        # Change the pixel values in the bounding box to a blurred image
        img_np[seg_mask == 1] = blurred_img_np[seg_mask == 1]

        # Convert numpy array back to PIL image
        img_blurred = Image.fromarray(img_np)
        
        if img_blurred.mode == 'RGBA':
            img_blurred = img_blurred.convert('RGB')

        # Save the blurred image to a BytesIO object
        img_io = BytesIO()
        img_blurred.save(img_io, 'JPEG', quality=70)
        img_io.seek(0)

        return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='blurred.jpg')

    return "Something went wrong", 500

if __name__ == '__main__':
    app.run(debug=True)