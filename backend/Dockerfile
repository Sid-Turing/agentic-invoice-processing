# Backend: FastAPI + Strands agent (Python 3.11)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# poppler-utils is required by pdf2image for PDF rendering
RUN apt-get update \
    && apt-get install -y --no-install-recommends poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy source and install the package (+ runtime deps) from pyproject
COPY . .
RUN pip install --upgrade pip && pip install .

EXPOSE 8010

# Apply migrations (creates the schema on an empty DB), then serve.
# Reference data is seeded on startup by the app (skip-if-exists).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8010"]
