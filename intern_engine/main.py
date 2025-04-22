from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from intern_engine.models import Users, Base
from dotenv import load_dotenv
import os
import threading
from intern_engine.grpc_server.grpc_server import serve
from intern_engine.services.services import (
    create_schedule_service,
    get_user_schedules_service,
    read_schedule_service,
    get_next_appointment_service
)


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
app = FastAPI()
grpc_thread = threading.Thread(target=serve, daemon=True)
grpc_thread.start()


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


@app.post('/schedule', status_code=201, response_model=dict, tags=["Schedule"])
async def create_schedule(schedule: SchedulesCreate):
    '''Создает расписание приема лекарств'''
    async with async_session() as session:
        result = await create_schedule_service(session, schedule)
        return result


@app.get('/schedules', response_model=list[int], tags=["Schedules"])
async def get_user_schedules(user_id: int):
    '''Возвращает список расписаний пользователя'''
    async with async_session() as session:
        schedules = await get_user_schedules_service(session, user_id)
        return schedules


@app.get('/schedule', response_model=list[str], tags=["Schedule"])
async def read_schedule(user_id: int, schedule_id: int):
    '''Возвращает данные о выбранном расписании с графиком приема на день'''
    async with async_session() as session:
        shedule = await read_schedule_service(session, user_id, schedule_id)
        return shedule


@app.get('/next_taking', response_model=list[str], tags=["Appointments"])
async def get_next_appointment(user_id: int):
    '''Возвращает данные о таблетках, которые необходимо принять в ближайшие период'''
    async with async_session() as session:
        schedules = await get_next_appointment_service(session, user_id)
        return schedules
