# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.api import api_router

# Initialize the FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Include the main API router
# All routes from api_router will be prefixed with /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}