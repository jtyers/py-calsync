from calsync.service import get_calendar_service
from calsync.util import now
from calsync.event import Event


class Calendar:
    def __init__(self, **attributes):
        self.attributes = attributes

        # copy these attributes onto the class itself as our code uses them directly
        for k in ["id", "summary", "summaryOverride"]:
            setattr(self, k, attributes.get(k))

    def events(
        self, timeMin=now(), maxResults=30, singleEvents=True, orderBy="startTime"
    ):
        # Call the Calendar API
        events_result = (
            get_calendar_service()
            .events()
            .list(
                calendarId=self.id,
                timeMin=timeMin,
                maxResults=maxResults,
                singleEvents=singleEvents,
                orderBy=orderBy,
            )
            .execute()
        )
        return [
            Event(calendarId=self.id, **evt) for evt in events_result.get("items", [])
        ]


def get_calendars():
    callist_result = get_calendar_service().calendarList().list(maxResults=50).execute()
    callist = callist_result.get("items", [])

    if not callist:
        return []

    return [Calendar(**cal) for cal in callist]
