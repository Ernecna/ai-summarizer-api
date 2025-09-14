# Dockerfile
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Eğer prod dosyasına geçtiysen:
# COPY requirements-prod.txt /app/
# RUN pip install --no-cache-dir -r requirements-prod.txt

# Tek dosya ile gidiyorsan:
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama
COPY ./app /app/app
COPY ./alembic.ini /app/
COPY ./migrations /app/migrations/

# Non-root (opsiyonel)
RUN addgroup --system app && adduser --system --group app && chown -R app:app /app
USER app

EXPOSE 8000
# CMD yok; Koyeb’de komutu override ediyoruz
