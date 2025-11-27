FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY setup.py .
COPY README.md .
COPY pulso/ ./pulso/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install package in development mode
RUN pip install -e .

# Install Playwright and browsers (optional, only if using playwright driver)
RUN pip install playwright && playwright install chromium && playwright install-deps chromium

# Create cache directory
RUN mkdir -p /cache

# Set environment variables
ENV PULSO_CACHE_DIR=/cache
ENV PULSO_LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

# Run as non-root user
RUN useradd -m -u 1000 pulso && \
    chown -R pulso:pulso /app /cache
USER pulso

# Default command (can be overridden)
CMD ["python"]
