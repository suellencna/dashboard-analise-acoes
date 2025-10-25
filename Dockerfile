FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create start script to handle PORT variable expansion
RUN echo '#!/bin/bash\nPORT=${PORT:-5000}\ngunicorn webhook_hotmart_optimized:app --bind 0.0.0.0:$PORT --timeout 15 --workers 2 --threads 2' > /app/start.sh && chmod +x /app/start.sh

# Run the application using the start script
CMD ["bash", "/app/start.sh"]
