FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directories
RUN mkdir -p /data/features /data/postgres

# Copy application code
COPY . .

# Expose API port
EXPOSE 8080

# Run the API server
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8080"]
