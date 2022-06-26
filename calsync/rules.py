from datetime import datetime

from calsync.config import get_config
from calsync.calendar import resolve_calendar

from calsync.util import parse_timedelta_string
from calsync.util import now

COPY_DEFAULTS = {
    "method": "copy",
    "look_back": "1 week",
    "look_forward": "12 weeks",
}


def run_rules():
    config = get_config("py-calsync.yaml")

    # process rules sequentially
    for rule in config["rules"]:
        method = rule["method"]

        if method == "copy":
            __run_copy_rule(rule)

        else:
            raise ValueError(f'unknown method "${method}"')


def __run_copy_rule(rule):
    src = resolve_calendar(rule["src"])
    dst = resolve_calendar(rule["dst"])

    # TODO: read events in the immediate past and distant future,
    # and copy from src cal to dst cal
    look_back = parse_timedelta_string(
        rule.get("look_back", COPY_DEFAULTS["look_back"])
    )
    look_forward = parse_timedelta_string(
        rule.get("look_forward", COPY_DEFAULTS["look_forward"])
    )

    events = src.list_events(
        timeMin=(datetime.utcnow() - look_back).isoformat(),
        timeMax=(datetime.utcnow() + look_forward).isoformat(),
    )

    for event in events:
        dst.create_event(event)
