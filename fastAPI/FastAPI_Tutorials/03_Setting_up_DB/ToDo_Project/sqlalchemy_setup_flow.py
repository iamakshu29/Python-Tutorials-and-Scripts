# sqlalchemy_setup_flow.py -- How to Configure a SQL DB with SQLAlchemy (Step-by-Step)

# =============================================
# THE FLOW: 7 steps, always in this order
# =============================================
#
#   STEP 1: DB URL          (db.py)
#   STEP 2: ENGINE          (db.py)
#   STEP 3: SESSION FACTORY (db.py)
#   STEP 4: BASE CLASS      (db.py)
#   STEP 5: MODELS          (models.py)
#   STEP 6: TABLE CREATION  (main.py -- one line at startup)
#   STEP 7: SESSION PER REQUEST (main.py -- get_db())
#
# Steps 1-4 are always in db.py (setup file).
# Step 5 is in models.py (one file per group of related tables, or one file for all).
# Steps 6-7 are in main.py (app entry point).


# =============================================
# STEP 1: DB URL -- which DB and where
# =============================================
# The connection string tells SQLAlchemy two things:
#   - WHICH database engine to use (sqlite, postgresql, mysql, etc.)
#   - WHERE the database is (file path, host, port, credentials)
#
# SQLite  (file-based, no server needed, good for dev/learning):
#   "sqlite:///./todos.db"         -> creates todos.db in the current directory
#
# PostgreSQL (server-based, used in production):
#   "postgresql://user:password@localhost:5432/dbname"
#
# MySQL:
#   "mysql+pymysql://user:password@localhost:3306/dbname"
#
# KEY POINT: This is the ONLY thing that changes when you switch databases.
# All the remaining steps are identical regardless of which SQL DB you use.

# SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"


# =============================================
# STEP 2: ENGINE -- permanent connection to the DB
# =============================================
# create_engine() creates a CONNECTION POOL -- a set of reusable connections
# that stay open for the lifetime of the app (not per-request).
# Think of it as the permanent bridge between your Python code and the DB.
# Created ONCE at startup, shared across all requests.
#
# connect_args={'check_same_thread': False}
#   -> SQLite-specific only. SQLite restricts its connection to one thread by default.
#   -> FastAPI uses multiple threads, so we disable this restriction.
#   -> Not needed for PostgreSQL or MySQL.

# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})


# =============================================
# STEP 3: SESSION FACTORY -- template for per-request sessions
# =============================================
# sessionmaker() creates a SESSION CLASS (a factory/template), not a session instance.
# Each incoming HTTP request calls this factory to get its own fresh session.
#
# A Session = a temporary workspace for ONE request:
#   - Stage changes inside it (db.add, db.delete)
#   - Nothing hits the DB until db.commit() is called
#   - If something goes wrong -> db.rollback() undoes everything staged in this session
#   - When done -> db.close() releases the connection back to the pool
#
# autocommit=False -> we manually call commit() after the route succeeds (via get_db)
# autoflush=False  -> SQLAlchemy won't auto-sync staged changes before queries
# bind=engine      -> links this session factory to our engine (connection pool)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================
# STEP 4: BASE CLASS -- registry of all models
# =============================================
# declarative_base() returns a Base class.
# Every SQLAlchemy model class inherits from it: class Todos(Base)
# This registers the model with SQLAlchemy's internal metadata tracker.
# Base.metadata in Step 6 uses this registry to know which tables to create.

# Base = declarative_base()


# =============================================
# STEP 5: MODELS -- Python classes that map to DB tables
# =============================================
# Defined in models.py (separate file, imported where needed).
# Each class = one table. Each class attribute = one column.
# Each class instance = one row in that table.
#
# class Todos(Base):
#     __tablename__ = "todos"
#     id          = Column(Integer, primary_key=True, index=True)
#     title       = Column(String)
#     description = Column(String)
#     priority    = Column(Integer)
#     complete    = Column(Boolean, default=False)
#
# SQLAlchemy reads this and knows:
#   - what the table is called in SQL ("todos")
#   - what columns it has and their types
#   - which column is the primary key (auto-increment)


# =============================================
# STEP 6: TABLE CREATION -- create tables at startup
# =============================================
# Called ONCE in main.py when the app starts.
# create_all() scans all classes registered with Base (Step 4 + Step 5)
# and creates their tables in the DB if they don't already exist.
# If a table already exists -> does nothing (safe to call every startup).
#
# models.Base.metadata.create_all(bind=engine)


# =============================================
# STEP 7: SESSION PER REQUEST -- get_db()
# =============================================
# Defined in main.py. Opens a fresh session for each request, then cleans up after.
# Uses Python's yield (generator) to split into setup and teardown:
#
# def get_db():
#     db = SessionLocal()   # SETUP: open a fresh session
#     try:
#         yield db          # hand it to the route; execution pauses here
#         db.commit()       # TEARDOWN: route finished OK -> persist all changes
#     except:
#         db.rollback()     # TEARDOWN: something failed -> undo all staged changes
#         raise
#     finally:
#         db.close()        # always release the session back to the connection pool
#
# FastAPI injects this via Depends(get_db) -- covered in main.py comments.


# =============================================
# DOES THIS FLOW CHANGE FOR OTHER DATABASES?
# =============================================
# For any SQL database (PostgreSQL, MySQL, SQLite, MSSQL):
#   -> Only STEP 1 (the URL string) changes.
#   -> Steps 2-7 are IDENTICAL. SQLAlchemy handles the differences internally.
#   -> This is the whole point of an ORM -- write once, switch DBs by changing one line.
#
# For NoSQL (MongoDB):
#   -> SQLAlchemy does NOT support NoSQL.
#   -> Use mongoengine (ODM = Object Document Mapper, the NoSQL equivalent of ORM).
#   -> mongoengine has a similar concept: you define Document classes instead of Base models,
#      connect to MongoDB with connect("dbname"), and query using MyDocument.objects(field=value).
#   -> No sessions, no transactions, no Base.metadata -- documents are stored as-is (JSON-like).
#   -> The mental model is similar (classes = collections, instances = documents)
#      but the setup and query API are completely different from SQLAlchemy.
