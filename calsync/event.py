COPY_SKIP_FIELDS = [
    "anyoneCanAddSelf",  # deprecated
    "attendees",  # to avoid triggering emails
    "colorId",  # intentional so copied event appears different
    "created",  # ro
    "creator",  # ro
    "etag",
    "hangoutLink",  # ro
    "htmlLink",
    "id",
    "organizer",
    "reminders",
    "sequence",
    "updated",  # ro
    # "recurrence",  # causes 403 errors if used in imports
]


def event_short_repr(evt):
    return f"Event(id={evt.id}, summary={evt.summary}, start={evt.start}, end={evt.end}, organizer={evt.attributes.get('organizer', {}).get('displayName')})"


class Event:
    def __init__(self, **attributes):
        self.attributes = attributes

        # copy these attributes onto the class itself as our code uses them directly
        for k in ["calendarId", "summary", "start", "end", "id"]:
            setattr(self, k, attributes.get(k))

    def __eq__(self, other):
        if type(other) is not Event:
            return False

        for a in self.attributes:
            if a not in other.attributes:
                return False
            if other.attributes[a] != self.attributes[a]:
                return False

        return True

    def __repr__(self):
        return (
            "Event(" + ", ".join([f"{k}={v}" for k, v in self.attributes.items()]) + ")"
        )

    def copy(self):
        new_attrs = {}
        for k in self.attributes:
            if k not in COPY_SKIP_FIELDS:
                new_attrs[k] = self.attributes[k]

        return Event(**new_attrs)

    def is_all_day(self):
        _start = self.attributes.get("start", {})
        _end = self.attributes.get("end", {})
        return (
            "dateTime" not in _start
            and "date" in _start
            and "dateTime" not in _end
            and "date" in _end
        )
