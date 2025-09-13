# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Ana router'ı uygulamaya dahil et
# Tüm endpoint'ler /api/v1 prefix'i ile başlayacak
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}