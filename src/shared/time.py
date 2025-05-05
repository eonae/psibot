from datetime import timedelta


def format_timedelta(td: timedelta) -> str:
    """Форматирует timedelta в строку формата HH:MM:SS.mmm"""
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


def parse_timedelta(time_str: str) -> timedelta:
    hours, minutes, seconds = map(float, time_str.split(":"))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)
