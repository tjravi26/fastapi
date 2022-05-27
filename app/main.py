from fastapi import FastAPI, Response, status, HTTPException, Depends
from .database import engine, get_db
from . import models, pydantic_models
from sqlalchemy.orm import Session
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


my_quotes = [
    {
        "title": "This is her 1st quote.",
        "content": "Beauty comes from within.",
        "id": 1
    },
    {
        "title": "This is her 2nd quote.",
        "content": "If not me, who? If not now, when?",
        "id": 2
    },
    {
        "title": "This is her 3rd quote.",
        "content": "Girls should never be afraid to be smart.",
        "id": 3
    },
    {
        "title": "This is her 4th quote.",
        "content": "The less you reveal, the more people can wonder.",
        "id": 4
    },
    {
        "title": "This the her 5th quote.",
        "content": "Feeling beautiful has nothing to do with what you look like, I promise.",
        "id": 5
    }

]


# Root page
@app.get("/")
async def root():
    return {"message": "Hello World"}


# Get all quotes
@app.get("/quotes", response_model=List[pydantic_models.PostResponse])
async def quotes(db: Session = Depends(get_db)):
    quotes = db.query(models.Quote).all()
    return quotes


# Create quotes
@app.post("/quotes", status_code=status.HTTP_201_CREATED,
          response_model=pydantic_models.PostResponse)
async def create_quotes(post: pydantic_models.Post,
                        db: Session = Depends(get_db)):
    # This will unpack the request data as a dictionary.
    new_quote = models.Quote(**post.dict())
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    return new_quote


# Get quotes by ID
@app.get("/quotes/{id}", response_class=pydantic_models.PostResponse)
async def get_quote(id: int, db: Session = Depends(get_db)):
    quote = db.query(models.Quote).filter(models.Quote.id == id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return quote


# Delete quotes by ID
@app.delete("/quotes/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(id: int, db: Session = Depends(get_db)):
    quote = db.query(models.Quote).filter(
        models.Quote.id == id)
    if quote.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    quote.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Update a quote by ID
@app.put("/quotes/{id}", response_model=pydantic_models.PostResponse)
async def update_quote(id: int, post: pydantic_models.Post,
                       db: Session = Depends(get_db)):
    quote_query = db.query(models.Quote).filter(models.Quote.id == id)
    quote = quote_query.first()
    if quote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    quote_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return quote_query.first()
