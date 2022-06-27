from datetime import datetime
import logging

from calsync.config import get_config
from calsync.calendar import resolve_calendar
from calsync.event import Event

from calsync.util import parse_timedelta_string

COPY_DEFAULTS = {
    # the method to use
    "method": "copy",
    # the period of time to look back and forward for events to copy
    "look_back": "1 week",
    "look_forward": "12 weeks",
    # if True, mark copied events as private, which prevents event propagation
    "private_copy": True,
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
        timeMin=(datetime.utcnow() - look_back).isoformat() + "Z",
        timeMax=(datetime.utcnow() + look_forward).isoformat() + "Z",
    )
    logging.info(f"found {len(events)} to copy", events=events)

    for event in events:
        new_event = event.copy()

        private_copy = rule.get("private_copy", COPY_DEFAULTS["private_copy"])
        if private_copy:
            new_event.attributes["privateCopy"] = True

        __transform(rule, new_event, src=src)

        logging.info("creating event in dst", event=new_event)
        dst.import_event(new_event)


def __transform(rule, event, src=None):
    if not rule.get("transform"):
        return

    if rule["transform"].get("description_append"):
        event.attributes["description"] = (
            event.attributes["description"]
            + "\n\n"
            + rule["transform"]["description_append"]
            .replace("$calendar_id", src.id)
            .replace("$calendar_summary", src.summary)
        )
