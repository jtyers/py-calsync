import logging

from calsync.rules import run_rules

logging.basicConfig(level=logging.DEBUG)


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    run_rules()


#    calendars = get_calendars()
#
#    for calendar in calendars:
#        print(
#            f"Calendar {calendar.summary} / {calendar.summaryOverride} ({calendar.id})"
#        )
#        for event in calendar.events(maxResults=5):
#            print(
#                ">",
#                event.summary,
#                event.start.get("dateTime", event.start.get("date")),
#                event.end.get("dateTime", event.end.get("date")),
#            )


if __name__ == "__main__":
    main()
