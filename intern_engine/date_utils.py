from datetime import datetime, timedelta
from .constants import START_TIME, STOP_TIME


def get_schedule(peridicity: int, duration: None) -> list[str]:
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
            times.append(f'{date.strftime("%Y-%m-%d")} {minutes.strftime(format)}')
    return times