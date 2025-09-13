# app/schemas/token.py
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    # Bu şema, JWT token'ın içine gömdüğümüz verinin yapısını temsil eder.
    # Şimdilik sadece email yeterli, ileride roller veya izinler de eklenebilir.
    email: str | None = None
