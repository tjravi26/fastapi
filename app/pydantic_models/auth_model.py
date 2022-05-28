from pydantic import BaseModel, EmailStr


class UserLoginAuth(BaseModel):
    email: EmailStr
    password: str
