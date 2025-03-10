from fastapi import FastAPI,  HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Users, Schedules, Base
from .date_utils import get_schedule
from dotenv import load_dotenv
from sqlalchemy import select
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

class SchedulesCreate(BaseModel):
    medicine: str
    periodicity: int
    duration: int
    user_id: int

class SchedulesResponse(BaseModel):
    id: int

class NextTakingResponse(BaseModel):
    medicine: str
    shedule: list[str]

@app.post('/schedule', response_model=SchedulesResponse)
async def create_schedule(schedule: SchedulesCreate):
    '''Создает расписание приема лекарств на день'''
    async with async_session() as session: 
        user = await session.execute(select(Users).where(Users.id == schedule.user_id))
        if not user.scalars().first():
            raise HTTPException(status_code=404, detail="user not found") 
        plan = Schedules(
        medicine=schedule.medicine,
        periodicity=schedule.periodicity,
        duration=schedule.duration,
        user_id=schedule.user_id
        )
        session.add(plan)
        await session.commit()
        await session.refresh(plan)
    return {'id': plan.id}

@app.get('/schedules', response_model=list[int])
async def get_user_schedules(user_id: int):
    '''Возвращает список расписаний пользователя'''
    async with async_session() as session:
        user = await session.execute(select(Users).where(Users.id == user_id))
        if not user.scalars().first():
            raise HTTPException(status_code=404, detail="user not found") 
        schedules = await session.execute(
            select(Schedules).where(Schedules.user_id == user_id)
        )
        schedules = schedules.scalars().all()
        if not schedules:
            raise HTTPException(status_code=404, detail="schedules not found")
        return [item.id for item in schedules]

@app.get('/schedule', response_model=list[str])
async def read_schedule(user_id: int, schedule_id: int):
    '''Вовзвращает данные о выбранном расписании с графиком приема на день'''
    async with async_session() as session: 
        shedule = await session.execute(select(Schedules).where((Schedules.id == schedule_id) & (Schedules.user_id == user_id)))
        shedule = shedule.scalars().first()
        if not shedule:
            raise HTTPException(status_code=404, detail='Shedule not found')
        return get_schedule(shedule.periodicity, shedule.duration)

@app.get('/next_taking', response_class=NextTakingResponse)
async def get_next_madicine():
    pass