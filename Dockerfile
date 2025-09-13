# Dockerfile (NİHAİ VERSİYON)

FROM python:3.11-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Adım 1: Bağımlılıkları kur (Docker cache'inden en iyi şekilde faydalanmak için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Adım 2: AI Modelini indir ve imajın içine kaydet
COPY download_model.py .
RUN python download_model.py

# Adım 3: Proje kodunu kopyala
# Her şeyi ayrı ayrı kopyalamak, worker.py hatasını kesin olarak çözer.
COPY ./app /app/app
COPY ./worker.py /app/
COPY ./alembic.ini /app/
COPY ./migrations /app/migrations/

EXPOSE 8000