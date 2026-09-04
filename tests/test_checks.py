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


def test_g6_flags_inline_handler_in_index_html(tmp_path):
    js = tmp_path / "js"
    js.mkdir()
    (js / "clean.js").write_text("export const x = 1;\n", encoding="utf-8")
    dirty_html = tmp_path / "index.html"
    dirty_html.write_text("<html><body><button onclick=\"x()\">Go</button></body></html>\n", encoding="utf-8")
    ok, msg = checks.g6_no_gate_in_js(js, dirty_html)
    assert ok is False and "index.html" in msg


def test_g6_passes_a_clean_index_html(tmp_path):
    js = tmp_path / "js"
    js.mkdir()
    (js / "clean.js").write_text("export const x = 1;\n", encoding="utf-8")
    clean_html = tmp_path / "index.html"
    clean_html.write_text("<html><body><script src=\"/js/app.js\" type=\"module\"></script></body></html>\n",
                          encoding="utf-8")
    ok, msg = checks.g6_no_gate_in_js(js, clean_html)
    assert ok is True


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


def test_g5_publication_committed_on_this_repo():
    assert checks.g5_publication_committed()[0] is True


# ---------------------------------------------------------------- G10 -------
# Lesson 5: prove the instrument can produce the OTHER answer before believing
# either. Known-bad must go red and known-good must go green, so a gate that is
# hardwired to pass cannot masquerade as a clean result.

from datetime import date

from model import COLUMNS

FIX_PLACES = Path(__file__).resolve().parent.parent / "pipeline" / "fixtures" / "places.csv"
TODAY = date(2026, 6, 1)


def _csv(tmp_path, *rows):
    """Write a valid events CSV holding the given rows (dicts of column overrides)."""
    lines = [",".join(COLUMNS)]
    for i, over in enumerate(rows, start=1):
        cells = {c: "" for c in COLUMNS}
        cells.update({
            "id": "%08d-1111-4111-8111-111111111111" % i,
            "name": over.get("name", "Fest %d" % i),
            "event_type": "festival",
            "cadence": "annual",
            "city": "Columbia",
            "state": "MO",
            "source_url": "https://example.com/%d" % i,
            "last_verified": "2026-05-01",
            "visibility": "published",
        })
        cells.update(over)
        lines.append(",".join(cells[c] for c in COLUMNS))
    p = tmp_path / "events.csv"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _g10(tmp_path, *rows):
    return checks.g10_dated_rows_not_all_past(
        csv_path=_csv(tmp_path, *rows), places_path=FIX_PLACES, today=TODAY)


def test_g10_red_when_every_published_row_is_dated_and_past(tmp_path):
    ok, msg = _g10(tmp_path,
                   {"start_date": "2026-01-10", "end_date": "2026-01-11"},
                   {"start_date": "2026-03-02", "end_date": "2026-03-02"})
    assert ok is False
    assert "2026-03-02" in msg and "2026-06-01" in msg


def test_g10_green_when_one_published_row_is_still_ahead(tmp_path):
    ok, msg = _g10(tmp_path,
                   {"start_date": "2026-01-10", "end_date": "2026-01-11"},
                   {"start_date": "2026-12-01"})
    assert ok is True
    assert "2026-12-01" in msg


def test_g10_green_on_a_row_dated_exactly_today(tmp_path):
    ok, _ = _g10(tmp_path, {"start_date": "2026-06-01"})
    assert ok is True


def test_g10_green_and_says_so_when_nothing_is_published(tmp_path):
    ok, msg = _g10(tmp_path, {"visibility": "draft", "start_date": "2026-01-10"})
    assert ok is True
    assert "no published rows" in msg


def test_g10_does_not_fire_when_an_undated_row_is_always_shown(tmp_path):
    ok, msg = _g10(tmp_path,
                   {"start_date": "2026-01-10", "end_date": "2026-01-11"},
                   {"name": "Year Round Market"})
    assert ok is True
    assert "carry no date" in msg


def test_g10_is_registered_in_the_gate_list():
    names = [n for n, _ in checks.GATES]
    assert "G10 dated-rows-not-all-past" in names
    assert len(names) == len(set(names))
