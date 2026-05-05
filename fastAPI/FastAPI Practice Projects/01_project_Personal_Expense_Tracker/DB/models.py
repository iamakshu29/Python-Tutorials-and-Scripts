from .db import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, func, Float

class Expenses(Base):
    __tablename__ = "expenses"

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String)
    amount = Column(Float)
    category = Column(String)
    date = Column(Date, server_default=func.current_date())
    paid = Column(Boolean, default=False)
