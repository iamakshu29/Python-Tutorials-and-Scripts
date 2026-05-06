# Steps to Implement Cursor-Based (nextPageToken style)
    # Step 1 — Create a new route separate from the offset one, same fake data.
    # Step 2 — Accept an optional next_page_token query param that defaults to None (meaning first page).
    # Step 3 — Decode the token — for simplicity, treat it as the last seen id from the previous page. If None, start from the beginning.
    # Step 4 — Filter your list to only return items whose id is greater than the last seen id, then take only limit items.
    # Step 5 — Generate the next token from the last item in the current page's results and include it in the response. If no more items exist, return null.
    # Step 6 — Test it by taking the next_page_token from the response and manually passing it into the next request.

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
    next_page_token: int | None = Query(default=None)
):
    start_index = 0

# if next_page_token has value
# then 
# find the index it matches and then show the result from index + 1 to limit. if it doesnot able to find return empty list []
    if next_page_token is not None:
        for index, item in enumerate(users_list):
            if item.get("user_id") == next_page_token:
                start_index = index + 1
                break
        else:
            return {"data":[], "pagination": {"error": "invalid cursor"}}

    
# For first time result next_page_token = None default value
# we print the elements till limit and next_page_token = last user_id of result.
    page = users_list[start_index:start_index + limit]
    next_page_token = page[-1]["user_id"] if page else None

    return {
        "data": page,
        "pagination": {
            "total": len(users_list),
            "limit": limit,
            "has_next": (start_index + limit) < len(users_list),
            "next_page_token": next_page_token
        }
    }

# http://localhost:8000/users?limit=20
# http://localhost:8000/users?limit=10&next_page_token=120
# http://localhost:8000/users?limit=21&next_page_token=130

# Add summary like though the concept or idea is correct but next_page_token didnot take the value from data...it is like timestamp or whatever it is