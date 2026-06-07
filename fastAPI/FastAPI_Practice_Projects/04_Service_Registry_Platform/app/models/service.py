from sqlalchemy import func, Uuid, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from database import Base


class EnvironmentSchema(str, Enum):
    DEV = "dev"
    PROD = "prod"
    STAGING = "staging"


class CurrentStatusSchema(str, Enum):
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
    webhook_url: Mapped[str | None] = mapped_column(nullable=True)
    current_status: Mapped[Enum] = mapped_column(
        SQLEnum(
            CurrentStatusSchema,
            name="current_health_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=CurrentStatusSchema.UNKNOWN,
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    registered_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    last_checked_at: Mapped[datetime | None] = mapped_column(nullable=True)
