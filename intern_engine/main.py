from fastapi import FastAPI,  HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from intern_engine.models import Users, Schedules, Base
from intern_engine.date_utils import get_schedule, get_time_period
from dotenv import load_dotenv
from sqlalchemy import select
from datetime import datetime, timedelta
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


@app.post('/schedule', response_model=SchedulesResponse)
async def create_schedule(schedule: SchedulesCreate):
    '''Создает расписание приема лекарств'''
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
    '''Возвращает данные о выбранном расписании с графиком приема на день'''
    async with async_session() as session: 
        shedule = await session.execute(select(Schedules).where((Schedules.id == schedule_id) & (Schedules.user_id == user_id)))
        shedule = shedule.scalars().first()
        if not shedule:
            raise HTTPException(status_code=404, detail='Shedule not found')
        return get_schedule(shedule.periodicity)


@app.get('/next_taking', response_model=list[str])
async def get_next_medicine(user_id: int):
    '''Возвращает данные о таблетках, которые необходимо принять в ближайшие период'''
    async with async_session() as session:
        schedules = await session.execute(select(Schedules).where(Schedules.user_id == user_id))
        schedules = schedules.scalars().all()
        if not schedules:
            raise HTTPException(status_code=404, detail='Shedules not found')
        for schedule in schedules:
            schedule_for_user = get_schedule(schedule.periodicity)
            taking = get_time_period(schedule_for_user)
        if not taking:
            raise HTTPException(status_code=200, detail='No reception')
        return taking
