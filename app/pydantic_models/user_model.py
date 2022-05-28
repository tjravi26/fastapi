from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserCreateResponse(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class UserGetResponse(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True
