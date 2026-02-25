# NZ Assets Text OCR – PaddleOCR Version (v1)

## Overview

This service provides an OCR inference API for detecting English text from road asset images using PaddleOCR.

The pipeline:
- Accepts base64 encoded images via REST API
- Runs text detection and recognition using PaddleOCR
- Applies filtering to remove Arabic and low-confidence noise
- Returns structured JSON output
- Runs inside Docker for easy deployment

---

## Model Details

- OCR Engine: PaddleOCR
- Language: English
- Detection: PP-OCRv3
- Recognition: PP-OCRv4
- Confidence threshold: 0.60
- Arabic filtering enabled

---

## API Endpoint

### POST
