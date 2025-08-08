# Use official Python image (slim variant to keep size small)
FROM python:3.11-slim

# Install system dependencies for Playwright + other tools
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium, Firefox, WebKit)
RUN python -m playwright install

# Copy the rest of your application code
COPY . .

# Expose any port if your bot uses (optional)
EXPOSE 8000

# Define environment variables if needed (optional)
# ENV NO_FLUFF_HEADLESS=true

# Default command to run your main script
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
