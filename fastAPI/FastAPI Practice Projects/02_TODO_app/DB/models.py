from datetime import timedelta, date
from .db import Base
from sqlalchemy import ForeignKey,Enum, Column, Integer, String, Boolean, Date, func, Float, DateTime, text

class Todos(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum("Pending", "In Progress", "Completed", create_type=True), default="Pending",nullable=False, index=True)
    priority = Column(Enum("High", "Low", "Medium", create_type=True), nullable=False)
    due_date = Column(Date, server_default=text("(DATE('now', '+7 days'))"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    user_id = Column(Integer,ForeignKey("users.id"), nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False)

# use Enum for list of Specific Values
# create_type=True tells SQLAlchemy to create a custom ENUM type in the database when you run migrations.
# SQLite / MySQL don't need it