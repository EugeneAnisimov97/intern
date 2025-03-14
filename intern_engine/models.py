from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from datetime import datetime, timedelta


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)


class Schedules(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True, index=True)
    medicine = Column(String, nullable=False, index=True)
    periodicity = Column(Integer, nullable=False, index=True)
    duration = Column(Integer, nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date_created = Column(DateTime, default=datetime.now, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    start_treatment = Column(DateTime,
                             default=lambda: (
                                 (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0)))
