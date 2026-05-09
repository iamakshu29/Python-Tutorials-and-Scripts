# models.py (05_Auth) - SQLAlchemy DB model definitions
# This builds on 03_Setting_up_DB/models.py — new concepts introduced here:
#   nullable=False, unique=True, ForeignKey
# See 03_Setting_up_DB/models.py for full explanation of Column, primary_key, index, default

# ForeignKey - enforces a relationship between two tables at the DB level
#              a column marked with ForeignKey("table.column") can only hold values
#              that already exist in the referenced table's column
#              the DB will REJECT an insert/update if the referenced value doesn't exist
from db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    complete = Column(Boolean, default=False)

    # ForeignKey("users.id") -> "users" is the table name, "id" is the primary key of that table
    # this means: every todo MUST belong to a user that already exists in the users table
    # if you try to insert a todo with an owner id that doesn't exist in users -> DB error
    # this enforces referential integrity: no orphan todos without a valid owner
    owner = Column(Integer, ForeignKey("users.id"), nullable=False)


# =============================================
# USERS TABLE
# =============================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    # we NEVER store plain-text passwords in DB
    # the actual password is hashed (via bcrypt) before saving - see auth.py
    hashed_password = Column(String, nullable=False)

    # default=True -> new users are active by default; can be set to False to deactivate/ban
    is_active = Column(Boolean, default=True)

    # role stores a string like "admin" or "user" to control access levels
    role = Column(String, nullable=False)
    