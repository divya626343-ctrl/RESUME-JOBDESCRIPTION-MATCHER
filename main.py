#============================================================
# main.py — FastAPI Application 
# ============================================================
# This file owns:
#   - App setup (templates, static files, uploads folder)
#   - HTTP routes (GET / and POST /match)
#   - File saving + cleanup
#   - Calling matcher.py for all ML work
#
# It deliberately contains NO ML logic — that all lives in
# matcher.py.
# ============================================================
import os
import logging
from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from  match import extract_text, ranking_resumes, is_allowed_file
 
#logging setup
logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


app = FastAPI(title="Resume Matcher", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


#=========saving and cleanup=======================

def save_files(upload: UploadFile):
    file = os.path.join(UPLOAD_DIR, upload.filename)
    with open(file, "wb") as f:
        f.write(upload.file.read())
    return file

def clean_up(paths: list[str]):
    for path in paths:
        try:
            os.remove(path)
            logger.info(f"Deleted: {path}")
        except OSError as e:
            logger.warning(f"Could not delete {path}: {e}")
 

#============HOMEPAGE===============================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "results": None,      # no results yet on first load
        "error":   None,
    })


@app.post('/match', response_class= HTMLResponse)
async def match(
    request:         Request,
    job_description: str            = Form(...),
    resumes:         list[UploadFile] = File(...),
):
     saved_paths = []
     resumes_data = []
     skipped = []

     #validating the input
     if not job_description.strip():
         return templates.TemplateResponse("index.html", {
            "request": request,
            "results": None,
            "error":   "Please enter a job description.",
        })
     valid_files = [f for f in resumes if f.filename]
     if not valid_files:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "results": None,
            "error":   "Please upload at least one resume.",
        })
 
     for upload in valid_files:
         if not is_allowed_file(upload.filename):
             skipped.append(upload.filename)
             logger.warning(f"Skipped unsupported file: {upload.filename}")
             continue
         
         try:
             path = save_files(upload)
             saved_paths.append(path)
             text = extract_text(path)
             resumes_data.append({'name': upload.filename, 'text': text})
         except Exception as e:
             logger.error(f"Error processing {upload.filename}: {e}")
             skipped.append(upload.filename)

     if not resumes_data:
         clean_up(saved_paths)
         return templates.TemplateResponse("index.html", {
            "request": request,
            "results": None,
            "error":   "No valid resumes could be processed. Check file types.",
        })
     #running core ml part of the model

     try:
         ranked = ranking_resumes(job_description, resumes_data)
     except Exception as e:
        logger.error(f"Ranking error: {e}")
        clean_up(saved_paths)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "results": None,
            "error":   f"Matching failed: {str(e)}",
        })
     finally:
        clean_up(saved_paths)

     return templates.TemplateResponse("index.html", {
        "request":  request,
        "results":  ranked,
        "top3":     ranked[:3],
        "skipped":  skipped if skipped else None,
        "error":    None,
        "total":    len(ranked),
      })
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
   
 
 