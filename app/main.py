from fastapi import FastAPI
from .database import engine
from . import models
from .routes import quotes, users


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

app.include_router(quotes.router)
app.include_router(users.router)


# Root page
@app.get("/")
async def root():
    return {"message": "Hello World"}
