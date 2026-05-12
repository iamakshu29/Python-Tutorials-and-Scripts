from .todos import DbDependency, user_dependency
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from models import User
from pydantic import BaseModel, Field
from passlib.context import CryptContext

router = APIRouter(
    prefix = "/users", tags = ["user"]
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

# this endpoint should return all information about the user that is currently logged in.
@router.get("/logged_users")
async def get_logged_in_users_info(user: user_dependency,db: DbDependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        return db.query(User).filter(user["user_id"] == User.id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")


class TodoUpdateCred(BaseModel):
    password: str = Field(min_length = 7, description="Enter Current Password")
    new_password: str = Field(min_length = 7, description="Enter New Password")

# has error, username is not passed anywhere neither in func definition username: str = Path(min_length = 3)
@router.put("/user/update_creds/{username}")
async def update_creds(user: user_dependency, db: DbDependency, cred: TodoUpdateCred):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        user_data = db.query(User).filter(User.id == user.get("user_id")).first()

        if not bcrypt_context.verify(cred.password, user_data.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect current password")
        else:
            if bcrypt_context.verify(cred.new_password, user_data.hashed_password):
                raise HTTPException(status_code=401, detail="New Password can not be same as old Password")

            hashed_pass = bcrypt_context.hash(cred.new_password)
            user_data.hashed_password = hashed_pass
            db.add(user_data)  
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred {e}")

    return "Password Updated Succesfully"
