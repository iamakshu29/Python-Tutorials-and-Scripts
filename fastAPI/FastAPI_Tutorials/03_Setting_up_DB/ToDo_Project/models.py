# models is a way for SQL Alchemy to be able to understand what kind of DB tables we are going to creating withing our DB in the future.
# DB model is an actual record that is inside a DB table

from db import Base
from sqlalchemy import Column, Integer, String, Boolean

class Todos(Base):
    __tablename__ = "todos" # table name inside DB

# Column Names
    id = Column(Integer,primary_key=True, index=True) # can be indexable, used for performance increasing
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)


# here the fields are present, which should be present in DB