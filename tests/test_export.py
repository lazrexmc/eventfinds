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
