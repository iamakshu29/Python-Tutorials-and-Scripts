# 01_books_project_basic/books.py — FastAPI Basics: CRUD Operations

# =============================================
# HOW TO RUN
# =============================================
# Development (auto-reload on save):  uvicorn books:app --reload
# Production:                         fastapi run books.py

from fastapi import FastAPI, HTTPException, Body

app = FastAPI()

books = [
            {"id":0,"title":"title one","author":"author one","category":"Maths"},
            {"id":1,"title":"title two","author":"author two","category":"Chemistry"},
            {"id":2,"title":"title three","author":"author three","category":"Physics"},
            {"id":3,"title":"title two","author":"author three","category":"Biology"},
            {"id":4,"title":"title four","author":"author two","category":"Chemistry"}
        ]
# FastAPI auto-converts dicts to JSON in responses, so we can return the books list directly as JSON.


# =============================================
# GET REQUEST METHOD
# =============================================
# Returns all books in the list as JSON.
@app.get("/books")
async def read_all_books():
    return books


# =============================================
# PATH PARAMS: Variable segments in the URL path
# =============================================
# Syntax: define {param_name} in the route → FastAPI extracts it → passed to the function arg.
# Flow: /books/id/2  →  book_id = 2 (extracted from path)  →  books[2] (returned)
#
# URL encoding: spaces are encoded as %20 in URLs.
#   /books/title/title%20one  →  book_title = "title one"
#
# RULE 1 — Always type-hint path params (book_id: int).
#   FastAPI treats ALL path params as strings by default.
#   Without ": int", book_id would be "2" (str) and books[book_id] would fail
#   because a list index must be an int, not a string.
@app.get("/books/id/{book_id}")
async def get_book_by_id(book_id: int):
    if book_id < 0 or book_id >= len(books):
        raise HTTPException(status_code=404, detail="Book not found")
    return books[book_id]

# casefold() is like lower() but more aggressive -- also handles international characters
# (French accents, German umlauts, etc.) beyond basic ASCII. Safer than lower() for comparisons.
@app.get("/books/title/{book_title}")
async def get_book_by_title(book_title: str):
    for book in books:
        if book.get("title","title one").casefold() == book_title.casefold():
            return book
        else:
            return {"title": "not found"}

# =============================================
# PATH PARAMS -- RULE 2: Route order matters
# =============================================
# FastAPI does NOT match routes purely in the order they are defined.
# It first tries to match by path STRUCTURE -- static (fixed) paths beat dynamic ones.
# BUT if two routes are equally dynamic and can match the same URL, the one defined FIRST wins.
#
# Safe rule: always define SPECIFIC routes BEFORE GENERIC dynamic ones.
# Example:
#   /books/category/   <- specific static path -- define FIRST
#   /books/{author}    <- generic dynamic path -- define AFTER
# If you flip the order, /books/category/ would be captured by /books/{author}
# with author = "category" -- wrong match.



# =============================================
# QUERY PARAMS: key=value pairs after "?" in the URL
# =============================================
# URL format: /books/category/?category=Chemistry
# FastAPI auto-reads function args that are NOT present in the URL path as query params.
# They are REQUIRED by default — add a default value (= None) to make them optional.
@app.get("/books/category/")
async def get_book_by_category(category: str):
    books_to_return = []
    for book in books:
        if book.get("category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# =============================================
# PATH PARAM vs QUERY PARAM — How FastAPI decides
# =============================================
# FastAPI checks whether the function argument name appears in the URL path pattern.
#   - Arg is in the path (e.g., {author})  → PATH param  (extracted from URL segment)
#   - Arg is NOT in the path               → QUERY param (read from ?key=value)
#
# If a function has multiple args and only SOME appear in the path,
# the rest are automatically treated as query params.
#
# Example below: {author} is in the path → path param
#                category is NOT in path  → query param
# Full URL: /books/author two?category=Chemistry
@app.get("/books/{author}")
async def get_book_by_author_and_category(author: str,category: str):
    books_to_return = []
    for book in books:
        if book.get("author").casefold() == author.casefold() and book.get("category").casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return



# =============================================
# POST REQUEST METHOD: Add a new book
# =============================================
# Sample request body: {"id":6,"title":"title five","author":"author five","category":"Computer Science"}
#
# Body() tells FastAPI to read this parameter from the REQUEST BODY, not from the URL.
# Must be imported: from fastapi import Body
# Body() and Body(...) behave identically — both mark the param as required from the request body.
#
# Why Body() is needed here:
#   `dict` is a primitive-like type — FastAPI won't auto-detect it as a request body.
#   Explicit Body() is required for raw types like dict, list.
#   Pydantic models are auto-detected as body without Body() — covered in Project 2 main.py.
@app.post("/books/add_book")
async def add_book(new_book: dict = Body()):
    books.append(new_book)
    return books

# =============================================
# PUT REQUEST METHOD: Replace an existing book
# =============================================
# Pass the full updated book object in the request body — matched by id, then replaced entirely.
@app.put("/books/update_book")
async def update_author(updated_book: dict = Body()):
    for i in range(len(books)):
        if books[i].get("id") == updated_book.get("id"):
            books[i] = updated_book


# =============================================
# NOTE: Common PUT mistake — don't change the match field
# =============================================
# We search/match books by "id" — so the updated_book MUST keep the SAME id as the original.
# If you change the id in your update payload (e.g., id:1 → id:8):
#   - The list still has id:1
#   - Your updated_book has id:8
#   - if condition never matches → no update happens
# Rule: the field you use to FIND the record must remain unchanged in the update payload.
# This problem is not faced when using DBs with auto-generated IDs — you typically don't include the ID in the update payload at all, just the fields to change.


# =============================================
# DELETE REQUEST METHOD: Remove a book by ID
# =============================================
# We iterate using index i → use books.pop(i) to remove by list INDEX (not by id value).
@app.delete("/books/delete_book")
async def update_book(book_id: int):
    for i in range(len(books)):
        if books[i].get("id") == book_id:
            books.pop(i)
            return f"{book_id} deleted successfully"
    return {"error": "book not found"}


# =============================================
# NOTE: Why books.pop(book_id) is WRONG
# =============================================
# pop(n) removes by LIST INDEX, not by id value.
#   1. IDs may not be sequential integers — could be random numbers like 204, 87, etc.
#   2. Even if IDs start sequential (0,1,2...), after any deletion index and id go out of sync:
#        Before delete: index 0 → id 0,  index 1 → id 1,  index 2 → id 2
#        After deleting id 1:  index 0 → id 0,  index 1 → id 2   ← mismatch
#      So pop(id_value) would now delete the WRONG book.
# Always search by id to get the LIST INDEX, then pop that index.
#
# =============================================
# NOTE: Why return after pop is necessary
# =============================================
# After books.pop(i), the list shrinks by 1.
# Continuing the for loop on a smaller list risks IndexError or skipping items.
# return exits the function immediately — correct and clean.