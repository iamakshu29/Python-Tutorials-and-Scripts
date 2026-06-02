# using limit_offset Pagination

from pydantic import BaseModel, Field
from math import ceil

class Pagination(BaseModel):
    page: int = Field(ge=1,default=1)
    limit: int = Field(ge=1,le=50,default=10)


def paginate(pagination: Pagination, data):

    offset = (pagination.page - 1) * pagination.limit
    end =  offset + pagination.limit
    page_data = data[offset:end]
    total = len(data)

    # Using DB Queries
    # items = query.offset((page - 1) * limit).limit(limit).all()

    response = {
        "data": page_data,
        "pagination":{
            "total": total,
            "limit": pagination.limit,
            "page": pagination.page,
            "has_next": end < total,
            "has_previous": pagination.page > 1,
            "total_pages": ceil(total/pagination.limit)
        }
    }

    return response