from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import numpy as np
import cv2

app = Flask(__name__)
CORS(app)

def blur_face():
    pass

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file:
        # Read the image via file.stream
        img = Image.open(file.stream)

        # Convert PIL image to numpy array
        img_np = np.array(img)

        # Apply blur using OpenCV
        blurred_img_np = cv2.GaussianBlur(img_np, (21, 21), 0)

        # Convert numpy array back to PIL image
        img_blurred = Image.fromarray(blurred_img_np)
        
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