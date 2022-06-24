class Event:
    def __init__(self, **attributes):
        self.attributes = attributes

        # copy these attributes onto the class itself as our code uses them directly
        for k in ["calendarId", "summary", "start", "end"]:
            setattr(self, k, attributes.get(k))
