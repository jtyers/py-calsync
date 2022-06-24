import datetime


def now():
    return datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
