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
