from .todos import DbDependency, user_dependency
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from models import Todos

router = APIRouter(
    prefix = "/admin", tags = ["admin"]
)

@router.get("/")
async def get_all_tasks(user: user_dependency,db: DbDependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        if user.get("user_role") != "admin":
            return "User Not Authorized"
        data = db.query(Todos).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")
    return data

@router.delete("/{todo_id}")
async def delete_all_tasks(user: user_dependency,db: DbDependency, todo_id: int = Path(gt = 0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        if user.get("user_role") != "admin":
            return "User Not Authorized"
        data = db.query(Todos).filter(Todos.id == todo_id).delete()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")
    if data == 0:
        raise HTTPException(status_code=404, detail="Todo not found")