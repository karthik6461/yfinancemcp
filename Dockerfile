# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY agent.py .
COPY main.py .

# Expose ports
EXPOSE 8000 8001

# Command to run both servers
CMD ["sh", "-c", "python server.py & uvicorn main:app --host 0.0.0.0 --port 8001"]