# app/schemas/token.py
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema for the JWT access token response.
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema for the data embedded within a JWT token (the payload).
    """
    # Using Optional[str] is compatible with older Python versions
    email: Optional[str] = None