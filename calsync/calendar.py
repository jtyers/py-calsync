from calsync.service import get_calendar_service
from calsync.util import now
from calsync.event import Event


# Values for Calendar that we ignore (treat as if they weren't there)
DISALLOWED_SUMMARIES = ["Calendar"]

# list of fields to clear for import/insert operations
READ_ONLY_EVENT_ATTRIBUTES = [
    #   "anyoneCanAddSelf",
    #   "created",
    #   "updated",
    #   "creator",
    #   "hangoutLink",
    #   "kind",
    #   "etag",
    #   "id",
    #   "status",
    #   "htmlLink",
    #   "eventType",
]


class Calendar:
    def __init__(self, **attributes):
        self.attributes = attributes

        # copy these attributes onto the class itself as our code uses them directly
        for k in ["id", "summary", "summaryOverride"]:
            setattr(self, k, attributes.get(k))

    def __eq__(self, other):
        if type(other) is not Calendar:
            return False

        for a in self.attributes:
            if a not in other.attributes:
                return False
            if other.attributes[a] != self.attributes[a]:
                return False

        return True

    def __repr__(self):
        return (
            "Calendar("
            + ", ".join([f"{k}={v}" for k, v in self.attributes.items()])
            + ")"
        )

    def get_name(self):
        for s in [self.summary, self.summaryOverride, self.id]:
            if s is not None and s not in DISALLOWED_SUMMARIES:
                return s

        return self.id

    def list_events(
        self,
        timeMin=now(),
        timeMax=None,
        maxResults=30,
        singleEvents=True,
        orderBy="startTime",
    ):
        # Call the Calendar API
        events_result = get_calendar_service().list_events(
            calendarId=self.id,
            timeMin=timeMin,
            timeMax=timeMax,
            maxResults=maxResults,
            singleEvents=singleEvents,
            orderBy=orderBy,
        )
        return [Event(calendarId=self.id, **evt) for evt in events_result]

    def delete_event(
        self,
        event,
    ):
        # Call the Calendar API
        events_result = get_calendar_service().delete_event(
            calendarId=self.id,
            eventId=event.id,
        )
        return [Event(calendarId=self.id, **evt) for evt in events_result]

    def import_event(self, event):
        new_event = event.copy()

        events_result = get_calendar_service().import_event(
            calendarId=self.id,
            body=new_event.attributes,
        )
        return Event(calendarId=self.id, **events_result)


__cached_callist = None


def get_calendars():
    global __cached_callist

    if __cached_callist is None:
        callist = get_calendar_service().list_calendars(maxResults=50)

        if not callist:
            __cached_callist = []
        else:
            __cached_callist = [Calendar(**cal) for cal in callist]

    return __cached_callist


def resolve_calendar(input):
    """Resolves the input to either a calendar name (summary) or ID"""
    if input in DISALLOWED_SUMMARIES:
        raise ValueError(f"disallowed summary input: {input}")

    for calendar in get_calendars():
        if calendar.summary == input:
            return calendar
        if calendar.summaryOverride == input:
            return calendar
        if calendar.id == input:
            return calendar

    raise ValueError(f'unknown calendar "${input}"')
