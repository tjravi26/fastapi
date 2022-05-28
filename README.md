# FastAPI Basics

---

- Installation - `$ pip install fastapi\[all\]`

### Basic folder structure

```python
./app
├── __init__.py # an empty py file
└── main.py # contains the app
```

### Basic route

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/") # Called path operation
async def root():
    return {"message": "Hello World"} # FastAPI automatically converts this to json.
```

- To run the app in the terminal `$ uvicorn app.main:app --reload `

### To create POST request

```python
...
from fastapi import Body

@app.post("/createposts")
async def create_posts(payLoad: dict = Body(...)):
    return {"new_post": f"{payLoad}"}
```

### Pydantic library

- Pydantic is a data validation and settings management using python type annotations.
  - Used to force the client to send the POST request body in a specific format.

```python
...
from pydantic import BaseModel

class Post(BaseModel): # Pydantic will use this model to check the post body format.
    title: str
    content: str
    # If user doesn't provide, the default is set to True.
    published: bool = True
    # If user doesn't provide, the default is set to None.
    rating: Optional[int] = None

@app.post("/quote")
async def create_posts(new_post: Quote): # Here we reference the class 'Quote'
	  print(new_quote.dict()) # Since 'new_quote' is a pydantic model, it has methods like 'dict()'
    return {"data": new_quote}
```

### To store data locally instead of a database

- FastAPI has a serialising feature. It will automatically convert list, array, dicts to json while returning.

```python
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

@app.post("/quotes")
async def create_posts(quote: Quote):
    quotes_dict = quote.dict()
    quotes_dict['id'] = randrange(0, 100000)
    my_quotes.append(quotes_dict)
    return {"data": quotes_dict}
```

- The POST request must have a title and content which will be added to the above list.

### To get quote by ID

```python
...
def find_quote(id):
    for quote in my_quotes:
        if quote["id"] == id:
            return quote

@app.get("/quotes/{id}")
async def get_quote(id:int): # :int here will convert incoming data to integer
    quote = find_quote(id)
    return {"message": quote}
```

### Return error code if quote not found

```python
...
from fastapi import, status, HTTPException

@app.get("/quotes/{id}")
async def get_quote(id: int):
    quote = find_quote(id)
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return {"message": quote}
```

- ‘HTTPException’ is used to raise an HTTP error.
- ’status’ consists a list of error codes.

### To delete a quote by ID

```python
...
from fastapi import Response

def get_quotes_index(id):
    for index, quote in enumerate(my_quotes):
        if quote['id'] == id:
            return index

@app.delete("/quotes/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(id: int):
    index = get_quote_index(id)
    if index is not None:
        my_quotes.pop(index)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

- First create a function which finds the quote by id.
- Call the function and if quote index found, delete it. Else, raise a HTTP exception error.

### To update a quote by ID

```python
...
@app.put("/quotes/{id}")
async def update_quote(id: int, quote: Quote):
    index = get_quote_index(id)
    if index is not None:
        quote_dict = quote.dict()
        quote_dict["id"] = id
        my_quotes[index] = quote_dict
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return {"message": quote_dict}
```

---

## Storing and manipulating data in a PostgresDB using Psycopg2

```python
import psycopg2
from psycopg2.extras import RealDictCursor # Used to show column names in output.
import time # Will be used for refreshing connection.
...
while True:
    try:
        conn = psycopg2.connect(host='localhost',
                                database='fastapi',
                                user='postgres',
                                password='7890',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Successfully connected to the database.')
        break
    except Exception as error:
        print("Connection to the database failed.")
        print("Error: ", error)
        time.sleep(2) # Will try to reconnect to database every 2 seconds.
```

### To get all the quotes from db:

```python
# Get all quotes
@app.get("/quotes")
async def quotes():
    cursor.execute(""" SELECT * FROM quotes """)
    quotes = cursor.fetchall()
    return {"quotes": quotes}
```

### To create a quote in the db:

```python
# Create quotes
@app.post("/quotes", status_code=status.HTTP_201_CREATED)
async def create_quotes(quote: Quote):
    cursor.execute(
        """ INSERT INTO quotes (title, content) VALUES (%s, %s) RETURNING * """, (quote.name, quote.content))
    new_quotes = cursor.fetchone()
    conn.commit()
    return {"quotes": new_quotes}
```

### To get a quote by ID from the db:

```python
# Get all quotes by ID
@app.get("/quotes/{id}")
async def get_quote(id: int):
    cursor.execute("""SELECT * FROM quotes WHERE id = %s""", (str(id)))
    quote = cursor.fetchone()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return {"Quote": quote}
```

### To delete a quote from the db:

```python
# Delete quotes by ID
@app.delete("/quotes/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(id: int):
    cursor.execute(
        """DELETE FROM quotes WHERE id = %s RETURNING *""", (str(id)))
    deleted_quote = cursor.fetchone()
    conn.commit()
    if deleted_quote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

### To update a quote in the db:

```python
# Update quotes by ID
@ app.put("/quotes/{id}")
async def update_quote(id: int, quote: Quote):
    cursor.execute(
        """UPDATE quotes SET title = %s, content = %s WHERE id = %s RETURNING *""",
        (quote.name, quote.content, str(id)))
    updated_quotes = cursor.fetchall()
    conn.commit()
    if updated_quotes is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return {"Updated quotes": updated_quotes}
```

---

## Storing and manipulating data in a PostgresDB using SQLAlchemy

- **Don’t try to mug up the shit below. Just copy and paste**.
- Create two new python files.

```python
./app
├── database.py # connects the app to Postgres using SQLAlchemy
└── models.py # contains the database models
```

### To connect to Postgres using SQLAlchemy:

```python
# ./app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'postgres://<username>:<password>@<ip_address>/<db_name>'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### To create database models:

```python
# .app/models.py

from .database import Base
from sqlalchemy import Column, Integer, String

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Import the database and models into main:

```python
# .app/main.py
...
from fastapi import Depends
from .database import engine, get_db
from . import models

models.Base.metadata.create_all(bind=engine)
```

- SQLAlchemy has a limitation. It can create new db.
  - But if we change the db schema in the `models.py` file, it won’t update the db.
  - To do this we must use - Alembic - a database migration tool.

### To add a new quote:

```python
# .app/main.py

# Create quotes
@app.post("/quotes", status_code=status.HTTP_201_CREATED)
async def create_quotes(quote: Quote, db: Session = Depends(get_db)):
    # This will unpack the request data as a dictionary.
    new_quote = models.Quote(**quote.dict())
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    return {"Quote": new_quote}
```

### To get a quote by ID:

```python
# .app/main.py

# Get quotes by ID
@app.get("/quotes/{id}")
async def get_quote(id: int, db: Session = Depends(get_db)):
    quote = db.query(models.Quote).filter(models.Quote.id == id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return {"Quote": quote}
```

### To delete a quote by ID:

```python
# .app/main.py

# Delete quotes by ID
@ app.delete("/quotes/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(id: int, db: Session = Depends(get_db)):
    quote = db.query(models.Quote).filter(models.Quote.id == id)
    if quote.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    quote.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

### To update a quote by ID:

```python
# .app/main.py

# Update a quote by ID
@app.put("/quotes/{id}")
async def update_quote(id: int, quote: Quote, db: Session = Depends(get_db)):
    quote_query = db.query(models.Quote).filter(models.Quote.id == id)
    quote = quote_query.first()
    if quote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    quote_query.update(quote.dict(), synchronize_session=False)
    db.commit()
    return {"Updated quote": quote_query.first()}
```

### To create a response model

    * Move the pydantic model from `main.py` into a new `pydantic_models.py` and import them into `main.py`

```python
# .app/pydantic_models.py

from pydantic import BaseModel

class Quote(BaseModel):  # This is a pydantic model.
    name: str
    content: str

class QuoteResponse(BaseModel):
	  name: str
    content: str
    class Config:
        orm_mode = True
```

- Import these models into `main.py`

```python
from . import pydantic_models
```

```python
# To create a new quote
@app.post("/quotes", response_model=pydantic_models.QuoteResponse)
```

---

## User registration model

```python
# .app/models.py
...
class User(Base): # This creates a user registration model
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
```

### User registration form pydantic model:

```python
# .app/pydantic_models.py
...
class UserCreate(BaseModel):
    email: str
    password: str

class UserCreateResponse(BaseModel):
    email: str
    class Config:
        orm_mode = True
```

### To create a new user:

```python
# .app/main.py

@app.post("/users", status_code=status.HTTP_201_CREATED,
          response_model=pydantic_models.UserCreateResponse)
async def create_user(user: pydantic_models.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
```

---

## Securing information with Hashing

- PassLib is a great Python package to handle password hashes.
- It supports many secure hashing algorithms and utilities to work with them.
- The recommended algorithm is “Bcrypt”.
- `$ pip install passlib\[bcrypt\]`

```python
# Create a file under .app/utils.py
# .app/utils.py
from passlib.context import CryptContext

# schemes tells passlib which hashing algorithm to use.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)
```

```python
# .app/main.py
...
from .utils import hash_password # new

# User registration
@app.post("/users", status_code=status.HTTP_201_CREATED,
          response_model=pydantic_models.UserCreateResponse)
async def create_user(user: pydantic_models.UserCreate,
                      db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password) # new
    user.password = hashed_password # new
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
```

### To get user information by ID:

- Create a new pydantic model for user info response.

```python
# .app/pydantic_models.py

class UserGetResponse(BaseModel):
    email: EmailStr
    class Config:
        orm_mode = True
```

```python
# .app/main.py

# Get user information
@app.get("/users/{id}", response_model=pydantic_models.UserGetResponse)
async def users(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the userID: {id} does not exist.")
    return user
```

---

## Refactoring code using APIRouter

```python
# new app structure

./app
├── __init__.py
├── database.py
├── main.py
├── models.py
├── pydantic_models.py
├── routes # shifted path operations this folder.
│   ├── quotes.py
│   └── users.py
└── utils.py
```

```python
# .app/main.py

from fastapi import FastAPI
from .database import engine
from . import models
from .routes import quotes, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(quotes.router) # new
app.include_router(users.router) # new

# Root page
@app.get("/")
async def root():
    return {"message": "Hello World"}
```

```python
# .app/routes/quotes.py

from fastapi import Depends, status, HTTPException, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, pydantic_models
from ..database import get_db

router = APIRouter( # new
    prefix="/quotes",
    tags=['Quotes ']
)

# Get all quotes
@router.get("/quotes", response_model=List[pydantic_models.QuoteResponse])
async def quotes(db: Session = Depends(get_db)):
    quotes = db.query(models.Quote).all()
    return quotes

# Create quotes
@router.post("/quotes", status_code=status.HTTP_201_CREATED,
             response_model=pydantic_models.QuoteResponse)
async def create_quotes(quote: pydantic_models.Quote,
                        db: Session = Depends(get_db)):
    # This will unpack the request data as a dictionary.
    new_quote = models.Quote(**quote.dict())
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    return new_quote

# Get quotes by ID
@router.get("/quotes/{id}", response_model=pydantic_models.QuoteResponse)
async def get_quote(id: int, db: Session = Depends(get_db)):
    quote = db.query(models.Quote).filter(models.Quote.id == id).first()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return quote

# Delete quotes by ID
@router.delete("/quotes/{id}", status_code=status.HTTP_204_NO_CONTENT)
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
@router.put("/quotes/{id}", response_model=pydantic_models.QuoteResponse)
async def update_quote(id: int, quote: pydantic_models.Quote,
                       db: Session = Depends(get_db)):
    quote_query = db.query(models.Quote).filter(models.Quote.id == id)
    quote = quote_query.first()
    if quote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    quote_query.update(quote.dict(), synchronize_session=False)
    db.commit()
    return quote_query.first()
```

```python
# .app/routes/users.py

from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, pydantic_models, utils
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter( # new
    prefix="/users",
    tags=['Users']
)
# User registration
@router.post("/users", status_code=status.HTTP_201_CREATED,
             response_model=pydantic_models.UserCreateResponse)
async def create_user(user: pydantic_models.UserCreate,
                      db: Session = Depends(get_db)):
    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Get user information
@router.get("/users/{id}", response_model=pydantic_models.UserGetResponse)
async def users(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the userID: {id} does not exist.")
    return user
```

---

## Using JWT Authentication

[image:252A67DE-1B7C-4337-9DD7-A645815C1170-27025-000057FB21503F11/Screenshot 2022-05-28 at 11.09.09 AM.jpg]

- Install `python-jose` to generate and verify the JWT tokens in Python.
  `$ pip install python-jose\[\cryptography]`

### Create a `utils.py` for password hashing

```python
# .app/utils.py

from passlib.context import CryptContext

# schemes tells passlib which hashing algorithm to use.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str): # Creates password hash
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password): # Verifies password hash
    return pwd_context.verify(plain_password, hashed_password)
```

### Create a `oauth2.py` file for creating a JWT token

```python
# .app/oauth2.py

from jose import jwt, JWTError
from datetime import datetime, timedelta

# To create a SECRET_KEY type `$ openssl rand -hex 32` in the terminal.
SECRET_KEY = "89e792e7589cb77ca7ea5758e3aa305e8aa45e93e945c205f31974ed03582571"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=[ALGORITHM])
    return encoded_jwt
```

### Create a router file for authentication

```python
# .app/routers/auth.py

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, utils, oauth2
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    tags=['Authentication']
)

@router.post("/login")
async def login_authentication(
        user_credentials: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"token_type": "bearer",
            "access_token": access_token}
```

### Import the `auth.py` into `main.py`

```python
# .app/main.py
...
from .routers import auth

app.include_router(auth.router)
```

- Now to get user bearer token, select type `form-data` to send user info in Postman instead of raw json.

### To verify user token:

```python
# .app/oauth2.py
...
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
    return verify_access_token(token, credentials_exception)
```

- To send Bearer token through Postman, use Headers instead of body.

### To set access token automatically in Postman

- The collection must be in an environment.
