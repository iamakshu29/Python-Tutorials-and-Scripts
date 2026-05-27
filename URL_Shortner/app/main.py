from fastapi import FastAPI
from routers import stats, urls, user, admin, redirect
from database import Base, engine

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(admin.router)
app.include_router(user.router)
app.include_router(urls.router)
app.include_router(stats.router)
app.include_router(redirect.router)