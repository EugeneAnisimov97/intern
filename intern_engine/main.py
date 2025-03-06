from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Schedules, Base
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI()

@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()

class ScheduleCreate(BaseModel):
    medicine: str
    periodicity: dict
    duration: int
    user_id: int

class ScheduleResponse(BaseModel):
    id: int

@app.post('/schedule', response_model=ScheduleResponse)
async def create_schedule(schedule: ScheduleCreate):
    plan = Schedules(
        medicine=schedule.medicine,
        periodicity=schedule.periodicity,
        duration=schedule.duration,
        user_id=schedule.user_id
    )
    async with async_session() as session:     
        session.add(plan)
        await session.commit()
        await session.refresh(plan)
    return {'id': plan.id}
