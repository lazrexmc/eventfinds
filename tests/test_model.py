import pytest
from datetime import date

import model
from model import (ValidationError, validate_header, validate_row, parse_months,
                   months_from_dates, slugify, COLUMNS)


def good_row(**over):
    r = {c: "" for c in COLUMNS}
    r.update({
        "id": "11111111-1111-4111-8111-111111111111",
        "name": "Boone County Fair", "event_type": "county_fair", "cadence": "annual",
        "city": "Columbia", "state": "MO", "county": "Boone",
        "start_date": "2026-07-21", "end_date": "2026-07-25",
        "source_url": "https://example.com/fair", "last_verified": "2026-08-30",
        "visibility": "published",
    })
    r.update(over)
    return r


def test_columns_are_the_contract():
    assert COLUMNS == ["id", "name", "event_type", "cadence", "city", "state", "county",
                       "start_date", "end_date", "months", "dates_text", "attendance_text",
                       "homepage_url", "source_url", "description", "last_verified",
                       "visibility", "featured"]
    assert not any(("contact" in c) or ("email" in c) or ("phone" in c) for c in COLUMNS)


def test_header_must_match_exactly():
    validate_header(COLUMNS)
    with pytest.raises(ValidationError):
        validate_header(COLUMNS + ["contact_email"])
    with pytest.raises(ValidationError):
        validate_header(list(reversed(COLUMNS)))


def test_valid_row_is_typed():
    r = validate_row(good_row(), 2)
    assert r["months"] == [7]
    assert r["featured"] is False
    assert r["county"] == "Boone"
    assert r["homepage_url"] is None
    assert r["end_date"] == "2026-07-25"


def test_months_derived_from_date_range_when_blank():
    r = validate_row(good_row(start_date="2026-11-20", end_date="2027-01-03"), 2)
    assert r["months"] == [1, 11, 12]


def test_explicit_months_win_over_dates():
    r = validate_row(good_row(months="6;7"), 2)
    assert r["months"] == [6, 7]


@pytest.mark.parametrize("field,value,fragment", [
    ("id", "", "id is blank"),
    ("id", "not-a-uuid", "UUID"),
    ("id", "11111111-1111-1111-8111-111111111111", "UUID"),   # version nibble is 1, not 4
    ("name", "", "name"),
    ("event_type", "hoedown", "event_type"),
    ("cadence", "sometimes", "cadence"),
    ("state", "Missouri", "state"),
    ("state", "", "state"),
    ("city", "", "city"),
    ("start_date", "July 4", "start_date"),
    ("visibility", "public", "visibility"),
    ("featured", "yes", "featured"),
    ("homepage_url", "www.example.com", "homepage_url"),
    ("months", "13", "months"),
    ("months", "6;6", "months"),
])
def test_bad_values_name_the_line_and_field(field, value, fragment):
    with pytest.raises(ValidationError) as ei:
        validate_row(good_row(**{field: value}), 7)
    assert "line 7" in str(ei.value)
    assert fragment in str(ei.value)


def test_end_before_start_and_end_without_start_fail():
    with pytest.raises(ValidationError):
        validate_row(good_row(start_date="2026-07-25", end_date="2026-07-21"), 3)
    with pytest.raises(ValidationError):
        validate_row(good_row(start_date="", end_date="2026-07-21"), 3)


def test_one_time_requires_start_date():
    with pytest.raises(ValidationError) as ei:
        validate_row(good_row(cadence="one_time", start_date="", end_date=""), 4)
    assert "one_time" in str(ei.value)


def test_published_requires_source_url_and_last_verified():
    with pytest.raises(ValidationError):
        validate_row(good_row(source_url=""), 2)
    with pytest.raises(ValidationError):
        validate_row(good_row(last_verified=""), 2)
    # a draft may omit both
    r = validate_row(good_row(visibility="draft", source_url="", last_verified=""), 2)
    assert r["visibility"] == "draft"


def test_unknown_column_in_row_is_rejected():
    raw = good_row()
    raw["contact_email"] = "x@example.com"
    with pytest.raises(ValidationError):
        validate_row(raw, 2)


def test_parse_months_and_months_from_dates():
    assert parse_months("") == []
    assert parse_months("3; 4 ;12") == [3, 4, 12]
    with pytest.raises(ValueError):
        parse_months("0")
    assert months_from_dates(date(2026, 7, 21), None) == [7]
    assert months_from_dates(date(2026, 7, 21), date(2026, 9, 2)) == [7, 8, 9]


def test_slugify():
    assert slugify("Boone County Fair", "Columbia", "MO") == "boone-county-fair-columbia-mo"
    assert slugify("  Art & Wine!  ", "St. Louis", "MO") == "art-wine-st-louis-mo"
