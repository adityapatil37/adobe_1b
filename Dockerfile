# Dockerfile for Offline Persona-Driven Document Intelligence
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python packages from local directory (completely offline)
RUN pip install -r requirements.txt

# Download spaCy model in build stage (if not pre-bundled)
# RUN python -m spacy download en_core_web_md --direct

# Create directories
RUN mkdir -p documents output

# Run application
CMD ["python", "main.py"]