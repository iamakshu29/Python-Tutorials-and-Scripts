# to make our URL string, connect to our FastAPI app to our DB, we use SQL Lite
# Also To open the DB connection, close the DB connection, able to create some tables 
# Installing SQL Alchemy, which is an ORM, whiich is what our fastAPI app will use and able to create a conn to DB and all other functions of DB
# pip install sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"
# this url is going to be used to create a location of this database on our fastAPI Application.

# to create a engine of our DB
engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread': False})

# now we create a session local, and each instance of the session local will have a db session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create a DB object
Base = declarative_base()


# SQL 
"""

insert into todos (title, description, priority, complete)
values ("Go to Store","To pick up eggs",4,False)

select * from todos;
select title from todos;
select * from todos where priority = 5;

update todos set complete = True where id = 5;

delete from todos where id = 5;

"""