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


class CurrentStatusSchema(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class Service(Base):
    __tablename__ = "services"

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, index=True, nullable=False, default=uuid4
    )
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    team: Mapped[str] = mapped_column(nullable=False)
    environment: Mapped[Enum] = mapped_column(
        SQLEnum(
            EnvironmentSchema,
            name="env_name",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    health_url: Mapped[str] = mapped_column(nullable=False)
    webhook_url: Mapped[str] = mapped_column(nullable=True)
    current_status: Mapped[Enum] = mapped_column(
        SQLEnum(
            CurrentStatusSchema,
            name="current_health_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(nullable=False)
    registered_by: Mapped[UUID] = mapped_column(Uuid, foreign_key="users.id")
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    last_checked_at: Mapped[datetime] = mapped_column(nullable=False)
