# 02_books_project_more_enhanced/books.py -- Data Models: Plain Class & Pydantic Validation

# =============================================
# PLAIN PYTHON CLASS: Book (no validation)
# =============================================
# A standard Python class used as the in-memory data model.
# No type enforcement here -- whatever you pass in gets stored as-is.
# FastAPI auto-serialises class objects to JSON by reading their attributes:
#   self.id -> "id": 1,  self.title -> "title": "...",  etc.
class Book:
    def __init__(self, id, title, author, description, rating,published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


# =============================================
# PYDANTIC: What it is and how it differs from a plain class
# =============================================
# Pydantic is a data validation library. In FastAPI it is used to:
#   - Validate incoming request body fields (type, length, range, etc.)
#   - Auto-generate API docs (Swagger) based on the model schema
#   - Parse and serialise data between Python and JSON
#
# KEY DIFFERENCES from a plain Python class:
#
# DIFFERENCE 1 -- Extra params passed during object creation:
#   Plain class: accepts any args, stores them all.
#   Pydantic:    silently DROPS undefined fields by default.
#     book = BookModel(id=1, title="HP1", is_bestseller=True)
#     book.model_dump() -> {'id': 1, 'title': 'HP1'}  <- is_bestseller gone
#   To raise a ValidationError instead: set extra = "forbid" in model_config.
#
# DIFFERENCE 2 -- Adding attributes dynamically after creation:
#   Plain class: book.new_key = "Hello"  <- works fine
#   Pydantic:    book.new_key = "Hello"  <- raises ValueError -- field not defined in schema
#
# Result: your API always returns EXACTLY the fields you defined -- nothing missing, nothing extra.
#
# NOTE: Attributes must be defined as CLASS-LEVEL annotations (not inside __init__).
# Pydantic enforces a strict schema-based contract: exact keys, exact types, no extras.

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# =============================================
# PYDANTIC MODEL: BookRequest (with validation)
# =============================================
# Used to validate the REQUEST BODY when creating a book.
# Inherits BaseModel from Pydantic -- this is what makes it a Pydantic model.
# Field() adds validation rules on top of the type hint:
#   min_length / max_length  -- string length constraints
#   gt (greater than) / lt (less than) -- numeric range constraints (exclusive)
class BookRequest(BaseModel):
    # Plain type hint without Pydantic: id: Optional[int] = None -- just marks it optional, no schema
    id: Optional[int] = Field(description='ID not needed on create', default=None)  # optional -- not sent on create
    title: str = Field(min_length=4, max_length=100)
    author: str = Field(min_length=1, max_length=30)
    description: str = Field(min_length=4, max_length=100)
    rating: int = Field(gt=0,lt=6)  # accepts 1 to 5 (exclusive: >0 and <6)
    published_date: int = Field(gt=1900, lt=2026)

    model_config = {
        "json_schema_extra": {
            "example" : {
                "title": "New book",
                "author": "Author Name",
                "description":"Book Description",
                "rating":4,
                "published_date":2029
            }
        }
    }

# =============================================
# NOTE: json_schema_extra vs default -- key difference
# =============================================
# json_schema_extra:
#   - Only affects SWAGGER UI (the interactive docs frontend)
#   - Shows a sample request body to guide the user -- ignored by Pydantic during validation
#   - Fields in the example are still REQUIRED -- Pydantic will error if they're missing
#
# default:
#   - Affects the BACKEND (Pydantic validation)
#   - Makes the field OPTIONAL -- if client doesn't send it, Pydantic fills it with the default
#   - Bad practice for required fields: API should reject missing data, not silently fill it
#
# Rule: use default ONLY for genuinely optional fields (like id on create).
#       use json_schema_extra to show sample values in Swagger without affecting validation.
# Note: id is not included in the example because it's optional (has default=None).