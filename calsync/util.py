from datetime import datetime
from datetime import timedelta

from pytimeparse import parse


def now():
    return datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time


def parse_timedelta_string(input):
    return timedelta(seconds=parse(input))
