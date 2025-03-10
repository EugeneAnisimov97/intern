from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB #работает только с бд postgres

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    
class Schedules(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True, index=True)
    medicine = Column(String, index=True)
    periodicity = Column(JSONB, index=True)
    duration = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)