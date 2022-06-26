from datetime import datetime

from unittest.mock import Mock
from unittest.mock import patch
from unittest.mock import call

from calsync.calendar import Calendar
from calsync.rules import COPY_DEFAULTS
from calsync.rules import run_rules
from calsync.event import Event
from calsync.util import parse_timedelta_string
from calsync.util import datetime_to_rfc3339


def test_run_copy_rule():
    config = {"rules": [{"method": "copy", "src": "foo", "dst": "bar"}]}

    # 'lock' the clock so millisecond-precision datetime assertions work
    utcnow_fixed = datetime.utcnow()

    calendar_foo = Mock(spec=Calendar)
    calendar_bar = Mock(spec=Calendar)

    source_events = [
        Event(id="123", summary="Event 123", start="2020-01-11T11:11:11Z"),
        Event(id="456", summary="Event 456", start="2020-04-14T12:12:12Z"),
        Event(id="789", summary="Event 789", start="2020-07-17T13:13:13Z"),
    ]

    # source_events with id removed
    expected_events = [
        Event(summary="Event 123", start="2020-01-11T11:11:11Z"),
        Event(summary="Event 456", start="2020-04-14T12:12:12Z"),
        Event(summary="Event 789", start="2020-07-17T13:13:13Z"),
    ]

    calendar_foo.list_events = Mock(return_value=source_events)
    calendar_bar.import_event = Mock()

    resolve_calendar_result = {
        "foo": calendar_foo,
        "bar": calendar_bar,
    }

    now_min = utcnow_fixed - parse_timedelta_string(COPY_DEFAULTS["look_back"])
    now_max = utcnow_fixed + parse_timedelta_string(COPY_DEFAULTS["look_forward"])

    resolve_calendar = Mock(side_effect=lambda x: resolve_calendar_result[x])

    get_config = Mock(return_value=config)

    with patch("calsync.rules.resolve_calendar", resolve_calendar):
        with patch("calsync.rules.get_config", get_config):
            with patch("calsync.rules.datetime") as mock_datetime:
                # https://docs.python.org/3/library/unittest.mock-examples.html#partial-mocking
                mock_datetime.utcnow.return_value = utcnow_fixed
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

                run_rules()

    calendar_foo.list_events.assert_called_with(
        timeMin=datetime_to_rfc3339(now_min),
        timeMax=datetime_to_rfc3339(now_max),
    )

    calendar_bar.import_event.assert_has_calls(
        [
            call(expected_events[0]),
            call(expected_events[1]),
            call(expected_events[2]),
        ]
    )
