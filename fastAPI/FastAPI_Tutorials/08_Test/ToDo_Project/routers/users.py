# routers/users.py -- User self-service router
# Routes here let a logged-in user view their own profile and update their own password.
# All routes are protected: a valid JWT token is required.

# DbDependency   - the DB session dependency (reused from todos.py)
# user_dependency - the JWT authentication dependency (injects decoded token as dict)
from .todos import DbDependency, user_dependency

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy.exc import SQLAlchemyError

# User - the SQLAlchemy model representing the "users" table
from models import User

# BaseModel, Field - Pydantic tools for defining and validating request body models
from pydantic import BaseModel, Field

# CryptContext - used here independently to verify/hash passwords for credential updates
from passlib.context import CryptContext

# prefix="/users"  -> all routes prefixed with /users
# tags=["user"]    -> groups routes under "user" in Swagger UI docs
router = APIRouter(prefix="/users", tags=["user"])

# separate CryptContext instance for this router (same config as auth.py)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =============================================
# GET /users/logged_users -> return profile of the currently logged-in user
# =============================================
# this endpoint only returns data for the user whose JWT token is in the request
# it does NOT accept a username/id parameter — the identity comes from the token
@router.get("/logged_users")
async def get_logged_in_users_info(user: user_dependency, db: DbDependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        # filter users table by the id extracted from the JWT (user["user_id"])
        # .first() returns the single matching user row (id is unique primary key)
        return db.query(User).filter(user["user_id"] == User.id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")


# =============================================
# Pydantic model for password update request
# =============================================
class TodoUpdateCred(BaseModel):
    # current password to verify the user actually owns the account before changing it
    password: str = Field(min_length=7, description="Enter Current Password")
    # the new password to replace the old one
    new_password: str = Field(min_length=7, description="Enter New Password")


# =============================================
# PUT /users/user/update_creds/{username} -> update the logged-in user's password
# =============================================
# NOTE: {username} is declared in the URL path but not used in the function — it's a bug.
#       The user identity already comes from the JWT (user_dependency), so the path
#       parameter is redundant. It should either be removed from the route or added
#       as a function argument: username: str = Path(min_length=3)
@router.put("/update_creds/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def update_creds(
    username: str, user: user_dependency, db: DbDependency, cred: TodoUpdateCred
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        # fetch the currently logged-in user's DB record using their id from the JWT
        user_data = db.query(User).filter(User.id == user.get("user_id")).first()

        # step 1: verify the current password matches what's stored in DB
        # if it doesn't match -> reject (prevents someone else changing the password)
        if not bcrypt_context.verify(cred.password, user_data.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect current password")
        else:
            # step 2: ensure the new password is different from the current one
            # bcrypt_context.verify(new_password, stored_hash) checks if they match
            if bcrypt_context.verify(cred.new_password, user_data.hashed_password):
                raise HTTPException(
                    status_code=401,
                    detail="New Password can not be same as old Password",
                )

            # step 3: hash the new password and update the DB record
            hashed_pass = bcrypt_context.hash(cred.new_password)
            user_data.hashed_password = hashed_pass
            db.add(user_data)  # re-stage; committed in get_db() after route completes

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")
