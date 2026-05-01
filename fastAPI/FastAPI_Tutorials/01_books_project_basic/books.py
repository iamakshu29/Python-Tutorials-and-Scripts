# uvicorn books:app --reload

# To run in production mode
# fastapi run books.py

from fastapi import FastAPI, HTTPException, Body

app = FastAPI()

books = [
            {"id":0,"title":"title one","author":"author one","category":"Maths"},
            {"id":1,"title":"title two","author":"author two","category":"Chemistry"},
            {"id":2,"title":"title three","author":"author three","category":"Physics"},
            {"id":3,"title":"title two","author":"author three","category":"Biology"},
            {"id":4,"title":"title four","author":"author two","category":"Chemistry"}
        ]
# ==========================GET REQUEST METHOD==================================
# simple get request which return books
@app.get("/books")
async def read_all_books():
    return books

# --------------Path paramters----------------

# %20 means space -> title%20one = title one
# explain below function also ..how id goes from path -> func args -> return value
@app.get("/books/id/{id}")
async def get_book_by_id(id: int):
    if id < 0 or id >= len(books):
        raise HTTPException(status_code=404, detail="Book not found")
    return books[id]

# casefold() is like lower() but more powerful and also used for itnernational text like french chars and other including basic english ones. or ASCII
@app.get("/books/title/{book_title}")
async def get_book_by_title(book_title: str):
    for book in books:
        if book.get("title","title one").casefold() == book_title.casefold():
            return book
        else:
            return {"title": "not found"}

# rewrite the below things as comment properly for notes.
# as per above 2 path parameters func.str
# specify 2 things, 
# first 
# its very vvv important to provide the proper variable type hints, using static typing.  like (id: int) as id is int in books list
# as FastAPI treats path parameters as strings by default.
# Second
# we can't have same type of path 
# In FastAPI, routes aren’t matched purely by chronological order, but the order you define them does matter when there’s ambiguity. 
# FastAPI first tries to match paths based on their structure—static (fixed) paths are more specific than dynamic ones—but, 
# if two routes can both match the same request (like `/items/special` and `/items/{item_id}`), then the one declared earlier will be used. 
# This means you can have similar-looking endpoints, but you must avoid overlaps where a dynamic parameter could accidentally capture a value meant for a specific route. 
# A safe pattern is to define more specific routes first or make your paths more explicit so they don’t conflict.




# --------------Query paramters----------------

# paratmeters that attached after ? and have key=value pairs -> "/books/?category=math"
# give some details about query params and explain below 

@app.get("/books/category/")
async def get_book_by_category(category: str):
    books_to_return = []
    for book in books:
        if book.get("category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# add comments about how to diff between path and query params in fast API
# as per me
# if func args is also in path - path params, if its only in func arg then its query param
# if there is one arg in path and rest are not then remaining are treated as query params and that particular arg is treated as path params. 
# Below as example

@app.get("/books/{author}")
async def get_book_by_author_and_category(author: str,category: str):
    books_to_return = []
    for book in books:
        if book.get("author").casefold() == author.casefold() and book.get("category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return



# ==========================POST REQUEST METHOD==================================
# {"id":6,"title":"title five","author":"author five","category":"Computer Science"}

# explain this...Body() meaning also Body(...) and Body() works same ..also add that we need to import Body from fastapi
@app.post("/books/add_book")
async def add_book(new_book: dict = Body()):
    books.append(new_book)
    return books

# ==========================PUT REQUEST METHOD==================================
@app.put("/books/update_book")
async def update_author(updated_book: dict = Body()):
    for i in range(len(books)):
        if books[i].get("id") == updated_book.get("id"):
            books[i] = updated_book

# One asshole mistake which I was doing is ....whatever field is used to search the data, I am updating the same field 
# in above example, we are filter out using id and I am updating its id only, so it is not able to find the field again .. So no update happened

# let say {id:1} so with update body I pasted the same {id:1} and update it to {id:8}. If condition never matches
# as it will never able to find the id:8 so no update will take place


# ==========================DELETE REQUEST METHOD==================================
@app.delete("/books/delete_book")
async def update_book(book_id: int):
    for i in range(len(books)):
        if books[i].get("id") == book_id:
            books.pop(i)
            return f"{book_id} deleted successfully"
    return {"error": "book not found"}

# Why not books.pop(book_id)?

# Because:
# First, the id might be random integer also
# Second, even if the id is serial wise, after deleting anyone of the book the index and id got mismatch
# index 0 - id 0, index 0 - id 1, index 0 - id 2
# after removing book with id 1
# index 0 - id 0, index 1 - id 2 (mismatch) so always take index

# Why need return or break?
# You need break or return not because of deletion itself, but to avoid continuing iteration on a list whose size has reduced or changed.