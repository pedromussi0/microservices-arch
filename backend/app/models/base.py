from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, DateTime

Base = declarative_base()

class TimeStampedBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)