from sqlalchemy import func, Uuid, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from database import Base


class EnvironmentSchema(Enum):
    DEV = "dev"
    PROD = "prod"
    STAGING = "staging"


class StatusSchema(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class Service(Base):
    __tablename__ = "services"

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, index=True, nullable=False, default=uuid4
    )
    service_id: Mapped[UUID] = mapped_column(Uuid, foreign_key="services.id")
    status: Mapped[Enum] = mapped_column(SQLEnum(
            StatusSchema, name="health_status", values_callable=lambda x: [e.value for e in x]
        ),nullable=False)
    response_time_ms: Mapped[int] = mapped_column(nullable=False)
    status_code: Mapped[int] = mapped_column(nullable=False)
    error_detail: Mapped[str] = mapped_column(nullable=True)
    checked_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
