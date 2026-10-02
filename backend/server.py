import os, re, uuid, shutil, threading, subprocess, json, time
from pathlib import Path
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS

ROOT=Path(__file__).resolve().parent
DOWNLOADS=ROOT/"downloads"
DOWNLOADS.mkdir(exist_ok=True)
MAX_BYTES=1024*1024*1024
JOBS={}
LOCK=threading.Lock()
ACTIVE=False

app=Flask(__name__, static_folder=str(ROOT.parent/"frontend"), static_url_path="")
CORS(app)

YOUTUBE={"youtube.com","www.youtube.com","youtu.be","www.youtu.be"}
INSTAGRAM={"instagram.com","www.instagram.com"}

def allowed_url(value):
    try:
        from urllib.parse import urlparse
        p=urlparse(value)
        host=p.hostname.lower() if p.hostname else ""
        return p.scheme in ("http","https") and host in YOUTUBE|INSTAGRAM
    except Exception:
        return False

def worker(job_id, url, media_type, quality):
    global ACTIVE
    job=JOBS[job_id]
    work=DOWNLOADS/job_id
    work.mkdir(parents=True,exist_ok=True)
    try:
        job.update(status="running",progress=0,message="yt-dlp started")
        if media_type=="video":
            if quality=="best":
                fmt="bv*+ba/b"
            else:
                fmt=f"bv*[height<={int(quality)}]+ba/b[height<={int(quality)}]"
            args=["yt-dlp","--no-playlist","--restrict-filenames","--newline","--progress",
                  "--max-filesize","1G","-f",fmt,"--merge-output-format","mp4",
                  "-o",str(work/"%(title)s.%(ext)s"),url]
        else:
            aq = quality if quality in {"128","192","320"} else "0"
            args=["yt-dlp","--no-playlist","--restrict-filenames","--newline","--progress",
                  "--max-filesize","1G","-x","--audio-format","mp3","--audio-quality",
                  aq,"-o",str(work/"%(title)s.%(ext)s"),url]

        p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace")
        lines=[]
        for line in p.stdout:
            line=line.strip()
            if not line: continue
            lines.append(line)
            m=re.search(r"\[download\]\s+(\d+(?:\.\d+)?)%",line)
            if m:
                job["progress"]=min(99,float(m.group(1)))
                job["message"]="Downloading…"
        code=p.wait()
        if code!=0:
            tail="\n".join(lines[-8:])
            low=tail.lower()
            if "private" in low or "login" in low:
                raise RuntimeError("Private or login-required content is not supported.")
            raise RuntimeError("yt-dlp could not download this URL. Check the link and content availability.")

        candidates=[p for p in work.iterdir() if p.is_file()]
        if not candidates: raise RuntimeError("No output file was produced.")
        out=max(candidates,key=lambda x:x.stat().st_mtime)
        if out.stat().st_size>MAX_BYTES: raise RuntimeError("Downloaded file is larger than 1 GB.")
        job.update(status="completed",progress=100,message="Ready",filename=out.name,file=str(out))
    except Exception as e:
        job.update(status="failed",progress=0,error=str(e),message="Download failed")
        shutil.rmtree(work,ignore_errors=True)
    finally:
        with LOCK: ACTIVE=False

@app.get("/")
def index(): return app.send_static_file("index.html")

@app.post("/api/download")
def create_download():
    global ACTIVE
    data=request.get_json(silent=True) or {}
    url=str(data.get("url","")).strip()
    media_type=data.get("type","video")
    quality=str(data.get("quality","best"))
    if not allowed_url(url): return jsonify(error="Only YouTube and Instagram URLs are supported."),400
    if media_type not in ("video","audio"): return jsonify(error="Invalid media type."),400
    valid_video={"best","360","480","720","1080"}; valid_audio={"best","128","192","320"}
    if quality not in (valid_video if media_type=="video" else valid_audio): return jsonify(error="Invalid quality."),400
    with LOCK:
        if ACTIVE: return jsonify(error="Another download is already running. Please wait."),429
        ACTIVE=True
    job_id=str(uuid.uuid4())
    JOBS[job_id]={"status":"queued","progress":0,"message":"Queued","filename":None,"file":None}
    threading.Thread(target=worker,args=(job_id,url,media_type,quality),daemon=True).start()
    return jsonify(jobId=job_id),202

@app.get("/api/download/<job_id>")
def status(job_id):
    try: uuid.UUID(job_id)
    except: return jsonify(error="Invalid job id"),400
    job=JOBS.get(job_id)
    if not job: return jsonify(error="Job not found"),404
    return jsonify({k:v for k,v in job.items() if k!="file"})

@app.get("/api/download/<job_id>/file")
def file(job_id):
    job=JOBS.get(job_id)
    if not job or job.get("status")!="completed": return jsonify(error="File not ready"),404
    path=Path(job["file"]).resolve()
    if not path.is_file() or DOWNLOADS.resolve() not in path.parents: return jsonify(error="File unavailable"),404
    return send_file(path,as_attachment=True,download_name=job["filename"])

def cleanup_loop():
    while True:
        time.sleep(1800)
        now=time.time()
        for jid in list(JOBS):
            path=DOWNLOADS/jid
            if path.exists() and now-path.stat().st_mtime>3600:
                shutil.rmtree(path,ignore_errors=True); JOBS.pop(jid,None)

threading.Thread(target=cleanup_loop, daemon=True).start()

if __name__=="__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, debug=False)
