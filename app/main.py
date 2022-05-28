from fastapi import FastAPI
from .database import engine
from . import models
from .routers import quotes, users, auth


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(quotes.router)
app.include_router(users.router)
app.include_router(auth.router)


# Root page
@app.get("/")
async def root():
    return {"message": "Hello World"}
