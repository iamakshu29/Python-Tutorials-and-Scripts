from sqlalchemy import func, Uuid, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from database import Base


class UserRoleSchema(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, index=True, nullable=False, default=uuid4
    )
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Enum] = mapped_column(
        SQLEnum(
            UserRoleSchema,
            name="user_role",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
