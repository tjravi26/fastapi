from fastapi import Depends, status, HTTPException, APIRouter, Response
from typing import List
from sqlalchemy.orm import Session
from .. import models, pydantic_models
from ..database import get_db


router = APIRouter(
    prefix="/quotes",
    tags=["Quotes"]
)


# Get all quotes
@router.get("/", response_model=List[pydantic_models.QuoteResponse])
async def quotes(db: Session = Depends(get_db)):
    quotes = db.query(models.Quote).all()
    return quotes


# Create quotes
@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=pydantic_models.QuoteResponse)
async def create_quotes(post: pydantic_models.Quote,
                        db: Session = Depends(get_db)):
    # This will unpack the request data as a dictionary.
    new_quote = models.Quote(**post.dict())
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    return new_quote


# Get quotes by ID
@router.get("/{id}", response_model=pydantic_models.QuoteResponse)
async def get_quote(id: int, db: Session = Depends(get_db)):
    quote = db.query(models.Quote).filter(models.Quote.id == id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return quote


# Delete quotes by ID
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
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
@router.put("/{id}", response_model=pydantic_models.QuoteResponse)
async def update_quote(id: int, post: pydantic_models.Quote,
                       db: Session = Depends(get_db)):
    quote_query = db.query(models.Quote).filter(models.Quote.id == id)
    quote = quote_query.first()
    if quote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    quote_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return quote_query.first()
