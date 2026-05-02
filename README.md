# ResuMatch

AI-powered resume ranking using semantic similarity. Upload multiple resumes against a job description and get them ranked by relevance.

## Tech Stack

- **Backend** — FastAPI + Python 3.11
- **ML** — Sentence Transformers (`all-MiniLM-L6-v2`)
- **Frontend** — HTML, CSS, Vanilla JS
- **Deployment** — Docker, AWS EC2 + ECR
- **CI/CD** — GitHub Actions

## Project Structure

```
resume-matcher/
├── main.py               # FastAPI routes
├── matcher.py            # ML logic (extract, embed, rank)
├── templates/index.html  # Jinja2 template
├── static/
│   ├── style.css
│   └── app.js
├── tests/
│   └── test_matcher.py
├── Dockerfile
└── requirements.txt
```

## Running Locally

```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Visit `http://localhost:8000`

## Running with Docker

```bash
docker build -t resume-matcher .
docker run -p 8000:8000 resume-matcher
```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## CI/CD

Pipeline runs automatically on push. Two stages:

- **Stage 1 (Test)** — runs on every push to `main` or `dev`
- **Stage 2 (Deploy)** — runs only on `main` after tests pass

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM access key |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key |
| `ECR_REPOSITORY` | ECR repo name e.g. `resume-matcher` |
| `SSH_HOST` | EC2 public IP |
| `SSH_KEY` | Contents of  `.pem` file |

> Set `AWS_REGION` in the `env` block of `cicd.yml` (default: `ap-south-1`)

## Supported File Types

PDF, DOCX, TXT
