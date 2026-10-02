# LinkDrop

A production-ready mobile-first YouTube and Instagram downloader UI backed by Python, Flask, yt-dlp, FFmpeg, and Gunicorn.

---

## Features

- **Supported Platforms**: YouTube & Instagram links.
- **Media Formats**: Video (mp4 with custom quality selection: Best, 1080p, 720p, 480p, 360p) and Audio (mp3 with custom quality selection: Best, 320, 192, 128 kbps).
- **Production Built**: Dockerized using Python 3.11 slim and system FFmpeg, ready for single-click Render deployment.
- **Single Active Download**: Limits concurrent downloads to 1 active process to manage server memory and CPU resources cleanly.
- **Automatic Cleanup**: Temporary files and completed jobs are automatically purged after expiration.

---

## 1. Local Windows Run Instructions

### Quick Start (Double-Click)
1. Double-click `start.bat`.
2. The script will set up the Python virtual environment (`backend/venv`), install dependencies, and launch the server on port `8000`.
3. Open `http://localhost:8000` in your browser.

### Manual Terminal Run
```cmd
python -m venv backend\venv
backend\venv\Scripts\activate
pip install -r backend/requirements.txt
set PORT=8000
python backend/server.py
```
Open `http://localhost:8000`.

### Local Wi-Fi Access (Phone on same network)
Find your local IP address using `ipconfig` (e.g. `192.168.1.50`), then open `http://192.168.1.50:8000` on your mobile browser.

---

## 2. Docker Run Instructions

### Build Docker Image
```bash
docker build -t linkdrop .
```

### Run Container
```bash
docker run -d -p 10000:10000 --name linkdrop-app linkdrop
```
Open `http://localhost:10000` in your browser.

---

## 3. GitHub Push Instructions

1. Initialize git (if not already initialized):
   ```bash
   git init
   ```
2. Add files and commit:
   ```bash
   git add .
   git commit -m "Convert LinkDrop to Render production deployment"
   ```
3. Link your GitHub repository and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/linkdrop.git
   git push -u origin main
   ```

---

## 4. Render Deployment Instructions

### Option A: Automatic Blueprint Deployment (Recommended)
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository (`linkdrop`).
4. Render will read `render.yaml` automatically and configure a free Docker Web Service.
5. Click **Apply**.

### Option B: Manual Web Service Setup
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** and select **Web Service**.
3. Select **Build and deploy from a Git repository** and pick your repository.
4. Set the following options:
   - **Environment**: `Docker`
   - **Region**: Select your preferred region
   - **Branch**: `main`
   - **Dockerfile Path**: `./Dockerfile`
5. Click **Create Web Service**.

---

## 5. Public URL Usage from Any Phone

Once deployed on Render, your application will have a public HTTPS domain (e.g., `https://linkdrop.onrender.com`).

1. Open `https://YOUR-APP-NAME.onrender.com` on any smartphone (iOS / Android) or PC from anywhere in the world.
2. Paste a YouTube or Instagram video link into the input field.
3. Choose format (**Video** / **Audio**) and desired quality level.
4. Tap **Download**. The download progress will display in real time.
5. Once completed, tap **Download File** to save the media directly to your phone's file storage or camera roll.

---

## Notes & Policy

- **Maximum Download Size**: 1 GB limit per media download.
- **Concurrency**: 1 active download job at a time.
- **Unsupported Content**: Private/login-required videos, DRM-protected content, and restricted links are not supported.
- **Terms**: Ensure you only download content you are permitted to access.
