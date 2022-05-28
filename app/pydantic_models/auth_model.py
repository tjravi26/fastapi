from typing import Optional
from pydantic import BaseModel, EmailStr


class UserLoginAuth(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    token_type: str
    access_token: str


class TokenData(BaseModel):
    id: Optional[str] = None
