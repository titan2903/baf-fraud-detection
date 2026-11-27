FROM python:3.12-slim

# libgomp1: runtime OpenMP yang dibutuhkan LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY app ./app
COPY models/lgbm_fraud.joblib ./models/

RUN useradd -r -u 1001 appuser
USER appuser

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# API_KEY diberikan saat docker run (--env-file .env berisi API_KEY=...), tidak disimpan di image
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
