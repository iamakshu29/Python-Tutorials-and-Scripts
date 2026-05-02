# db.py -- Database Setup: Engine, Session & Base

# =============================================
# WHAT IS AN ORM? (SQLAlchemy)
# =============================================
# ORM = Object Relational Mapper.
# Instead of writing raw SQL strings inside Python code, you work with Python classes & objects.
# SQLAlchemy translates those into SQL and executes them against the DB automatically.
#
# You already know SQL -- SQLAlchemy just lets you do the same things using Python:
#   SQL: SELECT * FROM todos          ->  db.query(Todos).all()
#   SQL: INSERT INTO todos VALUES ...  ->  db.add(todo_model)
#   SQL: DELETE FROM todos WHERE ...   ->  db.query(Todos).filter(...).delete()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# =============================================
# DATABASE URL: Connection string
# =============================================
# Tells SQLAlchemy which DB engine to use and where the DB is located.
# SQLite format:  sqlite:///./filename.db  (creates the file in the current directory)
# Other DBs:      postgresql://user:password@localhost/dbname
#                 mysql://user:password@localhost/dbname
SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"


# =============================================
# ENGINE: Core connection to the DB
# =============================================
# create_engine() sets up the connection pool -- the permanent bridge between Python and the DB file.
# Only one engine is created for the entire app lifetime (created once at startup).
#
# connect_args={'check_same_thread': False} is SQLite-specific:
#   SQLite by default restricts its connection to the thread that opened it.
#   FastAPI handles requests across multiple threads, so we disable this restriction.
#   Not needed for PostgreSQL or MySQL.
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})


# =============================================
# SESSION: A single unit of work with the DB
# =============================================
# A Session is a temporary workspace for one request:
#   - you stage changes (add, update, delete) inside it
#   - nothing is written to the DB until you call commit()
#   - if something goes wrong, you call rollback() to undo all staged changes
#
# sessionmaker() creates a Session CLASS (a factory), not a session instance yet.
# Each incoming request gets its own fresh session via get_db() in main.py.
#
# autocommit=False -> we manually control when to commit (safer, gives transaction control)
# autoflush=False  -> SQLAlchemy won't auto-sync pending changes before queries
#                     we commit explicitly after the route succeeds (handled in get_db)
# bind=engine      -> every session created from this factory uses our engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================
# BASE: Parent class for all DB model classes
# =============================================
# declarative_base() returns a Base class that all SQLAlchemy model classes must inherit from.
# When a class does class Todos(Base) as in models.py, SQLAlchemy registers it and learns its table name and columns.
# Base.metadata.create_all(bind=engine) in main.py then uses this registry to create tables in the DB.
Base = declarative_base()


# =============================================
# SQL QUICK REFERENCE
# =============================================
# Useful commands to seed/test data directly in the DB:
#
# INSERT:  insert into todos (title, description, priority, complete)
#          values ("Go to Store", "To pick up eggs", 4, False)
#
# SELECT:  select * from todos;
#          select title from todos;
#          select * from todos where priority = 5;
#
# UPDATE:  update todos set complete = True where id = 5;
#
# DELETE:  delete from todos where id = 5;
