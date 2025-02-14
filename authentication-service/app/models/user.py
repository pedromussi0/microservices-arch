from ctypes.wintypes import BYTE

from sqlalchemy import BLOB, Boolean, Column, LargeBinary, String

from app.models.base import TimeStampedBase


class User(TimeStampedBase):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(LargeBinary, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
