# app/api/__init__.py
from fastapi import APIRouter

from app.api.v1 import auth, users, notes

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(notes.router, prefix="/notes", tags=["Notes"])
