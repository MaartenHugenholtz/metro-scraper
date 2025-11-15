FROM python:3.12-slim

# Install system dependencies for Chromium / Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libgbm1 \
    libasound2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libxss1 \
    fonts-liberation \
    ca-certificates \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir playwright fastapi uvicorn bs4

# Install Chromium for Playwright and its dependencies
RUN playwright install chromium
RUN playwright install-deps

# Set working directory
WORKDIR /app
COPY . /app

# Expose FastAPI port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
