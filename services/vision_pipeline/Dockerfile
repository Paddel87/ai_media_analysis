FROM python:3.10-slim

# Install build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    git \
    && g++ --version \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Start the application
CMD ["python", "main.py"]
