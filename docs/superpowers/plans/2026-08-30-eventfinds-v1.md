# EventFinds v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A public, curated, filterable map-and-list directory of events, published as committed static JSON from one CSV, served from Cloudflare Pages at `eventfinds.pages.dev` for $0/month.

**Architecture:** A stdlib-only Python pipeline validates `data/events.csv`, geocodes published rows from `data/places.csv`, and exports `site/data/events.json` + `meta.json` behind ONE publish predicate; nine deterministic gates in `pipeline/checks.py` must pass before a push. A vanilla-JS page (ES modules, vendored Leaflet + markercluster) reads those two files, computes "upcoming" and distance in the browser, and renders an error box — never an empty map — when a file fails to load.

**Tech Stack:** Python 3.14 stdlib (pipeline), pytest 9 (pipeline tests), Node 24 `node --test` (page predicates), Leaflet 1.9.4 + Leaflet.markercluster (vendored, third-party), Cloudflare Pages (static host, root `site`, no build).

**Spec:** `docs/superpowers/specs/2026-08-30-eventfinds-v1-design.md` — the plan argues from it; executors read both. Method and traps: `F:\RapidForge\modules\event-finder.md` §5–§7.

## Global Constraints

- **No database, no server, no framework, no bundler, no LLM, no crawler, no accounts, no payments** (spec §1).
- **Nothing shared with Glizzness**: no key, project, data row, domain, brand; the strings `Glizzness` and `Midwest Event Finder` must not appear anywhere in this repo except this plan's attribution lines for the two third-party-style copies (spec §2 #15). Vendored Leaflet files and `verify_deploy.py` are copied **with attribution comments**; nothing else is copied.
- **The publish gate is one predicate, `is_published()` in `pipeline/export.py`, and nowhere else.** `site/js/` must not contain the tokens `visibility`, `published`, `draft`, `retired` (gate G6).
- **The CSV header is exactly the 18 columns in spec §4, in order.** No contact columns exist; a key containing `contact`, `email` or `phone` in `events.json` fails G7.
- **Failure is not emptiness**: the export exits 1 and names the row; the page shows the error box naming the file. Zero published rows is a valid, honest state (`event_count: 0`).
- **Deterministic export**: same CSV + places → byte-identical JSON except `generated_at`.
- **No inline `<style>` or `<script>`**; CSP has no `'unsafe-inline'`; no `<base>`; root-relative paths (`/js/app.js`).
- **Python files are ASCII-only** (Windows cp1252 trap): no em-dashes, arrows or curly quotes in `.py`; docs may use them. Check: `grep -nP "[^\x00-\x7F]" pipeline/*.py tests/*.py` must print nothing.
- **Commit after every task**; author `Lance McCarter <lancemccarter1316@hotmail.com>`; trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- **`site/data/` is committed** (it is the publication); `/data/` at the repo root is committed too (it is the source of truth). The `.gitignore` must be anchored (`/.venv/`, never `data/`).
- Run every command from the repo root `F:\EventFinds` with `python` (3.14) and `node` (24).

---

## File structure

```
.gitignore                     anchored ignores only
package.json                   {"type":"module"} so node --test can import site/js/*.js
README.md                      how to add an event, run the five commands, deploy (Task 12)
data/events.csv                SOURCE OF TRUTH; header only at v1
data/places.csv                city,state,lat,lng - the ONE geocoding table
pipeline/config.py             ROOT, paths, HOME, STALE_DAYS, PIPELINE_VERSION
pipeline/model.py              COLUMNS, enums, ValidationError, validate_header, validate_row,
                               parse_months, months_from_dates, slugify
pipeline/geocode.py            load_places, ring_offset, geocode, UnknownPlace
pipeline/assign_ids.py         fills blank id cells with uuid4 (CLI)
pipeline/export.py             is_published (THE gate), read_rows, build, write_publication, main
pipeline/checks.py             gates G1-G9 (CLI, exit 0 only on all-pass)
pipeline/serve_local.py        local server: correct MIME + production headers
pipeline/verify_deploy.py      origin-vs-git after every push (copied from the reference, attributed)
pipeline/fixtures/places.csv   Columbia only
pipeline/fixtures/negative.csv published + draft + retired rows (G2)
pipeline/fixtures/unknown_place.csv  one published row in a town places.csv lacks (G4)
tests/conftest.py              puts pipeline/ on sys.path
tests/test_model.py  test_geocode.py  test_export.py  test_assign_ids.py  test_verify_deploy.py  test_checks.py
tests/js/predicates.test.mjs   node --test for site/js/predicates.js
site/index.html                the shell
site/css/app.css               all styling (no inline)
site/js/predicates.js          pure functions: isUpcoming, haversineMiles, passesFilter, esc, distinctSorted, countyKey
site/js/data.js                fetchJson, FetchError, DataShapeError
site/js/app.js                 Leaflet + DOM wiring (ES module)
site/assets/vendor/leaflet/    leaflet.js, leaflet.css, leaflet.markercluster.js, MarkerCluster*.css, images/
site/data/events.json          THE PUBLICATION (committed)
site/data/meta.json
site/_headers                  CSP + security headers
```

---

### Task 1: Scaffold + `pipeline/model.py` (columns, enums, validation, slug, months)

**Files:**
- Create: `.gitignore`, `package.json`, `pipeline/config.py`, `pipeline/model.py`, `tests/conftest.py`, `data/events.csv`, `data/places.csv`
- Test: `tests/test_model.py`

**Interfaces:**
- Produces: `model.COLUMNS: list[str]` (18 names, spec §4 order); `model.EVENT_TYPES`, `model.CADENCES`, `model.VISIBILITIES`: tuples; `class ValidationError(Exception)`; `validate_header(fieldnames) -> None` (raises); `validate_row(raw: dict, line: int) -> dict` (raises; returns a typed row: strings or `None`, `months: list[int]`, `featured: bool`); `parse_months(s) -> list[int]` (raises `ValueError`); `months_from_dates(start: date, end: date | None) -> list[int]`; `slugify(name, city, state) -> str`. `config.HOME = {"name","lat","lng"}`, `config.EVENTS_CSV`, `config.PLACES_CSV`, `config.SITE_DATA`, `config.STALE_DAYS = 60`, `config.PIPELINE_VERSION = "1"`.

- [x] **Step 1: Write the scaffold files**

`.gitignore`:
```
# Anchored on purpose (an unanchored data/ once swallowed a whole publication). site/data/ and /data/ ARE committed.
/.venv/
__pycache__/
*.pyc
/.pytest_cache/
/node_modules/
.env
.env.*
```

`package.json`:
```json
{
  "name": "eventfinds",
  "private": true,
  "type": "module",
  "scripts": { "test": "node --test tests/js" }
}
```

`data/events.csv` (header only, one line, LF, no trailing spaces):
```
id,name,event_type,cadence,city,state,county,start_date,end_date,months,dates_text,attendance_text,homepage_url,source_url,description,last_verified,visibility,featured
```

`data/places.csv` (public geographic facts; add a town when an event names it):
```
city,state,lat,lng
Columbia,MO,38.9517,-92.3341
Jefferson City,MO,38.5767,-92.1735
Kansas City,MO,39.0997,-94.5786
St. Louis,MO,38.6270,-90.1994
Springfield,MO,37.2090,-93.2923
Sedalia,MO,38.7045,-93.2283
Boonville,MO,38.9739,-92.7430
Moberly,MO,39.4184,-92.4382
Hermann,MO,38.7036,-91.4374
Hannibal,MO,39.7084,-91.3585
Fulton,MO,38.8467,-91.9479
Rolla,MO,37.9514,-91.7713
```

`pipeline/config.py`:
```python
"""config.py - the per-deployment settings. ONE home per deployment (spec decision 5)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS_CSV = ROOT / "data" / "events.csv"
PLACES_CSV = ROOT / "data" / "places.csv"
SITE_DIR = ROOT / "site"
SITE_DATA = SITE_DIR / "data"

HOME = {"name": "Columbia, MO", "lat": 38.9517, "lng": -92.3341}
STALE_DAYS = 60          # a published row dated further in the past than this is WARNED about
PIPELINE_VERSION = "1"   # bump when the export contract changes
```

`tests/conftest.py`:
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
```

- [x] **Step 2: Write the failing tests**

`tests/test_model.py`:
```python
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
```

- [x] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest tests/test_model.py -q`
Expected: collection error `ModuleNotFoundError: No module named 'model'`.

- [x] **Step 4: Write `pipeline/model.py`**

```python
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
```

- [x] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_model.py -q`
Expected: all pass (about 30 including parametrised cases).

- [x] **Step 6: ASCII check and commit**

Run: `grep -nP "[^\x00-\x7F]" pipeline/*.py tests/*.py` — expected: no output.
```bash
git add .gitignore package.json data/events.csv data/places.csv pipeline/config.py pipeline/model.py tests/conftest.py tests/test_model.py
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "pipeline: source-file contract (columns, enums, validation, slug)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: `pipeline/geocode.py` (places table, lookup, ring offset, unknown place fails)

**Files:**
- Create: `pipeline/geocode.py`, `pipeline/fixtures/places.csv`
- Test: `tests/test_geocode.py`

**Interfaces:**
- Consumes: typed rows from `model.validate_row` (keys `id`, `city`, `state`, `name`).
- Produces: `class UnknownPlace(Exception)`; `load_places(path) -> dict[tuple[str,str], tuple[float,float]]` (raises `ValueError` on bad header, bad float, duplicate); `ring_offset(lat, lng, idx, n) -> tuple[float,float]`; `geocode(rows, places) -> dict[str, tuple[float,float]]` keyed by row `id`, values rounded to 5 dp; raises `UnknownPlace` whose message lists every `"City, ST (n rows: slug...)"` missing.

- [x] **Step 1: Write the fixture**

`pipeline/fixtures/places.csv`:
```
city,state,lat,lng
Columbia,MO,38.9517,-92.3341
```

- [x] **Step 2: Write the failing tests**

`tests/test_geocode.py`:
```python
import pytest
from pathlib import Path

from geocode import load_places, ring_offset, geocode, UnknownPlace
from model import slugify

FIX = Path(__file__).resolve().parent.parent / "pipeline" / "fixtures" / "places.csv"


def row(id_, name, city, state):
    return {"id": id_, "name": name, "city": city, "state": state}


def test_load_places_fixture():
    p = load_places(FIX)
    assert p[("Columbia", "MO")] == (38.9517, -92.3341)


def test_load_places_rejects_bad_header_and_duplicates(tmp_path):
    bad = tmp_path / "p.csv"
    bad.write_text("town,state,lat,lng\nX,MO,1,2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_places(bad)
    dup = tmp_path / "d.csv"
    dup.write_text("city,state,lat,lng\nX,MO,1,2\nX,MO,1.1,2.1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_places(dup)
    nan = tmp_path / "n.csv"
    nan.write_text("city,state,lat,lng\nX,MO,north,2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_places(nan)


def test_ring_offset_single_row_is_the_centroid_and_groups_spread_deterministically():
    assert ring_offset(38.0, -92.0, 0, 1) == (38.0, -92.0)
    a = ring_offset(38.0, -92.0, 0, 3)
    b = ring_offset(38.0, -92.0, 1, 3)
    assert a != b
    assert ring_offset(38.0, -92.0, 1, 3) == b            # deterministic
    assert abs(a[0] - 38.0) <= 0.0036 and abs(b[1] + 92.0) <= 0.0036


def test_geocode_two_rows_same_city_do_not_overlap():
    places = load_places(FIX)
    rows = [row("a", "A Fest", "Columbia", "MO"), row("b", "B Fest", "Columbia", "MO")]
    out = geocode(rows, places)
    assert set(out) == {"a", "b"}
    assert out["a"] != out["b"]
    for lat, lng in out.values():
        assert round(lat, 5) == lat and round(lng, 5) == lng


def test_unknown_place_names_every_missing_town_and_its_rows():
    places = load_places(FIX)
    rows = [row("a", "A Fest", "Columbia", "MO"),
            row("b", "B Fest", "Nowhere", "MO"),
            row("c", "C Fest", "Nowhere", "MO"),
            row("d", "D Fest", "Elsewhere", "KS")]
    with pytest.raises(UnknownPlace) as ei:
        geocode(rows, places)
    msg = str(ei.value)
    assert "Nowhere, MO" in msg and "Elsewhere, KS" in msg
    assert slugify("B Fest", "Nowhere", "MO") in msg
    assert "Columbia" not in msg
```

- [x] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest tests/test_geocode.py -q`
Expected: `ModuleNotFoundError: No module named 'geocode'`.

- [x] **Step 4: Write `pipeline/geocode.py`**

```python
"""geocode.py - city-centroid geocoding from data/places.csv, the ONE table.

Pins mark the city, not the venue (the page says so). Same-city rows get a deterministic ring
offset (~300 m) so they do not overlap. A (city, state) the table lacks FAILS the export by name -
it is never silently absent from the map.
ASCII only in this file.
"""
import csv
import math
from collections import OrderedDict

from model import slugify

PLACES_HEADER = ["city", "state", "lat", "lng"]
RING_DEG = 0.0035   # ~300-400 m


class UnknownPlace(Exception):
    """One or more (city, state) pairs are not in the places table. Message names them all."""


def load_places(path):
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if list(reader.fieldnames or []) != PLACES_HEADER:
            raise ValueError("%s: header must be city,state,lat,lng" % path)
        places = {}
        for n, r in enumerate(reader, start=2):
            key = (r["city"].strip(), r["state"].strip())
            if key in places:
                raise ValueError("%s line %d: duplicate place %s, %s" % (path, n, key[0], key[1]))
            try:
                places[key] = (float(r["lat"]), float(r["lng"]))
            except (TypeError, ValueError):
                raise ValueError("%s line %d: lat/lng not numeric for %s, %s"
                                 % (path, n, key[0], key[1]))
    return places


def ring_offset(lat, lng, idx, n):
    if n <= 1:
        return (lat, lng)
    ang = 2.0 * math.pi * idx / n
    return (lat + RING_DEG * math.cos(ang), lng + RING_DEG * math.sin(ang))


def geocode(rows, places):
    """rows: iterable of typed rows (id, name, city, state). Returns {id: (lat, lng)} rounded 5 dp.
    Raises UnknownPlace listing every missing town with its rows' slugs."""
    groups = OrderedDict()
    for r in rows:
        groups.setdefault((r["city"], r["state"]), []).append(r)
    missing = []
    for (city, state), group in groups.items():
        if (city, state) not in places:
            slugs = ", ".join(slugify(r["name"], r["city"], r["state"]) for r in group)
            missing.append("%s, %s (%d row%s: %s)" % (city, state, len(group),
                                                       "" if len(group) == 1 else "s", slugs))
    if missing:
        raise UnknownPlace("unknown place(s) - add them to data/places.csv: "
                           + "; ".join(missing))
    out = {}
    for (city, state), group in groups.items():
        lat0, lng0 = places[(city, state)]
        for idx, r in enumerate(group):
            lat, lng = ring_offset(lat0, lng0, idx, len(group))
            out[r["id"]] = (round(lat, 5), round(lng, 5))
    return out
```

- [x] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_geocode.py -q` — expected: 5 passed.

- [x] **Step 6: Commit**

```bash
git add pipeline/geocode.py pipeline/fixtures/places.csv tests/test_geocode.py
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "pipeline: centroid geocoding; unknown place fails by name

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: `pipeline/assign_ids.py` (fill blank ids once)

**Files:**
- Create: `pipeline/assign_ids.py`
- Test: `tests/test_assign_ids.py`

**Interfaces:**
- Produces: `assign_ids(csv_path) -> int` (number of ids assigned; rewrites the file in place, LF line endings, header unchanged, existing ids untouched); CLI `python pipeline/assign_ids.py [--csv PATH]` printing `assigned N id(s)`.

- [x] **Step 1: Write the failing tests**

`tests/test_assign_ids.py`:
```python
import csv
import re

from assign_ids import assign_ids
from model import COLUMNS, UUID4_RE

HEADER = ",".join(COLUMNS)


def test_blank_ids_get_uuid4_and_existing_ids_survive(tmp_path):
    p = tmp_path / "events.csv"
    p.write_text(
        HEADER + "\n"
        + "11111111-1111-4111-8111-111111111111,Keep Me,festival,annual,Columbia,MO,,,,,,,,,,,draft,\n"
        + ",New One,festival,annual,Columbia,MO,,,,,,,,,,,draft,\n",
        encoding="utf-8")
    assert assign_ids(p) == 1
    with open(p, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["id"] == "11111111-1111-4111-8111-111111111111"
    assert UUID4_RE.match(rows[1]["id"])
    assert rows[1]["name"] == "New One"
    assert p.read_bytes().count(b"\r\n") == 0
    assert assign_ids(p) == 0            # idempotent


def test_header_only_file_is_left_alone(tmp_path):
    p = tmp_path / "events.csv"
    p.write_text(HEADER + "\n", encoding="utf-8")
    assert assign_ids(p) == 0
    assert p.read_text(encoding="utf-8") == HEADER + "\n"
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_assign_ids.py -q` — expected: `ModuleNotFoundError`.

- [x] **Step 3: Write `pipeline/assign_ids.py`**

```python
"""assign_ids.py - give every row a permanent id, once.

Identity is a UUID4 assigned here and never derived from position (a spreadsheet row inserted in
the middle must not renumber anything). Run after adding rows; the export refuses a blank id.
ASCII only in this file.
"""
import argparse
import csv
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config                      # noqa: E402
from model import validate_header  # noqa: E402


def assign_ids(csv_path):
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        validate_header(reader.fieldnames)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)
    assigned = 0
    for r in rows:
        if r.get("id") is None or r["id"].strip() == "":
            r["id"] = str(uuid.uuid4())
            assigned += 1
    if assigned:
        with open(csv_path, "w", encoding="utf-8", newline="\n") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    return assigned


def main(argv=None):
    ap = argparse.ArgumentParser(description="fill blank id cells in the events CSV with UUID4s")
    ap.add_argument("--csv", default=str(config.EVENTS_CSV))
    a = ap.parse_args(argv)
    n = assign_ids(Path(a.csv))
    print("assigned %d id(s) in %s" % (n, a.csv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_assign_ids.py -q` — expected: 2 passed.

- [x] **Step 5: Commit**

```bash
git add pipeline/assign_ids.py tests/test_assign_ids.py
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "pipeline: assign_ids fills blank ids with uuid4, once

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: `pipeline/export.py` (CSV → `events.json` + `meta.json`; THE gate)

**Files:**
- Create: `pipeline/export.py`, `pipeline/fixtures/negative.csv`, `pipeline/fixtures/unknown_place.csv`
- Test: `tests/test_export.py`

**Interfaces:**
- Consumes: `model.validate_header/validate_row/slugify`, `geocode.load_places/geocode/UnknownPlace`, `config.HOME/STALE_DAYS/PIPELINE_VERSION`.
- Produces: `is_published(row) -> bool` (**the only publish predicate in the repo**); `read_rows(csv_path) -> list[dict]` (validated; adds `row["slug"]`; raises `ValidationError` on duplicate id or slug); `build(rows, places, home, generated_at: str, source_sha256: str, today: date) -> tuple[dict, dict, list]` returning `(events_doc, meta, stale_warnings)`; `EVENT_KEYS: tuple` (the exact per-event key set); `write_publication(out_dir: Path, events_doc, meta) -> None`; `sha256_file(path) -> str`; `main(argv) -> int` with `--csv`, `--places`, `--out`, `--today YYYY-MM-DD` flags; exit 1 with `ERROR:` line on any `ValidationError`/`UnknownPlace`; prints `WARN stale: <slug> (<date>)` per stale row and a final `exported N event(s)` line.

- [x] **Step 1: Write the fixtures**

`pipeline/fixtures/negative.csv`:
```
id,name,event_type,cadence,city,state,county,start_date,end_date,months,dates_text,attendance_text,homepage_url,source_url,description,last_verified,visibility,featured
11111111-1111-4111-8111-111111111111,Published Fest,festival,annual,Columbia,MO,Boone,2026-09-12,2026-09-13,,,,https://example.com/p,https://example.com/p-source,,2026-08-30,published,false
22222222-2222-4222-8222-222222222222,Draft Fest,festival,annual,Columbia,MO,Boone,2026-09-12,,,,,,https://example.com/d-source,,2026-08-30,draft,
33333333-3333-4333-8333-333333333333,Retired Fest,festival,annual,Columbia,MO,Boone,2026-09-12,,,,,,https://example.com/r-source,,2026-08-30,retired,
```

`pipeline/fixtures/unknown_place.csv`:
```
id,name,event_type,cadence,city,state,county,start_date,end_date,months,dates_text,attendance_text,homepage_url,source_url,description,last_verified,visibility,featured
44444444-4444-4444-8444-444444444444,Lost Fest,festival,annual,Nowhere,MO,,2026-10-01,,,,,,https://example.com/lost,,2026-08-30,published,
```

- [x] **Step 2: Write the failing tests**

`tests/test_export.py`:
```python
import json
from datetime import date
from pathlib import Path

import pytest

import export
from export import is_published, read_rows, build, write_publication, main, EVENT_KEYS
from geocode import load_places
from model import ValidationError, COLUMNS

FIX = Path(__file__).resolve().parent.parent / "pipeline" / "fixtures"
HOME = {"name": "Columbia, MO", "lat": 38.9517, "lng": -92.3341}
HEADER = ",".join(COLUMNS)


def test_is_published_is_the_only_gate():
    assert is_published({"visibility": "published"}) is True
    assert is_published({"visibility": "draft"}) is False
    assert is_published({"visibility": "retired"}) is False


def test_negative_gate_only_published_row_is_exported():
    rows = read_rows(FIX / "negative.csv")
    places = load_places(FIX / "places.csv")
    events_doc, meta, warns = build(rows, places, HOME, "2026-08-30T00:00:00+00:00", "abc", date(2026, 8, 30))
    ids = [e["id"] for e in events_doc["events"]]
    assert ids == ["11111111-1111-4111-8111-111111111111"]
    assert meta["event_count"] == 1
    assert meta["as_of"] == "2026-08-30"
    assert meta["event_types"] == ["festival"]
    assert meta["home"] == HOME
    assert warns == []


def test_event_keys_are_the_contract_and_carry_no_contacts():
    rows = read_rows(FIX / "negative.csv")
    events_doc, _, _ = build(rows, load_places(FIX / "places.csv"), HOME, "t", "s", date(2026, 8, 30))
    e = events_doc["events"][0]
    assert tuple(sorted(e.keys())) == tuple(sorted(EVENT_KEYS))
    assert not any(("contact" in k) or ("email" in k) or ("phone" in k) for k in e)
    assert e["slug"] == "published-fest-columbia-mo"
    assert e["months"] == [9]
    assert e["featured"] is False
    assert e["homepage_url"] == "https://example.com/p"
    assert e["description"] is None
    assert isinstance(e["lat"], float) and isinstance(e["lng"], float)


def test_unknown_place_exits_1_and_names_the_town(tmp_path, capsys):
    rc = main(["--csv", str(FIX / "unknown_place.csv"), "--places", str(FIX / "places.csv"),
               "--out", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "ERROR" in out and "Nowhere, MO" in out and "lost-fest-nowhere-mo" in out
    assert not (tmp_path / "events.json").exists()


def test_validation_error_exits_1_and_names_the_line(tmp_path, capsys):
    bad = tmp_path / "bad.csv"
    bad.write_text(HEADER + "\n"
                   + "11111111-1111-4111-8111-111111111111,X,festival,annual,Columbia,MO,,,,,,,,,,,public,\n",
                   encoding="utf-8")
    rc = main(["--csv", str(bad), "--places", str(FIX / "places.csv"), "--out", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 1 and "line 2" in out and "visibility" in out


def test_duplicate_id_and_duplicate_slug_fail(tmp_path):
    row = "11111111-1111-4111-8111-111111111111,Same,festival,annual,Columbia,MO,,,,,,,,,,,draft,\n"
    p = tmp_path / "dup_id.csv"
    p.write_text(HEADER + "\n" + row + row, encoding="utf-8")
    with pytest.raises(ValidationError) as ei:
        read_rows(p)
    assert "duplicate id" in str(ei.value)
    p2 = tmp_path / "dup_slug.csv"
    p2.write_text(HEADER + "\n" + row
                  + "22222222-2222-4222-8222-222222222222,Same,festival,annual,Columbia,MO,,,,,,,,,,,draft,\n",
                  encoding="utf-8")
    with pytest.raises(ValidationError) as ei:
        read_rows(p2)
    assert "duplicate slug" in str(ei.value)


def test_empty_source_is_an_honest_empty_publication(tmp_path, capsys):
    p = tmp_path / "empty.csv"
    p.write_text(HEADER + "\n", encoding="utf-8")
    rc = main(["--csv", str(p), "--places", str(FIX / "places.csv"), "--out", str(tmp_path)])
    assert rc == 0
    meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
    events = json.loads((tmp_path / "events.json").read_text(encoding="utf-8"))
    assert meta["event_count"] == 0 and meta["as_of"] is None and meta["event_types"] == []
    assert events == {"events": []}


def test_export_is_deterministic_except_generated_at(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    for out in (a, b):
        out.mkdir()
        assert main(["--csv", str(FIX / "negative.csv"), "--places", str(FIX / "places.csv"),
                     "--out", str(out)]) == 0
    assert (a / "events.json").read_bytes() == (b / "events.json").read_bytes()
    ma = json.loads((a / "meta.json").read_text(encoding="utf-8"))
    mb = json.loads((b / "meta.json").read_text(encoding="utf-8"))
    ma.pop("generated_at"); mb.pop("generated_at")
    assert ma == mb
    assert len(ma["source_sha256"]) == 64


def test_stale_published_row_is_warned_not_failed(tmp_path, capsys):
    p = tmp_path / "stale.csv"
    p.write_text(HEADER + "\n"
                 + "11111111-1111-4111-8111-111111111111,Old Fest,festival,annual,Columbia,MO,,2026-01-10,2026-01-11,,,,,https://example.com/s,,2026-01-12,published,\n",
                 encoding="utf-8")
    rc = main(["--csv", str(p), "--places", str(FIX / "places.csv"), "--out", str(tmp_path),
               "--today", "2026-08-30"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "WARN stale: old-fest-columbia-mo (2026-01-11)" in out
    assert "exported 1 event(s)" in out
```

- [x] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest tests/test_export.py -q` — expected: `ModuleNotFoundError: No module named 'export'`.

- [x] **Step 4: Write `pipeline/export.py`**

```python
"""export.py - data/events.csv -> site/data/events.json + meta.json.

THE PUBLISH GATE LIVES HERE, ONCE: is_published(). The page carries no copy of it (gate G6).
Failure is not emptiness: any defect exits 1 naming the row; a genuinely empty directory exports
honestly as event_count 0. Deterministic: same inputs -> byte-identical output except generated_at.
ASCII only in this file.
"""
import argparse
import csv
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config                                              # noqa: E402
from geocode import UnknownPlace, geocode, load_places     # noqa: E402
from model import ValidationError, slugify, validate_header, validate_row  # noqa: E402

EVENT_KEYS = (
    "id", "slug", "name", "event_type", "cadence", "city", "state", "county", "lat", "lng",
    "start_date", "end_date", "months", "dates_text", "attendance_text", "homepage_url",
    "source_url", "description", "last_verified", "featured",
)


def is_published(row):
    """THE publish gate. A row is public iff a human set visibility to published."""
    return row["visibility"] == "published"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(csv_path):
    """Validate every row; add slug; enforce unique id and unique slug. Raises ValidationError."""
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        validate_header(reader.fieldnames)
        rows = [validate_row(raw, n) for n, raw in enumerate(reader, start=2)]
    seen_id, seen_slug = {}, {}
    for n, r in enumerate(rows, start=2):
        r["slug"] = slugify(r["name"], r["city"], r["state"])
        if r["id"] in seen_id:
            raise ValidationError("line %d: duplicate id %s (also line %d)" % (n, r["id"], seen_id[r["id"]]))
        if r["slug"] in seen_slug:
            raise ValidationError("line %d: duplicate slug %s (also line %d)" % (n, r["slug"], seen_slug[r["slug"]]))
        seen_id[r["id"]] = n
        seen_slug[r["slug"]] = n
    return rows


def build(rows, places, home, generated_at, source_sha256, today):
    """Returns (events_doc, meta, stale_warnings). Raises UnknownPlace for a published row whose
    (city, state) the places table lacks. Only published rows are geocoded or exported."""
    published = [r for r in rows if is_published(r)]
    coords = geocode(published, places)
    events = []
    for r in published:
        lat, lng = coords[r["id"]]
        e = {k: r[k] for k in EVENT_KEYS if k not in ("lat", "lng")}
        e["lat"], e["lng"] = lat, lng
        events.append(e)
    events.sort(key=lambda e: e["slug"])
    stale = []
    for e in events:
        last = e["end_date"] or e["start_date"]
        if last and (today - date.fromisoformat(last)).days > config.STALE_DAYS:
            stale.append((e["slug"], last))
    verified = [e["last_verified"] for e in events if e["last_verified"]]
    meta = {
        "generated_at": generated_at,
        "as_of": max(verified) if verified else None,
        "event_count": len(events),
        "home": dict(home),
        "event_types": sorted({e["event_type"] for e in events}),
        "source_sha256": source_sha256,
        "pipeline_version": config.PIPELINE_VERSION,
    }
    return {"events": events}, meta, stale


def _dump(path, obj):
    text = json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    return len(text.encode("utf-8"))


def write_publication(out_dir, events_doc, meta):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    _dump(out_dir / "events.json", events_doc)
    _dump(out_dir / "meta.json", meta)


def main(argv=None):
    ap = argparse.ArgumentParser(description="export the events CSV to static JSON")
    ap.add_argument("--csv", default=str(config.EVENTS_CSV))
    ap.add_argument("--places", default=str(config.PLACES_CSV))
    ap.add_argument("--out", default=str(config.SITE_DATA))
    ap.add_argument("--today", default=None, help="YYYY-MM-DD; default = today (for the stale warning)")
    a = ap.parse_args(argv)
    today = date.fromisoformat(a.today) if a.today else date.today()
    try:
        rows = read_rows(a.csv)
        places = load_places(a.places)
        events_doc, meta, stale = build(
            rows, places, config.HOME,
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            sha256_file(a.csv), today)
    except (ValidationError, UnknownPlace, ValueError, OSError) as e:
        print("ERROR: %s" % e)
        return 1
    for slug, last in stale:
        print("WARN stale: %s (%s)" % (slug, last))
    write_publication(a.out, events_doc, meta)
    print("exported %d event(s) -> %s  (as_of=%s, types=%d)"
          % (meta["event_count"], a.out, meta["as_of"], len(meta["event_types"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_export.py -q` — expected: 9 passed.

- [x] **Step 6: Produce the real (empty) publication and commit it**

Run: `python pipeline/export.py` — expected: `exported 0 event(s) -> ...site\data  (as_of=None, types=0)`; `site/data/events.json` is `{"events": []}` and `meta.json` has `"event_count": 0`.
```bash
grep -nP "[^\x00-\x7F]" pipeline/*.py tests/*.py   # expected: nothing
git add pipeline/export.py pipeline/fixtures/negative.csv pipeline/fixtures/unknown_place.csv tests/test_export.py site/data/events.json site/data/meta.json
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "pipeline: export with the one publish gate; first (empty) publication

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: `pipeline/checks.py` (gates G1–G9)

**Files:**
- Create: `pipeline/checks.py`
- Test: `tests/test_checks.py`

**Interfaces:**
- Consumes: `export.read_rows/build/main/EVENT_KEYS`, `geocode.load_places`, `config.*`.
- Produces: gate functions `g1_source_valid()`, `g2_negative_gate()`, `g3_export_current()`, `g4_unknown_place()`, `g5_publication_committed()`, `g6_no_gate_in_js(site_js_dir=config.SITE_DIR / "js")`, `g7_named_columns(events_path=config.SITE_DATA / "events.json")`, `g8_stale()`, `g9_headers(headers_path=config.SITE_DIR / "_headers")`; each returns `(ok: bool | None, message: str)` where `None` = WARN/SKIP; `main(argv) -> int` prints one `PASS/FAIL/WARN` line per gate with its evidence and exits 0 only if no gate returned `False`. G6 and G9 tolerate the file/dir not existing yet by returning `False` with a message naming the path (they exist after Tasks 7–9).

- [ ] **Step 1: Write the failing tests**

`tests/test_checks.py`:
```python
from pathlib import Path

import checks


def test_g6_flags_gate_tokens_in_js(tmp_path):
    js = tmp_path / "js"
    js.mkdir()
    (js / "clean.js").write_text("export const x = 1; // upcoming only\n", encoding="utf-8")
    ok, msg = checks.g6_no_gate_in_js(js)
    assert ok is True
    (js / "dirty.js").write_text("if (e.visibility === 'published') {}\n", encoding="utf-8")
    ok, msg = checks.g6_no_gate_in_js(js)
    assert ok is False and "dirty.js" in msg and "visibility" in msg


def test_g7_requires_exact_keys_and_no_contact_keys(tmp_path):
    p = tmp_path / "events.json"
    keys = list(checks.EVENT_KEYS)
    good = "{\"events\": [{" + ",".join("\"%s\": null" % k for k in keys) + "}]}"
    p.write_text(good, encoding="utf-8")
    assert checks.g7_named_columns(p)[0] is True
    p.write_text(good.replace("\"description\": null", "\"contact_email\": null"), encoding="utf-8")
    ok, msg = checks.g7_named_columns(p)
    assert ok is False and "contact_email" in msg
    p.write_text("{\"events\": []}", encoding="utf-8")
    assert checks.g7_named_columns(p)[0] is True


def test_g9_headers_rules(tmp_path):
    h = tmp_path / "_headers"
    h.write_text("/*\n  Content-Security-Policy: default-src 'self'; script-src 'self'\n"
                 "  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n", encoding="utf-8")
    assert checks.g9_headers(h)[0] is True
    h.write_text("/*\n  Content-Security-Policy: default-src 'self'; style-src 'self' 'unsafe-inline'\n"
                 "  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n", encoding="utf-8")
    ok, msg = checks.g9_headers(h)
    assert ok is False and "unsafe-inline" in msg
    ok, msg = checks.g9_headers(tmp_path / "missing")
    assert ok is False


def test_g2_and_g4_run_against_the_fixtures():
    assert checks.g2_negative_gate()[0] is True
    assert checks.g4_unknown_place()[0] is True
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_checks.py -q` — expected: `ModuleNotFoundError: No module named 'checks'`.

- [ ] **Step 3: Write `pipeline/checks.py`**

```python
"""checks.py - THE GATES. Run before every push. Exit 0 only when no gate FAILS.

  G1 source-valid            data/events.csv parses; every row validates; ids + slugs unique
  G2 negative-gate           fixture with published/draft/retired -> only the published id exported
  G3 export-current          a fresh export of the committed CSV == site/data (ignoring generated_at)
  G4 unknown-place           fixture row in a town places.csv lacks -> exit 1 naming "Nowhere, MO"
  G5 publication-committed   site/data/events.json is NOT gitignored
  G6 no-gate-in-js           site/js carries none of: visibility published draft retired
  G7 named-columns           every exported event has exactly EVENT_KEYS; no contact/email/phone key
  G8 stale (WARN)            published rows dated > STALE_DAYS in the past - counted, never fails
  G9 headers                 _headers: CSP present, no 'unsafe-inline', nosniff, Referrer-Policy

Each gate prints PASS/FAIL/WARN with extracted evidence, never a child's exit code alone.
ASCII only in this file.
"""
import io
import json
import re
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config                                                      # noqa: E402
import export                                                      # noqa: E402
from export import EVENT_KEYS                                      # noqa: E402
from geocode import load_places                                    # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
GATE_TOKENS = ("visibility", "published", "draft", "retired")
CONTACT_FRAGMENTS = ("contact", "email", "phone")


def _run_export(csv_path, out_dir, today=None):
    argv = ["--csv", str(csv_path), "--places", str(FIXTURES / "places.csv"), "--out", str(out_dir)]
    if today:
        argv += ["--today", today]
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = export.main(argv)
    return rc, buf.getvalue()


def g1_source_valid():
    rows = export.read_rows(config.EVENTS_CSV)
    pub = sum(1 for r in rows if export.is_published(r))
    return True, "%d row(s), %d published; ids and slugs unique" % (len(rows), pub)


def g2_negative_gate():
    with tempfile.TemporaryDirectory(prefix="ef-g2-") as d:
        rc, out = _run_export(FIXTURES / "negative.csv", d)
        if rc != 0:
            return False, "fixture export failed: " + out.strip()
        ids = [e["id"] for e in json.loads((Path(d) / "events.json").read_text(encoding="utf-8"))["events"]]
    want = ["11111111-1111-4111-8111-111111111111"]
    if ids != want:
        return False, "exported ids %s, expected only %s (draft/retired leaked)" % (ids, want)
    return True, "1 of 3 fixture rows exported: the published one only; draft and retired absent"


def g3_export_current():
    with tempfile.TemporaryDirectory(prefix="ef-g3-") as d:
        rows = export.read_rows(config.EVENTS_CSV)
        places = load_places(config.PLACES_CSV)
        committed_meta = json.loads((config.SITE_DATA / "meta.json").read_text(encoding="utf-8"))
        events_doc, meta, _ = export.build(rows, places, config.HOME, committed_meta.get("generated_at", ""),
                                           export.sha256_file(config.EVENTS_CSV), date.today())
        export.write_publication(d, events_doc, meta)
        fresh_events = (Path(d) / "events.json").read_bytes()
        fresh_meta = json.loads((Path(d) / "meta.json").read_text(encoding="utf-8"))
    committed_events = (config.SITE_DATA / "events.json").read_bytes()
    committed_meta.pop("generated_at", None)
    fresh_meta.pop("generated_at", None)
    if fresh_events != committed_events:
        return False, "site/data/events.json differs from a fresh export - run: python pipeline/export.py"
    if fresh_meta != committed_meta:
        return False, "site/data/meta.json differs from a fresh export - run: python pipeline/export.py"
    return True, "site/data matches a fresh export of data/events.csv (%d events)" % meta["event_count"]


def g4_unknown_place():
    with tempfile.TemporaryDirectory(prefix="ef-g4-") as d:
        rc, out = _run_export(FIXTURES / "unknown_place.csv", d)
        exists = (Path(d) / "events.json").exists()
    if rc != 1:
        return False, "expected exit 1 for an unknown place, got %d" % rc
    if "Nowhere, MO" not in out:
        return False, "exit 1 but the town was not named: " + out.strip()
    if exists:
        return False, "exit 1 but events.json was still written"
    return True, "unknown town fails the export by name and writes nothing"


def g5_publication_committed():
    rel = "site/data/events.json"
    proc = subprocess.run(["git", "check-ignore", "-q", rel], cwd=str(config.ROOT), capture_output=True)
    if proc.returncode == 0:
        return False, rel + " is gitignored - the publication would never be committed"
    return True, rel + " is not ignored"


def g6_no_gate_in_js(site_js_dir=None):
    site_js_dir = Path(site_js_dir or (config.SITE_DIR / "js"))
    if not site_js_dir.is_dir():
        return False, "no directory %s yet" % site_js_dir
    hits = []
    for p in sorted(site_js_dir.glob("*.js")):
        text = p.read_text(encoding="utf-8")
        for tok in GATE_TOKENS:
            if re.search(r"\b%s\b" % tok, text):
                hits.append("%s: %s" % (p.name, tok))
    if hits:
        return False, "publish-gate vocabulary in the page: " + "; ".join(hits)
    return True, "%d js file(s) carry none of %s" % (len(list(site_js_dir.glob("*.js"))), " ".join(GATE_TOKENS))


def g7_named_columns(events_path=None):
    events_path = Path(events_path or (config.SITE_DATA / "events.json"))
    doc = json.loads(events_path.read_text(encoding="utf-8"))
    want = set(EVENT_KEYS)
    for e in doc.get("events", []):
        keys = set(e.keys())
        bad = [k for k in keys if any(f in k.lower() for f in CONTACT_FRAGMENTS)]
        if bad:
            return False, "contact-shaped key(s) %s in event %s" % (bad, e.get("id"))
        if keys != want:
            return False, "event %s keys %s != contract %s" % (e.get("id"), sorted(keys), sorted(want))
    return True, "%d event(s), each with exactly the %d contract keys" % (len(doc.get("events", [])), len(want))


def g8_stale():
    rows = export.read_rows(config.EVENTS_CSV)
    places = load_places(config.PLACES_CSV)
    _, _, stale = export.build(rows, places, config.HOME, "", "", date.today())
    if stale:
        return None, "%d published row(s) dated > %d days ago: %s" % (
            len(stale), config.STALE_DAYS, ", ".join("%s (%s)" % s for s in stale))
    return True, "no published row dated more than %d days in the past" % config.STALE_DAYS


def g9_headers(headers_path=None):
    headers_path = Path(headers_path or (config.SITE_DIR / "_headers"))
    if not headers_path.exists():
        return False, "missing %s" % headers_path
    text = headers_path.read_text(encoding="utf-8")
    csp = re.search(r"Content-Security-Policy:\s*(.+)", text)
    if not csp:
        return False, "no Content-Security-Policy line"
    if "unsafe-inline" in csp.group(1):
        return False, "CSP contains 'unsafe-inline'"
    if not re.search(r"X-Content-Type-Options:\s*nosniff", text):
        return False, "missing X-Content-Type-Options: nosniff"
    if not re.search(r"Referrer-Policy:\s*\S+", text):
        return False, "missing Referrer-Policy"
    return True, "CSP without unsafe-inline; nosniff; Referrer-Policy present"


GATES = [
    ("G1 source-valid", g1_source_valid),
    ("G2 negative-gate", g2_negative_gate),
    ("G3 export-current", g3_export_current),
    ("G4 unknown-place", g4_unknown_place),
    ("G5 publication-committed", g5_publication_committed),
    ("G6 no-gate-in-js", g6_no_gate_in_js),
    ("G7 named-columns", g7_named_columns),
    ("G8 stale", g8_stale),
    ("G9 headers", g9_headers),
]


def main(argv=None):
    failed = 0
    for name, fn in GATES:
        try:
            ok, msg = fn()
        except Exception as e:                       # a crashed gate is a FAIL with a reason
            ok, msg = False, "%s: %s" % (type(e).__name__, e)
        label = "PASS" if ok else ("WARN" if ok is None else "FAIL")
        if ok is False:
            failed += 1
        print("%s  %-26s %s" % (label, name, msg))
    print("\n%s: %d gate(s) failed" % ("ALL GATES PASS" if failed == 0 else "GATES FAILED", failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_checks.py -q` — expected: 4 passed.

- [ ] **Step 5: Run the gates for real**

Run: `python pipeline/checks.py` — expected now: G1–G5, G7, G8 PASS; **G6 and G9 FAIL** (no `site/js`, no `_headers` yet) with messages naming the missing paths; exit 1. This is the expected state until Tasks 7–9 land; record it in the commit message.

- [ ] **Step 6: Commit**

```bash
grep -nP "[^\x00-\x7F]" pipeline/*.py tests/*.py   # expected: nothing
git add pipeline/checks.py tests/test_checks.py
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "pipeline: nine gates (G6/G9 red until the site exists)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: `serve_local.py` + `verify_deploy.py` (copied, attributed) + tests

**Files:**
- Create: `pipeline/serve_local.py`, `pipeline/verify_deploy.py`
- Test: `tests/test_verify_deploy.py`

**Interfaces:**
- Produces: `python pipeline/serve_local.py` serves `site/` at `http://127.0.0.1:8765/` with `application/json` for `.json` and every header from `site/_headers`; `verify_deploy.compare(local: bytes, remote: bytes | None) -> "DEPLOYED" | "STALE" | "MISSING"`; `verify_deploy.MARKERS`; CLI `python pipeline/verify_deploy.py [--origin URL] [--json]` exit 0 only when all DEPLOYED.

- [ ] **Step 1: Write the failing test**

`tests/test_verify_deploy.py`:
```python
import verify_deploy as vd


def test_compare_verdicts():
    assert vd.compare(b"a\nb", b"a\nb") == "DEPLOYED"
    assert vd.compare(b"a\nb", b"a\r\nb") == "DEPLOYED"          # line endings are not drift
    assert vd.compare(b"a\nb", None) == "MISSING"
    assert vd.compare(b"a\nb", b"a\nc") == "STALE"
    injected = b"<html><script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" data-cf-beacon='{}'></script>\n</html>"
    assert vd.compare(b"<html>
</html>", injected) == "DEPLOYED"  # edge-injected analytics tag is not drift


def test_markers_cover_the_publication_and_the_page():
    files = [m[0] for m in vd.MARKERS if m[1] is not None]
    assert "site/data/events.json" in files and "site/data/meta.json" in files
    assert "site/index.html" in files and "site/js/app.js" in files
    assert vd.ORIGIN == "https://eventfinds.pages.dev"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_verify_deploy.py -q` — expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write `pipeline/serve_local.py`**

```python
"""serve_local.py - view site/ locally with production parity.

Correct MIME for .json (Windows registry entries can poison mimetypes into text/plain and serve a
silently blank page), Cache-Control: no-store so a re-export shows on refresh, and EVERY header
from site/_headers on every response - so the CSP is enforced here, not only in production.
Shape follows the EqualShares build's serve_local.py (RapidForge Build 001). Stdlib only.
ASCII only in this file.
"""
import functools
import sys
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765
MIME = {
    ".json": "application/json; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".txt": "text/plain; charset=utf-8",
}


def log(msg=""):
    print("[%s] %s" % (datetime.now().strftime("%H:%M:%S"), msg))


def parse_site_headers(site_dir):
    """The /* block of site/_headers as [(name, value)] - one source of truth, no hand-kept copy."""
    headers = []
    hf = Path(site_dir) / "_headers"
    if not hf.exists():
        log("WARNING: site/_headers not found - serving WITHOUT the production security headers")
        return headers
    in_star = False
    for line in hf.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith((" ", "\t")):
            in_star = (stripped == "/*")
            continue
        if in_star and ":" in stripped:
            name, _, value = stripped.partition(":")
            headers.append((name.strip(), value.strip()))
    return headers


SECURITY_HEADERS = []


class SiteHandler(SimpleHTTPRequestHandler):
    def guess_type(self, path):
        ext = Path(str(path)).suffix.lower()
        return MIME.get(ext) or super().guess_type(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        for name, value in SECURITY_HEADERS:
            self.send_header(name, value)
        super().end_headers()

    def log_message(self, fmt, *args):
        log("%s %s" % (self.address_string(), fmt % args))


def main():
    site = config.SITE_DIR
    if not site.is_dir():
        log("ERROR: site directory not found: %s" % site)
        return 1
    if not (site / "data" / "meta.json").exists():
        log("note: site/data/meta.json is missing - the page will show its error box until export.py runs")
    SECURITY_HEADERS.extend(parse_site_headers(site))
    log("serving %d security header(s) from site/_headers on every response" % len(SECURITY_HEADERS))
    handler = functools.partial(SiteHandler, directory=str(site))
    try:
        httpd = ThreadingHTTPServer((HOST, PORT), handler)
    except OSError as e:
        log("ERROR: cannot bind %s:%d (%s) - is another serve_local.py running?" % (HOST, PORT, e))
        return 1
    log("serving %s" % site)
    log("open  http://%s:%d/   (Ctrl+C to stop)" % (HOST, PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log("stopped")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Write `pipeline/verify_deploy.py`** — copy of the reference instrument, adapted only in `ORIGIN`, `MARKERS`, `HEADER_MARKERS`, the User-Agent, and the failure hint. Keep `compare()` and `fetch()` byte-for-byte.

```python
#!/usr/bin/env python
"""verify_deploy.py - does the origin serve what git holds?

Copied 2026-08-30 from the RapidForge `verify-deploy` code candidate (reference implementation:
the Glizzness project's tools/verify_deploy.py, stdlib, 2026-08-29). EventFinds is its second
consumer. Only ORIGIN, MARKERS, HEADER_MARKERS, the User-Agent and the hint text differ.

WHY. "Auto-deploys on push" is a sentence with no check; a Pages integration can die silently and
every push then "succeeds" into git only. Run this after every push that touches site/.

  python pipeline/verify_deploy.py
  python pipeline/verify_deploy.py --origin https://eventfinds.pages.dev
  python pipeline/verify_deploy.py --json

Exit 0 only when every marker is DEPLOYED. STALE = origin serves different bytes; MISSING = 404.
Not in CI on purpose: a push is not yet a deploy, so CI would race it.
ASCII only in this file.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://eventfinds.pages.dev"
# Files whose bytes must match the origin exactly: the page, its scripts, its stylesheet, the
# vendored library, and THE PUBLICATION (both JSON files). The headers file is checked by effect.
MARKERS = [
    ("site/index.html", "/"),
    ("site/js/app.js", "/js/app.js"),
    ("site/js/predicates.js", "/js/predicates.js"),
    ("site/js/data.js", "/js/data.js"),
    ("site/css/app.css", "/css/app.css"),
    ("site/data/events.json", "/data/events.json"),
    ("site/data/meta.json", "/data/meta.json"),
    ("site/assets/vendor/leaflet/leaflet.js", "/assets/vendor/leaflet/leaflet.js"),
    ("site/_headers", None),          # not served as a file; its effect is HEADER_MARKERS
]
HEADER_MARKERS = ["content-security-policy", "x-content-type-options", "referrer-policy"]

# Cloudflare Web Analytics injects exactly this tag into HTML responses at the edge (a zone setting,
# not a file in git). It is the one difference between git and the origin that is not drift.
_CF_BEACON = re.compile(rb"<script[^>]*static\.cloudflareinsights\.com/beacon\.min\.js[^>]*></script>")


def compare(local, remote):
    """DEPLOYED when the origin's bytes equal git's, ignoring line endings, whitespace runs and the
    edge-injected analytics tag (which also leaves a stray newline behind). Any other byte is STALE."""
    if remote is None:
        return "MISSING"
    norm = lambda b: re.sub(rb"\s+", b" ", _CF_BEACON.sub(b"", b.replace(b"\r\n", b"\n"))).strip()
    return "DEPLOYED" if norm(local) == norm(remote) else "STALE"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "eventfinds-verify-deploy/1.0",
                                               "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read(), {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, None, {}
    except Exception as e:
        return 0, None, {"error": "%s: %s" % (type(e).__name__, e)}


def main():
    ap = argparse.ArgumentParser(description="compare local site/ files with what the origin serves")
    ap.add_argument("--origin", default=ORIGIN)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    origin = a.origin.rstrip("/")

    results = []
    for local_rel, path in MARKERS:
        if path is None:
            continue
        local = (ROOT / local_rel).read_bytes()
        status, body, _ = fetch(origin + path)
        verdict = compare(local, body if status == 200 else None)
        results.append({"file": local_rel, "url": origin + path, "http": status, "verdict": verdict})

    status, _, headers = fetch(origin + "/")
    for h in HEADER_MARKERS:
        present = h in headers
        results.append({"file": "site/_headers", "url": origin + "/", "http": status,
                        "verdict": "DEPLOYED" if present else "MISSING", "header": h})

    bad = [r for r in results if r["verdict"] != "DEPLOYED"]
    if a.json:
        print(json.dumps({"origin": origin, "results": results, "failed": len(bad)}, indent=2))
        return 1 if bad else 0

    print("\nDeploy check - local site/ vs %s\n" % origin)
    for r in results:
        label = r.get("header", r["file"])
        mark = "PASS" if r["verdict"] == "DEPLOYED" else "FAIL"
        print("  %s  %-44s %-9s HTTP %s" % (mark, label, r["verdict"], r["http"]))
    if bad:
        print("\n  %d marker(s) not deployed. The origin is NOT serving the pushed site/ - check" % len(bad))
        print("  Cloudflare Dashboard -> Workers & Pages -> eventfinds -> Deployments (failed build? integration gone?).\n")
        return 1
    print("\n  ALL DEPLOYED - the origin serves exactly what git holds.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_verify_deploy.py -q` — expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
grep -nP "[^\x00-\x7F]" pipeline/*.py tests/*.py   # expected: nothing
git add pipeline/serve_local.py pipeline/verify_deploy.py tests/test_verify_deploy.py
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "pipeline: serve_local with header parity; verify_deploy (second consumer of the reference instrument)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: `site/js/predicates.js` (pure functions) + node tests

**Files:**
- Create: `site/js/predicates.js`
- Test: `tests/js/predicates.test.mjs`

**Interfaces:**
- Produces (ES module exports): `isUpcoming(e, todayISO, nowMonth) -> boolean`; `haversineMiles(lat1, lng1, lat2, lng2) -> number`; `passesFilter(e, filt, todayISO, nowMonth) -> boolean` where `filt = { month: "all"|"1".."12", distance: "all"|"50"|..., county: "all"|"<county>|<ST>", types: Set|null }` and `e.distance_mi` is a number or `undefined` (set by the page at load); `esc(s) -> string`; `distinctSorted(events, key) -> string[]`; `countyKey(e) -> string | null` (`"Boone|MO"`); `firstMonth(e) -> number` (99 when none). **This file must not contain the tokens `visibility`, `published`, `draft`, `retired`** (G6).

- [ ] **Step 1: Write the failing tests**

`tests/js/predicates.test.mjs`:
```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { isUpcoming, haversineMiles, passesFilter, esc, distinctSorted, countyKey, firstMonth }
  from "../../site/js/predicates.js";

const T = "2026-08-30", M = 8;
const ev = (o) => ({ cadence: "annual", start_date: null, end_date: null, months: [], ...o });

test("7.5 dated fixtures: dates win, for annual and one_time alike", () => {
  assert.equal(isUpcoming(ev({ start_date: "2026-08-29", end_date: "2026-08-29" }), T, M), false); // ended yesterday
  assert.equal(isUpcoming(ev({ start_date: "2026-08-30" }), T, M), true);                          // today
  assert.equal(isUpcoming(ev({ cadence: "one_time", start_date: "2026-08-30" }), T, M), true);
  assert.equal(isUpcoming(ev({ cadence: "one_time", start_date: "2026-08-29" }), T, M), false);
  assert.equal(isUpcoming(ev({ start_date: "2026-08-02", end_date: "2026-08-03", months: [8] }), T, M), false); // trap 6.3: month alone would say upcoming
});

test("month fallback only when no date exists; recurring always", () => {
  assert.equal(isUpcoming(ev({ months: [9] }), T, M), true);
  assert.equal(isUpcoming(ev({ months: [7] }), T, M), false);
  assert.equal(isUpcoming(ev({ months: [6, 8] }), T, M), true);
  assert.equal(isUpcoming(ev({}), T, M), true);
  assert.equal(isUpcoming(ev({ cadence: "recurring", months: [1] }), T, M), true);
});

test("haversine: Columbia to Kansas City is about 125 miles", () => {
  const d = haversineMiles(38.9517, -92.3341, 39.0997, -94.5786);
  assert.ok(d > 118 && d < 132, String(d));
  assert.equal(haversineMiles(38.9517, -92.3341, 38.9517, -92.3341), 0);
});

test("passesFilter: one object, one predicate", () => {
  const base = ev({ event_type: "festival", county: "Boone", state: "MO", months: [9], distance_mi: 0 });
  const all = { month: "all", distance: "all", county: "all", types: null };
  assert.equal(passesFilter(base, all, T, M), true);
  assert.equal(passesFilter(base, { ...all, types: new Set(["rodeo"]) }, T, M), false);
  assert.equal(passesFilter(base, { ...all, types: new Set(["festival"]) }, T, M), true);
  assert.equal(passesFilter(base, { ...all, month: "9" }, T, M), true);
  assert.equal(passesFilter(base, { ...all, month: "10" }, T, M), false);
  assert.equal(passesFilter(ev({ ...base, months: [] }), { ...all, month: "10" }, T, M), true); // no months = any month
  assert.equal(passesFilter(base, { ...all, county: "Boone|MO" }, T, M), true);
  assert.equal(passesFilter(base, { ...all, county: "Boone|IA" }, T, M), false);
  assert.equal(passesFilter({ ...base, distance_mi: 0 }, { ...all, distance: "50" }, T, M), true);   // trap 6.2: zero is a distance
  assert.equal(passesFilter({ ...base, distance_mi: 80 }, { ...all, distance: "50" }, T, M), false);
  assert.equal(passesFilter({ ...base, distance_mi: undefined }, { ...all, distance: "50" }, T, M), false); // unknown hidden under a cap
  assert.equal(passesFilter(ev({ ...base, months: [7] }), all, T, M), false); // passed events are absent
});

test("esc escapes the five characters", () => {
  assert.equal(esc(`<a href="x">&'</a>`), "&lt;a href=&quot;x&quot;&gt;&amp;&#39;&lt;/a&gt;");
  assert.equal(esc(null), "");
  assert.equal(esc(0), "0");
});

test("distinctSorted, countyKey, firstMonth", () => {
  const es = [ev({ event_type: "rodeo" }), ev({ event_type: "festival" }), ev({ event_type: "rodeo" }), ev({ event_type: null })];
  assert.deepEqual(distinctSorted(es, "event_type"), ["festival", "rodeo"]);
  assert.equal(countyKey({ county: "Boone", state: "MO" }), "Boone|MO");
  assert.equal(countyKey({ county: null, state: "MO" }), null);
  assert.equal(firstMonth(ev({ months: [11, 3] })), 3);
  assert.equal(firstMonth(ev({})), 99);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `node --test tests/js` — expected: failure `Cannot find module ... site/js/predicates.js`.

- [ ] **Step 3: Write `site/js/predicates.js`**

```js
// predicates.js - pure functions, no DOM, no Leaflet. Tested with node --test.
// "Upcoming" is computed from the browser date, from real dates where they exist;
// months are the fallback, never the override. Passed events are absent, not dimmed.

export function isUpcoming(e, todayISO, nowMonth) {
  if (e.cadence === "recurring") return true;
  const last = e.end_date || e.start_date;
  if (last) return last >= todayISO;
  const ms = Array.isArray(e.months) ? e.months : [];
  if (ms.length) return Math.max(...ms) >= nowMonth;
  return true;
}

export function haversineMiles(lat1, lng1, lat2, lng2) {
  const R = 3958.7613, rad = (d) => (d * Math.PI) / 180;
  const dLat = rad(lat2 - lat1), dLng = rad(lng2 - lng1);
  const a = Math.sin(dLat / 2) ** 2
    + Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

export function countyKey(e) {
  return e.county ? e.county + "|" + (e.state || "") : null;
}

export function firstMonth(e) {
  const ms = Array.isArray(e.months) ? e.months : [];
  return ms.length ? Math.min(...ms) : 99;
}

// filt = { month: "all"|"1".."12", distance: "all"|"50"|"100"|"150"|"250",
//          county: "all"|"<county>|<ST>", types: Set|null }
export function passesFilter(e, filt, todayISO, nowMonth) {
  if (e.lat == null || e.lng == null) return false;
  if (!isUpcoming(e, todayISO, nowMonth)) return false;
  if (filt.types && !filt.types.has(e.event_type)) return false;
  if (filt.distance !== "all") {
    const d = e.distance_mi;
    if (typeof d !== "number" || !Number.isFinite(d) || d > Number(filt.distance)) return false;
  }
  if (filt.county !== "all" && countyKey(e) !== filt.county) return false;
  if (filt.month !== "all") {
    const ms = Array.isArray(e.months) ? e.months : [];
    if (ms.length && !ms.includes(Number(filt.month))) return false;
  }
  return true;
}

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ESC[c]);
}

export function distinctSorted(events, key) {
  return [...new Set(events.map((e) => e[key]).filter((v) => v != null && v !== ""))].sort();
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `node --test tests/js` — expected: 6 tests pass.
Run: `python pipeline/checks.py` — expected: G6 now PASS (`1 js file(s) carry none of ...`); G9 still FAIL.

- [ ] **Step 5: Commit**

```bash
git add site/js/predicates.js tests/js/predicates.test.mjs
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "site: pure predicates (upcoming from dates, distance, one filter) with node tests

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: `site/js/data.js` (typed fetch; never resolves to emptiness)

**Files:**
- Create: `site/js/data.js`
- Test: `tests/js/data.test.mjs`

**Interfaces:**
- Produces: `class FetchError extends Error { path, status, detail }`; `class DataShapeError extends Error`; `fetchJson(path, fetchImpl = globalThis.fetch) -> Promise<any>` (throws `FetchError` on network error, non-2xx, or invalid JSON; `cache: "no-cache"`); `assertShape(meta, eventsDoc)` throws `DataShapeError` unless `eventsDoc.events` is an array and `meta.home.lat/lng` are finite numbers and `meta.event_count` is a number.

- [ ] **Step 1: Write the failing tests**

`tests/js/data.test.mjs`:
```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { fetchJson, FetchError, DataShapeError, assertShape } from "../../site/js/data.js";

const resp = (ok, status, body) => ({ ok, status, statusText: "S", json: async () => JSON.parse(body) });

test("fetchJson returns parsed JSON and passes no-cache", async () => {
  let seen;
  const f = async (p, o) => { seen = o; return resp(true, 200, '{"a":1}'); };
  assert.deepEqual(await fetchJson("/data/meta.json", f), { a: 1 });
  assert.equal(seen.cache, "no-cache");
});

test("fetchJson throws FetchError naming the path on HTTP error, bad JSON, network error", async () => {
  await assert.rejects(fetchJson("/data/x.json", async () => resp(false, 404, "")),
    (e) => e instanceof FetchError && e.path === "/data/x.json" && e.status === 404 && /404/.test(e.detail));
  await assert.rejects(fetchJson("/data/y.json", async () => resp(true, 200, "not json")),
    (e) => e instanceof FetchError && /JSON/.test(e.detail));
  await assert.rejects(fetchJson("/data/z.json", async () => { throw new Error("offline"); }),
    (e) => e instanceof FetchError && e.status === null && /offline/.test(e.detail));
});

test("assertShape rejects the wrong shape", () => {
  const meta = { event_count: 0, home: { name: "Columbia, MO", lat: 38.9, lng: -92.3 } };
  assertShape(meta, { events: [] });
  assert.throws(() => assertShape(meta, { events: "nope" }), DataShapeError);
  assert.throws(() => assertShape({ event_count: 0, home: {} }, { events: [] }), DataShapeError);
  assert.throws(() => assertShape({ home: meta.home }, { events: [] }), DataShapeError);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `node --test tests/js` — expected: `Cannot find module ... data.js`.

- [ ] **Step 3: Write `site/js/data.js`**

```js
// data.js - the fetch layer. One property is load-bearing: a failed fetch THROWS a typed error and
// never resolves to anything a caller could mistake for an empty result (static-publication-site
// trap 6.1). Same-origin static JSON only; there is no key and no config to blank.

export class FetchError extends Error {
  constructor(path, status, detail) {
    super("fetch of " + path + " failed: " + detail);
    this.name = "FetchError";
    this.path = path;      // named in the error box
    this.status = status;  // HTTP status, or null when the request never completed
    this.detail = detail;
  }
}

export class DataShapeError extends Error {
  constructor(message) { super(message); this.name = "DataShapeError"; }
}

export async function fetchJson(path, fetchImpl = globalThis.fetch) {
  let resp;
  try {
    resp = await fetchImpl(path, { cache: "no-cache" });
  } catch (err) {
    throw new FetchError(path, null, "network error (" + (err && err.message ? err.message : String(err)) + ")");
  }
  if (!resp.ok) {
    throw new FetchError(path, resp.status, "HTTP " + resp.status + (resp.statusText ? " " + resp.statusText : ""));
  }
  try {
    return await resp.json();
  } catch (err) {
    throw new FetchError(path, resp.status, "response is not valid JSON (" + (err && err.message ? err.message : String(err)) + ")");
  }
}

export function assertShape(meta, eventsDoc) {
  if (!eventsDoc || !Array.isArray(eventsDoc.events)) {
    throw new DataShapeError("data/events.json does not carry an events array");
  }
  const h = meta && meta.home;
  if (!h || !Number.isFinite(h.lat) || !Number.isFinite(h.lng)) {
    throw new DataShapeError("data/meta.json has no numeric home.lat / home.lng");
  }
  if (typeof meta.event_count !== "number") {
    throw new DataShapeError("data/meta.json has no numeric event_count");
  }
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `node --test tests/js` — expected: 9 tests pass. Run: `python pipeline/checks.py` — G6 still PASS.

- [ ] **Step 5: Commit**

```bash
git add site/js/data.js tests/js/data.test.mjs
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "site: typed fetch layer; a failed load can never look empty

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 9: Shell — `site/index.html`, `site/css/app.css`, `site/_headers`, vendored Leaflet

**Files:**
- Create: `site/index.html`, `site/css/app.css`, `site/_headers`, `site/assets/vendor/leaflet/*` (copied)
- Test: gate G9 (`python pipeline/checks.py`), plus `grep` checks below

**Interfaces:**
- Produces the element ids `app.js` (Task 10) wires: `#fresh`, `#error-box`, `#status`, `#crumb`, `#list-toggle`, `#f-month`, `#f-distance`, `#f-county`, `#ms-type`, `#ms-btn`, `#ms-panel`, `#ms-all`, `#ms-none`, `#ms-list`, `#f-reset`, `#map`, `#listpanel`, `#lp-count`, `#list-body`, `.lp-close`, `#drawer`, `#drawer-body`, `#drawer .close`. CSS classes: `.evt-dot span` (the dot — colour in CSS, not inline), `.lp-row`, `.lp-dot`, `.lp-onetime`, `.lp-empty`, `.badge .b-grey .b-blue .b-gold`, `.home`, `.error-box`.

- [ ] **Step 1: Vendor the libraries (third-party; MIT/BSD-2)**

```bash
mkdir -p site/assets/vendor/leaflet
SRC="/c/Users/lance/OneDrive/Desktop/MidMoConsultant/James Jason Trinton Johnson/Glizzness/site/assets/vendor/leaflet"
cp "$SRC/leaflet.js" "$SRC/leaflet.css" "$SRC/leaflet.markercluster.js" "$SRC/MarkerCluster.css" "$SRC/MarkerCluster.Default.css" site/assets/vendor/leaflet/
cp -r "$SRC/images" site/assets/vendor/leaflet/images
head -c 120 site/assets/vendor/leaflet/leaflet.js      # expect "Leaflet 1.9.4"
```
Add `site/assets/vendor/leaflet/README.txt`:
```
Leaflet 1.9.4 (BSD-2-Clause, https://leafletjs.com) and Leaflet.markercluster (MIT,
https://github.com/Leaflet/Leaflet.markercluster), vendored so the map never depends on a CDN
being up. Third-party code; upgrade by replacing these files.
```

- [ ] **Step 2: Write `site/_headers`**

```
# Cloudflare Pages response headers. The CSP is an ENUMERATION of what the page loads:
#   self                                   index.html, css/app.css, js/*.js (ES modules), data/*.json, vendored Leaflet
#   https://tile.openstreetmap.org and https://*.tile.openstreetmap.org   map tiles (img-src)
#   data:                                  Leaflet's inline marker/cluster images
# No 'unsafe-inline' anywhere: there is no inline <style> or <script> in this site (gate G9).
/*
  Content-Security-Policy: default-src 'self'; img-src 'self' data: https://tile.openstreetmap.org https://*.tile.openstreetmap.org; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; object-src 'none'; form-action 'self'; frame-ancestors 'none'
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer
  Permissions-Policy: camera=(), microphone=(), geolocation=()
```

- [ ] **Step 3: Write `site/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>EventFinds</title>
  <meta name="description" content="EventFinds: a curated, filterable map and list of upcoming events. Filter by month, distance, county and event type." />
  <link rel="stylesheet" href="/assets/vendor/leaflet/leaflet.css" />
  <link rel="stylesheet" href="/assets/vendor/leaflet/MarkerCluster.css" />
  <link rel="stylesheet" href="/assets/vendor/leaflet/MarkerCluster.Default.css" />
  <link rel="stylesheet" href="/css/app.css" />
</head>
<body>
  <div id="app">
    <header>
      <h1>EventFinds</h1>
      <span id="fresh" class="fresh" aria-live="polite"></span>
      <button id="list-toggle" type="button" aria-label="List view">List</button>
      <span id="crumb"></span>
    </header>
    <div id="filterbar">
      <span class="fb-label">Filter</span>
      <select id="f-month" aria-label="Month"><option value="all">Any month</option></select>
      <select id="f-distance" aria-label="Distance from home">
        <option value="all">Any distance</option>
        <option value="50">Within 50 mi</option>
        <option value="100">Within 100 mi</option>
        <option value="150">Within 150 mi</option>
        <option value="250">Within 250 mi</option>
      </select>
      <select id="f-county" aria-label="County"><option value="all">Any county</option></select>
      <div class="ms" id="ms-type">
        <button type="button" class="ms-btn" id="ms-btn" aria-expanded="false">All types</button>
        <div class="ms-panel" id="ms-panel" hidden>
          <div class="ms-actions"><button type="button" id="ms-all">All</button><button type="button" id="ms-none">None</button></div>
          <div id="ms-list"></div>
        </div>
      </div>
      <button id="f-reset" type="button">Reset</button>
    </div>
    <div id="main">
      <noscript><div class="error-box"><strong>This page requires JavaScript.</strong><p>EventFinds renders its map from static JSON in your browser; nothing renders without it, by design.</p></div></noscript>
      <div id="error-box" class="error-box" role="alert" hidden></div>
      <div id="map"></div>
      <div id="status" hidden></div>
      <div class="legend"><span>Zoom in to scatter, out to group. Pins show the city, not the venue.</span></div>
      <aside id="listpanel">
        <div class="lp-head">Events in view <span id="lp-count"></span>
          <button class="lp-close" type="button" aria-label="Close">&times;</button></div>
        <div id="list-body"></div>
      </aside>
      <aside id="drawer">
        <button class="close" type="button" aria-label="Close">&times;</button>
        <div id="drawer-body"></div>
      </aside>
    </div>
  </div>
  <script src="/assets/vendor/leaflet/leaflet.js"></script>
  <script src="/assets/vendor/leaflet/leaflet.markercluster.js"></script>
  <script type="module" src="/js/app.js"></script>
</body>
</html>
```

- [ ] **Step 4: Write `site/css/app.css`**

```css
:root { --bg:#12151a; --panel:#1b2028; --ink:#eef2f6; --muted:#a9b3bf; --accent:#3fb4a0; --blue:#5aa7e0; --gold:#e0b14a; --red:#d0594f; --line:#0a0c10; }
* { box-sizing: border-box; }
html, body { height: 100%; margin: 0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: var(--ink); background: var(--bg); }
#app { display: flex; flex-direction: column; height: 100%; }
header { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: var(--panel); border-bottom: 1px solid var(--line); z-index: 1000; }
header h1 { font-size: 17px; margin: 0; font-weight: 700; letter-spacing: .3px; }
.fresh { color: var(--muted); font-size: 12px; }
#crumb { color: var(--muted); font-size: 13px; margin-left: auto; }
#filterbar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 8px 14px; background: #161a21; border-bottom: 1px solid var(--line); z-index: 1000; }
#filterbar .fb-label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .4px; }
#filterbar select, #filterbar button { background: #242a34; color: var(--ink); border: 1px solid #343c48; border-radius: 6px; padding: 6px 8px; font-size: 13px; font-family: inherit; cursor: pointer; }
#filterbar #f-reset { margin-left: auto; }
#main { flex: 1; position: relative; }
#map { position: absolute; inset: 0; }
.error-box { position: absolute; top: 14px; left: 50%; transform: translateX(-50%); max-width: min(560px, 92vw); background: #3a1d1b; border: 1px solid var(--red); color: var(--ink); border-radius: 8px; padding: 12px 16px; z-index: 1400; font-size: 14px; }
.error-box[hidden] { display: none; }
.error-box p { margin: 6px 0 0; color: var(--muted); }
#status { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 8px 14px; font-size: 13px; z-index: 1100; }
#status[hidden] { display: none; }
.legend { position: absolute; bottom: 14px; left: 14px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 8px 12px; font-size: 11px; color: var(--muted); z-index: 1000; max-width: 62vw; }
.evt-dot span { display: block; width: 14px; height: 14px; border-radius: 50%; background: var(--accent); border: 1px solid var(--line); box-shadow: 0 0 0 1px rgba(0,0,0,.25); }
#list-toggle { cursor: pointer; background: #242a34; color: var(--ink); border: 1px solid #343c48; border-radius: 6px; padding: 6px 10px; font-weight: 600; font-size: 13px; }
#list-toggle.active { background: var(--accent); color: #06211c; border-color: var(--accent); }
#listpanel { position: absolute; top: 0; left: 0; width: min(330px, 85vw); height: 100%; background: var(--panel); border-right: 1px solid var(--line); transform: translateX(-105%); transition: transform .22s ease; z-index: 1150; overflow-y: auto; }
#listpanel.open { transform: translateX(0); }
.lp-head { position: sticky; top: 0; background: var(--panel); padding: 11px 14px; border-bottom: 1px solid var(--line); font-weight: 700; font-size: 14px; display: flex; align-items: center; gap: 8px; }
#lp-count { color: var(--muted); font-weight: 400; font-size: 12px; margin-left: auto; }
.lp-close, #drawer .close { cursor: pointer; color: var(--muted); background: none; border: none; font-size: 20px; line-height: 1; }
.lp-row { display: block; width: 100%; text-align: left; background: none; border: none; font-family: inherit; border-bottom: 1px solid #242a34; padding: 9px 14px; cursor: pointer; color: var(--ink); }
.lp-row:hover { background: #242a34; }
.lp-row .nm { font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 7px; }
.lp-row .sub { color: var(--muted); font-size: 11px; margin: 2px 0 0 18px; }
.lp-dot { width: 11px; height: 11px; border-radius: 50%; background: var(--accent); border: 1px solid var(--line); flex: none; }
.lp-onetime { color: var(--blue); font-weight: 600; }
.lp-empty { padding: 16px 14px; color: var(--muted); font-size: 13px; }
#drawer { position: absolute; top: 0; right: 0; width: min(380px, 90vw); height: 100%; background: var(--panel); border-left: 1px solid var(--line); transform: translateX(105%); transition: transform .22s ease; z-index: 1200; overflow-y: auto; padding: 18px; }
#drawer.open { transform: translateX(0); }
#drawer .close { float: right; font-size: 22px; }
#drawer h2 { margin: 0 28px 4px 0; font-size: 18px; }
#drawer .loc { color: var(--muted); font-size: 13px; margin-bottom: 12px; }
.badge { display: inline-block; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 999px; margin: 0 6px 6px 0; }
.b-grey { background: #343c48; color: var(--muted); }
.b-blue { background: var(--blue); color: #04223a; }
.b-gold { background: var(--gold); color: #2a1e02; }
#drawer dl { margin: 14px 0 0; font-size: 14px; }
#drawer dt { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .4px; margin-top: 12px; }
#drawer dd { margin: 2px 0 0; white-space: pre-line; }
#drawer a { color: var(--accent); }
#drawer .home { display: inline-block; margin-top: 16px; background: var(--accent); color: #06211c; text-decoration: none; font-weight: 700; padding: 9px 14px; border-radius: 7px; }
#drawer .src { display: block; margin-top: 10px; font-size: 12px; color: var(--muted); }
.ms { position: relative; }
.ms-btn[aria-expanded="true"] { border-color: var(--accent); }
.ms-panel { position: absolute; top: calc(100% + 4px); left: 0; z-index: 1300; background: var(--panel); border: 1px solid #343c48; border-radius: 8px; padding: 8px; min-width: 210px; max-height: 320px; overflow-y: auto; box-shadow: 0 8px 26px rgba(0,0,0,.55); }
.ms-panel[hidden] { display: none; }
.ms-actions { display: flex; gap: 8px; margin: 0 0 6px; }
.ms-actions button { flex: 1; }
#ms-list label { display: flex; align-items: center; gap: 7px; padding: 4px; font-size: 13px; color: var(--ink); white-space: nowrap; cursor: pointer; border-radius: 4px; }
#ms-list label:hover { background: #242a34; }
@media (max-width: 560px) {
  header { padding: 8px 10px; gap: 8px; }
  header h1 { font-size: 14px; }
  .fresh, #crumb { font-size: 11px; }
  #drawer, #listpanel { width: 100%; }
  #filterbar { gap: 6px; padding: 6px 10px; }
  #filterbar .fb-label { display: none; }
  #filterbar select, #filterbar button { padding: 5px 6px; font-size: 12px; }
  #filterbar #f-reset { margin-left: 0; }
}
```

- [ ] **Step 5: Verify the constraints and the gate**

```bash
grep -n -i -E "glizzness|midwest event finder" -r site pipeline tests data   # expected: no output
grep -n -E "<style|<script>|onclick=|style=\"" site/index.html                 # expected: no output (no inline)
grep -n "<base" site/index.html                                                # expected: no output
python pipeline/checks.py                                                       # expected: ALL GATES PASS (G8 may WARN)
```

- [ ] **Step 6: Commit**

```bash
git add site/index.html site/css/app.css site/_headers site/assets/vendor/leaflet
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "site: shell, stylesheet, CSP without unsafe-inline, vendored Leaflet 1.9.4 + markercluster

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 10: `site/js/app.js` (Leaflet + DOM wiring)

**Files:**
- Create: `site/js/app.js`
- Test: manual in the browser (Task 11 verifies with Playwright); gates G6/G7 (`python pipeline/checks.py`)

**Interfaces:**
- Consumes: `predicates.js` and `data.js` exports (Tasks 7–8); element ids from Task 9; `window.L` (vendored Leaflet, loaded before this module).
- Produces: the page. Boot order: fetch `/data/meta.json` then `/data/events.json` → `assertShape` → set `distance_mi` on every event (haversine from `meta.home`) → freshness line → `wireFilters()` → `render(true)`. Any throw → `renderFatal(err)` shows `#error-box` with the file name; the map is not rendered.

- [ ] **Step 1: Write `site/js/app.js`**

```js
// app.js - Leaflet + DOM wiring for EventFinds. All decisions live in predicates.js; this file
// only moves data to the screen. No copy of the exporter's gate exists here (gate G6).
import { haversineMiles, passesFilter, esc, distinctSorted, countyKey, firstMonth } from "./predicates.js";
import { fetchJson, FetchError, DataShapeError, assertShape } from "./data.js";

const $ = (id) => document.getElementById(id);
const errorBox = $("error-box"), statusEl = $("status"), crumbEl = $("crumb"), freshEl = $("fresh");
const drawer = $("drawer"), drawerBody = $("drawer-body");
const listPanel = $("listpanel"), listBody = $("list-body"), lpCount = $("lp-count");

const NOW = new Date();
const pad2 = (n) => String(n).padStart(2, "0");
const TODAY_ISO = `${NOW.getFullYear()}-${pad2(NOW.getMonth() + 1)}-${pad2(NOW.getDate())}`;
const NOW_M = NOW.getMonth() + 1;
const MONTH_NAMES = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

let META = null, EVENTS = [], eventsById = {}, listOpen = false;
const FILT = { month: "all", distance: "all", county: "all", types: null };

// ---------- error rendering: loud, named, never an empty map ----------
function describeError(err) {
  if (err instanceof FetchError) return "Failed to load " + err.path + " \u2014 " + err.detail + ". Nothing on this page is rendered from a failed fetch.";
  if (err instanceof DataShapeError) return err.message;
  return err && err.message ? err.message : String(err);
}
function renderFatal(err) {
  errorBox.replaceChildren();
  const strong = document.createElement("strong");
  strong.textContent = "This page could not load its data.";
  const p = document.createElement("p");
  p.textContent = describeError(err);
  errorBox.append(strong, p);
  errorBox.hidden = false;
  statusEl.hidden = true;
  console.error(err);
}
function setStatus(msg) { statusEl.textContent = msg; statusEl.hidden = !msg; }

// ---------- map ----------
const L = window.L;
const map = L.map("map", { zoomControl: true }).setView([38.9517, -92.3341], 7);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19, attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);
const clusterGroup = L.markerClusterGroup({
  maxClusterRadius: 55, showCoverageOnHover: false, spiderfyOnMaxZoom: true,
  zoomToBoundsOnClick: false, chunkedLoading: true,
}).addTo(map);
clusterGroup.on("clusterclick", (a) => {
  if (a.layer.getChildCount() <= 5) a.layer.spiderfy();
  else a.layer.zoomToBounds({ padding: [40, 40] });
});
const dotIcon = L.divIcon({ className: "evt-dot", iconSize: [16, 16], iconAnchor: [8, 8], html: "<span></span>" });

const visibleEvents = () => EVENTS.filter((e) => passesFilter(e, FILT, TODAY_ISO, NOW_M));

function render(fit) {
  clusterGroup.clearLayers();
  const vis = visibleEvents();
  const markers = [], pts = [];
  for (const e of vis) {
    const mk = L.marker([e.lat, e.lng], { icon: dotIcon }).bindTooltip(esc(e.name), { direction: "top" });
    mk.on("click", () => openDrawer(e));
    markers.push(mk);
    pts.push([e.lat, e.lng]);
  }
  clusterGroup.addLayers(markers);
  crumbEl.textContent = `${vis.length} event${vis.length === 1 ? "" : "s"}`;
  if (fit && pts.length) map.fitBounds(pts, { padding: [40, 40], maxZoom: 12 });
  renderList();
}
const applyFilters = () => render(true);

// ---------- list panel: events in the current viewport ----------
function whenText(e) {
  if (e.dates_text) return e.dates_text;
  if (e.start_date) return e.end_date && e.end_date !== e.start_date ? e.start_date + " to " + e.end_date : e.start_date;
  const ms = Array.isArray(e.months) ? e.months : [];
  return ms.length ? ms.map((m) => MONTH_NAMES[m]).join("/") : "";
}
function renderList() {
  if (!listOpen) return;
  const b = map.getBounds();
  const vis = visibleEvents().filter((e) => b.contains([e.lat, e.lng]));
  vis.sort((x, y) => firstMonth(x) - firstMonth(y) || x.name.localeCompare(y.name));
  lpCount.textContent = `${vis.length} in view`;
  listBody.innerHTML = vis.length
    ? vis.map((e) => {
        const when = whenText(e);
        const one = e.cadence === "one_time" ? ` \u00b7 <span class="lp-onetime">one-time</span>` : "";
        return `<button type="button" class="lp-row" data-id="${esc(e.id)}">
          <div class="nm"><span class="lp-dot"></span>${esc(e.name)}</div>
          <div class="sub">${esc(e.city)}, ${esc(e.state)}${when ? " \u00b7 " + esc(when) : ""}${one}</div>
        </button>`;
      }).join("")
    : `<div class="lp-empty">No events in this view. Pan or zoom out to see more.</div>`;
}
function toggleList(open) {
  listOpen = open === undefined ? !listOpen : open;
  listPanel.classList.toggle("open", listOpen);
  $("list-toggle").classList.toggle("active", listOpen);
  renderList();
}

// ---------- detail drawer ----------
const badge = (text, cls) => `<span class="badge ${cls}">${esc(text)}</span>`;
function openDrawer(e) {
  const badges = [badge((e.event_type || "").replace(/_/g, " "), "b-grey")];
  if (e.cadence === "one_time") badges.push(badge("One-time event", "b-blue"));
  if (e.featured === true) badges.push(badge("Featured", "b-gold"));
  const rows = [];
  const add = (label, val) => { if (val != null && val !== "") rows.push(`<dt>${esc(label)}</dt><dd>${esc(val)}</dd>`); };
  add("When", whenText(e));
  add("Size / attendance", e.attendance_text);
  add("Distance from " + META.home.name, typeof e.distance_mi === "number" ? Math.round(e.distance_mi) + " mi" : null);
  add("About", e.description);
  add("Last verified", e.last_verified);
  let home = "";
  if (e.homepage_url) {
    const url = /^https?:\/\//.test(e.homepage_url) ? e.homepage_url : "https://" + e.homepage_url;
    home = `<a class="home" href="${esc(url)}" target="_blank" rel="noopener">Event page</a>`;
  }
  const src = e.source_url ? `<a class="src" href="${esc(e.source_url)}" target="_blank" rel="noopener">Source</a>` : "";
  const countyTxt = e.county ? " \u00b7 " + esc(e.county) + (/county$/i.test(e.county) ? "" : " County") : "";
  drawerBody.innerHTML = `
    <h2>${esc(e.name)}</h2>
    <div class="loc">${esc(e.city)}, ${esc(e.state)}${countyTxt}</div>
    <div>${badges.join("")}</div>
    <dl>${rows.join("")}</dl>
    ${home}${src}`;
  drawer.classList.add("open");
}
document.querySelector("#drawer .close").addEventListener("click", () => drawer.classList.remove("open"));
listBody.addEventListener("click", (ev) => {
  const r = ev.target.closest(".lp-row");
  if (!r) return;
  const e = eventsById[r.dataset.id];
  if (!e) return;
  map.setView([e.lat, e.lng], Math.max(map.getZoom(), 13));
  openDrawer(e);
});
$("list-toggle").addEventListener("click", () => toggleList());
document.querySelector("#listpanel .lp-close").addEventListener("click", () => toggleList(false));
map.on("moveend", renderList);

// ---------- filters, built from the data ----------
function wireFilters() {
  const monthSel = $("f-month");
  for (let i = 1; i <= 12; i++) {
    const o = document.createElement("option");
    o.value = String(i); o.textContent = MONTH_NAMES[i];
    monthSel.appendChild(o);
  }
  const countySel = $("f-county");
  const keys = [...new Set(EVENTS.map(countyKey).filter(Boolean))].sort((a, b) => {
    const [ca, sa] = a.split("|"), [cb, sb] = b.split("|");
    return sa === sb ? ca.localeCompare(cb) : sa.localeCompare(sb);
  });
  for (const key of keys) {
    const [cty, st] = key.split("|");
    const o = document.createElement("option");
    o.value = key; o.textContent = `${cty} (${st})`;
    countySel.appendChild(o);
  }
  const pretty = (t) => t.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  const ALL_TYPES = distinctSorted(EVENTS, "event_type");
  FILT.types = new Set(ALL_TYPES);
  const msBtn = $("ms-btn"), msPanel = $("ms-panel"), msList = $("ms-list");
  const msLabel = () => {
    msBtn.textContent = FILT.types.size === ALL_TYPES.length ? "All types"
      : FILT.types.size === 0 ? "No types" : `${FILT.types.size}/${ALL_TYPES.length} types`;
  };
  for (const t of ALL_TYPES) {
    const lab = document.createElement("label");
    const cb = document.createElement("input");
    cb.type = "checkbox"; cb.checked = true;
    cb.addEventListener("change", () => { cb.checked ? FILT.types.add(t) : FILT.types.delete(t); msLabel(); applyFilters(); });
    lab.append(cb, document.createTextNode(" " + pretty(t)));
    msList.appendChild(lab);
  }
  const msSetAll = (on) => {
    FILT.types = on ? new Set(ALL_TYPES) : new Set();
    msList.querySelectorAll("input").forEach((cb) => { cb.checked = on; });
    msLabel(); applyFilters();
  };
  $("ms-all").addEventListener("click", () => msSetAll(true));
  $("ms-none").addEventListener("click", () => msSetAll(false));
  msBtn.addEventListener("click", () => {
    const willOpen = msPanel.hasAttribute("hidden");
    msPanel.toggleAttribute("hidden", !willOpen);
    msBtn.setAttribute("aria-expanded", willOpen ? "true" : "false");
  });
  document.addEventListener("click", (ev) => {
    if (!$("ms-type").contains(ev.target) && !msPanel.hasAttribute("hidden")) {
      msPanel.setAttribute("hidden", ""); msBtn.setAttribute("aria-expanded", "false");
    }
  });
  msLabel();
  const bind = (elId, key) => { const el = $(elId); el.addEventListener("change", () => { FILT[key] = el.value; applyFilters(); }); };
  bind("f-month", "month"); bind("f-distance", "distance"); bind("f-county", "county");
  $("f-reset").addEventListener("click", () => {
    FILT.month = "all"; FILT.distance = "all"; FILT.county = "all";
    monthSel.value = "all"; $("f-distance").value = "all"; countySel.value = "all";
    msSetAll(true);
  });
}

// ---------- boot ----------
(async function init() {
  try {
    setStatus("Loading\u2026");
    const meta = await fetchJson("/data/meta.json");
    const doc = await fetchJson("/data/events.json");
    assertShape(meta, doc);
    META = meta;
    EVENTS = doc.events;
    for (const e of EVENTS) {
      if (typeof e.lat === "number" && typeof e.lng === "number") e.distance_mi = haversineMiles(META.home.lat, META.home.lng, e.lat, e.lng);
    }
    eventsById = Object.fromEntries(EVENTS.map((e) => [String(e.id), e]));
    freshEl.textContent = `${META.event_count} event${META.event_count === 1 ? "" : "s"} \u00b7 verified as of ${META.as_of || "\u2014"}`;
    map.setView([META.home.lat, META.home.lng], 7);
    wireFilters();
    setStatus("");
    render(true);
    if (!EVENTS.length) setStatus("No events listed yet.");
    else if (!visibleEvents().length) setStatus("No upcoming events match. Try Reset.");
  } catch (err) {
    renderFatal(err);
  }
})();
```

- [ ] **Step 2: Gates and static checks**

```bash
python pipeline/checks.py                                    # expected: ALL GATES PASS (G6 covers app.js now)
node --test tests/js                                         # expected: all pass
grep -n -i -E "glizzness|midwest event finder" -r site        # expected: nothing
```

- [ ] **Step 3: Commit**

```bash
git add site/js/app.js
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "site: map, list, drawer and data-built filters wired to the predicates

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 11: Browser verification (three states) with a fixture export

**Files:**
- Uses: `pipeline/serve_local.py`, `pipeline/fixtures/negative.csv`; temporary edits to `site/data/` are reverted with `git checkout -- site/data`.
- Test: Playwright (MCP `browser_*` tools) against `http://127.0.0.1:8765/`.

- [ ] **Step 1: Start the local server in the background**

Run: `python pipeline/serve_local.py` (run_in_background). Expected log: `serving 4 security header(s)`.

- [ ] **Step 2: Empty state (the committed publication)**

Navigate to `http://127.0.0.1:8765/`. Expected: header shows `0 events · verified as of —`; `#status` reads `No events listed yet.`; `#error-box` hidden; **zero console errors** (`browser_console_messages`); the CSP header is present on the response (`browser_network_requests` shows `content-security-policy` on `/`).

- [ ] **Step 3: Loaded state (fixture export)**

Run: `python pipeline/export.py --csv pipeline/fixtures/negative.csv --places pipeline/fixtures/places.csv --out site/data` — expected `exported 1 event(s)`.
Reload. Expected: header `1 event · verified as of 2026-08-30`; one dot on the map near Columbia; click it → drawer shows `Published Fest`, badge `festival`, `When 2026-09-12 to 2026-09-13`, `Distance from Columbia, MO 0 mi` (**zero is shown** — trap 6.2), `Last verified 2026-08-30`, an `Event page` link with `rel="noopener"`, no contact text anywhere. Open `List` → `1 in view`. Set month to `Oct` → crumb `0 events`; `Reset` → `1 event`. Types panel shows exactly one checkbox, `Festival`. Zero console errors.

- [ ] **Step 4: Error state (a file removed)**

Run: `mv site/data/meta.json site/data/meta.json.bak`. Reload. Expected: `#error-box` visible with `Failed to load /data/meta.json — HTTP 404`; no dots; `#status` hidden. Restore: `mv site/data/meta.json.bak site/data/meta.json`.

- [ ] **Step 5: Restore the committed publication and stop the server**

```bash
git checkout -- site/data
python pipeline/checks.py     # expected: ALL GATES PASS
git status --short            # expected: empty
```
Stop the background server (TaskStop). Record the three observations (with the exact strings seen) in `CHATLOG.md` under a dated "Browser verification" entry — no screenshot claims, only what the tool output said.

- [ ] **Step 6: Commit the CHATLOG entry**

```bash
git add CHATLOG.md
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "verify: three page states observed in a browser (empty, loaded, error)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 12: README, whole-branch review, push, the one credentialed handoff

**Files:**
- Create: `README.md`
- Modify: `TODO.md` (RESUME block → "built; deployed pending Pages connect"), `CHATLOG.md`

- [ ] **Step 1: Write `README.md`**

```markdown
# EventFinds

A public, curated, filterable map-and-list directory of events. Static JSON published from one
CSV; no database, no server, no framework, $0/month. RapidForge Build 002.

## Add or change an event (the whole workflow)

1. Edit `data/events.csv` (header is fixed - 18 columns; see `pipeline/model.py` for the rules).
   Leave `id` blank for a new row. If the town is new, add it to `data/places.csv` first
   (`city,state,lat,lng` - city centroid; pins show the city, not the venue).
2. `python pipeline/assign_ids.py`     - gives new rows a permanent UUID
3. `python pipeline/export.py`         - writes `site/data/events.json` + `meta.json`; exits 1 naming
                                         any bad row or unknown town
4. `python pipeline/checks.py`         - nine gates; must print ALL GATES PASS
5. `python pipeline/serve_local.py`    - view at http://127.0.0.1:8765/ (production MIME + headers)
6. Commit `data/` AND `site/data/` together; push to `master`. Pages deploys.
7. `python pipeline/verify_deploy.py`  - the origin serves what git holds; exit 0 or it did not deploy

A row is public only when `visibility` is `published` (which also requires `source_url` and
`last_verified`). Draft and retired rows never leave the CSV. The page hides events whose date has
passed (or whose last month has passed when no date exists); it never dims them.

## Tests

    python -m pytest -q          # pipeline
    node --test tests/js         # page predicates and fetch layer

## Deploy

Cloudflare Pages, project `eventfinds`, connected to `lazrexmc/eventfinds`, production branch
`master`, root directory `site`, build command empty, output directory empty. Headers come from
`site/_headers`. There is no custom domain in v1.

## Method

Built from the RapidForge registry: `modules/event-finder.md` (the shape and its 21 traps),
`static-publication-site`, `deploy-runbook`. Decisions and the questionnaire that froze them are in
`CHATLOG.md`; the frozen spec is `docs/superpowers/specs/2026-08-30-eventfinds-v1-design.md`.
```

- [ ] **Step 2: Whole-branch adversarial review** — dispatch a reviewer (superpowers:requesting-code-review) with the spec and this plan; its brief is to *refute*: find any second copy of the gate, any inline style/script, any contact-shaped path, any place an empty state could be rendered from a failure, any non-determinism in the export, any ASCII violation in `.py`. Fix findings at the source (spec/plan first if they are design defects), re-run `python -m pytest -q`, `node --test tests/js`, `python pipeline/checks.py`.

- [ ] **Step 3: Update `TODO.md` and `CHATLOG.md`** — RESUME block: "v1 BUILT (rung one); all gates green; waiting on the one credentialed step: Lance connects Cloudflare Pages (root `site`, no build). Then `python pipeline/verify_deploy.py` must print ALL DEPLOYED (rung two)." CHATLOG: the review round's findings and fixes, verbatim.

- [ ] **Step 4: Final checks and push**

```bash
python -m pytest -q && node --test tests/js && python pipeline/checks.py
grep -nP "[^\x00-\x7F]" pipeline/*.py tests/*.py
grep -n -i -E "glizzness|midwest event finder" -r site pipeline tests data README.md
git add README.md TODO.md CHATLOG.md
git -c user.name="Lance McCarter" -c user.email="lancemccarter1316@hotmail.com" commit -m "docs: README (the workflow), RESUME block; v1 built, awaiting Pages connect

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git push origin master
```

- [ ] **Step 5: The handoff (one message to Lance, batched)** — Cloudflare Dashboard → Workers & Pages → Create → Pages → Connect to Git → `lazrexmc/eventfinds` → production branch `master`, **root directory `site`**, build command *empty*, build output *empty* → Save and Deploy. Trap (deploy-runbook 6.1): the dashboard funnels toward Workers; choose Pages. When he says it is connected: `python pipeline/verify_deploy.py` → expected `ALL DEPLOYED`; record in CHATLOG; message RapidForge with the deposit (event-finder → proven; verify-deploy second consumer ran; any new trap).

---

## Self-review

**Spec coverage.** §1/§2 decisions → Global Constraints + Tasks 1, 4, 9, 12. §3 layout → File structure (every path appears in a task). §4 source contract → Task 1 (`validate_row`), Task 3 (ids). §5 export contract → Task 4 (`EVENT_KEYS`, `meta`, determinism, failure/empty/stale). §6 vocabularies → Task 1 `EVENT_TYPES`; page builds from data → Task 10 `distinctSorted`. §7 page behaviour → Tasks 7 (upcoming/distance/filter), 8 (typed fetch), 9 (shell, CSP, legend, no inline, no base), 10 (map, list, drawer `!= null`, freshness line). §8 gates → Task 5 (G1–G9) + `node --test` (7.5 fixtures in Task 7) + browser states (Task 11). §9 deploy → Task 6 (`verify_deploy`), Task 12 (handoff). §10 out of scope → nothing here builds it.

**Placeholder scan.** No TBD/TODO/"similar to Task N"; every code step carries its code; the browser task lists exact expected strings.

**Type consistency.** `validate_row` returns `months: list[int]`, `featured: bool`, other columns `str | None` — `export.build` reads exactly those; `EVENT_KEYS` in `export.py` is what `checks.g7` imports and what `data.assertShape`/`app.js` consume (`lat`, `lng`, `months`, `featured`, `distance_mi` added page-side only). `passesFilter(e, filt, todayISO, nowMonth)` signature is identical in Task 7's tests and Task 10's `visibleEvents`. `fetchJson(path, fetchImpl)` default parameter keeps the browser call `fetchJson("/data/meta.json")` valid. Element ids in Task 9 match every `$("...")` in Task 10.
