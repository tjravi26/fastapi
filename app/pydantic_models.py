from pydantic import BaseModel, EmailStr


class Quote(BaseModel):  # This is a pydantic model.
    person: str
    content: str


class QuoteResponse(BaseModel):
    id: int
    person: str
    content: str

    class Config:
        orm_mode = True


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
