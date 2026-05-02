# uvicorn main:app --reload
from fastapi import FastAPI, Path, Query, HTTPException
from starlette import status # used to set Status Code Responses Explicitly 
from books import Book, BookRequest

app = FastAPI()

# project 1 we use the list of dict to populate item, but this time we take list of class object
books = [
    Book(1,"Computer Science pro","CodingwithRoby","Very Nice Book",5,2021),
    Book(2,"Be Fast with API","CodingwithRoby","Very great Book",5,2024),
    Book(3,"Master Endpoints","CodingwithRoby","Awesome Book",4,1923),
    Book(4,"HP1","author 1","Book Description",3,1967),
    Book(5,"HP2","author 2","Book Description",1,2000)
]

# output will be list of dict as JSON format, fastAPI auto convert it into dict, whereas key = param name (example self.id -> id: 1)
@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return books


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int = Path(gt=0)):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_book_by_rating(book_rating: int = Query(gt=0,lt=6)):
    rated_books = []
    for book in books:
        if book.rating == book_rating:
            rated_books.append(book)
    return rated_books


# creating a func to adding serialized id
def find_book_id(book: Book):
    if len(books) > 0:
        book.id = books[-1].id + 1
    else:
        book.id = 1
    return book


# explain this
# book_request: BookRequest -> type hinting book_request is of type BookRequest. For example count: int
# why book_request is taken as request body , not as query parameter? Asking because we are not specifically defining that it is query or it is request body
# because Because FastAPI doesn’t decide parameter source based on the name (book_request). It decides based on the type annotation.
# fastAPI use that rule
# if Pydantic model → request body
# if Primitive type (int, str, etc.) → path/query (depending on route)
# the type should be compatible to become a parameter like str, int then only it taken as paramter (either path or query), and if its object or Pydantic model then its taken as request body.

# Another ques in 01_project, when we are using the dict for in-memory DB and in post req we using this to ask for request body --> async def add_book(new_book: dict = Body()):
# but when we send Pydantic model we we are not using Body () .....WHY ??
# Why Body() is unnecessary with Pydantic ??
# FastAPI has this rule:
    # Simple types (int, str, bool, etc.) → query parameters by default
    # Pydantic models → request body by default
    # Explicit Body() → only needed when:
        # 1. Using raw types (dict, list, etc.)
        # 2. Adding extra validation/config (e.g., embed=True, examples)

@app.post("/create-book",status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    print(type(book_request))
    new_book = Book(**book_request.dict())
    print(type(new_book))
    books.append(find_book_id(new_book))

# The already present books are of data type - Class Book, but because of using Pydantic validation their data-type will be class BookRequest. So to make the data type same i.e. class Book , we write the code below.
# explanation
# book_request is of type BookRequest (a Pydantic model), which is used for validating the data sent in the Request body.
# book_request.dict() -> converts the validated data from a Pydantic Object into a standard Python dict.
# ** -> the unpacking operator. It takes the dictionary's key-value pairs and unpacks them into keyword arguments (kwargs).
# Book(...) -> means we are creating a new Book object using those unpacked arguments.
#
# complete process:
# book_request is first converted to a dict(), then the ** operator unpacks that dict into keyword arguments, and finally those arguments are used to create a new Book Object. 
# Note: Pydantic objects are typically converted into dict() or json() formats to be used elsewhere.



# if we updating single field then use separate single schema for it.
from pydantic import BaseModel
class BookUpdateDescription(BaseModel):
    description: str

@app.patch("/books/{book_id}",status_code=status.HTTP_202_ACCEPTED)
async def update_book_description(data: BookUpdateDescription,book_id: int = Path(gt=0)):
    book_changed = False
    for book in books:
        if book.id == book_id:
            book.description = data.description
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        return book


# path param should identify resource
# body should carry update data only
# schema should match operation intent

@app.delete("/books/{book_id}",status_code=status.HTTP_202_ACCEPTED)
async def delete_book(book_id: int = Path(gt=0)):
    for i, book in enumerate(books):
        if book.id == book_id:
            return books.pop(i)
    raise HTTPException(status_code=404, detail="Item not found")


"""
Assignment
    Add a new field to Book and BookRequest called published_date: int (for example, published_date: int = 2012).
    Enhance each Book to now have a published_date
    Then create a new GET Request method to filter by published_date
"""

@app.get("/books/publish/{date}", status_code=status.HTTP_200_OK)
async def get_book_by_date(date: int = Path(gt=1900,lt=2026)):
    for book in books:
        if book.published_date == date:
            return book
    raise HTTPException(status_code=404, detail="Item not found")


# How we added the validation in class using Pydantic
# Similarly we can add the validation in Paramters in both Path as well as Query
# SYNTAX 

# PAth parameter
# @app.get("/books/{book_id}")
# async def get_book_by_id(book_id: int = Path(gt=0)):

# Query Paramter
# @app.get("/books/")
# async def get_book_by_rating(book_rating: int = Query(gt=0,lt=6)):


# Adding HTTP Exception 
# by import HTTPException from fastapi 
# and raise it 
# Example
# @app.get("/books/{book_id}")
# async def get_book_by_id(book_id: int = Path(gt=0)):
#     for book in books:
#         if book.id == book_id:
#             return book
#     raise HTTPException(status_code=404, detail="Item not found")