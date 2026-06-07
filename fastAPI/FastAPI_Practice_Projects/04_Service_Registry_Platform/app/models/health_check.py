from sqlalchemy import func, Uuid, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from database import Base


class StatusSchema(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class HealthCheck(Base):
    __tablename__ = "health_checks"

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, index=True, nullable=False, default=uuid4
    )
    service_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("services.id"), nullable=False)
    status: Mapped[Enum] = mapped_column(SQLEnum(
            StatusSchema, name="health_status", values_callable=lambda x: [e.value for e in x]
        ), nullable=False)
    response_time_ms: Mapped[int] = mapped_column(nullable=False)
    status_code: Mapped[int] = mapped_column(nullable=False)
    error_detail: Mapped[str | None] = mapped_column(nullable=True)
    checked_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
