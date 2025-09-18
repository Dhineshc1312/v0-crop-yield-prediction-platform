# Multi-stage Dockerfile for SIH AI Harvesters Platform
# Supports both development and production environments

# Base stage with common dependencies
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    black \
    flake8 \
    mypy

# Copy source code
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /app/models /app/data/raw /app/data/processed /app/logs

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy source code
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Create necessary directories and set permissions
RUN mkdir -p /app/models /app/data/raw /app/data/processed /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
