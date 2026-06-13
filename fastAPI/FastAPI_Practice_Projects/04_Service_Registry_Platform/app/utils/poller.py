import asyncio
from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session
from dependencies import get_db
from models.service import Service
from services.health_service import is_healthy

DbDependency = Annotated[Session, Depends(get_db)]


async def poll_services(db: DbDependency):
    services = db.query(Service).filter(Service.is_active).all()
    for s in services:
        s.name
        is_healthy(s.name, db)
    await asyncio.sleep(30)


async def main():
    task = asyncio.create_task(poll_services())
    print("Poling Starts")
    await task
    print("Service Updated")


asyncio.run(main())
