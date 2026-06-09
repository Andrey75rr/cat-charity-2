from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer

from app.core.db import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime, default=None, nullable=True)
    fully_invested = Column(Boolean, default=False)
    invested_amount = Column(Integer, default=0)
