from fnmatch import fnmatch


def match_all_day_event(data, event):
    """Matches all-day events. Example config:

    filter:
        all_day_event: true
    """
    assert type(data) is bool
    return event.is_all_day() == data


def match_summary(data, event):
    """Matches an event summary, which can contain globs. Example config:

    filter:
        summary: Your order from Amazon*
    """
    assert type(data) is str
    return fnmatch(event.summary, data)


def match_not(data, event):
    """Matches the inverse of a nested match. Example config:

    filter:
        not:
            summary: Your order from Amazon*
    """
    assert type(data) is dict
    return not match(data, event)


def match_any_of(data, event):
    """Matches if any nested matches succeed. Example config:

    filter:
        any_of:
            - summary: Your order from Amazon*
            - summary: Your Amazon order*
    """
    assert type(data) is list

    for data_item in data:
        sub_match = match(data_item, event)
        if sub_match:
            return True

    return False


def match_all_of(data, event):
    """Matches if all nested matches succeed. Example config:

    filter:
        all_of:
            - summary: Your order from Amazon*
            - all_day_event: false
    """
    assert type(data) is list

    for data_item in data:
        sub_match = match(data_item, event)
        if not sub_match:
            return False

    return True


def match(data, event):
    """Matches a nested match. Called by other modules to start matching."""
    assert type(data) is dict
    assert len(data) == 1

    for k, v in data.items():
        # return straight away since there should just be one item
        return FILTERS[k](v, event)


FILTERS = {
    "all_day_event": match_all_day_event,
    "summary": match_summary,
    "all_of": match_all_of,
    "any_of": match_any_of,
    "not": match_not,
}
