from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import admin, applications, auth
from database import Base, engine
from utils.logger import config_logging
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from utils.rate_limiter import limiter
import os


# When pytest runs with testclient, it uses its own SQLite database. However, without asynccontextmanager,
# the application attempts to connect to PostgreSQL even during tests. Since PostgreSQL is not running during tests,
# this results in a silent connection error. By moving initialization into lifespan, it only executes when FastAPI starts.
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file_Path = os.path.join(log_dir, "app.log")
    config_logging(log_file_Path)
    yield


app = FastAPI(lifespan=lifespan)

# rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# routes
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(applications.router)
