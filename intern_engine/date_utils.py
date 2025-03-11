from datetime import datetime, timedelta
from .constants import START_TIME, STOP_TIME


def rounding_time(time_str: str) -> str:
    format = '%H:%M'
    time = datetime.strptime(time_str, format)
    minutes = time.minute
    hours = time.hour
    rounded_minutes = ((minutes + 14) // 15) * 15
    if rounded_minutes >= 60:
        hours += 1
        rounded_minutes = 0
    rounded_time = time.replace(hour=hours, minute=rounded_minutes)
    return rounded_time.strftime(format)


def get_schedule(peridicity: int, duration: int | None) -> list[str]:
    format = '%H:%M'
    start = datetime.strptime(START_TIME, format)
    stop = datetime.strptime(STOP_TIME, format)
    if peridicity < 1:
        raise ValueError('the frequency must be greater than 1')
    total_minutes = (stop - start).total_seconds() // 60
    interval = total_minutes / (peridicity - 1) if peridicity > 1 else 0
    current_date = datetime.today()
    times = []
    if duration is None or duration > 365:
        for i in range(peridicity):
            minutes = start + timedelta(minutes=interval * i)
            times.append(f'everyday  {minutes.strftime(format)}')
        return times
    for day in range(duration):
        date = current_date + timedelta(days=day)
        for i in range(peridicity):
            minutes = start + timedelta(minutes=interval * i)
            times.append(f'{date.strftime("%Y-%m-%d")} {rounding_time(minutes.strftime(format))}')
    return times


# def get_next_appointment(curr_date: str, medicine: str, peridicity: int, duraction: int | None) -> list[str]:
#     taking = []
#     schedule_for_user = get_schedule(peridicity, duraction)
#     for item in schedule_for_user:
#         if item[:13] == curr_date:
#             taking.append(f'{str(medicine)} - {item}')
#     return taking
