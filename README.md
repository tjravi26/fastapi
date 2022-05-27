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

@app.post("/posts")
async def create_posts(new_post: Post): # Here we reference the class 'Post'
	  print(new_post.dict()) # Since 'new_post' is a pydantic model, it has methods like 'dict()'
    return {"data": new_post}
```

### To store data locally instead of a database

- FastAPI has a serialising feature. It will automatically convert list, array, dicts to json while returning.

```python
my_posts = [
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

@app.post("/posts")
async def create_posts(post: Post):
    posts_dict = post.dict()
    posts_dict['id'] = randrange(0, 100000)
    my_posts.append(posts_dict)
    return {"data": posts_dict}
```

- The POST request must have a title and content which will be added to the above list.

### To get posts by ID

```python
...
def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post

@app.get("/posts/{id}")
async def get_post(id:int): # :int here will convert incoming data to integer
    post = find_post(id)
    return {"message": post}
```

### Return error code if post not found

```python
...
from fastapi import, status, HTTPException

@app.get("/posts/{id}")
async def get_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return {"message": post}
```

- ‘HTTPException’ is used to raise an HTTP error.
- ’status’ consists a list of error codes.

### To delete a post by ID

```python
...
from fastapi import Response

def get_post_index(id):
    for index, post in enumerate(my_posts):
        if post['id'] == id:
            return index

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    index = get_post_index(id)
    if index is not None:
        my_posts.pop(index)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

- First create a function which finds the post by id.
- Call the function and if post index found, delete it. Else, raise a HTTP exception error.

### To update a post by ID

```python
...
@app.put("/posts/{id}")
async def update_post(id: int, post: Post):
    index = get_post_index(id)
    if index is not None:
        post_dict = post.dict()
        post_dict["id"] = id
        my_posts[index] = post_dict
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return {"message": post_dict}
```

---

## Storing and manipulating data in a Database

### To connect to Postgres using Psycopg2

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

### To get all the posts from db:

```python
# Get all posts
@app.get("/posts")
async def posts():
    cursor.execute(""" SELECT * FROM quotes """)
    quotes = cursor.fetchall()
    return {"posts": posts}
```

### To create a post in the db:

```python
# Create posts
@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post):
    cursor.execute(
        """ INSERT INTO quotes (title, content) VALUES (%s, %s) RETURNING * """, (post.title, post.content))
    new_quotes = cursor.fetchone()
    conn.commit()
    return {"quotes": new_quotes}
```

### To get a post by ID from the db:

```python
# Get all posts by ID
@app.get("/posts/{id}")
async def get_post(id: int):
    cursor.execute("""SELECT * FROM quotes WHERE id = %s""", (str(id)))
    quote = cursor.fetchone()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return {"Quote": quote}
```

### To delete a post from the db:

```python
# Delete posts by ID
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    cursor.execute(
        """DELETE FROM quotes WHERE id = %s RETURNING *""", (str(id)))
    deleted_quote = cursor.fetchone()
    conn.commit()
    if deleted_quote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

### To update a post in the db:

```python
# Update posts by ID
@ app.put("/posts/{id}")
async def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE quotes SET title = %s, content = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, str(id)))
    updated_quotes = cursor.fetchall()
    conn.commit()
    if updated_quotes is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return {"Updated quotes": updated_quotes}
```
