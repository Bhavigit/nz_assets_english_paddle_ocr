# from flask import Flask, request
# import numpy as np
# import cv2
# import base64
# import logging
# import re
# from paddleocr import PaddleOCR
#
# app = Flask(__name__)
# app.logger.setLevel(logging.INFO)
#
# # LOAD PADDLE MODEL
# print("Loading PaddleOCR...")
# ocr = PaddleOCR(lang='en')
# print("PaddleOCR loaded")
#
# #  JSON FORMAT
# def process_results(results, width, height):
#
#     json_data = {
#         "width": int(width),
#         "height": int(height),
#         "un": "machine",
#         "object_type": [],
#         "class": [],
#         "xmin": [],
#         "xmax": [],
#         "ymin": [],
#         "ymax": [],
#         "confidence": [],
#         "rating": "",
#         "lane_type": [],
#         "lane_colour": [],
#         "lane_number": [],
#         "lane_location": [],
#         "lane_pixels": [],
#     }
#
#     for item in results:
#         points, text, conf = item
#
#         x_coords = [int(p[0]) for p in points]
#         y_coords = [int(p[1]) for p in points]
#
#         json_data["xmin"].append(min(x_coords))
#         json_data["xmax"].append(max(x_coords))
#         json_data["ymin"].append(min(y_coords))
#         json_data["ymax"].append(max(y_coords))
#         json_data["class"].append(text)
#         json_data["confidence"].append(float(conf))
#         json_data["object_type"].append("nz_assets_text")
#
#     return json_data
#
#
# #  IMAGE DECODE
# def decode_image(data):
#     encoded_image = data["instances"][0]["b64"]
#     encoded_image = base64.b64decode(encoded_image.encode() + b"==")
#     encoded_image = np.asarray(bytearray(encoded_image), dtype=np.uint8)
#     img = cv2.imdecode(encoded_image, cv2.IMREAD_COLOR)
#     return img
#
#
# #  FILTER
# def valid_english(text, conf):
#
#     if conf < 0.60:
#         return False
#
#     if re.search(r'[\u0600-\u06FF]', text):
#         return False
#
#     if not re.search(r'[A-Za-z]', text):
#         return False
#
#     if len(text.strip()) <= 2:
#         return False
#
#     return True
#
#
# #  MAIN API
# @app.route("/v1/models/nz_assets_text:predict", methods=["POST"])
# def detect():
#
#     image = decode_image(request.json)
#     h, w = image.shape[:2]
#
#     blur = cv2.bilateralFilter(image, 5, 25, 25)
#
#     paddle_out = ocr.ocr(blur)
#
#     final_results = []
#
#     if paddle_out[0] is not None:
#         for line in paddle_out[0]:
#
#             box = line[0]
#             text = line[1][0]
#             conf = line[1][1]
#
#             if not valid_english(text, conf):
#                 continue
#
#             final_results.append((box, text, conf))
#
#     results_json = process_results(final_results, w, h)
#
#     return {
#         "results": results_json,
#         "status": "200"
#     }
#
#
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)

"""
OCR Inference Server (v1)
-------------------------
Production-ready Flask API for English text detection using PaddleOCR.

Pipeline:
1. Receives base64 encoded image via POST request
2. Decodes image
3. Runs PaddleOCR detection + recognition
4. Applies filtering (remove Arabic + noise)
5. Returns structured JSON response

Endpoint:
POST /v1/models/nz_assets_text:predict

Designed to run inside Docker for deployment.
"""

from flask import Flask, request
import numpy as np
import cv2
import base64
import logging
import re
from paddleocr import PaddleOCR


# Flask App Initialization

app = Flask(__name__)
app.logger.setLevel(logging.INFO)


# Load PaddleOCR model

print("Loading PaddleOCR model...")
ocr = PaddleOCR(lang='en')
print("PaddleOCR loaded successfully")



# Format OCR output into required JSON structure

def process_results(results, width, height):
    """
    Convert OCR detections into structured JSON response.

    Args:
        results: list of (bbox, text, confidence)
        width: image width
        height: image height

    Returns:
        json dict
    """

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
    """
    Decode base64 image from incoming JSON request.

    Expected input format:
    {
        "instances":[{"b64":"..."}]
    }
    """

    encoded_image = data["instances"][0]["b64"]
    encoded_image = base64.b64decode(encoded_image.encode() + b"==")
    encoded_image = np.asarray(bytearray(encoded_image), dtype=np.uint8)
    img = cv2.imdecode(encoded_image, cv2.IMREAD_COLOR)
    return img



# English text filtering
# Removes Arabic, noise, low-confidence detections

def valid_english(text, conf):
    """
    Apply filtering rules to keep only valid English detections.
    """

    # confidence threshold
    if conf < 0.60:
        return False

    # remove arabic characters
    if re.search(r'[\u0600-\u06FF]', text):
        return False

    # must contain English letters
    if not re.search(r'[A-Za-z]', text):
        return False

    # remove very short garbage text
    if len(text.strip()) <= 2:
        return False

    return True



# Main OCR API endpoint

@app.route("/v1/models/nz_assets_text:predict", methods=["POST"])
def detect():
    """
    Main inference endpoint.

    Steps:
    - Decode image
    - Run PaddleOCR
    - Apply filtering
    - Return structured JSON
    """

    # decode incoming image
    image = decode_image(request.json)
    h, w = image.shape[:2]

    # light smoothing for better OCR
    blur = cv2.bilateralFilter(image, 5, 25, 25)

    # run paddle OCR
    paddle_out = ocr.ocr(blur)

    final_results = []

    if paddle_out[0] is not None:
        for line in paddle_out[0]:

            box = line[0]
            text = line[1][0]
            conf = line[1][1]

            # apply filtering
            if not valid_english(text, conf):
                continue

            final_results.append((box, text, conf))

    # format output
    results_json = process_results(final_results, w, h)

    return {
        "results": results_json,
        "status": "200"
    }


# Run server

if __name__ == "__main__":
    # runs inside docker on port 8000
    app.run(host="0.0.0.0", port=8000)