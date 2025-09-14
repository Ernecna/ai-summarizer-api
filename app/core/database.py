# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# .env değil, Koyeb environment'ından geliyor
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL  # <— asıl URL

# Neon için query string’inde sslmode=require zaten var
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()