from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from database import Base

class Url(Base):
    __tablename__ = "shorten_url"

    original_url = Column(String, nullable=False)
    urlCode = Column(String, nullable=False, primary_key=True, index=True)
    click_count = Column(Integer,nullable=False, default=0)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    expires_at = Column(DateTime(timezone=True),nullable=False)
    last_accessed_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    expired = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"),index=True)