from flask import Flask, request
import numpy as np
import cv2
import base64
import logging
import re
from paddleocr import PaddleOCR


# Flask app setup

app = Flask(__name__)
app.logger.setLevel(logging.INFO)


# Load PaddleOCR model 

print("Loading PaddleOCR model...")
ocr = PaddleOCR(lang='en')
print("PaddleOCR loaded")



# Convert OCR results to required JSON format

def process_results(results, width, height):

    json_data = {
        "width": int(width),
        "height": int(height),
        "un": "machine",
        "object_type": [],
        "class": [],
        "xmin": [],
        "xmax": [],
        "ymin": [],
        "ymax": [],
        "confidence": [],
        "rating": "",
        "lane_type": [],
        "lane_colour": [],
        "lane_number": [],
        "lane_location": [],
        "lane_pixels": [],
    }

    for item in results:
        points, text, conf = item

        x_coords = [int(p[0]) for p in points]
        y_coords = [int(p[1]) for p in points]

        json_data["xmin"].append(min(x_coords))
        json_data["xmax"].append(max(x_coords))
        json_data["ymin"].append(min(y_coords))
        json_data["ymax"].append(max(y_coords))
        json_data["class"].append(text)
        json_data["confidence"].append(float(conf))
        json_data["object_type"].append("nz_assets_text")

    return json_data



# Decode base64 image from API request

def decode_image(data):

    encoded_image = data["instances"][0]["b64"]
    encoded_image = base64.b64decode(encoded_image.encode() + b"==")
    encoded_image = np.asarray(bytearray(encoded_image), dtype=np.uint8)
    img = cv2.imdecode(encoded_image, cv2.IMREAD_COLOR)

    return img



# Filter English text only (remove arabic + noise)

def valid_english(text, conf):

    if conf < 0.60:
        return False

    # remove arabic text
    if re.search(r'[\u0600-\u06FF]', text):
        return False

    # must contain english
    if not re.search(r'[A-Za-z]', text):
        return False

    # remove short garbage
    if len(text.strip()) <= 2:
        return False

    return True



# Main API endpoint

@app.route("/v1/models/nz_assets_text:predict", methods=["POST"])
def detect():

    image = decode_image(request.json)
    h, w = image.shape[:2]

    # smoothing improves OCR slightly
    blur = cv2.bilateralFilter(image, 5, 25, 25)

    paddle_out = ocr.ocr(blur)

    final_results = []

    if paddle_out[0] is not None:
        for line in paddle_out[0]:

            box = line[0]
            text = line[1][0]
            conf = line[1][1]

            if not valid_english(text, conf):
                continue

            final_results.append((box, text, conf))

    results_json = process_results(final_results, w, h)

    app.logger.info(results_json)

    return {
        "results": results_json,
        "Status": "200"
    }



# Run server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
