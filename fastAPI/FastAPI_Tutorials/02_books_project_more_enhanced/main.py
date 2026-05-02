# 02_books_project_more_enhanced/main.py -- FastAPI Enhanced: Pydantic, Path/Query Validation & Status Codes
# uvicorn main:app --reload
from fastapi import FastAPI, Path, Query, HTTPException
from starlette import status  # provides named HTTP status code constants (e.g. status.HTTP_200_OK)
from books import Book, BookRequest

app = FastAPI()

# =============================================
# IN-MEMORY DB: List of Book class objects
# =============================================
# Project 1 used a list of dicts -- this project uses a list of Book class objects.
# FastAPI auto-serialises class objects to JSON: each attribute becomes a JSON key.
books = [
    Book(1,"Computer Science pro","CodingwithRoby","Very Nice Book",5,2021),
    Book(2,"Be Fast with API","CodingwithRoby","Very great Book",5,2024),
    Book(3,"Master Endpoints","CodingwithRoby","Awesome Book",4,1923),
    Book(4,"HP1","author 1","Book Description",3,1967),
    Book(5,"HP2","author 2","Book Description",1,2000)
]

# =============================================
# STATUS CODES: Explicit HTTP response codes
# =============================================
# status_code= tells FastAPI what HTTP status to return on a successful response.
# Using starlette.status constants instead of raw integers (e.g. 200) makes intent clear.
# Common ones used here:
#   HTTP_200_OK       -> successful GET
#   HTTP_201_CREATED  -> successful POST (new resource created)
#   HTTP_202_ACCEPTED -> successful PUT / PATCH / DELETE
# If validation or auth fails, FastAPI handles the error codes automatically.
# =============================================
# NOTE: How FastAPI serialises class objects to JSON
# =============================================
# The books list contains Book objects (class instances), not dicts.
# FastAPI auto-converts them to JSON by reading each attribute as a key-value pair:
#   self.id    -> "id": 1
#   self.title -> "title": "Computer Science pro"   ...and so on
# The attribute NAME becomes the JSON key, the attribute VALUE becomes the JSON value.
# Object -> Dict -> JSON -- this is how FastAPI handles class objects in responses.
@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return books


# Path(gt=0) -- adds validation directly to the PATH param: book_id must be > 0.
# Same gt/lt syntax as Pydantic Field(), but applied to URL parameters instead of body fields.
# If validation fails, FastAPI auto-returns 422 Unprocessable Entity (no manual raise needed).
@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int = Path(gt=0)):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")

# Query(gt=0,lt=6) -- adds validation to the QUERY param: book_rating must be 1 to 5.
# URL: /books/?book_rating=4
# Path() for path params, Query() for query params -- same syntax, different decorator.
@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_book_by_rating(book_rating: int = Query(gt=0,lt=6)):
    rated_books = []
    for book in books:
        if book.rating == book_rating:
            rated_books.append(book)
    return rated_books


# =============================================
# HELPER: Auto-assign next sequential ID
# =============================================
# Books created via POST don't include an id (it's Optional in BookRequest).
def find_book_id(book: Book):
    if len(books) > 0:
        book.id = books[-1].id + 1
    else:
        book.id = 1
    return book


# =============================================
# POST: Create a new book
# =============================================
# Ques Why book_request is taken as request body not query or path param ? Ans: because it is a pydantic model and fastAPI auto detect it as request body, if it was a primitive type then we would have needed Body() to explicitly mark it as request body.
# How FastAPI decides parameter source -- by TYPE ANNOTATION, not by argument name:
#   Pydantic model (BookRequest)     -> automatically REQUEST BODY
#   Primitive type (int, str, etc.)  -> PATH param or QUERY param
#
# This is why book_request: BookRequest is read from the body without needing Body().
# Contrast with Project 1: dict is primitive-like, so Body() was needed explicitly.
# FastAPI auto-validates the request body against the BookRequest schema before this function runs. create_book() only executes if validation passes.

# Why Body() is NOT needed with Pydantic:
#   Simple types (int, str, bool, dict, list) -> query/path by default -> need Body() to force body
#   Pydantic models                           -> request body by default -> Body() unnecessary

@app.post("/create-book",status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    print(type(book_request))
    new_book = Book(**book_request.dict())
    print(type(new_book))
    books.append(find_book_id(new_book))

# =============================================
# NOTE: Why Book(**book_request.dict())?
# =============================================
# The in-memory list stores Book objects -- but create_book receives a BookRequest (Pydantic) object.
# To keep the list consistent, we convert BookRequest -> Book:
#
#   Step 1: book_request.dict()
#           Converts the Pydantic object to a plain Python dict.
#           {'id': None, 'title': 'New book', 'author': 'Author Name', ...}
#
#   Step 2: **book_request.dict()
#           ** (unpacking operator) explodes the dict into keyword arguments:
#           Book(id=None, title='New book', author='Author Name', ...)
#
#   Step 3: Book(...)
#           Creates a standard Book object -- same type as all other items in the list.
#
# Rule: Pydantic objects are validated at the boundary -- then converted to dict() or json()
#       to be passed into functions or stored elsewhere in the app.



# =============================================
# PATCH: Partial update -- only one field
# =============================================
# PATCH is for PARTIAL updates (one or a few fields), vs PUT which replaces the entire record.
# Best practice: create a separate minimal schema for each specific update operation.
#   - path param -> identifies WHICH resource to update (book_id)
#   - body       -> carries ONLY the fields being changed (description here)
#   - schema     -> should match the operation's intent (only the updatable field)
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


# enumerate(books) returns (index, book) tuples -- used to get the list index for pop().
# pop(i) removes AND returns the deleted book, so the response body shows what was deleted.
@app.delete("/books/{book_id}",status_code=status.HTTP_202_ACCEPTED)
async def delete_book(book_id: int = Path(gt=0)):
    for i, book in enumerate(books):
        if book.id == book_id:
            return books.pop(i)
    raise HTTPException(status_code=404, detail="Item not found")

# =============================================
# ASSIGNMENT SOLUTION: Filter by published_date
# =============================================
# published_date was added to both Book (plain class) and BookRequest (with Field validation).
# Path(gt=1900, lt=2026) validates the date range directly on the path param.

@app.get("/books/publish/{date}", status_code=status.HTTP_200_OK)
async def get_book_by_date(date: int = Path(gt=1900,lt=2026)):
    for book in books:
        if book.published_date == date:
            return book
    raise HTTPException(status_code=404, detail="Item not found")


# =============================================
# QUICK SYNTAX RECAP
# =============================================
# Path/Query validation -- same gt/lt syntax as Pydantic Field(), applied to URL params:
#   Path parameter:   book_id: int = Path(gt=0)           -> /books/{book_id}
#   Query parameter:  book_rating: int = Query(gt=0,lt=6) -> /books/?book_rating=4
#
# HTTPException -- raised when the requested resource doesn't exist.
# FastAPI catches it and returns the correct error status + detail message to the client:
#   raise HTTPException(status_code=404, detail="Item not found")
#   Import: from fastapi import HTTPException