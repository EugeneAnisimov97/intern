from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB #работает только с бд postgres
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    
class Schedules(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True, index=True)
    medicine = Column(String, index=True)
    periodicity = Column(Integer)
    duration = Column(Integer, nullable=True, default=None)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date_created = Column(DateTime, default=datetime.now, nullable=False)
    is_active = Column(Integer, default=1)
    