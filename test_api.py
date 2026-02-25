import base64
import requests

url = "http://127.0.0.1:8000/v1/models/nz_assets_text:predict"

img_path = r"C:\Users\KarriBhavya\PycharmProjects\nz_assets_text_v1-arabic\nz_assets_text_v1-arabic\test_data\input_images\1~Riyadh Municipality~Riyad Trial 25~9055~Video_1741935860-0000229_458 - Copy.jpg"

with open(img_path, "rb") as f:
    img = base64.b64encode(f.read()).decode()

data = {
    "instances":[{"b64":img}],
    "s3_path":"english",
    "image_name":"test.jpg"
}

res = requests.post(url, json=data)
print(res.json())