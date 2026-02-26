FROM ubuntu:22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    libglib2.0-0 \
    curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /venv

# Upgrade pip
RUN /venv/bin/pip install --upgrade pip

# Copy requirements first (better docker caching)
COPY server_code/requirements.txt /app/requirements.txt

# Install python dependencies
RUN /venv/bin/pip install -r /app/requirements.txt

# Copy application code
COPY server_code/run_ocr.py /app/run_ocr.py

# Expose ports
EXPOSE 8000

# Start OCR API
CMD ["/venv/bin/python", "/app/run_ocr.py"]