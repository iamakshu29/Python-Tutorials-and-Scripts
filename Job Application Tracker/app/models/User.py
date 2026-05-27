from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, nullable = False, index = True)
    email = Column(String, unique=True, nullable = False, index=True)

    # Google Auth users have no password
    hashed_password = Column(String, nullable = True)

    google_id = Column(String, unique = True, nullable = True)
    role = Column(Enum("Admin","User", name="user_role", create_type=True), nullable = False)
    is_active = Column(Boolean, nullable = False, default = True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable = False)
    # think of adding username later....
