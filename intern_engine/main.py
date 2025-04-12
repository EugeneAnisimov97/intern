from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from intern_engine.models import Users, Schedules, Base
from intern_engine.date_utils import get_schedule_on_day, get_appointment, check_actual, sort_data
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
    async with async_session() as session:
        for user_id in range(4):
            user = await session.get(Users, user_id)
            if not user:
                create_user = Users(id=user_id)
                session.add(create_user)
                await session.commit()


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


class SchedulesCreate(BaseModel):
    medicine: str
    periodicity: int
    duration: int | None
    user_id: int


@app.post('/schedule', status_code=201, response_model=dict)
async def create_schedule(schedule: SchedulesCreate):
    '''Создает расписание приема лекарств'''
    async with async_session() as session:
        user = await session.execute(select(Users).where(Users.id == schedule.user_id))
        if not user.scalars().first():
            raise HTTPException(status_code=404, detail="Зверь не найден")
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
        schedules = await session.execute(
            select(Schedules).where(Schedules.user_id == user_id)
        )
        schedules = schedules.scalars().all()
        if not schedules:
            raise HTTPException(status_code=404, detail="Расписание не найдено")
        return [item.id for item in schedules]


@app.get('/schedule', response_model=list[str])
async def read_schedule(user_id: int, schedule_id: int):
    '''Возвращает данные о выбранном расписании с графиком приема на день'''
    async with async_session() as session:
        shedule = await session.execute(select(Schedules).where((Schedules.id == schedule_id) & (Schedules.user_id == user_id)))
        shedule = shedule.scalars().first()
        if not shedule:
            raise HTTPException(status_code=404, detail='Расписание не найдено')
        return get_schedule_on_day(shedule.periodicity, shedule.medicine)


@app.get('/next_taking', response_model=list[str])
async def get_next_appointment(user_id: int):
    '''Возвращает данные о таблетках, которые необходимо принять в ближайшие период'''
    async with async_session() as session:
        schedules = await session.execute(select(Schedules).where(Schedules.user_id == user_id))
        schedules = schedules.scalars().all()
        taking = []
        if not schedules:
            raise HTTPException(status_code=404, detail='Расписание не найдено')
        for schedule in schedules:
            if not check_actual(schedule.start_treatment, schedule.duration):
                schedule.is_active = False
                await session.commit()
            if schedule.is_active:
                schedule_for_user = get_schedule_on_day(schedule.periodicity, schedule.medicine)
                taking_time = get_appointment(schedule_for_user, schedule.start_treatment)  # Обращаю внимание, что если создали сегодня, лечение начнется со след. дня и ближайшую таблетку не получите
                taking.extend(taking_time)
        if not taking:
            raise HTTPException(status_code=200, detail='На сегодня приема нет')
        return sort_data(taking)
