class Book:
    def __init__(self, id, title, author, description, rating,published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


# With Pydantic, attributes must be defined as class attributes (at class level):
# Pydantic enforces a strict, schema-based contract that locks down the exact number of keys, the names of those keys, and the specific data types they must hold.
""" 

Here is how Pydantic behaves differently than standard Python classes regarding parameters:

1. Passing Extra Parameters (During Creation)
If you try to pass an extra, undefined parameter when creating the object, Pydantic will by default silently **drop/ignore** it. It won't let it sneak into your object or your JSON.


book = BookModel(id=1, title="HP1", is_bestseller=True)

# The resulting JSON will completely ignore 'is_bestseller'
print(book.model_dump()) # Output: {'id': 1, 'title': 'HP1'}
```
*(Note: You can even configure Pydantic with `extra = "forbid"` so that passing an extra parameter immediately crashes the app with a `ValidationError` instead of just ignoring it!)*

2. Dynamically Adding Parameters (After Creation)
Unlike standard Python objects where you can just invent new variables out of thin air, Pydantic actively overrides this behavior and puts a lock on the object. 

If you try to dynamically add a property that wasn't defined in the class:

book = BookModel(id=1, title="HP1")
# Trying to add a dynamic key later
book.new_dynamic_key = "Hello" 

Pydantic will immediately throw an error and crash: ValueError: "BookModel" object has no field "new_dynamic_key"
 Summary
By using Pydantic, your `BookModel` acts as an absolute, strict contract. It guarantees that the JSON leaving your API will have **exactly** the keys you defined—nothing missing, and nothing extra.
"""

# Pydantic is a library that is used for data modeling, data parsing and error handling
# commonly used as resource for data validation and how to handle data coming to our FastAPI application

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# we are inherting BaseModel here.
# to add validation to our data we use Field()
class BookRequest(BaseModel):
    # id: Optional[int] = None # type hinting syntax, no Pydantic
    id: Optional[int] = Field(description='ID not needed on create', default=None) # Pydantic syntax, so that user also know that is optional
    title: str = Field(min_length=4, max_length=100)
    author: str = Field(min_length=1, max_length=30)
    description: str = Field(min_length=4, max_length=100)
    rating: int = Field(gt=0,lt=6) # 1 and 5
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

# why to use json_schema_extra and not just default for all values
# default should not be used for required values, can be used for optional values
# if somehow user misses the field then it shoudl give error but default will fills the value for user (which the API shouldn't, its a bad API design)
# the behaviour might looks same in Swagger because its a frontend, but in backend its different.
# Backend (Pydantic behavior)
# example → implies fields should be provided as it is ignored during validation
# default → makes fields optional and used if field is missing

# default will affect the backend
# json_schema_extra just shows a sample request body in Swagger UI
# also notice that we didn't add id key in json_schema, as that optional....