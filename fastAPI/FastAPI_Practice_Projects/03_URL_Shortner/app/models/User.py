from sqlalchemy import func, Uuid, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from database import Base


class UserRole(str, Enum):
    admin = "Admin"
    user = "User"


class UserSubscription(str, Enum):
    basic = "Basic"
    premium = "Premium"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, nullable=False, index=True, default=uuid4
    )

    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)

    username: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)

    hashed_password: Mapped[str] = mapped_column(nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
    )

    subscription_type: Mapped[UserSubscription] = mapped_column(
        SQLEnum(
            UserSubscription,
            name="user_subscription",
            values_callable=lambda x: [e.value for e in x],
        ),
        default="Basic",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
