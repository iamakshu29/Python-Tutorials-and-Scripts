from sqlalchemy import ForeignKey, func, DateTime
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Uuid
from database import Base

# LESSON LEARNED:
# Do NOT use a mutable business value (like urlCode) as a Primary Key if it can change.
# urlCode is updated when a Premium user renews/upgrades a URL — this breaks FK references
# in child tables (like stats) because the referenced value no longer exists.
# FIX APPLIED: onupdate="CASCADE" — when urlCode changes in shorten_url, PostgreSQL
# automatically updates the urlCode in all stats rows that reference it.
# BETTER DESIGN (for future projects): always use a stable UUID as PK, never a business key.

class Stats(Base):
    __tablename__ = "stats"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, nullable=False, default=uuid4)
    urlCode: Mapped[str] = mapped_column(
        ForeignKey("shorten_url.urlCode", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    referrer: Mapped[str | None] = mapped_column(nullable=True)  # where the user came from (browser Referer header), None if typed directly
