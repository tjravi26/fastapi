from pydantic import BaseModel


class Quote(BaseModel):  # This is a pydantic model.
    person: str
    content: str


class QuoteResponse(BaseModel):
    id: int
    person: str
    content: str
    owner_id: int

    class Config:
        orm_mode = True
