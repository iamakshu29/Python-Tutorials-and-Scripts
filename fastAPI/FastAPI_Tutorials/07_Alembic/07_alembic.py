# Lightweight database migration tool for when using SQLAlchemy

# alembic init <folder_name> -> Initializes a new, generic environment for our app -> will create 2 things -> alembic.ini, alembic directory
# alembic revision -m <message> -> Create a new revision of the environment, with a revision ID. Here we write our DB script to change the schema.
# alembic upgrade <revision #> -> Run our upgrade migration to our database
# alembic downgrade -1 -> Run our downgrade migration to our database
