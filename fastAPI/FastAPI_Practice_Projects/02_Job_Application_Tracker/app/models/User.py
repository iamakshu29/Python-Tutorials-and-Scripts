from sqlalchemy import func, Uuid
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from database import Base
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime


class UserRole(str, Enum):
    ADMIN = "Admin"
    USER = "User"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        index=True,
        default=uuid4,
    )
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)

    # Google Auth users have no password
    hashed_password: Mapped[str | None] = mapped_column(nullable=True)

    google_id: Mapped[str | None] = mapped_column(unique=True, nullable=True)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(), nullable=False
    )
