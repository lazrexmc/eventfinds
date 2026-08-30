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
