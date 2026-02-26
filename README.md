# NZ Assets Text OCR – PaddleOCR Version

## Overview
This service provides an OCR inference API for detecting **English text from road asset images** using PaddleOCR.

The pipeline:
- Accepts base64 encoded image via REST API
- Detects and recognizes English text using PaddleOCR
- Filters Arabic text, symbols, and noise
- Returns structured JSON output
- Docker-ready for deployment

This version replaces EasyOCR with PaddleOCR to improve English text accuracy and reduce noise.

---

## Project Structure
