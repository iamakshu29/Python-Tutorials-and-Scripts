from fastapi import FastAPI
from routers import admin, applications, auth
from database import Base, engine

from utils.logger import config_logging
import os

app = FastAPI()
Base.metadata.create_all(bind=engine)

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file_Path = os.path.join(log_dir, "app.log")
config_logging(log_file_Path)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(applications.router)