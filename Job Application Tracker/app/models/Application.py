from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    func,
)
from database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, nullable=False)

    # SQLAlchemy is smart enough to look up the table named "users" and the column named "id" from its internal registry of tables.
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    company = Column(String, nullable=False)

    # name of enum...check schema.sql
    role_title = Column(
        Enum("Devops", "Tester", "Developer", name="role_status", create_type=True),
        nullable=False,
    )
    job_url = Column(String, nullable=True)

    # name of enum...check schema.sql
    status = Column(
        Enum(
            "Applied",
            "Interview",
            "Offer",
            "Rejected",
            "Ghosted",
            name="application_status",
            create_type=True,
        ),
        nullable=False,
    )

    applied_date = Column(DateTime, server_default=func.now(), nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
