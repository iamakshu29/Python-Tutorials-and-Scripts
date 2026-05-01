# uvicorn main:app --reload
from fastapi import FastAPI, Body, HTTPException
from books import Book, BookRequest

app = FastAPI()

# project 1 we use the list of dict to populate item, but this time we take list of class object
books = [
    Book(1,"Computer Science pro","CodingwithRoby","Very Nice Book",5),
    Book(2,"Be Fast with API","CodingwithRoby","Very great Book",5),
    Book(3,"Master Endpoints","CodingwithRoby","Awesome Book",4),
    Book(4,"HP1","author 1","Book Description",3),
    Book(5,"HP2","author 2","Book Description",1)
]

# output will be list of dict as JSON format, fastAPI auto convert it into dict, whereas key = param name (example self.id -> id: 1)
@app.get("/books")
async def read_all_books():
    return books


@app.get("/books/{book_id}")
async def get_book_by_id(book_id: int):
    for book in books:
        if book.id == book_id:
            return book

@app.get("/books/")
async def get_book_by_rating(book_rating: int):
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
@app.post("/create-book")
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

@app.patch("/books/{book_id}")
async def update_book_description(book_id: int, data: BookUpdateDescription):
    for book in books:
        if book.id == book_id:
            book.description = data.description
            return book
    return {"error": "Book not found"}


# path param should identify resource
# body should carry update data only
# schema should match operation intent