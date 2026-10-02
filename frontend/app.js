const API = "/api";
let type = "video";
let pollTimer = null;

const urlInput = document.getElementById("url");
const platform = document.getElementById("platform");
const quality = document.getElementById("quality");
const downloadBtn = document.getElementById("downloadBtn");
const status = document.getElementById("status");
const statusTitle = document.getElementById("statusTitle");
const statusDetail = document.getElementById("statusDetail");
const progressBar = document.getElementById("progressBar");
const result = document.getElementById("result");
const resultName = document.getElementById("resultName");
const fileLink = document.getElementById("fileLink");

function setOptions(){
  quality.innerHTML = "";
  const opts = type === "video"
    ? [["best","Auto"],["360","360p"],["480","480p"],["720","720p"],["1080","1080p"]]
    : [["best","Best"],["128","128 kbps"],["192","192 kbps"],["320","320 kbps"]];
  opts.forEach(([v,t]) => { const o=document.createElement("option"); o.value=v; o.textContent=t; quality.appendChild(o); });
}
setOptions();

document.querySelectorAll(".segmented button").forEach(btn => {
  btn.onclick=()=>{ document.querySelectorAll(".segmented button").forEach(x=>x.classList.remove("active")); btn.classList.add("active"); type=btn.dataset.type; setOptions(); };
});

urlInput.addEventListener("input",()=>{
  const v=urlInput.value.toLowerCase();
  platform.textContent = v.includes("instagram.com") ? "Instagram" : v.includes("youtube.com") || v.includes("youtu.be") ? "YouTube" : "";
});

document.getElementById("themeBtn").onclick=()=>{
  document.body.classList.toggle("light");
  document.getElementById("themeBtn").textContent=document.body.classList.contains("light")?"☾":"☀";
};

function showStatus(title, detail="", pct=0){
  status.classList.remove("hidden"); statusTitle.textContent=title; statusDetail.textContent=detail; progressBar.style.width=`${pct}%`;
}
function hideStatus(){status.classList.add("hidden")}
function validUrl(v){
  try { const u=new URL(v); return ["youtube.com","www.youtube.com","youtu.be","www.youtu.be","instagram.com","www.instagram.com"].includes(u.hostname.toLowerCase()); }
  catch{return false}
}

async function startDownload(){
  const url=urlInput.value.trim();
  if(!validUrl(url)){showStatus("Invalid link","Paste a valid YouTube or Instagram URL.",0);return}
  downloadBtn.disabled=true; result.classList.add("hidden"); showStatus("Checking link","Preparing download…",5);
  try{
    const r=await fetch(`${API}/download`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url,type,quality:quality.value})});
    const data=await r.json();
    if(!r.ok) throw new Error(data.error||"Download request failed");
    showStatus("Downloading", "Job started…", 10);
    poll(data.jobId);
  }catch(e){
    showStatus("Download failed",e.message,0);
    downloadBtn.disabled=false;
  }
}

async function poll(jobId){
  clearTimeout(pollTimer);
  try{
    const r=await fetch(`${API}/download/${encodeURIComponent(jobId)}`);
    const d=await r.json();
    if(!r.ok) throw new Error(d.error||"Status request failed");
    const pct=Number(d.progress||0);
    if(d.status==="queued"||d.status==="running"){
      showStatus(d.status==="queued"?"Preparing…":"Downloading",d.message||"Please wait…",pct);
      pollTimer=setTimeout(()=>poll(jobId),700);
    }else if(d.status==="completed"){
      showStatus("Completed",d.filename||"File ready",100);
      result.classList.remove("hidden"); resultName.textContent=d.filename||"Download";
      fileLink.href=`${API}/download/${encodeURIComponent(jobId)}/file`;
      fileLink.download=d.filename||"download";
      downloadBtn.disabled=false;
    }else{
      throw new Error(d.error||"Download failed");
    }
  }catch(e){
    showStatus("Download failed",e.message,0);
    downloadBtn.disabled=false;
  }
}
downloadBtn.onclick=startDownload;
urlInput.addEventListener("keydown",e=>{if(e.key==="Enter")startDownload()});
