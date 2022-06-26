from datetime import datetime
from datetime import timedelta

from pytimeparse import parse


def now():
    return datetime_to_rfc3339(datetime.utcnow())


def datetime_to_rfc3339(dt):
    return dt.isoformat() + "Z"  # 'Z' indicates UTC time


def parse_timedelta_string(input):
    return timedelta(seconds=parse(input))
