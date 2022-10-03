from datetime import datetime
import logging
import sys

from calsync.config import get_config
from calsync.calendar import resolve_calendar
from calsync.event import event_short_repr

from calsync.util import parse_timedelta_string

logger = logging.getLogger(__name__)

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

        elif method == "remove_deleted":
            __run_remove_deleted_rule(rule)

        else:
            raise ValueError(f'unknown method "${method}"')


def __run_copy_rule(rule):
    src = resolve_calendar(rule["src"])
    dst = resolve_calendar(rule["dst"])

    look_back = parse_timedelta_string(
        rule.get("look_back", COPY_DEFAULTS["look_back"])
    )
    look_forward = parse_timedelta_string(
        rule.get("look_forward", COPY_DEFAULTS["look_forward"])
    )

    # copy events from src to dst
    src_events = src.list_events(
        timeMin=(datetime.utcnow() - look_back).isoformat() + "Z",
        timeMax=(datetime.utcnow() + look_forward).isoformat() + "Z",
        singleEvents=False,
        orderBy="updated",
    )
    logger.info(f"found {len(src_events)} events")

    for event in src_events:
        logger.info(f"processing event {event_short_repr(event)}")
        try:
            if not __matches_filters(rule, event):
                logger.info("event did not match filters, skipping")
                continue

            new_event = event.copy()

            private_copy = rule.get("private_copy", COPY_DEFAULTS["private_copy"])
            if private_copy:
                new_event.attributes["privateCopy"] = True

            logger.info("running transforms")
            __transform(rule, new_event, src=src)

            logger.info(f"creating event in dst: {new_event}")
            dst.import_event(new_event)

        except Exception as ex:
            print("error occurred while processing event:", file=sys.stderr)
            print(event, file=sys.stderr)

            raise ex


def __run_remove_deleted_rule(rule):
    # check all events in dst have a matching src event
    if type(rule["src"]) is list:
        src = [resolve_calendar(x) for x in rule["src"]]
    else:
        src = [resolve_calendar(rule["src"])]

    dst = resolve_calendar(rule["dst"])

    look_back = parse_timedelta_string(
        rule.get("look_back", COPY_DEFAULTS["look_back"])
    )
    look_forward = parse_timedelta_string(
        rule.get("look_forward", COPY_DEFAULTS["look_forward"])
    )

    src_events = []
    for src_ in src:
        src_events.extend(
            src_.list_events(
                timeMin=(datetime.utcnow() - look_back).isoformat() + "Z",
                timeMax=(datetime.utcnow() + look_forward).isoformat() + "Z",
                singleEvents=False,
                orderBy="updated",
            )
        )
    logger.info(f"found {len(src_events)} events")

    dst_events = dst.list_events(
        timeMin=(datetime.utcnow() - look_back).isoformat() + "Z",
        timeMax=(datetime.utcnow() + look_forward).isoformat() + "Z",
        singleEvents=False,
        orderBy="updated",
    )
    logger.debug(f"found {len(dst_events)} events")

    for event in dst_events:
        logger.info(f"processing event {event_short_repr(event)}")

        try:
            matching_src_events = list(
                filter(
                    lambda x: x == event,
                    src_events,
                )
            )

            if not matching_src_events:
                # no matching source events, so delete
                if event.is_all_day():
                    # we skip deletes for all-days (but still warn) as there
                    # appears to be a bug (or mistake) where many all-days in
                    # my personal calendar were copied and then removed, particularly
                    # birthdays
                    logger.warn(
                        "no matching source event, it's all-day so won't delete"
                    )
                    continue

                logger.info("no matching source event, deleting")
                dst.delete_event(event)

        except Exception as ex:
            print("error occurred while processing event:", file=sys.stderr)
            print(event, file=sys.stderr)

            raise ex


def __matches_filters(rule, event):
    result = True

    for filter_ in rule.get("filter", []):
        match = filter_["match"]

        if "all_day_event" in match:
            if event.is_all_day() != match["all_day_event"]:
                return False

    return result


def __transform(rule, event, src):
    if not rule.get("transform"):
        return

    for transform in rule["transform"]:
        if transform.get("description_append"):
            event.attributes["description"] = (
                event.attributes.get("description", "")
                + "\n\n"
                + transform["description_append"]
                .replace("$calendar_id", src.id)
                .replace("$calendar_summary", src.summary)
                .replace("$calendar_name", src.get_name())
            )
