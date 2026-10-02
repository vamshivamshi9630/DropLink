FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000 \
    DENO_INSTALL="/root/.deno" \
    PATH="/root/.deno/bin:/usr/local/bin:${PATH}"

# Install system dependencies: ffmpeg, ca-certificates, curl, unzip, git
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    curl \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Deno and copy binary to /usr/local/bin for global availability
RUN curl -fsSL https://deno.land/install.sh | sh \
    && cp /root/.deno/bin/deno /usr/local/bin/deno \
    && chmod +x /usr/local/bin/deno

WORKDIR /app

# Copy requirements and install backend dependencies including latest yt-dlp master with default extras
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application code
COPY . /app/

# Explicitly verify during Docker build that tools are available
RUN yt-dlp --version \
    && deno --version \
    && ffmpeg -version \
    && ffprobe -version

EXPOSE 10000

# Start Flask app using Gunicorn (single worker for state tracking, 600s timeout for long media downloads)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 600 backend.server:app"]
