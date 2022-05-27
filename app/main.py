from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str


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
        time.sleep(2)

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


def find_post(id):
    for post in my_posts:
        if post["id"] == int(id):
            return post


def get_post_index(id):
    for index, post in enumerate(my_posts):
        if post['id'] == id:
            return index


# Root page
@app.get("/")
async def root():
    return {"message": "Hello World"}


# Get all posts
@app.get("/posts")
async def posts():
    cursor.execute(""" SELECT * FROM quotes """)
    posts = cursor.fetchall()
    return {"posts": posts}


# Create posts
@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post):
    cursor.execute(
        """ INSERT INTO quotes (title, content) VALUES (%s, %s) RETURNING * """, (post.title, post.content))
    new_quotes = cursor.fetchone()
    conn.commit()
    return {"data": new_quotes}


# Get all posts by ID
@app.get("/posts/{id}")
async def get_post(id: int):
    cursor.execute("""SELECT * FROM quotes WHERE id = %s""", (str(id)))
    quote = cursor.fetchone()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return {"Quote": quote}


# Delete posts by ID
@ app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    cursor.execute(
        """DELETE FROM quotes WHERE id = %s RETURNING *""", (str(id)))
    deleted_quote = cursor.fetchone()
    conn.commit()
    if deleted_quote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"A quote with the id: {id} was not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
