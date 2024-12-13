# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install build dependencies and compile requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Production stage
FROM python:3.11-slim as production

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 exporter
USER exporter

# Expose prometheus metrics port
EXPOSE 9090

# Run the exporter
CMD ["python", "main.py"]

# Development stage
FROM production as development

# Switch back to root for development tools
USER root

# Install development tools
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    flake8 \
    black \
    mypy

# Switch back to non-root user
USER exporter

# Use different command for development
CMD ["python", "-m", "pytest", "-v"]
