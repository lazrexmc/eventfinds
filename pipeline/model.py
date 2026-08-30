"""model.py - the source-file contract for data/events.csv.

Everything the export trusts about a row is decided here, once: the closed column list, the
vocabularies, the per-field rules, the slug. A defect is a ValidationError naming the line and the
field - never a crash, never a silently-skipped row.
ASCII only in this file (Windows cp1252 trap).
"""
import re
from datetime import date

COLUMNS = [
    "id", "name", "event_type", "cadence", "city", "state", "county",
    "start_date", "end_date", "months", "dates_text", "attendance_text",
    "homepage_url", "source_url", "description", "last_verified", "visibility", "featured",
]

EVENT_TYPES = (
    "state_fair", "county_fair", "festival", "food_truck_rally", "farmers_market", "oktoberfest",
    "craft_fair", "art_fair", "music_fest", "bbq_fest", "balloon_fest", "holiday_market",
    "cultural_fest", "sports_tournament", "rodeo", "car_show", "air_show", "winery", "concert",
    "market", "parade", "race", "other",
)
CADENCES = ("annual", "one_time", "recurring")
VISIBILITIES = ("published", "draft", "retired")

UUID4_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
STATE_RE = re.compile(r"^[A-Z]{2}$")
URL_RE = re.compile(r"^https?://\S+$")


class ValidationError(Exception):
    """A source-file defect with its line number. A controlled failure, not a crash."""


def validate_header(fieldnames):
    got = list(fieldnames or [])
    if got != COLUMNS:
        raise ValidationError(
            "header must be exactly: " + ",".join(COLUMNS) + " ; got: " + ",".join(got)
        )


def _blank(v):
    return v is None or str(v).strip() == ""


def parse_months(s):
    """'6;7' -> [6, 7]. Blank -> []. Raises ValueError on anything outside 1-12 or repeated."""
    if _blank(s):
        return []
    out = []
    for part in str(s).split(";"):
        part = part.strip()
        if not part.isdigit() or not 1 <= int(part) <= 12:
            raise ValueError("months entry %r is not an integer 1-12" % part)
        m = int(part)
        if m in out:
            raise ValueError("months repeats %d" % m)
        out.append(m)
    return out


def months_from_dates(start, end):
    """Every calendar month touched by [start, end]; end defaults to start. Sorted, max 12."""
    end = end or start
    ms = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month) and len(ms) < 12:
        if m not in ms:
            ms.append(m)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return sorted(ms)


def slugify(name, city, state):
    text = "%s %s %s" % (name, city, state)
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _date(value, field, line):
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValidationError("line %d: %s %r is not YYYY-MM-DD" % (line, field, value))


def validate_row(raw, line):
    """Validate one csv.DictReader row. Returns a typed dict with exactly COLUMNS as keys
    (strings or None; months -> list[int]; featured -> bool). Raises ValidationError."""
    extra = [k for k in raw.keys() if k not in COLUMNS and k is not None]
    if extra:
        raise ValidationError("line %d: unknown column(s) %s" % (line, ",".join(map(str, extra))))
    if None in raw:
        raise ValidationError("line %d: more cells than header columns" % line)
    r = {c: (None if _blank(raw.get(c)) else str(raw.get(c)).strip()) for c in COLUMNS}

    if r["id"] is None:
        raise ValidationError("line %d: id is blank (run: python pipeline/assign_ids.py)" % line)
    if not UUID4_RE.match(r["id"]):
        raise ValidationError("line %d: id %r is not a lowercase UUID4" % (line, r["id"]))
    if r["name"] is None:
        raise ValidationError("line %d: name is required" % line)
    if r["event_type"] not in EVENT_TYPES:
        raise ValidationError("line %d: event_type %r is not one of %s"
                              % (line, r["event_type"], ", ".join(EVENT_TYPES)))
    if r["cadence"] not in CADENCES:
        raise ValidationError("line %d: cadence %r is not one of %s"
                              % (line, r["cadence"], ", ".join(CADENCES)))
    if r["city"] is None:
        raise ValidationError("line %d: city is required" % line)
    if r["state"] is None or not STATE_RE.match(r["state"]):
        raise ValidationError("line %d: state %r must be a 2-letter code" % (line, r["state"]))

    start = _date(r["start_date"], "start_date", line) if r["start_date"] else None
    end = _date(r["end_date"], "end_date", line) if r["end_date"] else None
    if end and not start:
        raise ValidationError("line %d: end_date without start_date" % line)
    if start and end and end < start:
        raise ValidationError("line %d: end_date %s is before start_date %s"
                              % (line, r["end_date"], r["start_date"]))
    if r["cadence"] == "one_time" and not start:
        raise ValidationError("line %d: a one_time event requires start_date" % line)

    try:
        months = parse_months(r["months"])
    except ValueError as e:
        raise ValidationError("line %d: months: %s" % (line, e))
    if not months and start:
        months = months_from_dates(start, end)

    for field in ("homepage_url", "source_url"):
        if r[field] is not None and not URL_RE.match(r[field]):
            raise ValidationError("line %d: %s %r must start with http:// or https://"
                                  % (line, field, r[field]))
    if r["visibility"] not in VISIBILITIES:
        raise ValidationError("line %d: visibility %r is not one of %s"
                              % (line, r["visibility"], ", ".join(VISIBILITIES)))
    if r["last_verified"] is not None:
        _date(r["last_verified"], "last_verified", line)
    if r["visibility"] == "published":
        if r["source_url"] is None:
            raise ValidationError("line %d: a published row requires source_url" % line)
        if r["last_verified"] is None:
            raise ValidationError("line %d: a published row requires last_verified" % line)

    if r["featured"] is None or r["featured"].lower() == "false":
        featured = False
    elif r["featured"].lower() == "true":
        featured = True
    else:
        raise ValidationError("line %d: featured %r must be true, false or blank"
                              % (line, r["featured"]))

    r["months"] = months
    r["featured"] = featured
    return r
