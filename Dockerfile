FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=3000 \
    ACTACITE_DB_PATH=/app/data/actacite.sqlite3

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx tesseract-ocr libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data && chmod -R 755 /app

EXPOSE 3000
CMD ["python", "start.py"]
