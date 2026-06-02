from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, func, Uuid
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class RoleTitle(str, Enum):
    DEVOPS = "Devops"
    TESTER = "Tester"
    DEVELOPER = "Developer"


class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    GHOSTED = "Ghosted"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        index=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    company: Mapped[str] = mapped_column(
        nullable=False,
    )

    role_title: Mapped[RoleTitle] = mapped_column(
        SQLEnum(RoleTitle, name="role_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    job_url: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    status: Mapped[ApplicationStatus] = mapped_column(
        SQLEnum(ApplicationStatus, name="application_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    applied_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
