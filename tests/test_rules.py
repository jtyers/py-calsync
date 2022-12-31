import pytest

from contextlib import contextmanager
from datetime import datetime

from unittest.mock import Mock
from unittest.mock import patch
from unittest.mock import call

from calsync.calendar import Calendar
from calsync.rules.rules import COPY_DEFAULTS
from calsync.rules.rules import run_rules
from calsync.event import Event
from calsync.util import parse_timedelta_string
from calsync.util import datetime_to_rfc3339

RESOLVE_CALENDAR_ADDR = "calsync.rules.rules.resolve_calendar"
GET_CONFIG_ADDR = "calsync.rules.rules.get_config"
DATETIME_ADDR = "calsync.rules.rules.datetime"

# 'lock' the clock so millisecond-precision datetime assertions work
utcnow_fixed = datetime.utcnow()


def __tdstr_to_rfc3339_back(tdstr):
    return utcnow_fixed - parse_timedelta_string(tdstr)


def __tdstr_to_rfc3339_forward(tdstr):
    return utcnow_fixed + parse_timedelta_string(tdstr)


def __setup_mocks(config):
    calendar_foo = Mock(spec=Calendar, id="cid_foo", summary="cs_foo", name="cid_foo")
    calendar_bar = Mock(spec=Calendar, id="cid_bar", summary="cs_bar", name="cid_bar")
    calendar_baz = Mock(spec=Calendar, id="cid_baz", summary="cs_baz", name="cid_baz")

    calendar_foo.get_name = Mock(return_value="Foo")
    calendar_bar.get_name = Mock(return_value="Bar")
    calendar_baz.get_name = Mock(return_value="Baz")

    resolve_calendar_result = {
        "cs_foo": calendar_foo,
        "cs_bar": calendar_bar,
        "cid_baz": calendar_baz,  # baz only matches on cid
    }

    resolve_calendar = Mock(side_effect=lambda x: resolve_calendar_result[x])

    get_config = Mock(return_value=config)

    return calendar_foo, calendar_bar, calendar_baz, resolve_calendar, get_config


@contextmanager
def __patch_mocks(resolve_calendar, get_config):
    with patch(RESOLVE_CALENDAR_ADDR, resolve_calendar):
        with patch(GET_CONFIG_ADDR, get_config):
            with patch(DATETIME_ADDR) as mock_datetime:
                # https://docs.python.org/3/library/unittest.mock-examples.html#partial-mocking
                mock_datetime.utcnow.return_value = utcnow_fixed
                mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                yield None


def __run_copy_rule_test(
    config,
    foo_events=None,
    foo_expected_events=None,
    bar_events=None,
    bar_expected_events=None,
    baz_events=None,
    baz_expected_events=None,
    expected_look_back=COPY_DEFAULTS["look_back"],
    expected_look_forward=COPY_DEFAULTS["look_forward"],
):
    (
        calendar_foo,
        calendar_bar,
        calendar_baz,
        resolve_calendar,
        get_config,
    ) = __setup_mocks(config)

    input_events_data = [
        (calendar_foo, foo_events),
        (calendar_bar, bar_events),
        (calendar_baz, baz_events),
    ]

    imported_events_data = [
        (calendar_foo, foo_expected_events),
        (calendar_bar, bar_expected_events),
        (calendar_baz, baz_expected_events),
    ]

    for events_data in input_events_data:
        cal, events = events_data
        if events is not None:
            cal.list_events = Mock(return_value=events)

    for import_data in imported_events_data:
        cal, expected_events = import_data
        if expected_events is not None:
            cal.import_event = Mock()

    with __patch_mocks(resolve_calendar, get_config):
        run_rules()

    for events_data in input_events_data:
        cal, events = events_data

        if events is not None:
            cal.list_events.assert_called_with(
                timeMin=datetime_to_rfc3339(
                    __tdstr_to_rfc3339_back(expected_look_back)
                ),
                timeMax=datetime_to_rfc3339(
                    __tdstr_to_rfc3339_forward(expected_look_forward)
                ),
                singleEvents=False,
                orderBy="updated",
            )

    for import_data in imported_events_data:
        cal, expected_events = import_data

        if expected_events is not None:
            cal.import_event.assert_has_calls([call(e) for e in expected_events])


def __new_event(from_, del_=[], **kwargs):
    newattrs = from_.attributes.copy()
    for d in del_:
        del newattrs[d]
    for k, v in kwargs.items():
        newattrs[k] = v
    return Event(**newattrs)


@pytest.fixture
def event123():
    return Event(
        id="123",
        summary="Event 123",
        description="Event 123",
        start="2020-01-11T11:11:11Z",
    )


@pytest.fixture
def event123_nodesc():
    return Event(
        id="123",
        summary="Event 123",
        start="2020-01-11T11:11:11Z",
    )


@pytest.fixture
def event456():
    return Event(
        id="456",
        summary="Event 456",
        description="Event 456",
        start="2020-04-14T12:12:12Z",
    )


@pytest.fixture
def event123_all_day():
    return Event(
        id="123",
        summary="Event 123",
        description="Event 123",
        start={"date": "2020-01-11"},
        end={"date": "2020-01-12"},
    )


@pytest.fixture
def event456_all_day():
    return Event(
        id="456",
        summary="Event 456",
        description="Event 456",
        start={"date": "2020-04-14"},
        end={"date": "2020-04-14"},
    )


@pytest.fixture
def event789():
    return Event(
        id="789",
        summary="Event 789",
        description="Event 789",
        start="2020-07-17T13:13:13Z",
    )


def test_run_copy_rule(event123, event456, event789):
    config = {"rules": [{"method": "copy", "src": "cs_foo", "dst": "cs_bar"}]}

    __run_copy_rule_test(
        config,
        foo_events=[event123, event456, event789],
        bar_expected_events=[
            __new_event(from_=event123, del_=["id"], privateCopy=True),
            __new_event(from_=event456, del_=["id"], privateCopy=True),
            __new_event(from_=event789, del_=["id"], privateCopy=True),
        ],
    )


def test_run_copy_rule_3_calendars(event123, event456, event789):
    config = {
        "rules": [
            {"method": "copy", "src": "cs_foo", "dst": "cs_bar"},
            {"method": "copy", "src": "cs_foo", "dst": "cid_baz"},
        ]
    }

    __run_copy_rule_test(
        config,
        foo_events=[event123, event456, event789],
        bar_expected_events=[
            __new_event(from_=event123, del_=["id"], privateCopy=True),
            __new_event(from_=event456, del_=["id"], privateCopy=True),
            __new_event(from_=event789, del_=["id"], privateCopy=True),
        ],
        baz_expected_events=[
            __new_event(from_=event123, del_=["id"], privateCopy=True),
            __new_event(from_=event456, del_=["id"], privateCopy=True),
            __new_event(from_=event789, del_=["id"], privateCopy=True),
        ],
    )


def test_run_copy_rule_with_disabled_private_copy(event123, event456, event789):
    config = {
        "rules": [
            {"method": "copy", "src": "cs_foo", "dst": "cs_bar", "private_copy": False}
        ]
    }

    __run_copy_rule_test(
        config,
        foo_events=[event123, event456, event789],
        bar_expected_events=[
            __new_event(from_=event123, del_=["id"]),
            __new_event(from_=event456, del_=["id"]),
            __new_event(from_=event789, del_=["id"]),
        ],
    )


def test_run_copy_rule_with_different_look_back_forward(event123, event456, event789):
    config = {
        "rules": [
            {
                "method": "copy",
                "src": "cs_foo",
                "dst": "cs_bar",
                "private_copy": False,
                "look_back": "3 days",
                "look_forward": "3 days",
            }
        ]
    }

    __run_copy_rule_test(
        config,
        foo_events=[event123, event456, event789],
        bar_expected_events=[
            __new_event(from_=event123, del_=["id"]),
            __new_event(from_=event456, del_=["id"]),
            __new_event(from_=event789, del_=["id"]),
        ],
        expected_look_back="3 days",
        expected_look_forward="3 days",
    )


def test_run_copy_rule_with_description_append_transform_with_variables(
    event123, event456, event789
):
    config = {
        "rules": [
            {
                "method": "copy",
                "src": "cs_foo",
                "dst": "cs_bar",
                "transform": [
                    {"description_append": "Foo $calendar_id $calendar_summary Bar"}
                ],
            }
        ]
    }

    __run_copy_rule_test(
        config,
        foo_events=[event123, event456, event789],
        bar_expected_events=[
            __new_event(
                from_=event123,
                del_=["id"],
                privateCopy=True,
                description="Event 123\n\nFoo cid_foo cs_foo Bar",
            ),
            __new_event(
                from_=event456,
                del_=["id"],
                privateCopy=True,
                description="Event 456\n\nFoo cid_foo cs_foo Bar",
            ),
            __new_event(
                from_=event789,
                del_=["id"],
                privateCopy=True,
                description="Event 789\n\nFoo cid_foo cs_foo Bar",
            ),
        ],
    )


def test_run_copy_rule_with_description_append_transform_when_no_description(
    event123_nodesc,
):
    config = {
        "rules": [
            {
                "method": "copy",
                "src": "cs_foo",
                "dst": "cs_bar",
                "transform": [
                    {
                        "description_append": "Added from $calendar_name $calendar_id $calendar_summary"
                    }
                ],
            }
        ]
    }

    __run_copy_rule_test(
        config,
        foo_events=[event123_nodesc],
        bar_expected_events=[
            __new_event(
                from_=event123_nodesc,
                del_=["id"],
                privateCopy=True,
                description="\n\nAdded from Foo cid_foo cs_foo",
            ),
        ],
    )


def test_run_copy_rule_with_all_day_events_filtered_out(
    event123_all_day, event456_all_day, event789
):
    config = {
        "rules": [
            {
                "method": "copy",
                "src": "cs_foo",
                "dst": "cs_bar",
                "filter": {"all_day_event": False},
            }
        ]
    }

    __run_copy_rule_test(
        config,
        foo_events=[event123_all_day, event456_all_day, event789],
        bar_expected_events=[
            __new_event(from_=event789, del_=["id"], privateCopy=True),
        ],
    )


def test_run_copy_rule_with_all_day_events_only(
    event123_all_day, event456_all_day, event789
):
    config = {
        "rules": [
            {
                "method": "copy",
                "src": "cs_foo",
                "dst": "cs_bar",
                "filter": {"all_day_event": True},
            }
        ]
    }

    __run_copy_rule_test(
        config,
        foo_events=[event123_all_day, event456_all_day, event789],
        bar_expected_events=[
            __new_event(from_=event123_all_day, del_=["id"], privateCopy=True),
            __new_event(from_=event456_all_day, del_=["id"], privateCopy=True),
        ],
    )
