# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off

# Set work directory in container
WORKDIR /app

# Install system dependencies required for build
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code to container
COPY . .

# Create startup script
RUN echo '#!/bin/bash\nPORT=${PORT:-8080}\nexec uvicorn backend.server:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 60' > start.sh && chmod +x start.sh

# Expose the port (Railway will set PORT environment variable)
EXPOSE 8080

# Command to run the application using Uvicorn
# Use startup script to handle PORT environment variable  
CMD ["./start.sh"]
