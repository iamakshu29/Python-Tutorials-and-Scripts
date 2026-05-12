# routers/admin.py -- Admin-only router
# Routes here are restricted to users with role="admin".
# Unlike todos.py (which filters by owner), admin routes operate on ALL todos in the DB.
# The admin check is done manually inside each route by inspecting user.get("user_role").

# DbDependency   - the DB session dependency (reused from todos.py to avoid duplication)
# user_dependency - the JWT authentication dependency; injects the decoded token as a dict
from .todos import DbDependency, user_dependency

# APIRouter    - creates a mini-app with its own routes
# HTTPException - raises HTTP error responses
# Path         - validates and documents path parameters
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError

# Todos - the SQLAlchemy model representing the todos table
from models import Todos

# prefix="/admin"  -> all routes prefixed with /admin (e.g. GET /admin/, DELETE /admin/{id})
# tags=["admin"]   -> groups these routes under "admin" in Swagger UI docs
router = APIRouter(
    prefix="/admin", tags=["admin"]
)


# =============================================
# GET /admin/ -> return ALL todos across ALL users (admin only)
# =============================================
@router.get("/")
async def get_all_tasks(user: user_dependency, db: DbDependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        # role check: only proceed if the logged-in user is an admin
        # user_role is extracted from the JWT payload by get_current_user in auth.py
        if user.get("user_role") != "admin":
            return "User Not Authorized"  # non-admin users are rejected

        # no owner filter here — admin sees every todo in the DB regardless of who created it
        data = db.query(Todos).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    return data


# =============================================
# DELETE /admin/{todo_id} -> delete any todo by id (admin only)
# =============================================
@router.delete("/{todo_id}")
async def delete_all_tasks(user: user_dependency, db: DbDependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        if user.get("user_role") != "admin":
            return "User Not Authorized"

        # no owner filter — admin can delete any todo regardless of who owns it
        data = db.query(Todos).filter(Todos.id == todo_id).delete()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    if data == 0:  # 0 rows deleted means no todo with that id exists
        raise HTTPException(status_code=404, detail="Todo not found")