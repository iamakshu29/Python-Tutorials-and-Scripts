# models.py -- SQLAlchemy DB Model: Todos Table Definition

# =============================================
# SQLALCHEMY MODEL: Class = Table
# =============================================
# A SQLAlchemy model class defines a DB TABLE.
#   Class           = Table      (Todos class = "todos" table in the DB)
#   Class attribute = Column     (self.title = "title" column)
#   Class instance  = Row/Record (Todos(title="Buy milk", ...) = one row in the table)
#
# SQLAlchemy reads these class definitions to:
#   1. Create the actual table in the DB (via Base.metadata.create_all in main.py)
#   2. Map query results back into Python objects (so you get a Todos object, not raw SQL rows)
#
# This is DIFFERENT from Todo.py (the Pydantic model):
#   models.py / Todos class  -> defines the DB TABLE schema (what gets stored)
#   Todo.py   / Todo class   -> validates the incoming REQUEST BODY (what the client sends)
# Both have similar-looking fields but serve completely different purposes.

from db import Base
from sqlalchemy import Column, Integer, String, Boolean


# =============================================
# TODOS TABLE: Column definitions
# =============================================
class Todos(Base):
    __tablename__ = "todos"  # actual SQL table name used in queries

    # primary_key=True -> uniquely identifies each row; DB auto-increments this value
    # index=True       -> DB creates an index on this column for faster lookups
    #                     without index: DB scans every row to find a match (slow on large tables)
    #                     with index:    DB jumps directly to the row (like a book index)
    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    description = Column(String)
    priority = Column(Integer)

    # default=False -> if complete is not provided at insert time, DB stores False automatically
    complete = Column(Boolean, default=False)

# =================================
# Other Column() parameters to know
# (used in later projects like 05_Auth)
# =================================

# nullable=False
#   makes the column REQUIRED at the DB level
#   if you try to insert a row without this column -> DB raises an error
#   default (without nullable=False) is nullable=True, meaning the column is optional (can be NULL)
#   example: title = Column(String, nullable=False)

# unique=True
#   DB enforces that no two rows can have the same value in this column
#   trying to insert a duplicate value -> DB raises IntegrityError
#   use for: email, username, phone number, national ID — anything that must be one-of-a-kind
#   example: email = Column(String, unique=True, nullable=False)

# ForeignKey("users.id")
#   links a column in THIS table to a primary key column in ANOTHER table
#   "users" is the name of the other table (__tablename__ = "users")
#   "id"    is the column in that table that we are referencing (must be primary key)
#   the DB will REJECT any insert/update where the value doesn't exist in the referenced table
#   this enforces referential integrity: e.g., a todo can't have an owner that doesn't exist in users
#   example: owner = Column(Integer, ForeignKey("users.id"), nullable=False)

# server_default (for date columns)
#   sets the default value at the DB server level (not Python level)
#   useful for auto-stamping rows with the current date/time on insert
#   example: created_at = Column(Date, server_default=func.current_date())

# onupdate (for datetime columns)
#   automatically updates the column value every time that row is updated
#   useful for tracking when a record was last modified
#   example: updated_at = Column(DateTime, onupdate=func.current_timestamp())
# Enum("High","Low","Medium") -> To store only specific values


# =============================================
# NOTE: Why id is NOT in Todo.py (Pydantic model)
# =============================================
# id is auto-assigned by the DB on every INSERT (auto-increment primary key).
# The client should never set or override it -- that would be a data integrity risk.
# So id lives only here (DB schema), not in the request validation model.
