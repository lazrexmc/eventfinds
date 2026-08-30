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
