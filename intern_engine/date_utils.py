from datetime import datetime, timedelta
from .constants import START_TIME, STOP_TIME, PERIOD, FORMAT


def rounding_minutes(time: str) -> str:
    '''Округление минут до кратности 15'''
    time = datetime.strptime(time, FORMAT)
    minutes = time.minute
    hours = time.hour
    rounded_minutes = ((minutes + 14) // 15) * 15
    if rounded_minutes >= 60:
        hours += 1
        rounded_minutes = 0
    rounded_time = time.replace(hour=hours, minute=rounded_minutes)
    return rounded_time.strftime(FORMAT)


def get_schedule_on_day(peridicity: int, medicine: str,) -> list[str]:
    '''Создает расписание на день'''
    start = datetime.strptime(START_TIME, FORMAT)
    stop = datetime.strptime(STOP_TIME, FORMAT)
    if peridicity < 1:
        raise ValueError('Периодичность приема болжна быть больше 1')
    total_minutes = (stop - start).total_seconds() // 60
    interval = total_minutes / (peridicity - 1) if peridicity > 1 else 0
    times = []
    for i in range(peridicity):
        minutes = start + timedelta(minutes=interval * i)
        times.append(f'{medicine} - {rounding_minutes(minutes.strftime(FORMAT))}')
    return times


def get_appointment(schedule: list, start_treatment: datetime, PERIOD=PERIOD) -> list[str]:
    '''Возвращает прием лекарств на ближайшее время заданное периодом'''
    start_period = datetime.now()  # Начало периода будет задаваться через параметры конфигурации сервиса, а пока что так
    end_period = start_period + timedelta(minutes=PERIOD)
    taking = []
    if start_period < start_treatment:
        return []
    for item in schedule:
        time_medicine = datetime.strptime(item[-5:], FORMAT).time()
        if start_period <= datetime.combine(start_period.date(), time_medicine) <= end_period:
            taking.append(f'{item}')
    return taking


def check_actual(start_treatment: datetime, duration: int | None) -> bool:
    '''Считает, что лечение начинается со следующего дня после выписки и проверяет его актуальность'''
    stop_treatment = (start_treatment + timedelta(days=duration)).replace(hour=23, minute=59, second=59)
    if datetime.now() <= stop_treatment or duration is None:
        return True
    return False


def calc_next_day():
    return lambda: (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0)
