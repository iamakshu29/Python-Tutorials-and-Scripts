from sqlalchemy import ForeignKey, func, DateTime
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Uuid
from database import Base

class Stats(Base):
    __tablename__ = "stats"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, nullable=False, default=uuid4)
    urlCode: Mapped[str] = mapped_column(ForeignKey("shorten_url.urlCode"), nullable=False, index=True)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    referrer: Mapped[str | None] = mapped_column(nullable=True)  # where the user came from (browser Referer header), None if typed directly
