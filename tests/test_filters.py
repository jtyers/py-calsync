import pytest
import yaml
from io import StringIO

from calsync.event import Event

from calsync.filters import match


@pytest.fixture
def event123():
    return Event(
        id="123",
        summary="Event 123",
        description="Event 123",
        start="2020-01-11T11:11:11Z",
    )


def load_yaml(yaml_string):
    with StringIO(yaml_string) as y:
        return yaml.load(y)


def test_match():
    config = load_yaml(
        """
filter:
    all_day_event: true
    """
    )

    event = Event(
        id="123",
        summary="Event 123",
        description="Event 123",
        start={
            "date": "2020-01-11",
        },
        end={
            "date": "2020-01-12",
        },
    )

    assert match(config["filter"], event) is True


def test_match_not_all_day_event():
    config = load_yaml(
        """
filter:
    all_day_event: true
    """
    )

    event = Event(
        id="123",
        summary="Event 123",
        description="Event 123",
        start={
            "date": "2020-01-11",
        },
        end={
            "date": "2020-01-12",
        },
    )

    assert match(config["filter"], event) is True


def test_match_all_day_event():
    config = load_yaml(
        """
filter:
    all_day_event: false
    """
    )

    event = Event(
        id="123",
        summary="Event 123",
        description="Event 123",
        start={
            "dateTime": "2020-01-11",
        },
        end={
            "dateTime": "2020-01-12",
        },
    )

    assert match(config["filter"], event) is True


def test_match_summary_exact():
    config = load_yaml(
        """
filter:
    summary: Event 123
    """
    )

    event = Event(
        id="123",
        summary="Event 123",
        description="Event 123",
    )

    assert match(config["filter"], event) is True


def test_match_summary_glob():
    config = load_yaml(
        """
filter:
    summary: Event very*summary
    """
    )

    event = Event(
        id="123",
        summary="Event very long summary",
        description="Event 123",
    )

    assert match(config["filter"], event) is True


def test_match_summary_glob_fail():
    config = load_yaml(
        """
filter:
    summary: Event very*summary
    """
    )

    event = Event(
        id="123",
        summary="Event summary very long",
        description="Event 123",
    )

    assert match(config["filter"], event) is False


def test_match_all_of():
    config = load_yaml(
        """
filter:
    all_of:
        - summary: Event very*summary
        - all_day_event: False
    """
    )

    event = Event(
        id="123",
        summary="Event very long summary",
        description="Event 123",
        start={
            "dateTime": "2020-01-11",
        },
        end={
            "dateTime": "2020-01-12",
        },
    )

    assert match(config["filter"], event) is True


def test_match_all_of_fail():
    config = load_yaml(
        """
filter:
    all_of:
        - summary: Event very*summary
        - all_day_event: False
    """
    )

    event = Event(
        id="123",
        summary="Event very long summary",
        description="Event 123",
        start={
            "date": "2020-01-11",
        },
        end={
            "date": "2020-01-12",
        },
    )

    assert match(config["filter"], event) is False


def test_match_any_of():
    config = load_yaml(
        """
filter:
    any_of:
        - summary: Event very*summary
        - all_day_event: False
    """
    )

    event = Event(
        id="123",
        summary="Event very long summary",
        description="Event 123",
        start={
            "dateTime": "2020-01-11",
        },
        end={
            "dateTime": "2020-01-12",
        },
    )

    assert match(config["filter"], event) is True


def test_match_any_of_fail():
    config = load_yaml(
        """
filter:
    any_of:
        - summary: Event very*summary
        - all_day_event: False
    """
    )

    event = Event(
        id="123",
        summary="Event summary very long",
        description="Event 123",
        start={
            "date": "2020-01-11",
        },
        end={
            "date": "2020-01-12",
        },
    )

    assert match(config["filter"], event) is False


def test_match_not():
    config = load_yaml(
        """
filter:
    not:
        any_of:
            - summary: Event very*summary
            - all_day_event: False
    """
    )

    event = Event(
        id="123",
        summary="Event very long summary",
        description="Event 123",
        start={
            "dateTime": "2020-01-11",
        },
        end={
            "dateTime": "2020-01-12",
        },
    )

    assert match(config["filter"], event) is False


def test_match_not_fail():
    config = load_yaml(
        """
filter:
    not:
        any_of:
            - summary: Event very*summary
            - all_day_event: False
    """
    )

    event = Event(
        id="123",
        summary="Event summary very long",
        description="Event 123",
        start={
            "date": "2020-01-11",
        },
        end={
            "date": "2020-01-12",
        },
    )

    assert match(config["filter"], event) is True
