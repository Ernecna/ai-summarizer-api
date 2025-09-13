# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Veritabanı URL'sini config dosyamızdan alıyoruz
# Bu URL, docker-compose içindeki PostgreSQL container'ına işaret ediyor.
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# SQLAlchemy motorunu oluşturuyoruz.
# pool_pre_ping=True, veritabanı bağlantılarının havuzdan alınmadan önce
# hala aktif olup olmadığını kontrol eder. Bu, bağlantı kopması
# gibi sorunları önler.
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Veritabanı oturumları (session) oluşturmak için bir fabrika (factory)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM modellerimizin miras alacağı temel sınıf (base class)
# Tüm modellerimiz bu Base sınıfından türeyecek.
Base = declarative_base()

# --- BU SATIRLARI EKLE ---
# SQLAlchemy'nin ilişkileri kurabilmesi için tüm modellerin Base tarafından
# tanınması gerekir. Modelleri buraya import etmek bu işlemi garantiler.
from app.models.user import User
from app.models.note import Note

# FastAPI'nin Bağımlılık Enjeksiyonu (Dependency Injection) sistemi için
# kullanılacak fonksiyon. Her bir API isteği için yeni bir veritabanı
# oturumu açar ve istek bittiğinde (başarılı veya hatalı) oturumu kapatır.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()