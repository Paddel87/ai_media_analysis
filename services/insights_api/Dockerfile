FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY services/insights_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common services (required for insights_service)
COPY services/common ./services/common

# Copy data schema (required for insights_database)
COPY data_schema ./data_schema

# Copy application code
COPY services/insights_api .

# Set Python path for proper imports
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
