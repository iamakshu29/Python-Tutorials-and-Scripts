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
# Other parameters used in Column()
# =================================
# nullable=False # For required values, True is default i.e. empty value provide Null
# Column(Date,server_default=func.current_timestamp())
# Column(DateTime,onupdate=func.current_timestamp())
# Column(Date,onupdate=func.current_date())


# =============================================
# NOTE: Why id is NOT in Todo.py (Pydantic model)
# =============================================
# id is auto-assigned by the DB on every INSERT (auto-increment primary key).
# The client should never set or override it -- that would be a data integrity risk.
# So id lives only here (DB schema), not in the request validation model.
