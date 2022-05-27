from pydantic import BaseModel


class Post(BaseModel):  # This is a pydantic model.
    title: str
    content: str


class PostResponse(BaseModel):
    content: str

    class Config:
        orm_mode = True
