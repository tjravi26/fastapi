from pydantic import BaseModel


class Post(BaseModel):  # This is a pydantic model.
    title: str
    content: str
