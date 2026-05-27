from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, nullable = False, index = True)
    email = Column(String, unique=True, nullable = False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable = False)
    role = Column(Enum("Admin","User", name="user_role", create_type=True), nullable = False)
    subscription_type = Column(Enum("Basic","Premium",name="user_subscription", create_type=True),default="Basic", nullable = False)
    is_active = Column(Boolean, nullable = False, default = True)
    created_at = Column(DateTime(timezone=True),server_default=func.now(), nullable = False)