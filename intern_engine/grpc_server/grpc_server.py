from concurrent import futures
import grpc
from generated.grpc import medication_pb2_grpc, medication_pb2
from intern_engine.services.services import (
    create_schedule_service,
    get_user_schedules_service,
    read_schedule_service,
    get_next_appointment_service
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class ScheduleService(medication_pb2_grpc.ScheduleServiceServicer):
    async def create_schedule(self, request, context):
        '''Создает расписание приема лекарств'''
        schedule_data = {
            "medicine": request.medicine,
            "periodicity": request.periodicity,
            "duration": request.duration if request.HasField("duration") else None,
            "user_id": request.user_id
        }
        async with async_session() as session:
            result = await create_schedule_service(session, schedule_data)
            return medication_pb2.ScheduleResponse(id=result['id'])

    async def get_user_schedules(self, request, context):
        '''Возвращает список расписаний пользователя'''
        async with async_session() as session:
            schedules = await get_user_schedules_service(session, request.user_id)
            return medication_pb2.UserSchedulesResponse(schedule_ids=schedules)

    async def read_schedule(self, request, context):
        '''Возвращает данные о выбранном расписании с графиком приема на день'''
        async with async_session() as session:
            schedule_data = await read_schedule_service(
                session, request.user_id, request.schedule_id
            )
            return medication_pb2.ScheduleDataResponse(data=schedule_data)

    async def get_next_appointment(self, request, context):
        '''Получает данные о следующем приеме таблеток'''
        async with async_session() as session:
            appointments = await get_next_appointment_service(session, request.user_id)
            return medication_pb2.NextAppointmentResponse(appointments=appointments)


def serve():
    '''Запускает gRPC сервер'''
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    medication_pb2_grpc.add_ScheduleServiceServicer_to_server(
        ScheduleService(), server
    )
    server.add_insecure_port('[::]:8081')
    server.start()
    server.wait_for_termination()
