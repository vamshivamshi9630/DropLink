@echo off
title LinkDrop
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10+ and try again.
  pause
  exit /b 1
)

where yt-dlp >nul 2>nul
if errorlevel 1 (
  echo yt-dlp was not found. Installing/upgrading it...
  py -m pip install -U yt-dlp
)

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo.
  echo FFmpeg was not found in PATH.
  echo Install FFmpeg and add its bin folder to PATH.
  pause
  exit /b 1
)

if not exist "backend\venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  py -m venv backend\venv
)

echo Installing backend dependencies...
backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt

echo.
echo =====================================
echo LinkDrop running at:
echo http://localhost:8000
echo =====================================
echo.
start "" http://localhost:8000
set PORT=8000
backend\venv\Scripts\python.exe backend\server.py
pause
