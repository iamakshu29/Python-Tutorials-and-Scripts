from sqlalchemy import Boolean, ForeignKey, func, DateTime
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped

from database import Base


class Url(Base):
    __tablename__ = "shorten_url"

    original_url: Mapped[str] = mapped_column(nullable=False)

    urlCode: Mapped[str] = mapped_column(nullable=False, primary_key=True, index=True)

    click_count: Mapped[int] = mapped_column(nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    expired: Mapped[datetime] = mapped_column(Boolean, default=False)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
