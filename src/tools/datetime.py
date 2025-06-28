from datetime import datetime


def get_current_datetime() -> str:
    """
    Returns the current date and time in the format "YYYY-MM-DD HH:MM:SS".
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")