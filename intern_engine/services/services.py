from sqlalchemy.ext.asyncio import AsyncSession
from intern_engine.models import Schedules, Users
from sqlalchemy import select
from intern_engine.date_utils import get_schedule_on_day, get_appointment, check_actual, sort_data
from fastapi import HTTPException


async def create_schedule_service(session: AsyncSession, schedule: dict):
    '''Создает расписание приема лекарств'''
    user_id = schedule.user_id
    async with session as session:
        user = await session.execute(select(Users).where(Users.id == user_id))
        if not user.scalars().first():
            HTTPException(status_code=200, detail='Зверь не найден')
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


async def get_user_schedules_service(session: AsyncSession, user_id: int):
    '''Возвращает список расписаний пользователя'''
    async with session as session:
        schedules = await session.execute(
            select(Schedules).where(Schedules.user_id == user_id)
        )
        schedules = schedules.scalars().all()
        if not schedules:
            raise HTTPException(status_code=404, detail='Расписание не найдено')
        return [item.id for item in schedules]


async def read_schedule_service(session: AsyncSession, user_id: int, schedule_id: int):
    '''Возвращает данные о выбранном расписании с графиком приема на день'''
    async with session as session:
        shedule = await session.execute(select(Schedules).where((Schedules.id == schedule_id) & (Schedules.user_id == user_id)))
        shedule = shedule.scalars().first()
        if not shedule:
            raise HTTPException(status_code=404, detail='Расписание не найдено')
        return get_schedule_on_day(shedule.periodicity, shedule.medicine)


async def get_next_appointment_service(session: AsyncSession, user_id: int):
    '''Получает данные о следующем приеме таблеток'''
    async with session as session:
        schedules = await session.execute(select(Schedules).where(Schedules.user_id == user_id))
        schedules = schedules.scalars().all()
        taking = []
        if not schedules:
            raise ValueError("Расписание не найдено")
        for schedule in schedules:
            if not check_actual(schedule.start_treatment, schedule.duration):
                schedule.is_active = False
                await session.commit()
            if schedule.is_active:
                schedule_for_user = get_schedule_on_day(schedule.periodicity, schedule.medicine)
                taking_time = get_appointment(schedule_for_user, schedule.start_treatment)
                taking.extend(taking_time)
        if not taking:
            raise HTTPException(status_code=200, detail='На сегодня приема нет')
        return sort_data(taking)
