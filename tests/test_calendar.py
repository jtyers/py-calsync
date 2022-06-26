from unittest.mock import Mock
from unittest.mock import patch

from calsync.calendar import get_calendars, Calendar
from calsync.event import Event
from calsync.service import CalendarService


def test_get_calendars():
    list_calendars_result = [
        {
            "summary": "foo",
            "id": "foo",
        },
        {
            "summary": "bar",
            "id": "bar",
        },
        {
            "summary": "baz",
            "id": "baz",
        },
    ]

    expected_result = [
        Calendar(summary="foo", id="foo"),
        Calendar(summary="bar", id="bar"),
        Calendar(summary="baz", id="baz"),
    ]

    calendar_service = Mock()
    calendar_service.list_calendars = Mock(return_value=list_calendars_result)

    get_calendar_service = Mock(return_value=calendar_service)

    with patch("calsync.calendar.get_calendar_service", get_calendar_service):
        result = get_calendars()

    assert result == expected_result


def test_list_events():
    list_events_result = [
        {
            "summary": "foo",
            "id": "foo",
        },
        {
            "summary": "bar",
            "id": "bar",
        },
        {
            "summary": "baz",
            "id": "baz",
        },
    ]

    expected_result = [
        Event(summary="foo", id="foo", calendarId="calid"),
        Event(summary="bar", id="bar", calendarId="calid"),
        Event(summary="baz", id="baz", calendarId="calid"),
    ]

    calendar_service = Mock()
    calendar_service.list_events = Mock(return_value=list_events_result)

    get_calendar_service = Mock(return_value=calendar_service)

    with patch("calsync.calendar.get_calendar_service", get_calendar_service):
        result = Calendar(id="calid").list_events()

    assert result == expected_result


def test_create_event():
    create_event_result = {
        "summary": "foo",
        "start": "2020-06-01T16:16:12Z",
    }

    expected_result = Event(
        summary="foo", start="2020-06-01T16:16:12Z", calendarId="calid"
    )

    calendar_service = Mock()
    calendar_service.create_event = Mock(return_value=create_event_result)

    get_calendar_service = Mock(return_value=calendar_service)

    with patch("calsync.calendar.get_calendar_service", get_calendar_service):
        result = Calendar(id="calid").create_event(expected_result)

    assert result == expected_result
