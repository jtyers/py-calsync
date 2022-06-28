from copy import deepcopy


COPY_FIELDS = [
    "start",
    "iCalUID",
    "end",
    "summary",
    "description",
    "location",
]


class Event:
    def __init__(self, **attributes):
        self.attributes = attributes

        # copy these attributes onto the class itself as our code uses them directly
        for k in ["calendarId", "summary", "start", "end"]:
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
        for k in COPY_FIELDS:
            if k in self.attributes:
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
