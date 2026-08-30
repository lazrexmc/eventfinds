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
