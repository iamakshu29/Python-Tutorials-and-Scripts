from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import stats, urls, user, admin, redirect
from database import Base, engine
from utils.logger import config_logging
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from utils.rate_limiter import limiter
import os


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
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(urls.router)
app.include_router(stats.router)
app.include_router(redirect.router)
