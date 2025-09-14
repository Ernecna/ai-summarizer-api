# Dockerfile
FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Sistemde sık gereken paketler (psycopg ve uvicorn derdi yaşamamak için)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

# Bağımlılıklar
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY ./app /app/app
COPY ./alembic.ini /app/
COPY ./migrations /app/migrations/
# Eğer app kökünde ise:
# COPY . /app

# (Varsa) model indirici scriptini kodlar kopyalandıktan sonra çağır
# RUN python download_model.py

# Güvenlik için non-root kullanıcı (isteğe bağlı)
RUN addgroup --system app && adduser --system --group app && chown -R app:app /app
USER app

EXPOSE 8000

# CMD'yi boş bırakıyoruz; Koyeb servisinde komutu override edeceğiz
