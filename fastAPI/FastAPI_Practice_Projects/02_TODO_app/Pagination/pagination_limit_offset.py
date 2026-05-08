# Steps to Implement Limit/Offset Pagination in FastAPI
    # Step 1 — Create a basic FastAPI app with a /users route that returns a hardcoded list of 50–100 fake users all at once.
    # Step 2 — Add limit and offset as query parameters to that route with some default values.
    # Step 3 — Slice your list using those two values to return only a portion of the data.
    # Step 4 — Add metadata to your response like total, limit, offset, and a has_next boolean so the caller knows if more data exists.
    # Step 5 — Test it in your browser or Swagger UI (/docs) by changing limit and offset values manually and observing the output.

from fastapi import Query
from fastapi import FastAPI
from starlette import status

app = FastAPI()

users_list = [
    {"user_id":101,"name":"user-101"},{"user_id":102,"name":"user-102"},{"user_id":103,"name":"user-103"},
    {"user_id":104,"name":"user-104"},{"user_id":105,"name":"user-105"},{"user_id":106,"name":"user-106"},
    {"user_id":107,"name":"user-107"},{"user_id":108,"name":"user-108"},{"user_id":109,"name":"user-109"},
    {"user_id":110,"name":"user-110"},{"user_id":111,"name":"user-111"},{"user_id":112,"name":"user-112"},
    {"user_id":113,"name":"user-113"},{"user_id":114,"name":"user-114"},{"user_id":115,"name":"user-115"},
    {"user_id":116,"name":"user-116"},{"user_id":117,"name":"user-117"},{"user_id":118,"name":"user-118"},
    {"user_id":119,"name":"user-119"},{"user_id":120,"name":"user-120"},{"user_id":121,"name":"user-121"},
    {"user_id":122,"name":"user-122"},{"user_id":123,"name":"user-123"},{"user_id":124,"name":"user-124"},
    {"user_id":125,"name":"user-125"},{"user_id":126,"name":"user-126"},{"user_id":127,"name":"user-127"},
    {"user_id":128,"name":"user-128"},{"user_id":129,"name":"user-129"},{"user_id":130,"name":"user-130"},
    {"user_id":131,"name":"user-131"},{"user_id":132,"name":"user-132"},{"user_id":133,"name":"user-133"},
    {"user_id":134,"name":"user-134"},{"user_id":135,"name":"user-135"},{"user_id":136,"name":"user-136"},
    {"user_id":137,"name":"user-137"},{"user_id":138,"name":"user-138"},{"user_id":139,"name":"user-139"},
    {"user_id":140,"name":"user-140"},{"user_id":141,"name":"user-141"},{"user_id":142,"name":"user-142"},
    {"user_id":143,"name":"user-143"},{"user_id":144,"name":"user-144"},{"user_id":145,"name":"user-145"},
    {"user_id":146,"name":"user-146"},{"user_id":147,"name":"user-147"},{"user_id":148,"name":"user-148"},
    {"user_id":149,"name":"user-149"},{"user_id":150,"name":"user-150"}
]


@app.get("/users",status_code=status.HTTP_200_OK)
def get_users(
    limit: int = Query(gt=0,default=10), 
    offset: int = Query(ge=0,default=0)
):
    end = offset + limit
    page_data = users_list[offset:end]

    response = {
        "data": page_data,
        "pagination": {
            "total": len(users_list),
            "limit": limit,
            "offset": offset,
            "has_next": (offset + limit) < len(users_list)
        }
    }
    return response

# http://localhost:8000/users             → first 10
# http://localhost:8000/users?offset=10   → next 10
# http://localhost:8000/users?limit=5&offset=20  → 5 items from position 20