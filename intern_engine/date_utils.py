from datetime import datetime, timedelta
from .constants import START_TIME, STOP_TIME, PERIOD


def rounding_time(time: str) -> str:
    format = '%H:%M'
    time = datetime.strptime(time, format)
    minutes = time.minute
    hours = time.hour
    rounded_minutes = ((minutes + 14) // 15) * 15
    if rounded_minutes >= 60:
        hours += 1
        rounded_minutes = 0
    rounded_time = time.replace(hour=hours, minute=rounded_minutes)
    return rounded_time.strftime(format)


def get_schedule(peridicity: int) -> list[str]:
    format = '%H:%M'
    start = datetime.strptime(START_TIME, format)
    stop = datetime.strptime(STOP_TIME, format)
    if peridicity < 1:
        raise ValueError('the frequency must be greater than 1')
    total_minutes = (stop - start).total_seconds() // 60
    interval = total_minutes / (peridicity - 1) if peridicity > 1 else 0
    times = []
    for i in range(peridicity):
        minutes = start + timedelta(minutes=interval * i)
        times.append(f'{rounding_time(minutes.strftime(format))}')
    return times


def get_time_period(schedule: list, PERIOD=PERIOD) -> list[str]:
    start_period = datetime.now()
    end_period = start_period + timedelta(minutes=PERIOD)
    taking = []
    print(start_period, end_period)
    for item in schedule:
        corr_time = datetime.strptime(item, '%H:%M').time()
        if start_period <= datetime.combine(start_period.date(), corr_time) <= end_period:
            taking.append(item)
    return taking
