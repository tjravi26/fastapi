from pydantic import BaseModel, EmailStr


class Post(BaseModel):  # This is a pydantic model.
    title: str
    content: str


class PostResponse(BaseModel):
    content: str

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserCreateResponse(BaseModel):
    email: str

    class Config:
        orm_mode = True
