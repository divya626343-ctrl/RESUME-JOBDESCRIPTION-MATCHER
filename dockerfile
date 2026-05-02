# ============================================================
# Dockerfile — Resume Matcher
# ============================================================

# ── Stage: base image ────────────────────────────────────────
FROM python:3.11-slim


# ── System dependencies ──────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ────────────────────────────────────────
WORKDIR /app


# ── Install Python dependencies ──────────────────────────────
COPY requirements.txt .

RUN pip install --no-cache-dir torch==2.3.0 \
    --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt


# ── Pre-download the transformer model ───────────────────────
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('all-MiniLM-L6-v2'); \
print('Model downloaded and cached.')"


# ── Copy application code ─────────────────────────────────────
# Done AFTER pip install and model download so that changing
# app code doesn't invalidate those expensive cached layers.
COPY main.py    .
COPY matcher.py .
COPY templates/ ./templates/
COPY static/    ./static/


# ── Create uploads folder ─────────────────────────────────────
RUN mkdir -p uploads


# ── Expose port ───────────────────────────────────────────────

EXPOSE 8000


# ── Start command ─────────────────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]