# ============================================================
# matcher.py — Pure ML Logic
# ============================================================
# This file owns everything related to:
#   1. Extracting text from uploaded files
#   2. Cleaning that text
#   3. Generating semantic embeddings
#   4. Scoring and ranking resumes
#
# It is completely independent of FastAPI — you could call
# these functions from a CLI, a test, or any other framework.
# ============================================================
 
import os 
import re
import docx2txt
import PyPDF2
from sentence_transformers import SentenceTransformer, util
import logging


logger = logging.getLogger(__name__)

# ── Allowed file extensions ──────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


#---- model loading -------------------------------------
logger.info("Loading sentence transformer model...")
MODEL = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("Model ready.")

#validating the input file type
def is_allowed_file(filename: str) -> bool:
    "return whether the file is supported or not"
    _, extension = os.path.splitext(filename.lower())
    return extension in ALLOWED_EXTENSIONS

#=========extracting text from different file type==========

#function to text from pdf file
def extract_pdf(path: str) -> str:
    text = " "
    with open("path", "rb") as f:
        reader = PyPDF2.PdfReader(f)
    for i, pages in enumerate(reader.pages):
        page_text = pages.extract_text()
        if page_text:
            text += page_text
        else:
            logger.warning(f"PDF page {i+1} in '{path}' has no text layer — skipped.")
    return text

def extract_doc(path: str) -> str:
    return docx2txt.process(path)

def extract_txt(path: str) -> str:
    with open(path, "r", encoding = 'utf-8') as f:
        text = f.read()
    return text


#mapping exactors 
_EXTRACTORS = {
    ".pdf":  extract_pdf,
    ".docx": extract_doc,
    ".txt":  extract_txt,
}

def extract_text(path: str) -> str:
    extension = os.path.splitext(path.lower())[1]
    if extension not in _EXTRACTORS:
        raise ValueError("invalid file type")
    else:
        return _EXTRACTORS[extension](path)
    

#==========Text_cleaning===========================

def clean_text(text: str) -> str:
   
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

#===========embeddings and similarity===============

def embed(text: str):

    return MODEL.encode(text, convert_to_tensor=True )

def similarity(vec_01, vec_02) -> float:
    score = float(util.cos_sim(vec_01, vec_02).item())
    return score

#============ranking of resumes======================

def ranking_resumes(job_description : str, resumes: list[dict]) ->list[dict]:

    job_clean = clean_text(job_description)
    job_embed = embed(job_clean)



    scores = []
    for resume in resumes:
        resume_clean = clean_text(resume["text"])
        resume_embed = embed(resume_clean)
        score = similarity(job_embed, resume_embed)
        percentage = round(score*100, 1)
        if percentage >= 75:
         score_label = "Excellent"
        elif percentage >= 55:
         score_label = "Good"
        elif percentage >= 35:
          score_label = "Moderate"
        else:
          score_label = "poor"
 
 


        scores.append({
            "name":  resume["name"],
            "score": percentage,
            "label": score_label,
        })
        logger.info(f"  {resume['name']} → {percentage}%")

    ranked = sorted(scores, key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(ranked):
        r["rank"] = i + 1
 
    logger.info("Ranking complete.")
    return ranked



 
