from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# pip install pymysql for MYSQL
# MYSQL_DATABSE_URL = "mysql+pymysql://root:admin@127.0.0.1:3306/TodoApplicationDatabase"
# engine = create_engine(MYSQL_DATABSE_URL)

# pip install psycopg2-binary for PostgreSQL
# POSTGRESQL_DATABASE_URL = "postgresql://postgres:admin@localhost/TodoApplicationDatabase"
# engine = create_engine(POSTGRESQL_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
